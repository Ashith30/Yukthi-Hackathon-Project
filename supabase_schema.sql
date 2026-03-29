-- ══════════════════════════════════════════
-- YUKTHI — Supabase Database Schema
-- Run this in your Supabase SQL Editor
-- ══════════════════════════════════════════

-- ── 1. Profiles Table ──────────────────────
CREATE TABLE IF NOT EXISTS profiles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
  name TEXT,
  email TEXT,
  personality_report JSONB,
  assessment_answers JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policies: users can only see/edit their own profile
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── 2. Chat History Table ──────────────────
CREATE TABLE IF NOT EXISTS chat_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  domain TEXT NOT NULL CHECK (domain IN ('career', 'finance', 'planning')),
  prompt TEXT NOT NULL,
  response JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own chat history" ON chat_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat history" ON chat_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── 3. Cognitive Analyses Table ───────────
CREATE TABLE IF NOT EXISTS cognitive_analyses (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  analysis_type TEXT NOT NULL CHECK (analysis_type IN ('typing', 'speech')),
  patterns_data JSONB,
  result JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE cognitive_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own analyses" ON cognitive_analyses
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses" ON cognitive_analyses
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── 4. Cognitive Alerts Table ─────────────
CREATE TABLE IF NOT EXISTS cognitive_alerts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  alert_type TEXT NOT NULL,
  message TEXT NOT NULL,
  severity TEXT DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high')),
  sent_to_email TEXT,
  acknowledged BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE cognitive_alerts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own alerts" ON cognitive_alerts
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own alerts" ON cognitive_alerts
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── 5. Monitoring Setup Table ─────────────
CREATE TABLE IF NOT EXISTS monitoring_setup (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
  monitored_name TEXT NOT NULL,
  wellwisher_email TEXT NOT NULL,
  relationship TEXT,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE monitoring_setup ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own monitoring setup" ON monitoring_setup
  FOR ALL USING (auth.uid() = user_id);

-- ── 6. Indexes for performance ─────────────
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_domain  ON chat_history(domain);
CREATE INDEX IF NOT EXISTS idx_chat_history_created ON chat_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cognitive_analyses_user ON cognitive_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_cognitive_analyses_created ON cognitive_analyses(created_at DESC);

-- ── 7. Updated_at trigger ──────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_monitoring_updated_at
  BEFORE UPDATE ON monitoring_setup
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ══════════════════════════════════════════
-- DONE! Your database is ready.
-- Go to your Supabase project → SQL Editor
-- Paste and run this entire file.
-- ══════════════════════════════════════════
