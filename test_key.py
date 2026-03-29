import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

models = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-flash-lite-latest",
    "gemini-3-flash-preview"
]

for m in models:
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Ping")
        print(f"SUCCESS: {m}")
    except Exception as e:
        print(f"FAIL: {m} -> {type(e).__name__}: {str(e)[:50]}")
