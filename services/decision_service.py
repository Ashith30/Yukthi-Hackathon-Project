import os
import requests
import json
import google.generativeai as genai

# Clients
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

FRED_KEY = os.getenv("FRED_API_KEY")
AV_KEY = os.getenv("ALPHA_VANTAGE_KEY")


# ─────────────────────────────────────────────
# CAREER DECISION MAKING
# ─────────────────────────────────────────────

def get_career_decision(user_prompt: str, personality: dict) -> dict:
    """Creates a 'digital twin' scenario and career advice."""
    
    personality_ctx = ""
    if personality:
        personality_ctx = f"""
User's personality profile:
- Type: {personality.get('personality_type', 'Unknown')}
- Core traits: {', '.join(personality.get('core_traits', []))}
- Strengths: {', '.join(personality.get('strengths', []))}
- Decision style: {personality.get('decision_style', '')}
- Growth areas: {', '.join(personality.get('growth_areas', []))}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""You are a master career guidance AI. Analyze the user's career situation and return ONLY valid JSON. 

{personality_ctx}

User's career query/situation:
"{user_prompt}"

INSTRUCTION: You must strictly tailor every single piece of advice using their exact personality profile. Do not give generic advice. E.g., if their growth area is 'public speaking', push them to address it. If their trait is 'highly analytical', suggest paths requiring deep focus. It must be valid, reasonable, and highly effective for THEIR personality.

Create a response as if you are their "digital twin" — you deeply understand their thinking, BUT you also see their blind spots. Return this JSON:

{{
  "twin_thinking": "2-3 sentences narrating what the user is probably thinking/planning right now (first person, as their twin)",
  "blind_spot": "The key thing they might be missing or underestimating based on their growth areas (1-2 sentences, direct)",
  "path_assessment": {{
    "current_direction": "Description of their current trajectory",
    "alignment_score": 78,
    "alignment_label": "Excellent Alignment / Needs Adjustment / Course Correction Needed"
  }},
  "immediate_advice": "Specific, actionable advice for right now deeply tied to their personality traits (2-3 sentences)",
  "skill_gaps": ["skill1", "skill2", "skill3"],
  "skill_strengths": ["strength1", "strength2"],
  "3_month_action": ["Action 1", "Action 2", "Action 3"],
  "6_month_milestone": "What success looks like in 6 months",
  "market_insight": "1-2 sentences about the current job market relevant to their field",
  "salary_range": "Realistic salary range if applicable (or N/A)",
  "encouragement": "One genuine, specific encouraging statement tailored to their emotional energy source"
}}"""
    
    import time
    from google.api_core.exceptions import ResourceExhausted

    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3-flash-preview"]
    
    last_err = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name, generation_config={"response_mime_type": "application/json"})
            response = model.generate_content(prompt)
            return json.loads(response.text.strip())
        except ResourceExhausted as e:
            last_err = e
        except Exception as e:
            last_err = e
            
    # Fallback to prevent app crash
    return {
      "twin_thinking": "I am looking for the next step in my career, but I'm unsure which path offers the best balance.",
      "blind_spot": "You might be prioritizing immediate comfort over long-term strategic positioning.",
      "path_assessment": {"current_direction": "Exploring options", "alignment_score": 50, "alignment_label": "Needs Adjustment"},
      "immediate_advice": "Take an hour this week to explicitly map out where you want to be in 5 years, regardless of your current role.",
      "skill_gaps": ["Strategic Planning", "Networking"],
      "skill_strengths": ["Adaptability", "Observation"],
      "3_month_action": ["Update your resume", "Reach out to 3 industry peers", "Research alternative roles"],
      "6_month_milestone": "Secured interviews or transitioned into a trial project.",
      "market_insight": "The market currently rewards specialized skills combined with strong communication abilities.",
      "salary_range": "Market average",
      "encouragement": "You have the analytical skills to figure this out. Trust your process."
    }

