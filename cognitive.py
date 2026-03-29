from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import os
from supabase import create_client, ClientOptions
from services.cognitive_service import analyze_typing_patterns, analyze_audio_file, send_wellwisher_alert

cognitive_bp = Blueprint("cognitive", __name__)

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

@cognitive_bp.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    
    # Fetch recent analyses
    try:
        supabase = get_supabase()
        analyses = supabase.table("cognitive_analyses")\
            .select("*")\
            .eq("user_id", session["user"]["id"])\
            .order("created_at", desc=True)\
            .limit(10)\
            .execute()
        recent = analyses.data or []
    except Exception:
        recent = []
    
    return render_template("cognitive/index.html", user=session["user"], 
                           personality=session.get("personality_report"),
                           recent_analyses=recent)

@cognitive_bp.route("/setup-monitoring", methods=["GET", "POST"])
def setup_monitoring():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    
    if request.method == "GET":
        return render_template("cognitive/setup.html", user=session["user"])
    
    data = request.get_json()
    monitored_name = data.get("monitored_name")
    wellwisher_email = data.get("wellwisher_email")
    relationship = data.get("relationship")
    
    try:
        supabase = get_supabase()
        supabase.table("monitoring_setup").upsert({
            "user_id": session["user"]["id"],
            "monitored_name": monitored_name,
            "wellwisher_email": wellwisher_email,
            "relationship": relationship,
            "active": True
        }).execute()
        
        session["monitoring"] = {
            "monitored_name": monitored_name,
            "wellwisher_email": wellwisher_email
        }
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@cognitive_bp.route("/analyze-typing", methods=["POST"])
def analyze_typing():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    patterns = data.get("patterns", {})
    user_name = session["user"]["name"]
    
    try:
        result = analyze_typing_patterns(patterns, user_name)
        
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 400
            
        # Store analysis
        supabase = get_supabase()
        supabase.table("cognitive_analyses").insert({
            "user_id": session["user"]["id"],
            "analysis_type": "typing",
            "patterns_data": patterns,
            "result": result
        }).execute()
        
        # Alert well-wisher if needed
        if result.get("should_alert_wellwisher"):
            monitoring = session.get("monitoring", {})
            if monitoring.get("wellwisher_email"):
                send_status = send_wellwisher_alert(
                    monitoring["wellwisher_email"],
                    user_name,
                    result.get("alert_message", ""),
                    "typing"
                )
                try:
                    supabase.table("cognitive_alerts").insert({
                        "user_id": session["user"]["id"],
                        "alert_message": result.get("alert_message", ""),
                        "alert_type": "typing",
                        "status": "sent" if send_status.get("sent") else "failed"
                    }).execute()
                except Exception as alert_log_err:
                    print(f"Failed to log alert to Supabase: {alert_log_err}")
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@cognitive_bp.route("/analyze-speech", methods=["POST"])
def analyze_speech():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if "audio" not in request.files:
        return jsonify({"error": "No audio provided"}), 400
        
    audio_file = request.files["audio"]
    if audio_file.filename == '':
        return jsonify({"error": "No audio provided"}), 400
        
    user_name = session["user"]["name"]
    
    try:
        import tempfile
        import os
        
        # Save audio file to a temporary file
        ext = os.path.splitext(audio_file.filename)[1] or ".mp3"
        fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        
        try:
            audio_file.save(temp_path)
            result = analyze_audio_file(temp_path, user_name)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        supabase = get_supabase()
        
        if "error" in result:
            return jsonify({"success": False, "error": result["error"]}), 400
            
        supabase.table("cognitive_analyses").insert({
            "user_id": session["user"]["id"],
            "analysis_type": "speech",
            "result": result
        }).execute()
        
        if result.get("should_alert_wellwisher"):
            monitoring = session.get("monitoring", {})
            if monitoring.get("wellwisher_email"):
                send_status = send_wellwisher_alert(
                    monitoring["wellwisher_email"],
                    user_name,
                    result.get("alert_message", ""),
                    "speech"
                )
                try:
                    supabase.table("cognitive_alerts").insert({
                        "user_id": session["user"]["id"],
                        "alert_message": result.get("alert_message", ""),
                        "alert_type": "speech",
                        "status": "sent" if send_status.get("sent") else "failed"
                    }).execute()
                except Exception as alert_log_err:
                    print(f"Failed to log alert to Supabase: {alert_log_err}")
        
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@cognitive_bp.route("/dashboard-data")
def dashboard_data():
    """Real-time data for the monitoring dashboard."""
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        supabase = get_supabase()
        analyses = supabase.table("cognitive_analyses")\
            .select("*")\
            .eq("user_id", session["user"]["id"])\
            .order("created_at", desc=True)\
            .limit(30)\
            .execute()
        
        alerts = supabase.table("cognitive_alerts")\
            .select("*")\
            .eq("user_id", session["user"]["id"])\
            .order("created_at", desc=True)\
            .limit(5)\
            .execute()
        
        return jsonify({
            "analyses": analyses.data or [],
            "alerts": alerts.data or []
        })
    except Exception as e:
        return jsonify({"analyses": [], "alerts": [], "error": str(e)})
