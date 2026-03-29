import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    generation_config={"response_mime_type": "application/json"}
)

prompt = """You are an expert behavioral psychologist. Generate exactly 20 unique, highly insightful multiple-choice questions designed to assess the Big Five personality traits. 
The questions must be completely different every single time you are asked. BE CREATIVE. Use unique situational, hypothetical, or behavioral scenarios rather than generic questions. 
Each question must have exactly 4 options.

Return ONLY valid JSON in this exact structure:
[
  {
    "question": "The question text...",
    "options": ["Option A", "Option B", "Option C", "Option D"]
  }
]"""

def generate_batch():
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        qs = json.loads(text)
        return qs if isinstance(qs, list) else []
    except Exception as e:
        print(f"Error generating batch: {e}")
        return []

def run():
    print("Starting generation of 200 questions...")
    all_questions = []
    
    # Generate 10 batches of 20 questions
    for i in range(10):
        print(f"Generating batch {i+1}/10...")
        batch = generate_batch()
        all_questions.extend(batch)
        time.sleep(2) # Give the API a brief rest
        
    print(f"Generated {len(all_questions)} total questions. Formatting and saving...")
    
    # Assign IDs and save
    os.makedirs("../data", exist_ok=True)
    
    final_questions = []
    for idx, q in enumerate(all_questions):
        final_questions.append({
            "id": idx + 1,
            "question": q.get("question", ""),
            "options": q.get("options", [])
        })
        
    with open("../data/questions.json", "w", encoding="utf-8") as f:
        json.dump(final_questions, f, indent=2)
        
    print(f"Successfully saved {len(final_questions)} questions to data/questions.json!")

if __name__ == "__main__":
    run()
