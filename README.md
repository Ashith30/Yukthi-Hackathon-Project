# 🧠 YUKTHI — Complete Setup Guide

A full-stack AI-powered platform for personality-driven decision making and early cognitive health monitoring.

---

## 🗂️ Project Structure

```
yukthi_guard/
├── app.py                    ← Main Flask application (entry point)
├── requirements.txt          ← Python dependencies
├── .env.example              ← Copy this to .env and fill keys
├── supabase_schema.sql       ← Run this in Supabase SQL Editor
│
├── routes/
│   ├── auth.py               ← Login, register, logout
│   ├── assessment.py         ← Personality quiz & report
│   ├── decision.py           ← Career, finance, planning
│   └── cognitive.py          ← Typing & speech analysis
│
├── services/
│   ├── personality_service.py  ← Claude AI personality analysis
│   ├── decision_service.py     ← Career (Claude) + Finance (FRED/AV) + Planning (Gemini)
│   └── cognitive_service.py    ← AssemblyAI speech + Claude typing analysis
│
├── templates/
│   ├── base.html             ← Layout with sidebar
│   ├── landing.html
│   ├── auth/login.html
│   ├── auth/register.html
│   ├── assessment/quiz.html
│   ├── assessment/report.html
│   ├── dashboard/index.html
│   ├── decision/index.html
│   ├── decision/career.html
│   ├── decision/finance.html
│   ├── decision/planning.html
│   └── cognitive/index.html
│
└── static/
    ├── css/main.css          ← Full design system
    └── js/main.js            ← UI utilities & renderers
```

---

## 🛠️ APIs & Services Used

| Service | Purpose | Free Tier | Sign Up |
|---------|---------|-----------|---------|
| **Supabase** | Database + Auth (users, profiles, history) | 500MB + 50k auth | supabase.com |
| **Anthropic Claude** | Personality analysis, career twin, cognitive analysis | $5 free credit | console.anthropic.com |
| **Google Gemini** | Productive planning module | Free (15 RPM) | aistudio.google.com |
| **FRED API** | US economic data (inflation, rates, GDP) | Completely free | fred.stlouisfed.org/docs/api/api_key.html |
| **Alpha Vantage** | Stock/market data | 25 req/day free | alphavantage.co/support/#api-key |
| **AssemblyAI** | Speech transcription + analysis | 5 hours/month free | assemblyai.com |

---

## ⚙️ Step-by-Step Setup (Complete Beginner Guide)

### STEP 1: Install Python

1. Go to **python.org/downloads** → Download Python 3.11+
2. During install: ✅ Check "Add Python to PATH"
3. Open terminal/command prompt and verify:
   ```
   python --version
   ```

---

### STEP 2: Download the Project

Option A — If you have Git:
```bash
git clone <your-repo-url>
cd yukthi_guard
```

Option B — Just copy the project folder to your computer.

---

### STEP 3: Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# You'll see (venv) at the start of your terminal line
```

---

### STEP 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: Flask, Anthropic, Google Gemini, Supabase, AssemblyAI, requests, etc.

---

### STEP 5: Set Up Supabase (Free Database)

1. Go to **supabase.com** → Sign Up (free)
2. Click **"New Project"** → Name it "cogni-guard"
3. Wait ~2 min for project to initialize
4. Go to **Settings → API** in your Supabase dashboard
5. Copy:
   - **Project URL** (looks like: `https://abcxyz.supabase.co`)
   - **anon public key** (long string starting with `eyJ...`)
6. Go to **SQL Editor** in Supabase sidebar
7. Paste the entire contents of `supabase_schema.sql` → Click **Run**
8. Go to **Authentication → Settings** → Enable Email confirmations (or disable for testing)

---

### STEP 6: Get Your API Keys

**Anthropic Claude:**
1. Go to console.anthropic.com → Sign up
2. Click "API Keys" → "Create Key"
3. Copy the key (starts with `sk-ant-...`)

**Google Gemini:**
1. Go to aistudio.google.com → Sign in with Google
2. Click "Get API Key" → "Create API Key"
3. Copy the key (starts with `AIza...`)

**FRED (Free Economic Data):**
1. Go to fred.stlouisfed.org/docs/api/api_key.html
2. Register for free → Get your API key immediately

