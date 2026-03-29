import os
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from routes.auth import auth_bp
from routes.assessment import assessment_bp
from routes.decision import decision_bp
from routes.cognitive import cognitive_bp

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "cogni-guard-secret-2024")
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(assessment_bp, url_prefix="/assessment")
app.register_blueprint(decision_bp, url_prefix="/decision")
app.register_blueprint(cognitive_bp, url_prefix="/cognitive")

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth.login"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    user = session["user"]
    personality = session.get("personality_report", None)
    return render_template("dashboard/index.html", user=user, personality=personality)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
