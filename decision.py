from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import os
from supabase import create_client, ClientOptions
from services.decision_service import get_career_decision, get_finance_decision, get_planning_decision, get_career_flowchart, get_omni_decision

decision_bp = Blueprint("decision", __name__)

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

def require_login():
    if "user" not in session:
        return False
    return True

def save_chat_history(domain: str, prompt: str, result: dict):
    """Save chat interaction to Supabase."""
    try:
        supabase = get_supabase()
        supabase.table("chat_history").insert({
            "user_id": session["user"]["id"],
            "domain": domain,
            "prompt": prompt,
            "response": result
        }).execute()
    except Exception:
        pass

@decision_bp.route("/")
def index():
    if not require_login():
        return redirect(url_for("auth.login"))
    return render_template("decision/index.html", user=session["user"],
                           personality=session.get("personality_report"))

@decision_bp.route("/career", methods=["GET"])
def career():
    if not require_login():
        return redirect(url_for("auth.login"))
    return render_template("decision/career.html", user=session["user"],
                           personality=session.get("personality_report"))

@decision_bp.route("/career/analyze", methods=["POST"])
def career_analyze():
    if not require_login():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt.strip():
        return jsonify({"error": "Please enter your career situation"}), 400
    
    try:
        result = get_career_decision(prompt, session.get("personality_report"))
        save_chat_history("career", prompt, result)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@decision_bp.route("/career/flowchart", methods=["POST"])
def career_flowchart():
    if not require_login():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt.strip():
        return jsonify({"error": "Missing career situation"}), 400
        
    try:
        flowchart_markdown = get_career_flowchart(prompt, session.get("personality_report"))
        return jsonify({"success": True, "flowchart": flowchart_markdown})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@decision_bp.route("/finance", methods=["GET"])
def finance():
    if not require_login():
        return redirect(url_for("auth.login"))
    return render_template("decision/finance.html", user=session["user"],
                           personality=session.get("personality_report"))

@decision_bp.route("/finance/analyze", methods=["POST"])
def finance_analyze():
    if not require_login():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt.strip():
        return jsonify({"error": "Please describe your financial situation"}), 400
    
    try:
        result = get_finance_decision(prompt, session.get("personality_report"))
        save_chat_history("finance", prompt, result)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@decision_bp.route("/planning", methods=["GET"])
def planning():
    if not require_login():
        return redirect(url_for("auth.login"))
    return render_template("decision/planning.html", user=session["user"],
                           personality=session.get("personality_report"))

@decision_bp.route("/planning/analyze", methods=["POST"])
def planning_analyze():
    if not require_login():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    prompt = data.get("prompt", "")
    wants_flowchart = data.get("wants_flowchart", False)
    
    if not prompt.strip():
        return jsonify({"error": "Please describe your planning challenge"}), 400
    
    try:
        result = get_planning_decision(prompt, session.get("personality_report"), wants_flowchart)
        save_chat_history("planning", prompt, result)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@decision_bp.route("/omni", methods=["GET"])
def omni():
    if not require_login():
        return redirect(url_for("auth.login"))
    return render_template("decision/omni.html", user=session["user"],
                           personality=session.get("personality_report"))

@decision_bp.route("/omni/analyze", methods=["POST"])
def omni_analyze():
    if not require_login():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt.strip():
        return jsonify({"error": "Please describe your life decision"}), 400
    
    try:
        result = get_omni_decision(prompt, session.get("personality_report"))
        save_chat_history("omni", prompt, {"domains_processed": len(result)})
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@decision_bp.route("/history")
def history():
    if not require_login():
        return redirect(url_for("auth.login"))
    try:
        supabase = get_supabase()
        records = supabase.table("chat_history")\
            .select("*")\
            .eq("user_id", session["user"]["id"])\
            .order("created_at", desc=True)\
            .limit(20)\
            .execute()
        return jsonify({"history": records.data})
    except Exception as e:
        return jsonify({"history": [], "error": str(e)})