**Alpha Vantage (Free Stock Data):**
1. Go to alphavantage.co/support/#api-key
2. Fill the form → Key sent instantly to your email

**AssemblyAI (Speech Analysis):**
1. Go to assemblyai.com → Sign up
2. Dashboard → Copy your API key

---

### STEP 7: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Open .env in any text editor and fill in your keys:
```

Your `.env` file should look like:
```
SECRET_KEY=any-random-string-you-make-up-like-abc123xyz
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
ANTHROPIC_API_KEY=sk-ant-api03-...
GEMINI_API_KEY=AIzaSyC...
FRED_API_KEY=abcdef1234567890
ALPHA_VANTAGE_KEY=ABCDEFG1234
ASSEMBLYAI_API_KEY=your-assemblyai-key
```

---

### STEP 8: Run the Application

```bash
# Make sure your virtual environment is active (you see (venv))
python app.py
```

You'll see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

Open your browser → Go to **http://localhost:5000**

---

## 🚀 How to Use YUKTHI

### First Time Flow:
1. **Register** → Create your account
2. **Verify email** (check inbox — Supabase sends confirmation)
3. **Take the personality quiz** → 10 questions, type your thoughts for real-time AI insights
4. **View your report** → Your personality portrait with Big Five scores
5. **Start using features:**
   - 🧭 Career → Type your career situation → Get digital twin analysis
   - 📈 Finance → Describe your money question → Get real market data + advice
   - 📅 Planning → Describe your goal → Get a weekly schedule + priority matrix
   - 🛡️ Cognitive → Type naturally or upload audio → Get health analysis

---

## 📱 Mobile App (Future APK)

The current version is a **Progressive Web App (PWA)** — it works on mobile browsers.

For a native Android APK, you would:
1. Use **Kivy** (Python) or **React Native** for the app shell
2. The app records typing patterns from native keyboard events
3. Call recordings analyzed via AssemblyAI's mobile SDK
4. Results synced to the same Supabase database

The web version already has mobile-responsive design. Users can:
- "Add to Home Screen" on Android Chrome → Works like an app
- All features function on mobile browser

---

## 🔧 Deployment (Making it Live on the Internet)

### Option A: Render.com (Recommended — Free)
1. Push code to GitHub
2. Go to render.com → New Web Service
3. Connect GitHub repo
4. Set: Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn app:app`
6. Add all environment variables in Render's dashboard
7. Deploy → You get a live URL!

### Option B: Railway.app (Also Free)
1. Go to railway.app → New Project → Deploy from GitHub
2. Add environment variables
3. Deploy

---

## 🐛 Troubleshooting

**"ModuleNotFoundError"**
→ Make sure your virtual environment is active: `source venv/bin/activate`

**"supabase connection failed"**
→ Check your SUPABASE_URL and SUPABASE_KEY in .env

**"Anthropic API error"**
→ Make sure you have credits on console.anthropic.com

**"Port 5000 already in use"**
→ Run: `python app.py --port 5001` or kill the process using port 5000

**Login not working after register**
→ Check Supabase → Authentication → Email confirmations. Disable for development.

---

## 📊 What Data is Stored in Supabase

| Table | What's Stored |
|-------|--------------|
| `profiles` | User name, email, personality report JSON |
| `chat_history` | Domain (career/finance/planning), prompt, AI response |
| `cognitive_analyses` | Typing metrics, speech analysis results |
| `cognitive_alerts` | Alerts sent to well-wishers |
| `monitoring_setup` | Who monitors whom, alert email |

All tables have **Row Level Security (RLS)** — users can only access their own data.

---

## ⚕️ Important Disclaimers

- YUKTHI is **not a medical device**
- Cognitive analysis is for **awareness and early screening only**
- Always consult qualified healthcare professionals for medical concerns
- Financial advice is **AI-generated** and not from a licensed financial advisor
- Career guidance is AI-powered and should supplement, not replace, professional advice

---

## 🆘 Need Help?

- Check the browser's Developer Console (F12) for JavaScript errors
- Check your terminal for Python/Flask errors
- All API responses are logged in debug mode

Happy building! 🚀
