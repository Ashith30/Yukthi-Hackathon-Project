/* ══════════════════════════════════════════
   YUKTHI — main.js
   ══════════════════════════════════════════ */

// ── Toast ──────────────────────────────────
function showToast(message, type = "") {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast show ${type}`;
  setTimeout(() => toast.classList.remove("show"), 3500);
}

// ── API Helper ─────────────────────────────
async function apiPost(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });
  return res.json();
}

// ── Button Loading State ───────────────────
function setLoading(btn, loading) {
  if (!btn) return;
  if (loading) {
    btn.classList.add("loading");
    btn.disabled = true;
  } else {
    btn.classList.remove("loading");
    btn.disabled = false;
  }
}

// ── Overlay ────────────────────────────────
function showOverlay(text = "Analyzing...") {
  let overlay = document.getElementById("loadingOverlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "loadingOverlay";
    overlay.className = "loading-overlay";
    overlay.innerHTML = `<div class="loading-spinner"></div><p class="loading-text">${text}</p>`;
    document.body.appendChild(overlay);
  } else {
    overlay.querySelector(".loading-text").textContent = text;
  }
  requestAnimationFrame(() => overlay.classList.add("show"));
}

function hideOverlay() {
  const overlay = document.getElementById("loadingOverlay");
  if (overlay) {
    overlay.classList.remove("show");
  }
}

// ── Animate number counter ─────────────────
function animateCount(el, target, duration = 1000) {
  const start = 0;
  const step = (timestamp) => {
    const progress = Math.min((timestamp - startTime) / duration, 1);
    el.textContent = Math.round(start + (target - start) * easeOut(progress));
    if (progress < 1) requestAnimationFrame(step);
  };
  const easeOut = t => 1 - Math.pow(1 - t, 3);
  let startTime;
  requestAnimationFrame(ts => { startTime = ts; step(ts); });
}

// ── Score Ring SVG ─────────────────────────
function buildScoreRing(score, color = "#4C6EF5", size = 100) {
  const r = (size / 2) - 8;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  return `
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
      <circle cx="${size/2}" cy="${size/2}" r="${r}" 
              fill="none" stroke="#E9ECEF" stroke-width="7"/>
      <circle cx="${size/2}" cy="${size/2}" r="${r}" 
              fill="none" stroke="${color}" stroke-width="7"
              stroke-dasharray="${dash} ${circ}"
              stroke-linecap="round"
              style="transform:rotate(-90deg);transform-origin:50% 50%;transition:stroke-dasharray 1s ease"/>
    </svg>`;
}

// ── Typing Pattern Tracker ─────────────────
class TypingTracker {
  constructor() {
    this.keystrokes = [];
    this.backspaces = 0;
    this.totalKeys = 0;
    this.sessionStart = Date.now();
    this.wordTimestamps = [];
    this.lastKeyTime = null;
    this.pauses = [];
  }

  recordKey(event) {
    const now = Date.now();
    this.totalKeys++;

    if (event.key === "Backspace" || event.key === "Delete") this.backspaces++;

    if (event.key === " " && this.lastKeyTime) {
      this.wordTimestamps.push(now);
      const pause = now - this.lastKeyTime;
      if (pause > 2000) this.pauses.push(pause);
    }

    this.lastKeyTime = now;
    this.keystrokes.push({ key: event.key, time: now });
  }

  getMetrics() {
    const sessionMinutes = (Date.now() - this.sessionStart) / 60000;
    const words = this.wordTimestamps.length;
    const avgWpm = sessionMinutes > 0 ? Math.round(words / sessionMinutes) : 0;

    // WPM variance (rhythm consistency)
    let rhythmScore = 100;
    if (this.wordTimestamps.length > 3) {
      const gaps = [];
      for (let i = 1; i < this.wordTimestamps.length; i++) {
        gaps.push(this.wordTimestamps[i] - this.wordTimestamps[i-1]);
      }
      const mean = gaps.reduce((a,b) => a+b, 0) / gaps.length;
      const variance = gaps.reduce((a,b) => a + Math.pow(b - mean, 2), 0) / gaps.length;
      rhythmScore = Math.max(0, Math.min(100, 100 - (Math.sqrt(variance) / mean) * 50));
    }

    return {
      avg_wpm: avgWpm,
      wpm_variance: 0,
      backspace_rate: this.totalKeys > 0 ? this.backspaces / this.totalKeys : 0,
      avg_pause_ms: this.pauses.length > 0 ? this.pauses.reduce((a,b)=>a+b,0)/this.pauses.length : 0,
      long_pause_count: this.pauses.filter(p => p > 3000).length,
      session_minutes: sessionMinutes,
      total_keystrokes: this.totalKeys,
      error_rate: this.totalKeys > 0 ? this.backspaces / this.totalKeys : 0,
      rhythm_score: Math.round(rhythmScore)
    };
  }

  updateDisplay() {
    const m = this.getMetrics();
    const wpmEl = document.getElementById("metricWpm");
    const bsEl  = document.getElementById("metricBackspace");
    const pauseEl = document.getElementById("metricPause");
    const rhythmEl = document.getElementById("metricRhythm");
    if (wpmEl)    wpmEl.textContent    = m.avg_wpm;
    if (bsEl)     bsEl.textContent     = (m.backspace_rate * 100).toFixed(1) + "%";
    if (pauseEl)  pauseEl.textContent  = m.long_pause_count;
    if (rhythmEl) rhythmEl.textContent = m.rhythm_score;
  }
}

// ── Decision Result Renderer ───────────────
function renderCareerResult(result) {
  const el = document.getElementById("careerResult");
  if (!el) return;
  const align = result.path_assessment || {};
  const score = align.alignment_score || 70;
  const scoreColor = score >= 75 ? "#37B24D" : score >= 55 ? "#F59F00" : "#FA5252";

  el.innerHTML = `
    <div class="twin-card">
      <div class="twin-header">
        <div class="twin-avatar">🤖</div>
        <div>
          <div class="twin-label">Your Digital Twin Thinking</div>
        </div>
      </div>
      <p class="twin-text">"${result.twin_thinking}"</p>
    </div>

    <div class="alert-card" style="border-left-color: var(--amber);">
      <div style="font-weight:700; margin-bottom:5px; font-size:14px;">
        ⚠️ Blind Spot Alert
      </div>
      <p style="font-size:14px; color: var(--text-secondary);">${result.blind_spot}</p>
    </div>

    <div class="grid-2" style="margin-bottom:20px;">
      <div class="card card-sm">
        <div class="result-section-title">Path Alignment</div>
        <div class="alignment-meter">
          <div>
            <div class="score-ring-wrap">
              ${buildScoreRing(score, scoreColor, 80)}
            </div>
          </div>
          <div>
            <div style="font-size:13px; font-weight:700; color:${scoreColor}">
              ${align.alignment_label || "Evaluating..."}
            </div>
            <div style="font-size:13px; color:var(--text-muted); margin-top:4px;">
              ${align.current_direction || ""}
            </div>
          </div>
        </div>
      </div>
      <div class="card card-sm">
        <div class="result-section-title">Timeline</div>
        <div style="font-size:14px; color:var(--text-secondary); margin-bottom:10px;">${result["6_month_milestone"] || ""}</div>
        <div style="font-size:12px; color:var(--text-muted);">Salary Range</div>
        <div style="font-weight:700; color:var(--indigo);">${result.salary_range || "N/A"}</div>
      </div>
    </div>

    <div class="grid-2" style="margin-bottom:20px;">
      <div>
        <div class="result-section-title">✅ 3-Month Action Plan</div>
        <ul class="action-list">
          ${(result["3_month_action"]||[]).map(a=>`<li>${a}</li>`).join("")}
        </ul>
      </div>
      <div>
        <div class="result-section-title">🎯 Skill Gaps to Close</div>
        <div class="tag-list">
          ${(result.skill_gaps||[]).map(s=>`<span class="badge badge-rose">${s}</span>`).join("")}
        </div>
        <div class="result-section-title" style="margin-top:14px;">💪 Your Strengths</div>
        <div class="tag-list">
          ${(result.skill_strengths||[]).map(s=>`<span class="badge badge-green">${s}</span>`).join("")}
        </div>
      </div>
    </div>

    <div class="card" style="background:var(--teal-soft); border-color:var(--teal);">
      <div style="font-size:13px; font-weight:700; color:var(--teal); margin-bottom:6px;">
        💬 Market Insight
      </div>
      <p style="font-size:14px; color:var(--text-secondary);">${result.market_insight || ""}</p>
    </div>

    <div class="card card-sm" style="margin-top:16px; background:var(--indigo-soft);">
      <div style="font-size:13px; font-weight:700; color:var(--indigo); margin-bottom:5px;">✨ A Note For You</div>
      <p style="font-size:14px; color:var(--text-secondary); font-style:italic;">${result.encouragement || ""}</p>
    </div>

    <!-- Career Flowchart Area -->
    <div id="flowchartContainer" class="card" style="margin-top:24px; text-align:center;">
      <div style="margin-bottom:12px;">
        <div style="font-size:14px; font-weight:700; margin-bottom:4px;">Want a visual map?</div>
        <p style="font-size:13px; color:var(--text-muted);">Visualize your exact career trajectory based on your personality profile.</p>
      </div>
      <button class="btn btn-primary" id="generateFlowchartBtn" onclick="generateCareerFlowchart()">
        <i class="fas fa-sitemap"></i>
        <span class="btn-text">Generate Visual Career Flowchart</span>
        <div class="spinner"></div>
      </button>
      <div id="flowchartRenderArea" style="margin-top:20px; text-align:left; display:none; overflow-x:auto;"></div>
    </div>
  `;
  el.style.display = "block";
  el.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function generateCareerFlowchart() {
  const prompt = document.getElementById("careerPrompt").value.trim();
  const btn = document.getElementById("generateFlowchartBtn");
  
  if (!prompt) {
    showToast("Prompt missing. Cannot generate flowchart.", "error");
    return;
  }
  
  setLoading(btn, true);
  showToast("Synthesizing visual nodes...", "info");
  
  try {
    const res = await apiPost("/decision/career/flowchart", { prompt });
    if (res.success && res.flowchart) {
      const renderArea = document.getElementById("flowchartRenderArea");
      renderArea.style.display = "block";
      // Ensure any previous rendering styles are cleared out
      renderArea.innerHTML = `<div class="mermaid">${res.flowchart}</div>`;
      
      // Let Mermaid parse and render the flowchart SVG
      if (window.mermaid) {
        mermaid.init(undefined, renderArea.querySelectorAll('.mermaid'));
      }
      
      // Hide the generate button after successful generation
      btn.style.display = "none";
      showToast("Flowchart ready!", "success");
    } else {
      showToast(res.error || "Failed to generate flowchart.", "error");
    }
  } catch (e) {
    console.error(e);
    showToast("Connection error while rendering flowchart.", "error");
  } finally {
    setLoading(btn, false);
  }
}

function renderFinanceResult(result) {
  const el = document.getElementById("financeResult");
  if (!el) return;
  const riskClass = {
    "Low": "risk-low", "Medium": "risk-medium",
    "High": "risk-high", "Very High": "risk-very-high"
  }[result.risk_level] || "risk-medium";

  const econData = result.econ_data_used || {};
  const econPills = Object.entries(econData).map(([k,v]) =>
    v.value ? `<span class="econ-pill">📊 ${k.replace(/_/g,' ')}: ${parseFloat(v.value).toFixed(2)}%</span>` : ""
  ).join("");

  el.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:16px; flex-wrap:wrap;">
        <span class="risk-badge ${riskClass}">
          ⚡ ${result.risk_level} Risk
        </span>
        ${result.confidence_score ? `
        <div style="display:flex;align-items:center;gap:6px;">
          ${buildScoreRing(result.confidence_score, "#20C997", 50)}
          <div style="font-size:12px;color:var(--text-muted);">${result.confidence_score}% confidence</div>
        </div>` : ""}
      </div>
      <p style="font-size:14.5px; color:var(--text-secondary);">${result.situation_summary || ""}</p>
      ${econPills ? `<div class="tag-list" style="margin-top:12px;">${econPills}</div>` : ""}
    </div>

    <div class="alert-card success" style="margin-bottom:16px;">
      <div style="font-weight:700; margin-bottom:6px;">📋 Recommendation</div>
      <p style="font-size:14px; color:var(--text-secondary);">${result.recommendation}</p>
    </div>

    <div class="grid-2" style="margin-bottom:20px;">
      <div>
        <div class="result-section-title">✅ Do This</div>
        <ul class="action-list">
          ${(result.do_this||[]).map(a=>`<li>${a}</li>`).join("")}
        </ul>
      </div>
      <div>
        <div class="result-section-title">🚫 Avoid This</div>
        <ul class="action-list">
          ${(result.avoid_this||[]).map(a=>`<li>${a}</li>`).join("")}
        </ul>
      </div>
    </div>

    <div class="card card-sm" style="background:var(--amber-soft); border-color:var(--amber); margin-bottom:16px;">
      <div style="font-size:13px;font-weight:700;color:var(--amber);margin-bottom:6px;">⏱️ Timeline</div>
      <p style="font-size:14px;color:var(--text-secondary);">${result.timeline || ""}</p>
    </div>

    <div class="card card-sm">
      <div class="result-section-title">🌐 Economic Context</div>
      <p style="font-size:14px;color:var(--text-secondary);">${result.economic_context || ""}</p>
    </div>

    <div class="card card-sm" style="margin-top:12px; background:var(--rose-soft);">
      <div style="font-size:12px; font-weight:600; color:var(--rose); margin-bottom:4px;">
        ⚠️ Before you proceed, ask yourself:
      </div>
      <p style="font-size:14px; font-style:italic; color:var(--text-secondary);">${result.emergency_check || ""}</p>
    </div>

    <p style="font-size:11.5px;color:var(--text-muted);margin-top:12px;font-style:italic;">
      ${result.disclaimer || "This is not financial advice. Consult a qualified financial advisor."}
    </p>
  `;
  el.style.display = "block";
  el.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderPlanningResult(result) {
  const el = document.getElementById("planningResult");
  if (!el) return;

  const schedule = (result.weekly_schedule || []).map(d => `
    <div class="schedule-day">
      <div class="schedule-day-name">${d.day.substring(0,3)}</div>
      <div class="schedule-focus">${d.focus || ""}</div>
      ${(d.tasks||[]).map(t=>`<div class="schedule-task">${t}</div>`).join("")}
    </div>
  `).join("");

  const matrix = result.priority_matrix || {};

  const flowchartHTML = result.mermaid_flowchart ? `
    <div class="card" style="margin-top:20px; overflow-x:auto;">
      <div class="result-section-title">🗺️ Visual Roadmap</div>
      <div class="mermaid planning-mermaid" style="display:flex; justify-content:center; min-width:600px;">
        ${result.mermaid_flowchart}
      </div>
    </div>
  ` : "";

  el.innerHTML = `
    <div class="card" style="margin-bottom:20px;">
      <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin-bottom:12px;">
        <span class="badge badge-indigo">${result.planning_framework || "Custom"}</span>
        <span class="badge badge-teal">${result.complexity_level || "Moderate"}</span>
      </div>
      <p style="font-size:14.5px; color:var(--text-secondary);">${result.goal_clarity || ""}</p>
      <p style="font-size:14px; color:var(--text-muted); margin-top:8px;">${result.framework_explanation || ""}</p>
    </div>

    <div class="result-section-title">📅 Weekly Structure</div>
    <div class="schedule-grid" style="margin-bottom:24px;">${schedule}</div>

    <div class="grid-2" style="margin-bottom:20px;">
      <div>
        <div class="result-section-title">🎯 Urgent & Important</div>
        <ul class="action-list">
          ${(matrix.urgent_important||[]).map(t=>`<li>${t}</li>`).join("")}
        </ul>
        <div class="result-section-title" style="margin-top:14px;">📌 Not Urgent but Important</div>
        <ul class="action-list">
          ${(matrix.not_urgent_important||[]).map(t=>`<li>${t}</li>`).join("")}
        </ul>
      </div>
      <div>
        <div class="result-section-title">⚡ Quick Wins</div>
        <ul class="action-list">
          ${(result.quick_wins||[]).map(t=>`<li>${t}</li>`).join("")}
        </ul>
        <div class="result-section-title" style="margin-top:14px;">🚫 Consider Eliminating</div>
        <ul class="action-list">
          ${(matrix.neither||[]).map(t=>`<li>${t}</li>`).join("")}
        </ul>
      </div>
    </div>

    <div class="grid-2" style="margin-bottom:20px;">
      <div class="card card-sm" style="background:var(--teal-soft);">
        <div style="font-size:12px;font-weight:700;color:var(--teal);margin-bottom:6px;">🏁 30-Day Milestone</div>
        <p style="font-size:14px;color:var(--text-secondary);">${result["30_day_milestone"]||""}</p>
      </div>
      <div class="card card-sm" style="background:var(--violet-soft);">
        <div style="font-size:12px;font-weight:700;color:var(--violet);margin-bottom:6px;">🚀 90-Day Vision</div>
        <p style="font-size:14px;color:var(--text-secondary);">${result["90_day_vision"]||""}</p>
      </div>
    </div>

    <div class="card card-sm">
      <div class="result-section-title">🔥 Daily Non-Negotiables</div>
      <div class="tag-list">
        ${(result.daily_non_negotiables||[]).map(h=>`<span class="badge badge-amber">${h}</span>`).join("")}
      </div>
      ${result.tools_recommended ? `
      <div class="result-section-title" style="margin-top:14px;">🛠️ Recommended Tools</div>
      <div class="tag-list">
        ${(result.tools_recommended||[]).map(t=>`<span class="tag">${t}</span>`).join("")}
      </div>` : ""}
    </div>

    <div class="card card-sm" style="margin-top:12px; background:var(--indigo-soft);">
      <div style="font-size:13px;font-weight:700;color:var(--indigo);margin-bottom:6px;">💡 Motivation Strategy</div>
      <p style="font-size:14px;color:var(--text-secondary);">${result.motivation_strategy||""}</p>
    </div>
    
    ${flowchartHTML}
  `;
  el.style.display = "block";
  el.scrollIntoView({ behavior: "smooth", block: "start" });
  
  if (result.mermaid_flowchart && window.mermaid) {
    try {
      mermaid.init(undefined, el.querySelectorAll('.planning-mermaid'));
    } catch(e) {
      console.error("Mermaid parsing error:", e);
    }
  }
}

function renderCognitiveResult(result, containerId = "cognitiveResult") {
  const el = document.getElementById(containerId);
  if (!el) return;
  
  const colorMap = { green: "green", yellow: "yellow", orange: "orange", red: "red" };
  const color = colorMap[result.status_color] || "green";
  const iconMap = { green: "✅", yellow: "⚠️", orange: "🟠", red: "🔴" };
  const icon = iconMap[result.status_color] || "✅";

  el.innerHTML = `
    <div class="alert-banner ${color}" style="margin-bottom:20px;">
      <div class="alert-banner-icon">${icon}</div>
      <div>
        <div class="alert-banner-title">${result.status || "Analysis Complete"}</div>
        <div class="alert-banner-text">${result.summary || result.speech_rate_assessment || ""}</div>
      </div>
    </div>

    ${(result.observations||[]).length ? `
    <div class="card" style="margin-bottom:16px;">
      <div class="card-title" style="margin-bottom:14px;">📊 Detailed Observations</div>
      ${(result.observations||[]).map(obs => {
        const isObj = typeof obs === "object";
        const flag = isObj ? obs.flag : false;
        const text = isObj ? `<strong>${obs.marker}</strong>: ${obs.value} — ${obs.assessment}` : obs;
        return `<div style="display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid var(--border-light);">
          <span style="font-size:14px;">${flag ? "⚠️" : "✅"}</span>
          <span style="font-size:14px;color:var(--text-secondary);">${text}</span>
        </div>`;
      }).join("")}
    </div>` : ""}

    <div class="grid-2" style="margin-bottom:16px;">
      ${result.positive_signs?.length ? `
      <div>
        <div class="result-section-title">✅ Positive Signs</div>
        <ul class="action-list">
          ${result.positive_signs.map(s=>`<li>${s}</li>`).join("")}
        </ul>
      </div>` : ""}
      ${result.alert_signals?.length ? `
      <div>
        <div class="result-section-title">⚠️ Signals to Watch</div>
        <ul class="action-list">
          ${result.alert_signals.map(s=>`<li>${s}</li>`).join("")}
        </ul>
      </div>` : ""}
    </div>

    <div class="card card-sm" style="background:var(--indigo-soft);">
      <div style="font-size:13px;font-weight:700;color:var(--indigo);margin-bottom:6px;">📋 Recommendation</div>
      <p style="font-size:14px;color:var(--text-secondary);">${result.recommendation || ""}</p>
    </div>

    ${result.should_alert_wellwisher ? `
    <div class="alert-banner red" style="margin-top:16px;">
      <div class="alert-banner-icon">🔔</div>
      <div>
        <div class="alert-banner-title">Well-wisher Alert Sent</div>
        <div class="alert-banner-text">${result.alert_message || ""}</div>
      </div>
    </div>` : ""}

    <p style="font-size:12px;color:var(--text-muted);margin-top:12px;font-style:italic;">
      ⚕️ This analysis is for awareness only and does not constitute medical diagnosis. 
      Consult a healthcare professional for any concerns.
    </p>
  `;
  el.style.display = "block";
}

// Global tracker instance
window.typingTracker = null;

// ── OMNI DECISION ARCHITECT ─────────────────────
async function analyzeOmni() {
  const prompt = document.getElementById("omniPrompt").value.trim();
  const btn = document.getElementById("omniBtn");
  
  if (!prompt) {
    showToast("Please provide a decision/situation.", "error");
    return;
  }
  
  setLoading(btn, true);
  showOverlay("Synthesizing Life Domains...");
  document.getElementById("omniResult").style.opacity = "0";
  setTimeout(() => { document.getElementById("omniResult").style.display = "none"; }, 300);
  
  try {
    const res = await apiPost("/decision/omni/analyze", { prompt });
    if (res.success && Array.isArray(res.result)) {
      renderOmniResult(res.result);
      showToast("Synthesis Complete.", "success");
    } else {
      showToast(res.error || "Analysis failed to parse domains.", "error");
    }
  } catch(e) {
    showToast("Connection anomaly.", "error");
  } finally {
    setLoading(btn, false);
    hideOverlay();
  }
}

function renderOmniResult(domains) {
  const resultArea = document.getElementById("omniResult");
  const mindmapRender = document.getElementById("omniMindmapRender");
  const accordionContainer = document.getElementById("omniAccordionContainer");
  
  if (!domains || domains.length === 0) return;
  
  // 1. Build mermaid Mindmap Syntax
  let mindmapText = "mindmap\\n  root((Omni-Decision Node))";
  
  let htmlAccordion = "";
  
  domains.forEach((d, i) => {
    // Escape string for mermaid node
    let safeDomain = d.domain ? d.domain.replace(/[()"]/g, '') : `Domain ${i}`;
    mindmapText += `\\n    ${safeDomain}`;
    
    // Add sub-nodes safely
    let bl = d.bottom_line ? d.bottom_line.replace(/[()"]/g, '').substring(0, 45) + "..." : "";
    if (bl) mindmapText += `\\n      ${bl}`;
    
    // Accordion Construction
    const colorTheme = d.complexity > 75 ? "rgba(239, 68, 68, 0.15)" : d.complexity > 40 ? "rgba(245, 158, 11, 0.15)" : "rgba(32, 201, 151, 0.15)";
    const colorText = d.complexity > 75 ? "var(--red)" : d.complexity > 40 ? "var(--amber)" : "var(--teal)";
    
    htmlAccordion += `
      <div class="omni-acc-item" id="omni-acc-${i}">
        <div class="omni-acc-header" onclick="toggleOmniAccordion('omni-acc-${i}')">
          <div class="omni-acc-title">
            <span>${d.domain}</span>
            <span class="omni-score-badge" style="background:${colorTheme}; color:${colorText};">Hardness: ${d.complexity}/100</span>
          </div>
          <i class="fas fa-chevron-down omni-acc-icon" style="color:var(--text-muted);"></i>
        </div>
        <div class="omni-acc-body">
          <div style="font-weight:700; color:var(--text-primary); margin-bottom:12px; font-size:14.5px;">${d.bottom_line}</div>
          
          <div class="grid-2" style="margin-bottom:12px; gap:16px;">
            <div style="background:rgba(32, 201, 151, 0.05); padding:12px; border-radius:8px; border:1px solid rgba(32, 201, 151, 0.2);">
              <div style="font-size:12px; font-weight:700; color:var(--teal); text-transform:uppercase; margin-bottom:8px;">✅ DO THIS</div>
              <ul style="margin:0; padding-left:18px; font-size:13.5px; color:var(--text-secondary);">
                ${(d.do_this || []).map(x => `<li style="margin-bottom:4px;">${x}</li>`).join("")}
              </ul>
            </div>
            
            <div style="background:rgba(239, 68, 68, 0.05); padding:12px; border-radius:8px; border:1px solid rgba(239, 68, 68, 0.2);">
              <div style="font-size:12px; font-weight:700; color:var(--red); text-transform:uppercase; margin-bottom:8px;">🚫 AVOID THIS</div>
              <ul style="margin:0; padding-left:18px; font-size:13.5px; color:var(--text-secondary);">
                ${(d.avoid_this || []).map(x => `<li style="margin-bottom:4px;">${x}</li>`).join("")}
              </ul>
            </div>
          </div>
          
          ${(d.critical_metrics && d.critical_metrics.length > 0) ? `
          <div style="background:var(--bg-card); border-top:1px dashed var(--border-light); padding-top:12px;">
            <div style="font-size:12px; font-weight:700; color:var(--indigo); text-transform:uppercase; margin-bottom:6px;">📈 Critical Metrics</div>
            <div style="font-size:13px; color:var(--text-muted);">
              ${d.critical_metrics.join(" &bull; ")}
            </div>
          </div>
          ` : ""}
        </div>
      </div>
    `;
  });
  
  // Inject syntax
  mindmapRender.innerHTML = `<div class="mermaid">${mindmapText}</div>`;
  accordionContainer.innerHTML = htmlAccordion;
  
  // Reveal UI
  resultArea.style.display = "block";
  setTimeout(() => { resultArea.style.opacity = "1"; }, 50);
  
  // Render Mermaid dynamically
  if (window.mermaid) {
    try {
      mermaid.init(undefined, mindmapRender.querySelectorAll('.mermaid'));
    } catch(e) { console.error("Mermaid error:", e); }
  }
}

// ── Theme Switcher ─────────────────────────
function changeTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('cogni_theme', theme);
}

document.addEventListener('DOMContentLoaded', () => {
  const select = document.getElementById('themeSelect');
  if (select) {
    const savedTheme = localStorage.getItem('cogni_theme') || 'light';
    select.value = savedTheme;
  }
});