def get_career_flowchart(user_prompt: str, personality: dict) -> str:
    """Generates a highly personalized, efficient Mermaid.js flowchart mapping the user's career path."""
    
    personality_ctx = ""
    if personality:
        personality_ctx = f"Personality Type: {personality.get('personality_type', 'Unknown')}. Core traits: {', '.join(personality.get('core_traits', []))}. Decision style: {personality.get('decision_style', '')}. Growth areas: {', '.join(personality.get('growth_areas', []))}."
        
    prompt = f"""You are an elite career strategist. The user wants a highly detailed, realistic, and efficient flowchart mapping out their career path based on their situation and personality.
    
User Situation: "{user_prompt}"
{personality_ctx}

INSTRUCTION: Create a highly tailored Mermaid.js graph (graph TD). 
- Do NOT use markdown backticks around your response. Return ONLY the raw Mermaid syntax.
- The chart should map out Step 1 to Step 5 (milestones), with decision branches where necessary.
- It MUST be realistic and efficient, customized heavily for their specific personality type.
- IMPORTANT: ALWAYS wrap node text in double quotes to prevent syntax errors. Example: id["Label (Extra Info)"]
- Keep node text concise and highly readable.
- If there are options, use diamond shapes {{}}.

Example output format strictly:
graph TD
    A["Start: 12-Month Plan"] --> B["Skill Assessment"]
    B --> C{{"Choose Path"}}
    C -->|"High Risk"| D["Startup Option"]
    C -->|"Stability"| E["Corporate Option"]
    ...
"""

    import time
    from google.api_core.exceptions import ResourceExhausted
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3-flash-preview"]
    
    last_err = None
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Clean up markdown output commonly forced by LLM
            if "```mermaid" in text:
                text = text.split("```mermaid")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1]
            return text.strip()
        except ResourceExhausted as e:
            last_err = e
        except Exception as e:
            last_err = e
            
    # Generic fallback flowchart
    return """graph TD
    Start[User Journey Beginning] --> Assess(Evaluate Current Skills)
    Assess --> Goal{{Define 5-Year Goal}}
    Goal -->|Upskill Needed| Learn[Take Certified Courses]
    Goal -->|Ready to Pivot| Apply[Targeted Applications]
    Learn --> Apply
    Apply --> Inter[Interview Cycles]
    Inter --> Offer[Secure New Role]"""



# ─────────────────────────────────────────────
# FINANCE DECISION MAKING
# ─────────────────────────────────────────────

def get_fred_data(series_id: str) -> dict:
    """Fetch economic data from FRED."""
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_KEY,
            "file_type": "json",
            "limit": 5,
            "sort_order": "desc"
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        obs = data.get("observations", [])
        if obs:
            return {"value": obs[0]["value"], "date": obs[0]["date"], "series": series_id}
        return {}
    except Exception:
        return {}

def get_stock_data(symbol: str) -> dict:
    """Fetch stock/market data from Alpha Vantage."""
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": AV_KEY
        }
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        quote = data.get("Global Quote", {})
        if quote:
            return {
                "symbol": symbol,
                "price": quote.get("05. price", "N/A"),
                "change_pct": quote.get("10. change percent", "N/A"),
                "volume": quote.get("06. volume", "N/A")
            }
        return {}
    except Exception:
        return {}

def get_finance_decision(user_prompt: str, personality: dict) -> dict:
    """Finance decision with real market data context."""
    
    # Gather relevant economic data
    econ_data = {}
    prompt_lower = user_prompt.lower()
    
    if any(w in prompt_lower for w in ["inflation", "cost", "price", "budget"]):
        econ_data["inflation"] = get_fred_data("CPIAUCSL")
    if any(w in prompt_lower for w in ["interest", "loan", "mortgage", "debt", "rate"]):
        econ_data["fed_funds_rate"] = get_fred_data("FEDFUNDS")
    if any(w in prompt_lower for w in ["job", "unemployment", "salary", "work", "income"]):
        econ_data["unemployment"] = get_fred_data("UNRATE")
    if any(w in prompt_lower for w in ["gdp", "economy", "recession", "growth"]):
        econ_data["gdp_growth"] = get_fred_data("A191RL1Q225SBEA")
    
    # Stock data if mentioned
    stocks = {}
    common_tickers = ["AAPL", "TSLA", "GOOGL", "MSFT", "NIFTY50", "SPY", "QQQ", "AMZN"]
    for ticker in common_tickers:
        if ticker.lower() in prompt_lower:
            stocks[ticker] = get_stock_data(ticker)

    econ_ctx = json.dumps(econ_data, indent=2) if econ_data else "No specific economic data fetched"
    stocks_ctx = json.dumps(stocks, indent=2) if stocks else "No specific stocks mentioned"
    
    personality_ctx = ""
    if personality:
        personality_ctx = f"User personality: {personality.get('personality_type')}, traits: {', '.join(personality.get('core_traits', []))}"

    prompt = f"""You are a personal finance advisor with access to real economic data. Return ONLY valid JSON.

{personality_ctx}

User's financial question:
"{user_prompt}"

Real economic context:
{econ_ctx}

Stock data:
{stocks_ctx}

Return this JSON:
{{
  "situation_summary": "Brief summary of what the user is considering (2 sentences)",
  "risk_level": "Low / Medium / High / Very High",
  "risk_explanation": "Why this risk level (1-2 sentences)",
  "economic_context": "How current economic conditions affect this decision (2-3 sentences referencing the real data if available)",
  "recommendation": "Clear, specific recommendation (3-4 sentences)",
  "do_this": ["Action 1", "Action 2", "Action 3"],
  "avoid_this": ["Pitfall 1", "Pitfall 2"],
  "timeline": "Recommended timeline for this decision",
  "data_insights": "Key insight from economic data (or general market wisdom if no data)",
  "alternatives": ["Alternative approach 1", "Alternative approach 2"],
  "emergency_check": "Question to ask yourself before proceeding",
  "confidence_score": 85, 
  "disclaimer": "Brief appropriate financial disclaimer"
}}
IMPORTANT: Replace 85 with your actual dynamic integer confidence score between 1 and 100!
"""

    from google.api_core.exceptions import ResourceExhausted
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3-flash-preview"]
    
    last_err = None
    text = ""
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json\n"):
                    text = text[5:]
                elif text.startswith("json"):
                    text = text[4:]
            text = text.strip()
            break
        except ResourceExhausted as e:
            last_err = e
        except Exception as e:
            last_err = e

    if not text:
        # Fallback dictionary if all fail due to quota
        return {
            "situation_summary": "Evaluating financial situation",
            "risk_level": "Medium",
            "risk_explanation": "Insufficient data to accurately grade risk without AI analysis.",
            "economic_context": "The AI is currently heavily overloaded. Please try again soon.",
            "recommendation": "Pause major financial commitments until a detailed analysis can be generated.",
            "do_this": ["Review your budget manually"],
            "avoid_this": ["Impulse commitments"],
            "timeline": "Revisit in 2 hours",
            "data_insights": "Analysis paused due to network limit.",
            "alternatives": ["Consult with a human financial advisor"],
            "emergency_check": "Is this expense strictly necessary right now?",
            "confidence_score": 20,
            "disclaimer": "This is a fallback placeholder. System is rate-limited.",
            "econ_data_used": econ_data,
            "stocks_used": stocks
        }
            
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {"error": "Failed to parse JSON response"}
        
    result["econ_data_used"] = econ_data
    result["stocks_used"] = stocks
    return result


