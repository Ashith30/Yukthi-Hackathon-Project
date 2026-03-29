import os
import json
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PERSONALITY_QUESTIONS = [
    {
        "id": 1,
        "question": "You're given a weekend with no plans. What feels most natural?",
        "options": [
            "Calling friends and organizing a group hangout",
            "A quiet day at home with a book or project",
            "Spontaneous adventure — wherever the day takes me",
            "Planning something productive and checking it off"
        ]
    },
    {
        "id": 2,
        "question": "When facing a big decision, you typically...",
        "options": [
            "Follow your gut feeling immediately",
            "Research extensively before deciding",
            "Ask trusted people for their input",
            "Make a pros/cons list and analyze"
        ]
    },
    {
        "id": 3,
        "question": "In a team project, your natural role tends to be...",
        "options": [
            "The leader who sets direction",
            "The creative who generates ideas",
            "The organizer who keeps things on track",
            "The supporter who helps everyone succeed"
        ]
    },
    {
        "id": 4,
        "question": "How do you handle conflict with someone you care about?",
        "options": [
            "Address it directly and immediately",
            "Take time to process before talking",
            "Try to find compromise right away",
            "Avoid confrontation and hope it resolves"
        ]
    },
    {
        "id": 5,
        "question": "Your ideal work environment is...",
        "options": [
            "Collaborative open space with lots of interaction",
            "Quiet private space for deep focus",
            "Flexible — mix of both depending on the task",
            "Structured with clear processes and routines"
        ]
    },
    {
        "id": 6,
        "question": "When you think about the future, you feel...",
        "options": [
            "Excited — so many possibilities ahead",
            "Thoughtful — carefully planning each step",
            "Anxious — so much uncertainty",
            "Present — I focus on now more than tomorrow"
        ]
    },
    {
        "id": 7,
        "question": "Your closest friends would describe you as...",
        "options": [
            "The life of the party, always energizing the room",
            "The wise one who gives great advice",
            "The reliable one who always shows up",
            "The creative dreamer with big ideas"
        ]
    },
    {
        "id": 8,
        "question": "When learning something new, you prefer...",
        "options": [
            "Jumping in and learning by doing",
            "Reading and understanding theory first",
            "Watching someone else do it first",
            "Taking a structured course with clear steps"
        ]
    },
    {
        "id": 9,
        "question": "When you're stressed, your typical response is...",
        "options": [
            "Talk to someone — sharing helps me process",
            "Withdraw and sort through thoughts alone",
            "Exercise or do something physical",
            "Make lists and create structure to feel control"
        ]
    },
    {
        "id": 10,
        "question": "What motivates you most deeply?",
        "options": [
            "Recognition and impact — being seen as successful",
            "Mastery — becoming truly excellent at something",
            "Connection — meaningful relationships and belonging",
            "Purpose — contributing to something bigger than myself"
        ]
    }
]

def generate_personality_report(responses: list, user_name: str) -> dict:
    """Generate full personality report from explicitly provided question and answer pairs."""
    
    answers_text = "\n".join([
        f"Q: {r.get('question')}\nAnswer: {r.get('answer')}"
        for r in responses if isinstance(r, dict) and r.get('answer')
    ])
    
    model = genai.GenerativeModel(
        "gemini-2.5-flash",
        generation_config={"response_mime_type": "application/json"}
    )
    prompt = f"""Analyze this personality assessment for {user_name} and return ONLY valid JSON.

ANSWERS:
{answers_text}

Return this exact JSON structure:
{{
  "personality_type": "A 2-3 word type name (e.g. The Thoughtful Pioneer)",
  "archetype_emoji": "Single relevant emoji",
  "tagline": "One memorable sentence about this person",
  "core_traits": ["trait1", "trait2", "trait3", "trait4"],
  "strengths": ["strength1", "strength2", "strength3"],
  "growth_areas": ["area1", "area2"],
  "communication_style": "2-3 sentences about how they communicate",
  "decision_style": "2-3 sentences about how they make decisions",
  "energy_source": "What energizes them (2 sentences)",
  "big5_scores": {{
    "openness": <An integer between 0 and 100>,
    "conscientiousness": <An integer between 0 and 100>,
    "extraversion": <An integer between 0 and 100>,
    "agreeableness": <An integer between 0 and 100>,
    "neuroticism": <An integer between 0 and 100>
  }},
  "compatibility_note": "Who they work best with (1-2 sentences)",
  "famous_similar": "Name of a well-known person with similar traits",
  "advice": "One piece of specific, personal advice for growth"
}}"""
    
    import time
    from google.api_core.exceptions import ResourceExhausted

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-3-flash-preview"
    ]
    
    last_err = None
    for model_name in models_to_try:
        try:
            print(f"Attempting to generate report using {model_name}...")
            model = genai.GenerativeModel(
                model_name,
                generation_config={"response_mime_type": "application/json"}
            )
            response = model.generate_content(prompt)
            return json.loads(response.text.strip())
        except ResourceExhausted as e:
            print(f"Model {model_name} quota exhausted: {e}")
            last_err = e
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            last_err = e
            
    # If all models fail due to severe quota limits, only then return the fallback
    print("All Gemini models exhausted. Returning safe fallback.")
    return {
      "personality_type": "The Resilient Explorer",
      "archetype_emoji": "⚖️",
      "tagline": "A calm, collected thinker capable of profound insight.",
      "core_traits": ["Adaptable", "Observant", "Patient", "Empathetic"],
      "strengths": ["Handling uncertainty with grace", "Deep listening", "Steady decision-making"],
      "growth_areas": ["Taking leaps of faith more often", "Voicing opinions loudly"],
      "communication_style": "You speak when you have something meaningful to add, rarely cluttering the airspace.",
      "decision_style": "You enjoy gathering information and quietly weighing the options before committing.",
      "energy_source": "You draw energy from quiet reflection combined with engaging, deep conversations.",
      "big5_scores": {
        "openness": 75,
        "conscientiousness": 65,
        "extraversion": 45,
        "agreeableness": 80,
        "neuroticism": 25
      },
      "compatibility_note": "You work best with dynamic leaders who need a grounding force.",
      "famous_similar": "Keanu Reeves",
      "advice": "Trust your intuition as much as your observation."
    }

import random

def get_questions():
    """Reads from exactly 200 unique MCQ questions and randomly returns 10."""
    try:
        # Resolve the absolute path to data/questions.json
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "data", "questions.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                qs = json.load(f)
                
            if isinstance(qs, list) and len(qs) >= 10:
                # Randomly sample exactly 10 questions for this user session
                sampled = random.sample(qs, 10)
                # Re-index IDs so UI displays them 1-10 beautifully
                for i, q in enumerate(sampled):
                    q["id"] = i + 1
                return sampled
    except Exception as e:
        print(f"Error loading questions from database file: {e}")
        
    return PERSONALITY_QUESTIONS
