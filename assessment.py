from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, Response
import os
import json
from supabase import create_client, ClientOptions
from services.personality_service import (
    generate_personality_report,
    get_questions
)

assessment_bp = Blueprint("assessment", __name__)

import time
import jwt

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_KEY"))
    
    # If using anon key, we pass the user's token. We must check for expiration to prevent raw RLS database errors.
    if "user" in session and "access_token" in session["user"] and not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        try:
            decoded = jwt.decode(session["user"]["access_token"], options={"verify_signature": False})
            if decoded.get("exp", 0) < time.time():
                session.clear() # Clear the stale Flask session
                raise ValueError("Your login session token has expired. Please log out and log in again.")
        except Exception as e:
            if "expired" in str(e):
                raise e
                
        options = ClientOptions(headers={"Authorization": f"Bearer {session['user']['access_token']}"})
        # Explicitly returning it with ClientOptions bypassing GoTrue state issues
        return create_client(url, key, options=options)
        
    return create_client(url, key)

@assessment_bp.route("/quiz")
def quiz():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    questions = get_questions()
    return render_template("assessment/quiz.html", questions=questions, user=session["user"])

@assessment_bp.route("/submit", methods=["POST"])
def submit():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    answers = data.get("answers", [])
    user_name = session["user"]["name"]
    
    try:
        report = generate_personality_report(answers, user_name)
        
        # Save to Supabase
        supabase = get_supabase()
        supabase.table("profiles").update({
            "personality_report": report,
            "assessment_answers": answers
        }).eq("user_id", session["user"]["id"]).execute()
        
        session["personality_report"] = report
        return jsonify({"success": True, "report": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@assessment_bp.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    
    personality = session.get("personality_report")
    if not personality:
        return redirect(url_for("assessment.quiz"))
    
    return render_template("assessment/report.html", report=personality, user=session["user"])

@assessment_bp.route("/update-trait", methods=["POST"])
def update_trait():
    """Allow user to correct a personality insight."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    field = data.get("field")
    value = data.get("value")
    
    report = session.get("personality_report", {})
    if field in report:
        report[field] = value
        session["personality_report"] = report
        
        supabase = get_supabase()
        supabase.table("profiles").update({
            "personality_report": report
        }).eq("user_id", session["user"]["id"]).execute()
    
    return jsonify({"success": True})