# ─────────────────────────────────────────────
# PRODUCTIVE PLANNING (GEMINI)
# ─────────────────────────────────────────────

def get_planning_decision(user_prompt: str, personality: dict, wants_flowchart: bool = False) -> dict:
    """Productivity planning using Google Gemini."""
    
    personality_ctx = ""
    if personality:
        personality_ctx = f"User Personality: {personality.get('personality_type', 'Unknown')}. Traits: {', '.join(personality.get('core_traits', []))}."
        
    mermaid_instruction = ""
    if wants_flowchart:
        mermaid_instruction = ',\n  "mermaid_flowchart": "Generate a chronologically sequenced Mermaid.js graph TD diagram representing the roadmap for this plan. Start with graph TD.\\nIMPORTANT: ALWAYS wrap node text in double quotes to prevent syntax errors e.g. A[\\"Phase 1 (Start)\\"]\\nExample:\\ngraph TD\\nA[\\"Goal\\"] --> B[\\"Phase 1\\"]\\nB --> C[\\"Phase 2\\"]\\nreturn ONLY the raw mermaid string syntax (use \\\\n for newlines in JSON). No markdown ticks inside the string."'
        
    prompt = f"""You are an elite productivity and strategic planning AI. The user needs a concrete plan to achieve a specific goal.
{personality_ctx}

User's goal/situation:
"{user_prompt}"

Return ONLY valid JSON matching this exact structure, with NO markdown formatting outside the JSON:
{{
  "goal_clarity": "One brutal, clear sentence clarifying what they are actually trying to achieve.",
  "complexity_level": "Low/Medium/High/Extreme",
  "planning_framework": "Name of best framework (e.g. OKRs, Timeblocking, Deep Work)",
  "framework_explanation": "Why this framework perfectly fits their situation and personality.",
  "weekly_schedule": [
    {{"day": "Monday", "focus": "Theme", "tasks": ["Task 1", "Task 2"]}},
    {{"day": "Tuesday", "focus": "Theme", "tasks": ["Task 1", "Task 2"]}},
    {{"day": "Wednesday", "focus": "Theme", "tasks": ["Task 1", "Task 2"]}},
    {{"day": "Thursday", "focus": "Theme", "tasks": ["Task 1", "Task 2"]}},
    {{"day": "Friday", "focus": "Theme", "tasks": ["Task 1", "Task 2"]}},
    {{"day": "Saturday", "focus": "Rest/Review", "tasks": ["Task 1"]}},
    {{"day": "Sunday", "focus": "Rest/Review", "tasks": ["Task 1"]}}
  ],
  "priority_matrix": {{
    "urgent_important": ["Task 1"],
    "not_urgent_important": ["Task 1"],
    "urgent_not_important": ["Task 1"],
    "neither": ["Task 1"]
  }},
  "energy_optimization": "1 sentence advice on when they should execute the hardest tasks based on normal energy curves.",
  "blockers": ["Potential blocker 1", "Potential blocker 2"],
  "quick_wins": ["Instant action they can do today"],
  "30_day_milestone": "Exact state they should reach in 30 days.",
  "90_day_vision": "Exact state they should reach in 90 days.",
  "daily_non_negotiables": ["Daily Habit 1", "Daily Habit 2"],
  "tools_recommended": ["Tool 1", "Tool 2"],
  "motivation_strategy": "A harsh, direct strategy to keep them disciplined rather than relying on motivation."{mermaid_instruction}
}}
"""
    
    from google.api_core.exceptions import ResourceExhausted
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3-flash-preview"]
    
    last_err = None
    text = ""
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip().lstrip("```json").rstrip("```").strip()
            break
        except ResourceExhausted as e:
            last_err = e
        except Exception as e:
            last_err = e

    if not text:
        return {
          "goal_clarity": "Server is hitting a rate limit block. Unable to assess goal.",
          "complexity_level": "Unknown",
          "planning_framework": "Retry Later",
          "framework_explanation": "The AI is currently resting due to quota limits.",
          "weekly_schedule": [
            {"day": "Information", "focus": "System Pause", "tasks": ["Please try again in 5 minutes"]}
          ],
          "priority_matrix": {
            "urgent_important": [], "not_urgent_important": [], "urgent_not_important": [], "neither": []
          },
          "energy_optimization": "Conserve your energy until the servers return.",
          "blockers": ["API Rate Limits"],
          "quick_wins": ["Taking a break"],
          "30_day_milestone": "Unknown",
          "90_day_vision": "Unknown",
          "daily_non_negotiables": [],
          "tools_recommended": [],
          "motivation_strategy": "Patience is a virtue."
        }

    try:
        return json.loads(text)
    except Exception:
        return {"error": "Failed to parse JSON response"}


