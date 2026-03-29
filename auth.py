from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import os
from supabase import create_client, ClientOptions

auth_bp = Blueprint("auth", __name__)

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
        client = create_client(url, key, options=options)
        
        # Supabase v2 Python client requires explictly setting session for RLS to evaluate auth.uid()
        refresh_token = session["user"].get("refresh_token", "dummy-refresh-token")
        try:
            client.auth.set_session(session["user"]["access_token"], refresh_token)
        except Exception:
            pass # Suppress refresh failures if dummy token is used, as access_token is already valid
            
        return client
        
    return create_client(url, key)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    try:
        supabase = get_supabase()
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user_data = {
            "id": res.user.id,
            "email": res.user.email,
            "name": res.user.user_metadata.get("name", email.split("@")[0]),
            "access_token": res.session.access_token
        }
        session["user"] = user_data
        
        # Load existing personality report if available
        profile = supabase.table("profiles").select("*").eq("user_id", res.user.id).execute()
        if profile.data:
            session["personality_report"] = profile.data[0].get("personality_report")
        
        return jsonify({"success": True, "has_assessment": bool(session.get("personality_report"))})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")
    
    try:
        supabase = get_supabase()
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"name": name}}
        })
        
        # Create profile row
        supabase.table("profiles").insert({
            "user_id": res.user.id,
            "name": name,
            "email": email,
            "personality_report": None
        }).execute()
        
        return jsonify({"success": True, "message": "Account created! Please verify your email."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

@auth_bp.route("/check")
def check_session():
    if "user" in session:
        return jsonify({"authenticated": True, "user": session["user"]})
    return jsonify({"authenticated": False}), 401
