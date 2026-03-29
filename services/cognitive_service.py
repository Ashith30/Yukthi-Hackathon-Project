import os
import json
import google.generativeai as genai
import assemblyai as aai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# ──────────────────────────────────────────────
# TYPING PATTERN ANALYSIS
# ──────────────────────────────────────────────

def analyze_typing_patterns(patterns: dict, user_name: str) -> dict:
    """Analyze typing patterns for cognitive markers."""
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""You are a neurology-aware AI assistant analyzing typing behavior for early cognitive change signals.
IMPORTANT: You are NOT a doctor. This is for screening/awareness only, not diagnosis.

User: {user_name}
Typing data collected:
- Average WPM: {patterns.get('avg_wpm', 0)}
- WPM variance: {patterns.get('wpm_variance', 0)}
- Backspace rate: {patterns.get('backspace_rate', 0):.1%}
- Average pause between words (ms): {patterns.get('avg_pause_ms', 0)}
- Long pauses (>3s): {patterns.get('long_pause_count', 0)}
- Session duration (minutes): {patterns.get('session_minutes', 0)}
- Total keystrokes: {patterns.get('total_keystrokes', 0)}
- Error correction rate: {patterns.get('error_rate', 0):.1%}
- Rhythm consistency score (0-100): {patterns.get('rhythm_score', 80)}

Return ONLY valid JSON:
{{
  "overall_score": 85,
  "status": "Normal / Mild Signal / Moderate Signal / Consult Recommended",
  "status_color": "green / yellow / orange / red",
  "summary": "2-3 sentence summary of findings",
  "observations": [
    {{"marker": "Typing speed", "value": "72 WPM", "assessment": "Within normal range", "flag": false}},
    {{"marker": "Error rate", "value": "8%", "assessment": "Slightly elevated", "flag": true}}
  ],
  "positive_signs": ["Positive observation 1", "Positive observation 2"],
  "alert_signals": [],
  "recommendation": "Specific recommendation based on findings",
  "should_alert_wellwisher": false,
  "alert_message": "",
  "next_check_in_days": 7
}}"""
    
    response = model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json\n"):
            text = text[5:]
        elif text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        analysis = json.loads(text)
        analysis.setdefault("recommendation", "Typing patterns look normal. No immediate action required.")
        analysis.setdefault("status", "Analysis Complete")
        analysis.setdefault("status_color", "green")
        analysis.setdefault("observations", [])
        return analysis
    except json.JSONDecodeError as err:
        return {"error": "Failed to evaluate typing patterns. Please try again with longer text."}

# ──────────────────────────────────────────────
# SPEECH / CALL ANALYSIS
# ──────────────────────────────────────────────

def analyze_audio_file(audio_url: str, user_name: str) -> dict:
    """Analyze audio for cognitive speech markers using AssemblyAI."""
    
    try:
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            sentiment_analysis=True,
            auto_highlights=True,
            speech_threshold=0.1
        )
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_url, config=config)
        
        if transcript.status == aai.TranscriptStatus.error:
            return {"error": f"Transcription failed: {transcript.error}"}
            
        if not transcript.text or len(transcript.text.split()) < 3:
            return {"error": "Audio contains too little speech to effectively analyze. Please upload a longer or clearer recording."}
        
        speech_data = {
            "text": transcript.text or "",
            "words": len((transcript.text or "").split()),
            "confidence": transcript.confidence or 0,
            "audio_duration": transcript.audio_duration or 0,
            "sentiment": transcript.sentiment_analysis or []
        }
        
        # Analyze for cognitive markers with Gemini
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""Analyze this speech transcript for early cognitive change indicators.
This is NOT medical diagnosis — it's a wellness screening tool.

User: {user_name}
Transcript: "{speech_data['text']}"
Word count: {speech_data['words']}
Confidence: {speech_data['confidence']:.2%}
Duration: {speech_data['audio_duration']}s
Speech rate: {speech_data['words'] / max(speech_data['audio_duration']/60, 0.1):.1f} words/min

Return ONLY valid JSON:
{{
  "speech_score": 88,
  "status": "Normal / Mild Signal / Moderate Signal / Consult Recommended",
  "status_color": "green / yellow / orange / red",
  "speech_rate_assessment": "Assessment of speaking pace",
  "coherence_score": 90,
  "vocabulary_richness": "High / Moderate / Low",
  "observations": ["Observation 1", "Observation 2"],
  "positive_signs": ["Good sign 1"],
  "alert_signals": [],
  "should_alert_wellwisher": false,
  "alert_message": "",
  "recommendation": "Specific recommendation",
  "transcript_excerpt": "First 200 chars of transcript"
}}"""
        
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json\n"):
                text = text[5:]
            elif text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        analysis = json.loads(text)
        
        # Ensure default values for required keys that Gemini might omit
        analysis.setdefault("recommendation", "Continue monitoring speech patterns. Consider discussing with a healthcare professional if you have ongoing concerns.")
        analysis.setdefault("status", "Analysis Complete")
        analysis.setdefault("status_color", "green")
        analysis.setdefault("observations", [])
        analysis.setdefault("positive_signs", [])
        analysis.setdefault("alert_signals", [])
        
        analysis["full_transcript"] = speech_data["text"]
        return analysis
        
    except json.JSONDecodeError as json_err:
        return {"error": "Failed to parse analysis results from AI. Please try again or provide a different recording.", "details": str(json_err)}
    except Exception as e:
        return {"error": str(e), "status": "Error", "status_color": "red"}


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_wellwisher_alert(wellwisher_email: str, patient_name: str, alert_message: str, analysis_type: str):
    """Send email alert to well-wisher via SMTP."""
    sender_email = os.getenv("MAIL_USERNAME")
    sender_password = os.getenv("MAIL_PASSWORD")
    smtp_server = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("MAIL_PORT", 587))
    
    if not sender_email or not sender_password:
        print("Warning: MAIL_USERNAME and MAIL_PASSWORD are not set in .env")
        return {
            "sent": False,
            "error": "Email credentials not configured in environment variables."
        }
        
    msg = MIMEMultipart()
    msg['From'] = f"YUKTHI Alerts <{sender_email}>"
    msg['To'] = wellwisher_email
    msg['Subject'] = f"Cognitive Alert for {patient_name} — YUKTHI"
    
    body = (
        f"Hello,\n\n"
        f"We are reaching out from YUKTHI because you are the designated well-wisher for {patient_name}.\n\n"
        f"Our recent {analysis_type} assessment has detected potential cognitive changes that may require your attention.\n\n"
        f"Alert Details:\n{alert_message}\n\n"
        f"Please check in with {patient_name} when you get a chance.\n\n"
        f"Stay well,\nThe YUKTHI System"
    )
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, wellwisher_email, msg.as_string())
        server.quit()
        return {"sent": True, "to": wellwisher_email}
    except Exception as e:
        print(f"Failed to send SMTP email: {e}")
        return {"sent": False, "error": str(e)}