# ─────────────────────────────────────────────
# OMNI-DOMAIN UNIVERSAL DECISION ENGINE
# ─────────────────────────────────────────────

def get_omni_decision(user_prompt: str, personality: dict) -> list:
    """Universal domain analysis generating a nested mind map of constraints."""
    
    personality_ctx = ""
    if personality:
        personality_ctx = f"""
User Profile: {personality.get('personality_type', 'Unknown')}
Traits: {', '.join(personality.get('core_traits', []))}
Growth: {', '.join(personality.get('growth_areas', []))}
"""

    prompt = f"""You are an elite, ultra-advanced universal systems architect. The user is facing a complex decision or life situation.
You must brutally dissect their situation across MULTIPLE relevant domains (e.g., Financial, Career, Emotional, Legal, Logistics, Technical, whatever applies).
Do not write paragraphs. Return ONLY a strict JSON Array of Objects.

{personality_ctx}

User's situation/query:
"{user_prompt}"

INSTRUCTIONS:
- Identify between 3 to 6 distinct domains this decision impacts.
- For each domain, generate a strict evaluation object tailored to their personality traits.
- Use brutally short, actionable sentences.

Return this EXACT JSON Array format:
[
  {{
    "domain": "Name of Domain (e.g. Financial Liability)",
    "bottom_line": "1 brutal truth sentence summarizing the core issue here",
    "complexity": 75, // Integer (1-100) indicating how hard this domain is to solve
    "do_this": ["Action item 1", "Action item 2", "Action item 3"],
    "avoid_this": ["Pitfall to avoid 1", "Pitfall to avoid 2"],
    "critical_metrics": ["Metric to track 1", "Metric to track 2"]
  }},
  // ... more domains
]
"""
    
    from google.api_core.exceptions import ResourceExhausted
    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3-flash-preview"]
    
    last_err = None
    text = ""
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip().lstrip("```json").rstrip("```").strip()
            # If it's still prefixed with ```
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            break
        except ResourceExhausted as e:
            last_err = e
        except Exception as e:
            last_err = e

    if not text:
        return [
            {
                "domain": "System Diagnostic",
                "bottom_line": "The Universal Architect AI is currently resting due to maximum rate limits.",
                "complexity": 100,
                "do_this": ["Wait 5 minutes", "Refresh the portal"],
                "avoid_this": ["Panic", "Spamming the analyze button"],
                "critical_metrics": ["Time elapsed"]
            }
        ]

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "error" in parsed:
            return [parsed]
        if isinstance(parsed, dict) and len(parsed) == 1:
            # Handle if the AI wrapped the array in a dict key like {"domains": [...]}
            key = list(parsed.keys())[0]
            if isinstance(parsed[key], list):
                return parsed[key]
        return parsed
    except Exception:
        return [{"domain": "Parsing Error", "bottom_line": "AI returned invalid JSON array."}]
