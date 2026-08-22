from __future__ import annotations

from .assistant_productivity_dashboard import (
    productivity_html_panels,
    productivity_readiness_coach_html,
    productivity_styles,
)
from .assistant_results_dashboard import (
    results_dashboard_html_panels,
    results_dashboard_styles,
)


def unified_assistant_html() -> str:
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jarvis Unified Assistant</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #edf2f7;
      --surface: #ffffff;
      --soft: #f7fafc;
      --border: #c5d2df;
      --text: #172235;
      --muted: #526276;
      --accent: #155e9b;
      --accent-dark: #0d4777;
      --accent-light: #e8f2fa;
      --safe: #176b45;
      --safe-bg: #edf8f2;
      --warn: #8a5200;
      --warn-bg: #fff8e8;
      --danger: #a12626;
      --danger-bg: #fff1f1;
      --focus: #ffbf47;
      --code-bg: #1e293b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font: 16px/1.5 "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    header {
      background: #14263b;
      color: #fff;
      padding: 18px clamp(16px, 3.5vw, 40px);
      border-bottom: 4px solid #5e87ad;
      position: sticky;
      top: 0;
      z-index: 10;
    }
    header .header-inner {
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    header h1 {
      margin: 0;
      font-size: clamp(1.3rem, 2.2vw, 1.7rem);
      display: flex;
      align-items: center;
      gap: 10px;
    }
    header .tagline {
      margin: 2px 0 0;
      color: #dce8f4;
      font-size: 0.88rem;
    }
    .header-nav {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }
    .header-nav a {
      text-decoration: none;
      color: #fff;
      background: rgba(255, 255, 255, 0.12);
      padding: 6px 12px;
      border-radius: 5px;
      font-size: 0.88rem;
      font-weight: 600;
      border: 1px solid rgba(255, 255, 255, 0.25);
      transition: background 0.15s ease;
    }
    .header-nav a:hover {
      background: rgba(255, 255, 255, 0.24);
    }
    .header-nav a.active {
      background: var(--accent);
      border-color: #7db0dd;
    }
    main {
      max-width: 1400px;
      margin: 0 auto;
      padding: 18px clamp(14px, 2.5vw, 32px) 60px;
      display: grid;
      gap: 18px;
    }
    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(15, 35, 55, 0.05);
    }
    .banner {
      border-left: 6px solid var(--accent);
      background: var(--accent-light);
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 0.92rem;
    }
    .banner.warning {
      border-left-color: var(--warn);
      background: var(--warn-bg);
    }
    .banner.danger {
      border-left-color: var(--danger);
      background: var(--danger-bg);
    }
    .banner.safe {
      border-left-color: var(--safe);
      background: var(--safe-bg);
    }
    .banner.high-stakes {
      border-left-color: #ea580c;
      background: #fff7ed;
      color: #9a3412;
      border-radius: 6px;
      padding: 10px 14px;
    }
    .status-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 14px;
      background: #f1f5f9;
      border: 1px solid var(--border);
      border-radius: 7px;
      font-size: 0.88rem;
    }
    .status-bar .pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 9px;
      border-radius: 12px;
      font-weight: 600;
      font-size: 0.82rem;
    }
    .pill.active { background: #dcfce7; color: #14532d; }
    .pill.inactive { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
    .pill.strong { background: #dbeafe; color: #1e40af; }
    .pill.moderate { background: #fef3c7; color: #92400e; }
    .pill.weak { background: #fee2e2; color: #991b1b; }
    .pill.override { background: #f3e8ff; color: #6b21a8; }
    .pill.high-stakes { background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }
    .pill.cancelled { background: #fee2e2; color: #991b1b; }
    .chat-container {
      display: grid;
      gap: 16px;
      min-height: 280px;
    }
    .empty-state {
      text-align: center;
      padding: 40px 20px;
      background: var(--soft);
      border: 2px dashed var(--border);
      border-radius: 9px;
    }
    .empty-state h3 {
      margin: 0 0 8px;
      color: var(--accent-dark);
    }
    .empty-state p {
      margin: 0 0 18px;
      color: var(--muted);
      max-width: 680px;
      margin-left: auto;
      margin-right: auto;
    }
    .starter-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      justify-content: center;
      margin-top: 12px;
    }
    .starter-chip {
      background: #fff;
      border: 1px solid var(--border);
      padding: 7px 12px;
      border-radius: 20px;
      font-size: 0.86rem;
      color: var(--accent-dark);
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .starter-chip:hover {
      background: var(--accent-light);
      border-color: var(--accent);
    }
    .turn {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 16px;
      display: grid;
      gap: 12px;
      box-shadow: 0 2px 6px rgba(15, 35, 55, 0.04);
    }
    .turn.user-turn {
      background: #f8fafc;
      border-left: 5px solid var(--accent);
    }
    .turn.jarvis-turn {
      background: #ffffff;
      border-left: 5px solid #0d9488;
    }
    .turn-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-size: 0.86rem;
    }
    .turn-title {
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .turn-body {
      font-size: 0.96rem;
      line-height: 1.6;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }
    .route-info-card {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 14px;
      font-size: 0.88rem;
    }
    .route-info-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }
    .route-rationale {
      color: var(--muted);
      font-size: 0.85rem;
    }
    .response-section {
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid #e2e8f0;
    }
    .response-section h4 {
      margin: 0 0 6px;
      font-size: 0.9rem;
      color: var(--accent-dark);
    }
    .key-points-list {
      margin: 0;
      padding-left: 20px;
    }
    .key-points-list li {
      margin-bottom: 4px;
      font-size: 0.92rem;
    }
    .citations-card {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 6px;
      padding: 10px 14px;
      font-size: 0.85rem;
      color: #166534;
      margin-top: 8px;
    }
    .turn-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-top: 4px;
    }
    button, .button {
      font: inherit;
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
      padding: 8px 14px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    button:hover:not(:disabled) {
      background: var(--accent-dark);
      border-color: var(--accent-dark);
    }
    button.secondary {
      background: #fff;
      color: var(--accent);
      border-color: var(--border);
    }
    button.secondary:hover:not(:disabled) {
      background: #f1f5f9;
      border-color: var(--accent);
    }
    button.small {
      padding: 4px 10px;
      font-size: 0.82rem;
    }
    button.danger {
      background: var(--danger);
      border-color: var(--danger);
      color: #fff;
    }
    button.danger:hover:not(:disabled) {
      background: #881b1b;
      border-color: #881b1b;
    }
    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .action-bridge-card {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 7px;
      padding: 12px 14px;
      margin-top: 8px;
      display: grid;
      gap: 10px;
    }
    .action-bridge-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .action-form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 10px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 12px;
    }
    .action-field {
      display: grid;
      gap: 4px;
      font-size: 0.86rem;
    }
    .action-field label {
      font-weight: 600;
      color: var(--muted);
      font-size: 0.8rem;
    }
    .action-field select, .action-field input {
      padding: 6px 8px;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      font-size: 0.88rem;
      background: #fff;
    }
    .action-preview-box {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 0.86rem;
      display: grid;
      gap: 6px;
    }
    .action-result-box {
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 0.88rem;
      display: grid;
      gap: 6px;
    }
    .action-result-box.succeeded {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #14532d;
    }
    .action-result-box.blocked {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #991b1b;
    }
    .action-result-box.waiting {
      background: #fffbeb;
      border: 1px solid #fde68a;
      color: #92400e;
    }
    .composer-card {
      position: sticky;
      bottom: 12px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 14px;
      box-shadow: 0 4px 16px rgba(15, 35, 55, 0.12);
      display: grid;
      gap: 10px;
      z-index: 5;
    }
    .composer-textarea {
      width: 100%;
      min-height: 70px;
      padding: 10px 12px;
      border: 1px solid #94a3b8;
      border-radius: 6px;
      font: inherit;
      font-size: 0.96rem;
      resize: vertical;
    }
    .composer-textarea:focus {
      outline: 2px solid var(--accent);
      border-color: var(--accent);
    }
    .composer-options {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      font-size: 0.88rem;
    }
    .options-left {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 12px;
    }
    .options-right {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }
    .toggle-label {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      cursor: pointer;
      user-select: none;
      font-weight: 500;
    }
    select {
      font: inherit;
      padding: 5px 8px;
      border: 1px solid #94a3b8;
      border-radius: 5px;
      background: #fff;
      font-size: 0.88rem;
    }
    .staged-prior-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #f3e8ff;
      border: 1px solid #d8b4fe;
      border-radius: 6px;
      padding: 6px 12px;
      font-size: 0.85rem;
      color: #6b21a8;
    }
    .staging-drawer {
      background: var(--soft);
      border: 1px solid #93c5fd;
      border-radius: 8px;
      padding: 14px;
      display: grid;
      gap: 12px;
    }
    .staging-drawer h3 {
      margin: 0;
      font-size: 1.05rem;
      color: var(--accent-dark);
    }
    .alternatives-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 10px;
    }
    .alt-card {
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 0.86rem;
      display: grid;
      gap: 4px;
    }
    .json-panel {
      background: var(--code-bg);
      color: #f8fafc;
      border-radius: 6px;
      padding: 12px;
      font-family: Consolas, Monaco, "Courier New", monospace;
      font-size: 0.84rem;
      max-height: 300px;
      overflow: auto;
    }
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #1e293b;
      color: #fff;
      padding: 10px 18px;
      border-radius: 6px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      font-size: 0.9rem;
      z-index: 100;
      opacity: 0;
      transition: opacity 0.2s ease;
      pointer-events: none;
    }
    .toast.show { opacity: 1; }

    /* Active Generating Card */
    .generating-card {
      border: 2px solid #3b82f6;
      background: #eff6ff;
      border-radius: 9px;
      padding: 16px;
      display: grid;
      gap: 10px;
      box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
      animation: pulse-border 2.5s infinite ease-in-out;
    }
    @keyframes pulse-border {
      0%, 100% { border-color: #3b82f6; }
      50% { border-color: #93c5fd; }
    }
    .generating-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }

    /* PRODUCTIVITY_STYLES_PLACEHOLDER */
  </style>
</head>
<body>
<header>
  <div class="header-inner">
    <div>
      <h1>Jarvis Unified Assistant</h1>
      <p class="tagline">Supervised conversational interface over 37 local response agents</p>
    </div>
    <nav class="header-nav">
      <a href="/assistant" class="active">Assistant</a>
      <a href="/dashboard">Dashboard</a>
      <a href="/actions">Action Center</a>
      <a href="/dashboard#response-agents">Workbench</a>
      <a href="/memory">Memory Center</a>
      <a href="/knowledge">Knowledge Library</a>
      <a href="/models">Models Center</a>
    </nav>
  </div>
</header>

<main>
  <!-- System Status Bar -->
  <section class="status-bar" aria-label="System status">
    <div style="display:flex; flex-wrap:wrap; align-items:center; gap:8px;">
      <span class="pill active" id="session-mode-pill">Session-Only · In-Memory</span>
      <span class="pill" id="generation-pill">Local Generation: Checking...</span>
      <span class="pill" id="agents-pill">37 Response Agents Ready</span>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <button id="view-result-board-btn" class="secondary small" type="button">
        Result Board (<span id="result-board-count">0</span>)
      </button>
      <button id="clear-session-btn" class="secondary small" type="button">Clear Transcript</button>
    </div>
  </section>

  <!-- PRODUCTIVITY_PANELS_PLACEHOLDER -->

  <!-- Staged Prior Context Indicator -->
  <div id="staged-prior-context-bar" class="staged-prior-bar" style="display:none;">
    <span><strong>Staged Prior Context:</strong> <span id="staged-prior-summary"></span></span>
    <button id="clear-prior-context-btn" class="secondary small" style="border-color:#d8b4fe;" type="button">Dismiss</button>
  </div>

  <!-- Conversation Transcript Area -->
  <section id="chat-container" class="chat-container">
    <div id="empty-state" class="empty-state">
      <h3>Welcome to the Unified Jarvis Assistant</h3>
      <p>Supervised conversational interface over 37 local response agents. Local-only, private, and fully under your control.</p>

      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:10px; max-width:850px; margin:0 auto 18px; text-align:left;">
        <div style="background:#fff; border:1px solid var(--border); border-radius:7px; padding:10px 12px; font-size:0.84rem;">
          <strong style="color:var(--accent); font-size:0.9rem;">1. Describe Needs</strong><br>
          Type your natural-language task in the composer below.
        </div>
        <div style="background:#fff; border:1px solid var(--border); border-radius:7px; padding:10px 12px; font-size:0.84rem;">
          <strong style="color:var(--accent); font-size:0.9rem;">2. Choose Agent</strong><br>
          Use auto-routing or pick from the 37 Command Center agents.
        </div>
        <div style="background:#fff; border:1px solid var(--border); border-radius:7px; padding:10px 12px; font-size:0.84rem;">
          <strong style="color:var(--accent); font-size:0.9rem;">3. Context Kit</strong><br>
          Assemble optional notes, prior answers, or project context.
        </div>
        <div style="background:#fff; border:1px solid var(--border); border-radius:7px; padding:10px 12px; font-size:0.84rem;">
          <strong style="color:var(--accent); font-size:0.9rem;">4. Check Readiness</strong><br>
          Verify deterministic readiness before dispatching.
        </div>
        <div style="background:#fff; border:1px solid var(--border); border-radius:7px; padding:10px 12px; font-size:0.84rem;">
          <strong style="color:var(--accent); font-size:0.9rem;">5. Dispatch Safely</strong><br>
          Execute locally with complete auditability.
        </div>
      </div>

      <div style="font-weight:600; font-size:0.88rem; margin-bottom:8px; color:var(--text);">Quick Starters:</div>
      <div class="starter-chips">
        <button class="starter-chip" data-prompt="Help me plan a 3-month strength training and nutrition routine">Fitness & Nutrition Plan</button>
        <button class="starter-chip" data-prompt="Draft an executive summary of our Q3 product roadmap update">Drafting Executive Brief</button>
        <button class="starter-chip" data-prompt="Inspect the Jarvis registered project and check workspace structure">Inspect Jarvis Project</button>
        <button class="starter-chip" data-prompt="We need to evaluate moving to a new apartment vs renewing current lease">Decision Analysis</button>
        <button class="starter-chip" data-prompt="Troubleshoot intermittent Wi-Fi disconnection on Windows 11 PC">PC Troubleshooting</button>
        <button class="starter-chip" data-prompt="Organize my project files and personal notes structure">Knowledge Organizer</button>
        <button class="starter-chip" data-prompt="Coordinate my weekly commitments across career, fitness, and home">Life Dashboard Coordinator</button>
      </div>
    </div>
  </section>

  <!-- Route Preview / Staging Drawer -->
  <section id="staging-drawer" class="staging-drawer" style="display:none;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div style="display:flex; align-items:center; gap:10px;">
        <h3>Route & Payload Preview</h3>
        <span id="drawer-confidence-pill" class="pill">Confidence</span>
        <span id="drawer-readiness-pill" class="pill">Readiness</span>
      </div>
      <button id="close-drawer-btn" class="secondary small" type="button">Close Preview</button>
    </div>

    <div class="route-info-card">
      <div class="route-info-header">
        <strong>Recommended Agent:</strong> <span id="drawer-agent-name"></span>
        <span class="muted" id="drawer-category"></span>
      </div>
      <div class="route-rationale" id="drawer-rationale"></div>
    </div>

    <div id="drawer-high-stakes" class="banner high-stakes" style="display:none;"></div>
    <div id="drawer-ambiguity-notice" class="banner warning" style="display:none;"></div>

    <div>
      <div style="font-weight:600; font-size:0.88rem; margin-bottom:6px;">Alternative Candidate Agents:</div>
      <div class="alternatives-grid" id="drawer-alternatives-grid"></div>
    </div>

    <div>
      <div style="font-weight:600; font-size:0.88rem; margin-bottom:4px;">Payload Readiness Notes:</div>
      <div id="drawer-readiness-notes" class="muted" style="font-size:0.85rem;"></div>
    </div>

    <div>
      <div style="font-weight:600; font-size:0.88rem; margin-bottom:4px;">Edit Prepared Request Payload (JSON):</div>
      <textarea id="drawer-payload-editor" class="composer-textarea" style="font-family:Consolas,monospace; font-size:0.85rem; min-height:110px;"></textarea>
    </div>

    <div style="display:flex; justify-content:flex-end; gap:8px;">
      <button id="drawer-cancel-btn" class="secondary" type="button">Cancel</button>
      <button id="drawer-execute-btn" type="button">Run Selected Agent</button>
    </div>
  </section>

  <!-- Result Board Drawer -->
  <section id="result-board-drawer" class="panel" style="display:none;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
      <h3 style="margin:0;">Session Result Board</h3>
      <button id="close-result-board-btn" class="secondary small" type="button">Close</button>
    </div>
    <p class="muted" style="margin:0 0 12px; font-size:0.88rem;">Key decisions, briefs, and plans collected during this session. In-memory only.</p>
    <div id="result-board-items" style="display:grid; gap:10px;"></div>
  </section>

  <!-- PRODUCTIVITY_READINESS_COACH_PLACEHOLDER -->

  <!-- Composer Area -->
  <div class="composer-card" id="composer">
    <textarea
      id="prompt-input"
      class="composer-textarea"
      placeholder="Type a request for Jarvis (e.g., 'Plan a healthy weekly meal prep routine' or 'Summarize these notes')..."
      rows="3"
    ></textarea>

    <div class="composer-options">
      <div class="options-left">
        <label class="toggle-label" title="Query relevant local memories if available">
          <input type="checkbox" id="opt-memory">
          <span>Include Memory</span>
        </label>
        <label class="toggle-label" title="Query Knowledge Library documents">
          <input type="checkbox" id="opt-knowledge">
          <span>Include Knowledge</span>
        </label>
        <label class="toggle-label" title="Select generation behavior">
          <span>Generation:</span>
          <select id="opt-generation">
            <option value="local_model_with_fallback" selected>Local Model (with Fallback)</option>
            <option value="local_model">Local Model Only</option>
            <option value="deterministic">Deterministic Only</option>
          </select>
        </label>
        <label class="toggle-label" title="Manually override agent routing">
          <span>Agent:</span>
          <select id="opt-agent-override">
            <option value="">Auto-Route (Deterministic)</option>
          </select>
        </label>
      </div>

      <div class="options-right">
        <button id="preview-route-btn" class="secondary" type="button">Preview Route</button>
        <button id="submit-btn" type="button">Ask Jarvis</button>
      </div>
    </div>
  </div>
</main>

<div class="toast" id="toast" role="alert"></div>

<script>
(function() {
  // In-memory session state (strictly non-persistent: not in localStorage, cookies, or DB)
  const sessionState = {
    transcript: [], // list of { role: 'user'|'jarvis', data: ... }
    resultBoard: [],
    stagedPriorContext: null,
    catalogAgents: [],
    projects: [],
    generationStatus: null,
    stagedAnalysis: null,
    isGenerating: false,
  };

  let activeRuntimeId = null;
  let activePoller = null;
  let activeTimer = null;

  const byId = (id) => document.getElementById(id);

  function showToast(message, duration = 3000) {
    const toast = byId('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), duration);
  }

  function escapeHtml(text) {
    if (!text) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  async function apiFetch(path, options = {}) {
    const res = await fetch(path, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });
    const data = await res.json().catch(() => ({ detail: 'Invalid JSON response from server.' }));
    if (!res.ok) {
      const msg = typeof data.detail === 'string' ? data.detail : (data.detail && (data.detail.message || data.detail.error)) || 'Request failed.';
      throw new Error(msg);
    }
    return data;
  }

  // Load system, generation status, and registered projects
  async function loadSystemStatus() {
    try {
      const genStatus = await apiFetch('/api/generation/status');
      sessionState.generationStatus = genStatus;
      const pill = byId('generation-pill');
      if (genStatus.enabled) {
        pill.className = 'pill active';
        pill.textContent = `Local Generation: Active (${genStatus.modelName || 'Ollama'})`;
      } else {
        pill.className = 'pill inactive';
        pill.textContent = 'Local Generation: Off (Deterministic)';
      }
    } catch (err) {
      byId('generation-pill').textContent = 'Local Generation: Unavailable';
    }

    try {
      const catalog = await apiFetch('/agents/local-response-agents/discovery');
      if (catalog && catalog.agents) {
        sessionState.catalogAgents = catalog.agents;
        populateAgentOverrideDropdown(catalog.agents);
        byId('agents-pill').textContent = `${catalog.agents.length} Response Agents Ready`;
      }
    } catch (err) {
      byId('agents-pill').textContent = 'Agents Discovery Error';
    }

    try {
      const projects = await apiFetch('/projects');
      if (Array.isArray(projects)) {
        sessionState.projects = projects;
      }
    } catch (err) {
      sessionState.projects = [];
    }
  }

  function populateAgentOverrideDropdown(agents) {
    const select = byId('opt-agent-override');
    select.replaceChildren();
    const defaultOpt = document.createElement('option');
    defaultOpt.value = '';
    defaultOpt.textContent = 'Auto-Route (Deterministic)';
    select.append(defaultOpt);

    // Group by category
    const groups = {};
    agents.forEach(agent => {
      const cat = agent.category || 'General';
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(agent);
    });

    Object.keys(groups).sort().forEach(category => {
      const optgroup = document.createElement('optgroup');
      optgroup.label = category;
      groups[category].forEach(agent => {
        const opt = document.createElement('option');
        opt.value = agent.agentId || agent.agent_id;
        opt.textContent = agent.displayName || agent.display_name || agent.name;
        optgroup.append(opt);
      });
      select.append(optgroup);
    });
  }

  function setStagedPriorContext(context) {
    sessionState.stagedPriorContext = context;
    const bar = byId('staged-prior-context-bar');
    const summarySpan = byId('staged-prior-summary');
    if (context) {
      summarySpan.textContent = `${context.agentName || context.agentId} response (${(context.summary || context.response || '').slice(0, 70)}...)`;
      bar.style.display = 'flex';
      showToast('Prior answer attached as context for next message.');
    } else {
      bar.style.display = 'none';
    }
  }

  byId('clear-prior-context-btn').addEventListener('click', () => {
    setStagedPriorContext(null);
  });

  // Analyze request using deterministic routing engine
  async function analyzeRoute(promptText, explicitAgentId = null) {
    const payload = {
      requestText: promptText,
      explicitAgentId: explicitAgentId || byId('opt-agent-override').value || null,
      memoryEnabled: byId('opt-memory').checked,
      knowledgeEnabled: byId('opt-knowledge').checked,
      generationMode: byId('opt-generation').value,
      priorAgentContext: sessionState.stagedPriorContext ? {
        source_agent_id: sessionState.stagedPriorContext.agentId,
        source_response_id: sessionState.stagedPriorContext.responseId,
        summary: sessionState.stagedPriorContext.summary || sessionState.stagedPriorContext.response || '',
      } : null,
      webContext: [],
    };

    return await apiFetch('/api/assistant/analyze-route', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  function showStagingDrawer(analysisResult) {
    sessionState.stagedAnalysis = analysisResult;
    const drawer = byId('staging-drawer');
    const route = analysisResult.route;
    const readiness = analysisResult.readiness;

    byId('drawer-agent-name').textContent = route.selected_display_name;
    byId('drawer-category').textContent = `[${route.category}]`;
    byId('drawer-rationale').textContent = route.routing_rationale;

    const confPill = byId('drawer-confidence-pill');
    confPill.className = `pill ${route.confidence_tier}`;
    confPill.textContent = `Confidence: ${route.confidence_tier.replace('_', ' ')}`;

    // High stakes banner
    const hsBanner = byId('drawer-high-stakes');
    if (route.high_stakes) {
      hsBanner.style.display = 'block';
      hsBanner.innerHTML = `<strong>High-Stakes Category (${escapeHtml(route.high_stakes_category || route.category)}):</strong> ${escapeHtml(route.safety_reminders.join(' '))}`;
    } else {
      hsBanner.style.display = 'none';
    }

    // Ambiguity notice
    const ambNotice = byId('drawer-ambiguity-notice');
    if (route.is_ambiguous) {
      ambNotice.style.display = 'block';
      ambNotice.innerHTML = `<strong>Ambiguous Match:</strong> ${escapeHtml(route.ambiguity_reason || 'Multiple agents scored similarly.')}`;
    } else {
      ambNotice.style.display = 'none';
    }

    // Alternatives grid
    const altGrid = byId('drawer-alternatives-grid');
    altGrid.replaceChildren();
    if (route.alternatives && route.alternatives.length) {
      route.alternatives.forEach(alt => {
        const card = document.createElement('div');
        card.className = 'alt-card';
        card.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>${escapeHtml(alt.display_name)}</strong>
            <button class="secondary small" type="button" data-switch-id="${escapeHtml(alt.agent_id)}">Switch</button>
          </div>
          <div class="muted" style="font-size:0.8rem;">${escapeHtml(alt.category)} · ${escapeHtml(alt.reason)}</div>
        `;
        card.querySelector('button').addEventListener('click', async () => {
          byId('opt-agent-override').value = alt.agent_id;
          const reAnalysis = await analyzeRoute(analysisResult.request_text, alt.agent_id);
          showStagingDrawer(reAnalysis);
        });
        altGrid.append(card);
      });
    }

    // Readiness
    const readPill = byId('drawer-readiness-pill');
    if (readiness.is_ready) {
      readPill.className = 'pill active';
      readPill.textContent = 'Ready';
    } else {
      readPill.className = 'pill weak';
      readPill.textContent = 'Incomplete';
    }
    byId('drawer-readiness-notes').textContent = readiness.readiness_notes;

    // Editable JSON
    byId('drawer-payload-editor').value = JSON.stringify(analysisResult.prepared_payload, null, 2);

    drawer.style.display = 'grid';
    drawer.scrollIntoView({ behavior: 'smooth' });
  }

  byId('close-drawer-btn').addEventListener('click', () => {
    byId('staging-drawer').style.display = 'none';
  });
  byId('drawer-cancel-btn').addEventListener('click', () => {
    byId('staging-drawer').style.display = 'none';
  });

  // Execute staged agent call
  async function executeStagedAgent() {
    if (!sessionState.stagedAnalysis) return;
    const analysis = sessionState.stagedAnalysis;
    const selectedAgentId = analysis.route.selected_agent_id;

    let payloadToExecute = analysis.prepared_payload;
    try {
      const editedText = byId('drawer-payload-editor').value;
      payloadToExecute = JSON.parse(editedText);
    } catch (err) {
      alert('Invalid JSON in request payload editor. Please correct before running.');
      return;
    }

    byId('staging-drawer').style.display = 'none';
    await runAgent(analysis.request_text, selectedAgentId, analysis.route, payloadToExecute);
  }

  byId('drawer-execute-btn').addEventListener('click', executeStagedAgent);

  // Core execution flow with active generation control and cancellation
  async function runAgent(promptText, agentId, routeInfo, payload) {
    if (sessionState.isGenerating) return;
    sessionState.isGenerating = true;

    // Append user turn
    const userTurn = {
      role: 'user',
      timestamp: new Date().toLocaleTimeString(),
      text: promptText,
      options: {
        memory: !!payload.memory,
        knowledge: !!payload.knowledge,
        generation: payload.generation ? payload.generation.mode : 'deterministic',
        priorContext: !!payload.prior_agent_context,
      }
    };
    sessionState.transcript.push(userTurn);
    renderTranscript();

    // Lock composer controls
    byId('submit-btn').disabled = true;
    byId('preview-route-btn').disabled = true;
    byId('prompt-input').disabled = true;
    byId('drawer-execute-btn').disabled = true;

    // Active generating UI card
    const isLocalModel = payload.generation && payload.generation.mode && payload.generation.mode !== 'deterministic';
    const container = byId('chat-container');
    const generatingDiv = document.createElement('article');
    generatingDiv.className = 'turn generating-card';
    generatingDiv.id = 'active-generating-turn';

    const modelDisplay = (sessionState.generationStatus && sessionState.generationStatus.modelName) || 'Local Model';
    const startTime = Date.now();

    generatingDiv.innerHTML = `
      <div class="generating-header">
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="pill active" style="background:#2563eb; color:#fff;">Jarvis is generating locally</span>
          <span class="pill strong">${escapeHtml(routeInfo ? routeInfo.selected_display_name : agentId)}</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="muted" id="gen-elapsed-time">Elapsed: 0.0s</span>
          <button class="danger small" id="stop-generation-btn" type="button">Stop generation</button>
        </div>
      </div>
      <div style="display:flex; flex-wrap:wrap; gap:12px; font-size:0.88rem; color:var(--muted);">
        <span>Model: <strong>${escapeHtml(modelDisplay)}</strong></span>
        <span>Phase: <strong id="gen-phase-indicator">connecting</strong></span>
        <span id="gen-runtime-id-label" style="display:none;">Runtime: <strong id="gen-runtime-id"></strong></span>
      </div>
    `;

    container.append(generatingDiv);
    generatingDiv.scrollIntoView({ behavior: 'smooth' });

    // Stop button event
    const stopBtn = generatingDiv.querySelector('#stop-generation-btn');
    stopBtn.addEventListener('click', async () => {
      stopBtn.disabled = true;
      stopBtn.textContent = 'Stopping...';
      try {
        await apiFetch('/api/generation/cancel', {
          method: 'POST',
          body: JSON.stringify({
            confirmation: 'CANCEL LOCAL GENERATION',
            expectedRuntimeId: activeRuntimeId || null,
            actor: 'local_user'
          })
        });
        showToast('Cancellation requested...');
        byId('gen-phase-indicator').textContent = 'cancelling';
      } catch (err) {
        showToast('Cancellation notice: ' + err.message);
      }
    });

    // Start elapsed timer
    activeTimer = setInterval(() => {
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      const span = byId('gen-elapsed-time');
      if (span) span.textContent = `Elapsed: ${elapsed}s`;
    }, 100);

    // Start runtime status poller if local model used
    if (isLocalModel) {
      activePoller = setInterval(async () => {
        try {
          const runtime = await apiFetch('/api/generation/active');
          if (runtime && runtime.active) {
            activeRuntimeId = runtime.runtimeId;
            const phaseSpan = byId('gen-phase-indicator');
            if (phaseSpan) phaseSpan.textContent = runtime.phase || 'generating';
            const rtLabel = byId('gen-runtime-id-label');
            const rtSpan = byId('gen-runtime-id');
            if (rtLabel && rtSpan && runtime.runtimeId) {
              rtLabel.style.display = 'inline';
              rtSpan.textContent = runtime.runtimeId.slice(0, 8) + '...';
            }
          }
        } catch (e) {
          // Keep polling quietly
        }
      }, 800);
    }

    try {
      const responseData = await apiFetch('/api/assistant/execute', {
        method: 'POST',
        body: JSON.stringify({
          agentId: agentId,
          payload: payload,
        })
      });

      const jarvisTurn = {
        role: 'jarvis',
        timestamp: new Date().toLocaleTimeString(),
        agentId: agentId,
        route: routeInfo,
        response: responseData,
        rawPayload: payload,
        detectedIntent: null,
        selectedActionType: 'inspect_project',
        selectedProject: (sessionState.projects && sessionState.projects.length === 1) ? sessionState.projects[0].name : '',
        actionBridgeOpen: false,
        policyStatus: null,
        policyReason: null,
        dryRunResult: null,
      };

      try {
        const intent = await apiFetch('/api/assistant/actions/detect-intent', {
          method: 'POST',
          body: JSON.stringify({ requestText: promptText, agentId: agentId })
        });
        jarvisTurn.detectedIntent = intent;
        if (intent && intent.actionable && intent.detectedActionType) {
          jarvisTurn.selectedActionType = intent.detectedActionType;
          if (intent.detectedProjectName) {
            jarvisTurn.selectedProject = intent.detectedProjectName;
          }
          jarvisTurn.actionBridgeOpen = true;
        }
      } catch (e) {
        // quiet fallback
      }

      sessionState.transcript.push(jarvisTurn);

      // Consume staged prior context after use
      setStagedPriorContext(null);
      byId('prompt-input').value = '';
    } catch (err) {
      const errorTurn = {
        role: 'jarvis',
        timestamp: new Date().toLocaleTimeString(),
        agentId: agentId,
        route: routeInfo,
        error: err.message,
      };
      sessionState.transcript.push(errorTurn);
    } finally {
      // Clear poller & timer
      if (activeTimer) clearInterval(activeTimer);
      if (activePoller) clearInterval(activePoller);
      activeTimer = null;
      activePoller = null;
      activeRuntimeId = null;
      sessionState.isGenerating = false;

      // Remove generating card
      const genCard = byId('active-generating-turn');
      if (genCard) genCard.remove();

      // Unlock composer
      byId('submit-btn').disabled = false;
      byId('preview-route-btn').disabled = false;
      byId('prompt-input').disabled = false;
      byId('drawer-execute-btn').disabled = false;
      byId('prompt-input').focus();

      renderTranscript();
    }
  }

  // Render complete conversation transcript in page memory
  function renderTranscript() {
    const container = byId('chat-container');
    const empty = byId('empty-state');

    if (!sessionState.transcript.length) {
      empty.style.display = 'block';
      container.replaceChildren(empty);
      return;
    }

    empty.style.display = 'none';
    container.replaceChildren();

    sessionState.transcript.forEach((turn, index) => {
      const turnDiv = document.createElement('article');
      turnDiv.className = `turn ${turn.role === 'user' ? 'user-turn' : 'jarvis-turn'}`;

      if (turn.role === 'user') {
        const chips = [];
        if (turn.options.memory) chips.push('<span class="pill active">Memory</span>');
        if (turn.options.knowledge) chips.push('<span class="pill active">Knowledge</span>');
        if (turn.options.priorContext) chips.push('<span class="pill override">Prior Context</span>');

        turnDiv.innerHTML = `
          <div class="turn-header">
            <span class="turn-title">You</span>
            <div style="display:flex; align-items:center; gap:6px;">
              ${chips.join(' ')}
              <span class="muted">${escapeHtml(turn.timestamp)}</span>
            </div>
          </div>
          <div class="turn-body">${escapeHtml(turn.text)}</div>
        `;
      } else {
        // Jarvis turn
        if (turn.error) {
          turnDiv.innerHTML = `
            <div class="turn-header">
              <span class="turn-title">Jarvis · ${escapeHtml(turn.route ? turn.route.selected_display_name : turn.agentId)}</span>
              <span class="muted">${escapeHtml(turn.timestamp)}</span>
            </div>
            <div class="banner danger">
              <strong>Execution Notice:</strong> ${escapeHtml(turn.error)}
            </div>
          `;
        } else {
          const resp = turn.response || {};
          const isCancelled = resp.status === 'cancelled' || (resp.generationContext && resp.generationContext.status === 'cancelled');
          const primaryText = resp.generatedResponse ? resp.generatedResponse.response : (resp.summary || resp.brief || resp.plan || resp.draft || resp.response || JSON.stringify(resp, null, 2));

          let cancelledBannerHtml = '';
          if (isCancelled) {
            cancelledBannerHtml = `
              <div class="banner warning" style="margin-bottom:10px;">
                <strong>Generation Cancelled:</strong> Local generation was stopped by user.
                ${resp.fallbackUsed ? 'The deterministic response remains available below.' : ''}
              </div>
            `;
          }

          let keyPointsHtml = '';
          if (resp.generatedResponse && resp.generatedResponse.keyPoints && resp.generatedResponse.keyPoints.length) {
            keyPointsHtml = `
              <div class="response-section">
                <h4>Key Points</h4>
                <ul class="key-points-list">
                  ${resp.generatedResponse.keyPoints.map(kp => `<li>${escapeHtml(kp)}</li>`).join('')}
                </ul>
              </div>
            `;
          }

          let citationsHtml = '';
          if (resp.generatedResponse && resp.generatedResponse.citations && resp.generatedResponse.citations.length) {
            citationsHtml = `
              <div class="citations-card">
                <strong>Citations / Evidence:</strong>
                <ul style="margin:4px 0 0; padding-left:18px;">
                  ${resp.generatedResponse.citations.map(c => `<li>${escapeHtml(c)}</li>`).join('')}
                </ul>
              </div>
            `;
          }

          let safetyNotesHtml = '';
          const safetyNotes = (resp.generatedResponse && resp.generatedResponse.safetyNotes) || resp.safetyNotes || (turn.route && turn.route.safety_reminders);
          if (safetyNotes && safetyNotes.length) {
            safetyNotesHtml = `
              <div class="banner warning" style="margin-top:10px; font-size:0.85rem;">
                <strong>Safety & Scope:</strong> ${escapeHtml(Array.isArray(safetyNotes) ? safetyNotes.join(' ') : String(safetyNotes))}
              </div>
            `;
          }

          let hsNoticeHtml = '';
          if (turn.route && turn.route.high_stakes) {
            hsNoticeHtml = `
              <div class="banner high-stakes" style="margin-bottom:10px; font-size:0.86rem;">
                <strong>High-Stakes Warning:</strong> Jarvis provides informational planning only. No professional diagnosis, filing, transaction, or emergency action is performed.
              </div>
            `;
          }

          turnDiv.innerHTML = `
            <div class="turn-header">
              <span class="turn-title">Jarvis</span>
              <div style="display:flex; align-items:center; gap:6px;">
                <span class="pill strong">${escapeHtml(turn.route ? turn.route.selected_display_name : turn.agentId)}</span>
                ${isCancelled ? '<span class="pill cancelled">Cancelled</span>' : (resp.actualMode ? `<span class="pill ${resp.actualMode === 'deterministic' ? 'inactive' : 'active'}">${escapeHtml(resp.actualMode)}</span>` : '')}
                <span class="muted">${escapeHtml(turn.timestamp)}</span>
              </div>
            </div>

            <div class="route-info-card" style="margin-bottom:8px;">
              <div class="route-info-header">
                <strong>Selected Agent:</strong> ${escapeHtml(turn.route ? turn.route.selected_display_name : turn.agentId)}
                <span class="muted">(${escapeHtml(turn.route ? turn.route.category : '')})</span>
                <span class="pill ${turn.route ? turn.route.confidence_tier : ''}">${escapeHtml(turn.route ? turn.route.confidence_tier : '')}</span>
              </div>
              <div class="route-rationale">${escapeHtml(turn.route ? turn.route.routing_rationale : 'Deterministic execution.')}</div>
            </div>

            ${hsNoticeHtml}
            ${cancelledBannerHtml}

            ${renderDecisionResultHtml(turn, resp, index)}

            <div class="turn-body" ${(resp.comparisonMatrix || resp.suggestedDirection) ? 'style="display:none;"' : ''}>${escapeHtml(primaryText)}</div>

            ${keyPointsHtml}
            ${citationsHtml}
            ${safetyNotesHtml}

            <div class="turn-actions">
              <button class="secondary small" type="button" data-action="use-prior" data-turn-idx="${index}">Use as prior context for next message</button>
              <button class="secondary small" type="button" data-action="add-board" data-turn-idx="${index}">Add to Result Board</button>
              <button class="secondary small" type="button" data-action="add-kit" data-turn-idx="${index}">Add to Context Kit</button>
              <button class="secondary small" type="button" data-action="toggle-json" data-turn-idx="${index}">Inspect Metadata & JSON</button>
            </div>

            <div class="json-panel" id="json-panel-${index}" style="display:none; margin-top:8px;">
              <pre class="json-viewer">${escapeHtml(JSON.stringify(resp, null, 2))}</pre>
            </div>

            <div class="action-bridge-card" id="action-bridge-${index}">
              <div class="action-bridge-header">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="pill dry-run">Action Bridge</span>
                  <span class="muted" style="font-size:0.84rem;">
                    ${turn.detectedIntent && turn.detectedIntent.actionable ?
                      `Candidate action detected: <strong>${escapeHtml(turn.detectedIntent.detectedActionType)}</strong>` :
                      (turn.detectedIntent && !turn.detectedIntent.supported ?
                        `<span style="color:var(--danger);">${escapeHtml(turn.detectedIntent.explanation)}</span>` :
                        'Informational response only · No action taken.')}
                  </span>
                </div>
                <button class="secondary small" type="button" data-action="toggle-action-bridge" data-turn-idx="${index}">
                  ${turn.actionBridgeOpen ? 'Close Action Bridge' : (turn.detectedIntent && turn.detectedIntent.actionable ? 'Prepare Action Proposal' : 'Prepare Action')}
                </button>
              </div>

              ${turn.actionBridgeOpen ? `
                <div style="display:grid; gap:10px; margin-top:8px; padding-top:8px; border-top:1px solid #e2e8f0;">
                  <div class="action-form-grid">
                    <div class="action-field">
                      <label for="action-type-select-${index}">Proposed Action Type</label>
                      <select id="action-type-select-${index}" data-turn-idx="${index}">
                        <option value="inspect_project" ${turn.selectedActionType === 'inspect_project' ? 'selected' : ''}>inspect_project (Read-Only Inspection)</option>
                        <option value="read_project_text_files" ${turn.selectedActionType === 'read_project_text_files' ? 'selected' : ''}>read_project_text_files (Read Project Source Files)</option>
                        <option value="write_report" ${turn.selectedActionType === 'write_report' ? 'selected' : ''}>write_report (Structured Report Creation)</option>
                        <option value="modify_project_files_with_codex" ${turn.selectedActionType === 'modify_project_files_with_codex' ? 'selected' : ''}>modify_project_files_with_codex (Controlled Coding with Codex)</option>
                      </select>
                    </div>
                    <div class="action-field">
                      <label for="action-project-select-${index}">Target Registered Project</label>
                      <select id="action-project-select-${index}" data-turn-idx="${index}">
                        <option value="">-- Select Registered Project --</option>
                        ${(sessionState.projects || []).map(p => `<option value="${escapeHtml(p.name)}" ${turn.selectedProject === p.name ? 'selected' : ''}>${escapeHtml(p.name)} (${escapeHtml(p.path)})</option>`).join('')}
                      </select>
                    </div>
                  </div>

                  ${turn.selectedActionType === 'read_project_text_files' ? `
                    <div style="display:grid; gap:8px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <label style="font-weight:600; font-size:0.85rem;">Select Safe Project Files (Max 5):</label>
                        <span class="pill ${(turn.selectedRelativePaths || []).length > 0 ? 'allowed' : 'inactive'}">
                          Selected: ${(turn.selectedRelativePaths || []).length} / 5
                        </span>
                      </div>
                      <div style="display:flex; gap:6px;">
                        <input type="text" id="file-catalog-search-${index}" placeholder="Filter project files..." style="font-size:0.82rem; padding:4px 8px; flex:1;" value="${escapeHtml(turn.fileCatalogFilter || '')}" />
                        <button class="secondary small" type="button" data-action="refresh-file-catalog" data-turn-idx="${index}">Refresh</button>
                      </div>
                      <div id="file-catalog-list-${index}" style="max-height:160px; overflow-y:auto; border:1px solid #cbd5e1; border-radius:4px; background:#fff; padding:4px;">
                        ${renderFileCatalogItems(index, turn)}
                      </div>
                      <div class="muted" style="font-size:0.8rem;">
                        <strong>Security Invariant:</strong> Only safe source/text files from registered project are listed. Protected patterns, dependencies, caches, and binary files are automatically excluded.
                      </div>
                    </div>
                  ` : ''}

                  ${turn.selectedActionType === 'write_report' ? `
                    <div style="display:grid; gap:8px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px;">
                      <div class="action-field">
                        <label for="report-title-input-${index}">Report Title</label>
                        <input type="text" id="report-title-input-${index}" value="${escapeHtml(turn.reportTitle || `${turn.selectedProject || 'Project'} Summary Report`)}" placeholder="Enter report title..." />
                      </div>
                      <div class="action-field">
                        <label for="report-content-input-${index}">Report Content (Markdown)</label>
                        <textarea id="report-content-input-${index}" rows="5" style="width:100%; font-family:inherit; font-size:0.85rem; padding:8px; border:1px solid #94a3b8; border-radius:5px; resize:vertical;" placeholder="Review/edit report content...">${escapeHtml(turn.reportContent !== undefined ? turn.reportContent : primaryText)}</textarea>
                      </div>
                      <div class="muted" style="font-size:0.8rem;">
                        <strong>Safe Output Rule:</strong> Report will be saved to Jarvis reports directory (<code>data/jarvis/reports/assistant</code>) as a new <code>.md</code> file. Project source files are never modified.
                      </div>
                    </div>
                  ` : ''}

                  ${turn.selectedActionType === 'modify_project_files_with_codex' ? `
                    <div style="display:grid; gap:10px; background:#fbfcfe; border:1px solid #c7d2fe; border-radius:6px; padding:12px;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#3730a3; font-size:0.92rem;">Controlled Coding with Codex (Extreme-Budget Mode)</strong>
                        <span class="pill allowed">1 Run Max · 0 Auto Checks · 0 Auto Repairs</span>
                      </div>

                      <div style="display:grid; gap:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                          <label style="font-weight:600; font-size:0.85rem;">Select Existing Target Files (1 to 10 files):</label>
                          <span class="pill ${(turn.selectedRelativePaths || []).length > 0 ? 'allowed' : 'inactive'}">
                            Selected: ${(turn.selectedRelativePaths || []).length} / 10
                          </span>
                        </div>
                        <div style="display:flex; gap:6px;">
                          <input type="text" id="file-catalog-search-${index}" placeholder="Filter project files..." style="font-size:0.82rem; padding:4px 8px; flex:1;" value="${escapeHtml(turn.fileCatalogFilter || '')}" />
                          <button class="secondary small" type="button" data-action="refresh-file-catalog" data-turn-idx="${index}">Refresh</button>
                        </div>
                        <div id="file-catalog-list-${index}" style="max-height:160px; overflow-y:auto; border:1px solid #cbd5e1; border-radius:4px; background:#fff; padding:4px;">
                          ${renderFileCatalogItems(index, turn)}
                        </div>
                        <div class="muted" style="font-size:0.78rem;">
                          <strong>Safety Invariant:</strong> Existing files only (no new files, renames, or deletions). Approval-time SHA-256 hashes are locked into the machine manifest.
                        </div>
                      </div>

                      <div style="display:grid; gap:8px;">
                        <div class="action-field">
                          <label for="coding-goal-${index}">Coding Task Goal</label>
                          <input type="text" id="coding-goal-${index}" value="${escapeHtml(turn.codingGoal !== undefined ? turn.codingGoal : (turn.prompt || ''))}" placeholder="High-level goal for this change..." />
                        </div>
                        <div class="action-field">
                          <label for="coding-scope-${index}">Exact Scope (What to modify)</label>
                          <textarea id="coding-scope-${index}" rows="3" style="width:100%; font-family:inherit; font-size:0.85rem; padding:6px; border:1px solid #94a3b8; border-radius:4px; resize:vertical;" placeholder="Describe exact requested modifications...">${escapeHtml(turn.codingScope !== undefined ? turn.codingScope : primaryText)}</textarea>
                        </div>
                        <div class="action-field">
                          <label for="coding-non-goals-${index}">Non-Goals (What NOT to touch)</label>
                          <input type="text" id="coding-non-goals-${index}" value="${escapeHtml(turn.codingNonGoals !== undefined ? turn.codingNonGoals : 'Do not modify unselected files, install dependencies, or edit tests.')}" placeholder="Explicit non-goals and restrictions..." />
                        </div>
                      </div>

                      <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px; margin-top:4px;">
                        <span class="muted" style="font-size:0.8rem;">Generates a verified scope manifest and requests plan approval. Nothing executes yet.</span>
                        <button class="small" style="background:#4338ca; border-color:#4338ca;" type="button" data-action="prepare-coding-plan" data-turn-idx="${index}">Prepare Conservative Plan</button>
                      </div>

                      ${turn.codingPlan ? `
                        <div style="background:#fff; border:1px solid #a5b4fc; border-radius:6px; padding:12px; display:grid; gap:8px; margin-top:6px;">
                          <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                              <strong style="color:#312e81;">Conservative Plan: <code>${escapeHtml(turn.codingPlan.planId)}</code></strong>
                              <div class="muted" style="font-size:0.8rem;">Task: <code>${escapeHtml(turn.codingPlan.taskId)}</code> · Project: <strong>${escapeHtml(turn.codingPlan.projectName)}</strong></div>
                            </div>
                            <span class="pill ${turn.codingPlan.status === 'approved_for_future_execution' ? 'succeeded' : (turn.codingPlan.status === 'execution_consumed' ? 'inactive' : (turn.codingPlan.status === 'waiting_for_approval' ? 'waiting_for_approval' : 'blocked'))}">
                              ${escapeHtml(turn.codingPlan.status.toUpperCase())}
                            </span>
                          </div>

                          <div style="font-size:0.82rem;">
                            <strong>Approved Scope Manifest:</strong>
                            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px; padding:6px 8px; margin-top:4px; max-height:120px; overflow-y:auto; font-family:Consolas, Monaco, monospace; font-size:0.78rem;">
                              ${(turn.codingPlan.allowedFiles || []).map(f => {
                                const h = (turn.codingPlan.allowedFileHashes || {})[f] || '';
                                return `<div><strong>${escapeHtml(f)}</strong> <span class="muted">(SHA: ${escapeHtml(h.slice(0, 12))}...)</span></div>`;
                              }).join('')}
                            </div>
                          </div>

                          <div style="display:flex; flex-wrap:wrap; gap:6px; font-size:0.75rem;">
                            <span class="pill allowed">Max Runs: 1</span>
                            <span class="pill allowed">Max Lines: 700</span>
                            <span class="pill allowed">Checks: Disabled</span>
                            <span class="pill allowed">Repairs: Disabled</span>
                            <span class="pill allowed">Clean Baseline Required</span>
                            <span class="pill allowed">No Auto Commit/Push</span>
                          </div>

                          ${turn.codingPlan.status === 'waiting_for_approval' ? `
                            <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px; border-top:1px solid #f1f5f9; padding-top:8px;">
                              <span class="muted" style="font-size:0.8rem;">Requires confirmation: <code>APPROVE CONSERVATIVE CODEX PLAN</code></span>
                              <div style="display:flex; gap:6px;">
                                <button class="secondary small" type="button" data-action="reject-coding-plan" data-turn-idx="${index}">Reject Plan</button>
                                <button class="small" style="background:#15803d; border-color:#15803d;" type="button" data-action="approve-coding-plan" data-turn-idx="${index}">Approve Conservative Plan</button>
                              </div>
                            </div>
                          ` : ''}

                          ${turn.codingPlan.status === 'approved_for_future_execution' && !turn.codingActive && !turn.codingExecutionResult ? `
                            <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:6px; padding:10px; display:grid; gap:8px; margin-top:4px;">
                              <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="color:#166534;">Plan Approved for Future Execution</strong>
                                <span class="pill succeeded">Ready</span>
                              </div>
                              <p class="muted" style="font-size:0.82rem; margin:0;">
                                Preflight will check clean Git worktree and unchanged file hashes. Exactly one Codex child will run in workspace-write sandbox. No automated checks or repairs will run.
                              </p>
                              <div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
                                <span class="muted" style="font-size:0.8rem;">Requires confirmation: <code>EXECUTE APPROVED CODEX CHANGE</code></span>
                                <button class="small" style="background:#15803d; border-color:#15803d;" type="button" data-action="execute-coding-plan" data-turn-idx="${index}">Execute Approved Change</button>
                              </div>
                            </div>
                          ` : ''}
                        </div>
                      ` : ''}

                      ${turn.codingActive ? `
                        <div style="background:#fffbeb; border:2px solid #f59e0b; border-radius:6px; padding:12px; display:grid; gap:8px; margin-top:6px;">
                          <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong style="color:#b45309;">Codex Process Active (Single Run Mode)...</strong>
                            <span class="pill waiting">Running</span>
                          </div>
                          <div class="muted" style="font-size:0.82rem;">
                            Jarvis is supervising Codex execution on <strong>${escapeHtml(turn.selectedProject)}</strong>. Zero automated tests or repairs will run.
                          </div>
                          <div style="display:flex; justify-content:flex-end;">
                            <button class="small" style="background:#b91c1c; border-color:#b91c1c;" type="button" data-action="cancel-coding-execution" data-turn-idx="${index}">Stop Codex Execution</button>
                          </div>
                        </div>
                      ` : ''}

                      ${turn.codingExecutionResult ? `
                        <div class="action-result-box ${turn.codingExecutionResult.status === 'succeeded' ? 'succeeded' : (turn.codingExecutionResult.status === 'blocked' ? 'blocked' : 'waiting')}" style="margin-top:8px; border-width:2px;">
                          <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong>${escapeHtml(turn.codingExecutionResult.message)}</strong>
                            <span class="pill ${escapeHtml(turn.codingExecutionResult.status)}">${escapeHtml(turn.codingExecutionResult.status.toUpperCase())}</span>
                          </div>
                          <div class="muted" style="font-size:0.84rem; margin-top:2px;">
                            Execution ID: <code>${escapeHtml(turn.codingExecutionResult.executionId)}</code> · Exit Code: <strong>${escapeHtml(turn.codingExecutionResult.exitCode)}</strong> · Baseline SHA: <code>${escapeHtml(turn.codingExecutionResult.baselineHeadSha || 'unknown')}</code>
                          </div>

                          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:6px; margin:6px 0;">
                            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px 8px; font-size:0.82rem;">
                              <span class="muted">Changed Files:</span> <strong>${escapeHtml(turn.codingExecutionResult.changedFileCount)}</strong>
                            </div>
                            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px 8px; font-size:0.82rem;">
                              <span class="muted">Added Lines:</span> <strong style="color:#166534;">+${escapeHtml(turn.codingExecutionResult.addedLines)}</strong>
                            </div>
                            <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px 8px; font-size:0.82rem;">
                              <span class="muted">Deleted Lines:</span> <strong style="color:#991b1b;">-${escapeHtml(turn.codingExecutionResult.deletedLines)}</strong>
                            </div>
                          </div>

                          ${turn.codingExecutionResult.changedFiles && turn.codingExecutionResult.changedFiles.length ? `
                            <div style="font-size:0.82rem; margin-top:4px;">
                              <strong>Changed Files in Workspace:</strong>
                              <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px; font-family:Consolas, Monaco, monospace; font-size:0.78rem;">
                                ${turn.codingExecutionResult.changedFiles.map(f => `<div>${escapeHtml(f)}</div>`).join('')}
                              </div>
                            </div>
                          ` : ''}

                          <div style="display:flex; flex-wrap:wrap; gap:6px; font-size:0.75rem; margin-top:4px;">
                            <span class="pill allowed">Checks: SKIPPED (Extreme-Budget)</span>
                            <span class="pill allowed">Repairs: SKIPPED (Extreme-Budget)</span>
                            <span class="pill allowed">No Auto Commit/Push</span>
                          </div>

                          ${turn.codingExecutionResult.requiresUserReview ? `
                            <div style="background:#fef2f2; border:1px solid #f87171; border-radius:4px; padding:8px; font-size:0.82rem; color:#991b1b; margin-top:6px;">
                              <strong>Policy Review Warning:</strong> ${escapeHtml((turn.codingExecutionResult.reviewReasons || []).join('; '))}
                            </div>
                          ` : ''}

                          <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:8px;">
                            <button class="small" style="background:#2563eb; border-color:#2563eb;" type="button" data-action="review-changed-files" data-turn-idx="${index}">Review Changed Files in Source Reader</button>
                            <button class="secondary small" type="button" data-action="add-codex-board" data-turn-idx="${index}">Add to Result Board</button>
                            <a href="/actions" class="button-link small" style="display:inline-block; font-size:0.8rem; padding:3px 8px; background:var(--accent); color:#fff; border-radius:4px; text-decoration:none;">View in Action Center</a>
                          </div>
                        </div>
                      ` : ''}
                    </div>
                  ` : ''}

                  ${turn.selectedActionType !== 'modify_project_files_with_codex' ? `
                    <div class="action-preview-box" id="action-policy-preview-${index}">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong>Policy Preview:</strong>
                        <span class="pill ${turn.policyStatus === 'allowed' ? 'succeeded' : (turn.policyStatus === 'blocked' ? 'blocked' : (turn.policyStatus === 'approval_required' ? 'waiting_for_approval' : 'inactive'))}" id="policy-status-pill-${index}">
                          ${escapeHtml((turn.policyStatus || (turn.selectedProject ? 'ready' : 'needs_project')).toUpperCase())}
                        </span>
                      </div>
                      <div class="muted" id="policy-reason-${index}">
                        ${escapeHtml(turn.policyReason || (turn.selectedProject ? 'Project selected. Ready for policy check.' : 'Select a registered project target to preview policy status.'))}
                      </div>
                    </div>

                    <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px;">
                      <span class="muted" style="font-size:0.82rem;">Supervised dry-run task is validated via TaskQueue &amp; SafeActionRuntime. Nothing is executed.</span>
                      <button class="small" type="button" data-action="submit-dry-run" data-turn-idx="${index}">Validate Dry Run</button>
                    </div>

                    ${turn.dryRunResult ? `
                      <div class="action-result-box ${turn.dryRunResult.task && turn.dryRunResult.task.status === 'succeeded' ? 'succeeded' : (turn.dryRunResult.task && turn.dryRunResult.task.status === 'blocked' ? 'blocked' : 'waiting')}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                          <strong>${escapeHtml(turn.dryRunResult.summary)}</strong>
                          <span class="pill ${escapeHtml(turn.dryRunResult.task ? turn.dryRunResult.task.status : 'validated')}">${escapeHtml(turn.dryRunResult.task ? turn.dryRunResult.task.status : 'done')}</span>
                        </div>
                        <div class="muted" style="font-size:0.84rem;">
                          Dry-Run Task ID: <code>${escapeHtml(turn.dryRunResult.taskId)}</code>
                          ${turn.dryRunResult.receipts && turn.dryRunResult.receipts.length ? ` · Receipt ID: <code>${escapeHtml(turn.dryRunResult.receipts[0].receipt_id)}</code>` : ''}
                        </div>
                        <div style="margin-top:4px;">
                          <a href="/actions" class="button-link small" style="display:inline-block; font-size:0.8rem; padding:3px 8px; background:var(--accent); color:#fff; border-radius:4px; text-decoration:none;">View in Action Center</a>
                        </div>
                      </div>
                    ` : ''}

                    ${turn.dryRunResult && turn.selectedActionType === 'inspect_project' && turn.dryRunResult.task && turn.dryRunResult.task.status === 'succeeded' && !turn.realExecutionResult ? `
                      <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:6px; padding:12px; margin-top:8px; display:grid; gap:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                          <strong style="color:#166534;">Ready for Supervised Read-Only Execution:</strong>
                          <span class="pill succeeded">Dry-Run Proof Verified</span>
                        </div>
                        <div class="muted" style="font-size:0.84rem;">
                          Target: <strong>${escapeHtml(turn.selectedProject)}</strong> · Tool: <code>filesystem_tool</code> (Read-Only)
                        </div>
                        <div style="display:flex; flex-wrap:wrap; gap:6px; font-size:0.8rem;">
                          <span class="pill allowed">Read-Only</span>
                          <span class="pill allowed">Registered-Project Only</span>
                          <span class="pill allowed">No Shell / No Writes</span>
                          <span class="pill allowed">Protected Files Skipped</span>
                        </div>
                        <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px; margin-top:4px;">
                          <span class="muted" style="font-size:0.82rem;">Inspects workspace metadata synchronously without file modification.</span>
                          <button class="small" style="background:#15803d; border-color:#15803d;" type="button" data-action="execute-read-only" data-turn-idx="${index}">Execute Read-Only Inspection</button>
                        </div>
                      </div>
                    ` : ''}

                    ${turn.dryRunResult && turn.selectedActionType === 'read_project_text_files' && turn.dryRunResult.task && turn.dryRunResult.task.status === 'succeeded' && !turn.readExecutionResult ? `
                      <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:6px; padding:12px; margin-top:8px; display:grid; gap:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                          <strong style="color:#166534;">Ready to Read Selected Project Files:</strong>
                          <span class="pill succeeded">Dry-Run Proof Verified</span>
                        </div>
                        <div class="muted" style="font-size:0.84rem;">
                          Target: <strong>${escapeHtml(turn.selectedProject)}</strong> · Tool: <code>filesystem_tool</code> (Read-Only) · Files: <strong>${(turn.selectedRelativePaths || []).length} selected</strong>
                        </div>
                        <div style="display:flex; flex-wrap:wrap; gap:6px; font-size:0.8rem;">
                          <span class="pill allowed">Read Only</span>
                          <span class="pill allowed">Max 5 Files</span>
                          <span class="pill allowed">Protected Files Blocked</span>
                          <span class="pill allowed">No Shell</span>
                          <span class="pill allowed">No Writes</span>
                          <span class="pill allowed">Session Only</span>
                        </div>
                        <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px; margin-top:4px;">
                          <span class="muted" style="font-size:0.82rem;">Reads bounded source text synchronously into session memory without persisting content.</span>
                          <button class="small" style="background:#15803d; border-color:#15803d;" type="button" data-action="execute-project-text-read" data-turn-idx="${index}">Read Selected Project Files</button>
                        </div>
                      </div>
                    ` : ''}

                    ${turn.dryRunResult && turn.selectedActionType === 'write_report' && turn.dryRunResult.task && turn.dryRunResult.task.status === 'succeeded' && !turn.reportExecutionResult ? `
                      <div style="background:#eff6ff; border:1px solid #93c5fd; border-radius:6px; padding:12px; margin-top:8px; display:grid; gap:8px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                          <strong style="color:#1e40af;">Ready to Create Local Markdown Report:</strong>
                          <span class="pill succeeded">Dry-Run Proof Verified</span>
                        </div>
                        <div class="muted" style="font-size:0.84rem;">
                          Target: <strong>${escapeHtml(turn.selectedProject)}</strong> · Tool: <code>report_tool</code> (Non-Destructive Write)
                        </div>
                        <div style="display:flex; flex-wrap:wrap; gap:6px; font-size:0.8rem;">
                          <span class="pill allowed">New File Only</span>
                          <span class="pill allowed">Markdown Only</span>
                          <span class="pill allowed">Jarvis Reports Directory</span>
                          <span class="pill allowed">No Overwrite</span>
                          <span class="pill allowed">Project Files Unchanged</span>
                          <span class="pill allowed">Explicit Confirmation</span>
                        </div>
                        <div style="display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px; margin-top:4px;">
                          <span class="muted" style="font-size:0.82rem;">Writes a new .md report under data/jarvis/reports/assistant without modifying project source.</span>
                          <button class="small" style="background:#2563eb; border-color:#2563eb;" type="button" data-action="execute-report" data-turn-idx="${index}">Create Local Report</button>
                        </div>
                      </div>
                    ` : ''}
                  ` : ''}

                  ${turn.realExecutionResult ? `
                    <div class="action-result-box succeeded" style="margin-top:10px; border-width:2px; background:#f0fdf4; border-color:#22c55e;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#15803d;">Read-only inspection executed.</strong>
                        <span class="pill succeeded">Executed Read-Only</span>
                      </div>
                      <div class="muted" style="font-size:0.84rem;">
                        Project: <strong>${escapeHtml(turn.realExecutionResult.projectName)}</strong> · Real Task ID: <code>${escapeHtml(turn.realExecutionResult.taskId)}</code> · Receipt ID: <code>${escapeHtml(turn.realExecutionResult.receiptId)}</code>
                      </div>
                      ${turn.realExecutionResult.inspectionResult ? `
                        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:6px; margin:6px 0;">
                          <div style="background:#fff; border:1px solid #bbf7d0; border-radius:4px; padding:6px 8px; font-size:0.82rem;">
                            <span class="muted">Scanned Files:</span> <strong>${escapeHtml(turn.realExecutionResult.inspectionResult.scannedFiles)}</strong>
                          </div>
                          <div style="background:#fff; border:1px solid #bbf7d0; border-radius:4px; padding:6px 8px; font-size:0.82rem;">
                            <span class="muted">Protected Skipped:</span> <strong>${escapeHtml(turn.realExecutionResult.inspectionResult.protectedSkippedFiles)}</strong>
                          </div>
                          <div style="background:#fff; border:1px solid #bbf7d0; border-radius:4px; padding:6px 8px; font-size:0.82rem;">
                            <span class="muted">Skipped Dirs:</span> <strong>${escapeHtml(turn.realExecutionResult.inspectionResult.skippedDirs)}</strong>
                          </div>
                        </div>
                        ${turn.realExecutionResult.inspectionResult.docsDetected && turn.realExecutionResult.inspectionResult.docsDetected.length ? `
                          <div style="font-size:0.82rem; color:var(--muted); margin-top:4px;">
                            <strong>Detected Documentation:</strong> ${turn.realExecutionResult.inspectionResult.docsDetected.map(d => `<code>${escapeHtml(d.relativePath || d.filename || d.title || 'doc')}</code>`).join(', ')}
                          </div>
                        ` : ''}
                        ${turn.realExecutionResult.inspectionResult.warnings && turn.realExecutionResult.inspectionResult.warnings.length ? `
                          <div style="font-size:0.82rem; color:#b45309; margin-top:2px;">
                            <strong>Warnings:</strong> ${turn.realExecutionResult.inspectionResult.warnings.map(w => escapeHtml(w)).join('; ')}
                          </div>
                        ` : ''}
                      ` : ''}
                      <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:6px;">
                        <button class="secondary small" type="button" data-action="use-inspection-prior" data-turn-idx="${index}">Use inspection result as prior context</button>
                        <button class="secondary small" type="button" data-action="add-inspect-board" data-turn-idx="${index}">Add to Result Board</button>
                        <a href="/actions" class="button-link small" style="display:inline-block; font-size:0.8rem; padding:3px 8px; background:var(--accent); color:#fff; border-radius:4px; text-decoration:none;">View in Action Center</a>
                      </div>
                    </div>
                  ` : ''}

                  ${turn.readExecutionResult ? `
                    <div class="action-result-box succeeded" style="margin-top:10px; border-width:2px; background:#f0fdf4; border-color:#22c55e;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#15803d;">Project source files read successfully.</strong>
                        <span class="pill succeeded">Read ${turn.readExecutionResult.readResult ? turn.readExecutionResult.readResult.totalFiles : (turn.readExecutionResult.totalFiles || 0)} Files</span>
                      </div>
                      <div class="muted" style="font-size:0.84rem;">
                        Project: <strong>${escapeHtml(turn.readExecutionResult.projectName)}</strong> · Total Size: <strong>${escapeHtml(turn.readExecutionResult.readResult ? turn.readExecutionResult.readResult.totalBytes : (turn.readExecutionResult.totalBytes || 0))} bytes</strong> · Real Task ID: <code>${escapeHtml(turn.readExecutionResult.taskId)}</code> · Receipt ID: <code>${escapeHtml(turn.readExecutionResult.receiptId)}</code>
                      </div>
                      ${turn.readExecutionResult.readResult && turn.readExecutionResult.readResult.files ? `
                        <div style="display:grid; gap:8px; margin-top:8px;">
                          ${turn.readExecutionResult.readResult.files.map(f => `
                            <div style="background:#fff; border:1px solid #bbf7d0; border-radius:5px; padding:8px; font-size:0.82rem;">
                              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <strong><code>${escapeHtml(f.relativePath)}</code></strong>
                                <span class="muted">${escapeHtml(f.sizeBytes)} bytes · ${escapeHtml(f.lineCount)} lines · SHA: <code>${escapeHtml((f.sha256 || '').slice(0, 10))}...</code></span>
                              </div>
                              <pre style="max-height:220px; overflow:auto; background:#0f172a; color:#f8fafc; padding:8px 10px; border-radius:4px; font-family:Consolas, Monaco, 'Courier New', monospace; font-size:0.78rem; line-height:1.4; margin:0; white-space:pre-wrap; word-break:break-all;"><code>${escapeHtml(f.content)}</code></pre>
                            </div>
                          `).join('')}
                        </div>
                      ` : ''}
                      ${turn.readExecutionResult.readResult && turn.readExecutionResult.readResult.warnings && turn.readExecutionResult.readResult.warnings.length ? `
                        <div style="font-size:0.82rem; color:#b45309; margin-top:4px;">
                          <strong>Warnings:</strong> ${turn.readExecutionResult.readResult.warnings.map(w => escapeHtml(w)).join('; ')}
                        </div>
                      ` : ''}
                      <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:6px;">
                        <button class="secondary small" type="button" data-action="use-source-prior" data-turn-idx="${index}">Use selected file content as prior context</button>
                        <button class="secondary small" type="button" data-action="add-read-board" data-turn-idx="${index}">Add to Result Board</button>
                        <a href="/actions" class="button-link small" style="display:inline-block; font-size:0.8rem; padding:3px 8px; background:var(--accent); color:#fff; border-radius:4px; text-decoration:none;">View in Action Center</a>
                      </div>
                    </div>
                  ` : ''}

                  ${turn.reportExecutionResult ? `
                    <div class="action-result-box succeeded" style="margin-top:10px; border-width:2px; background:#eff6ff; border-color:#3b82f6;">
                      <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#1d4ed8;">Local Markdown report created.</strong>
                        <span class="pill succeeded">Created Report</span>
                      </div>
                      <div class="muted" style="font-size:0.84rem;">
                        Project: <strong>${escapeHtml(turn.reportExecutionResult.projectName)}</strong> · Real Task ID: <code>${escapeHtml(turn.reportExecutionResult.taskId)}</code> · Receipt ID: <code>${escapeHtml(turn.reportExecutionResult.receiptId)}</code>
                      </div>
                      ${turn.reportExecutionResult.reportResult ? `
                        <div style="background:#fff; border:1px solid #bfdbfe; border-radius:5px; padding:8px 10px; margin:6px 0; font-size:0.84rem; display:grid; gap:4px;">
                          <div><strong>File:</strong> <code>${escapeHtml(turn.reportExecutionResult.reportResult.filename)}</code></div>
                          <div><strong>Saved to:</strong> <code>${escapeHtml(turn.reportExecutionResult.reportResult.relativeReportPath)}</code> (Jarvis reports directory)</div>
                          <div><strong>Size:</strong> ${escapeHtml(turn.reportExecutionResult.reportResult.charCount)} characters (${escapeHtml(turn.reportExecutionResult.reportResult.byteCount)} bytes)</div>
                          <div style="font-size:0.8rem; color:#166534; font-weight:600;">✓ No project files were modified · Existing files were not overwritten</div>
                        </div>
                      ` : ''}
                      <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:6px;">
                        <button class="secondary small" type="button" data-action="use-report-prior" data-turn-idx="${index}">Use report summary as prior context</button>
                        <button class="secondary small" type="button" data-action="add-report-board" data-turn-idx="${index}">Add to Result Board</button>
                        <a href="/actions" class="button-link small" style="display:inline-block; font-size:0.8rem; padding:3px 8px; background:var(--accent); color:#fff; border-radius:4px; text-decoration:none;">View in Action Center</a>
                      </div>
                    </div>
                  ` : ''}
                </div>
              ` : ''}
            </div>
          `;

          // Bind turn actions
          turnDiv.querySelector(`[data-action="use-prior"]`).addEventListener('click', () => {
            const agentName = turn.route ? turn.route.selected_display_name : turn.agentId;
            setStagedPriorContext({
              agentId: turn.agentId,
              agentName: agentName,
              responseId: (resp.responseContext && resp.responseContext.responseId) || (resp.generation && resp.generation.responseId) || '',
              summary: primaryText,
            });
            byId('composer').scrollIntoView({ behavior: 'smooth' });
          });

          turnDiv.querySelector(`[data-action="add-board"]`).addEventListener('click', () => {
            addToResultBoard(turn);
          });

          turnDiv.querySelector(`[data-action="add-kit"]`).addEventListener('click', () => {
            const agentName = turn.route ? turn.route.selected_display_name : turn.agentId;
            addContextKitItem('prior_turn', `${agentName} (Turn #${index + 1})`, primaryText);
          });

          turnDiv.querySelector(`[data-action="toggle-json"]`).addEventListener('click', () => {
            const p = byId(`json-panel-${index}`);
            p.style.display = p.style.display === 'none' ? 'block' : 'none';
          });

          // Bind structured decision result actions
          const decUsePrior = turnDiv.querySelector(`[data-dec-action="use-prior"]`);
          if (decUsePrior) {
            decUsePrior.addEventListener('click', () => {
              const agentName = turn.route ? turn.route.selected_display_name : turn.agentId;
              setStagedPriorContext({
                agentId: turn.agentId,
                agentName: agentName,
                responseId: (resp.responseContext && resp.responseContext.responseId) || (resp.generation && resp.generation.responseId) || '',
                summary: `Decision: ${resp.decision || primaryText}. Suggested: ${resp.suggestedDirection ? resp.suggestedDirection.option : ''}`,
              });
              byId('composer').scrollIntoView({ behavior: 'smooth' });
            });
          }

          const decAddBoard = turnDiv.querySelector(`[data-dec-action="add-board"]`);
          if (decAddBoard) {
            decAddBoard.addEventListener('click', () => addToResultBoard(turn));
          }

          const decAddKit = turnDiv.querySelector(`[data-dec-action="add-kit"]`);
          if (decAddKit) {
            decAddKit.addEventListener('click', () => {
              addContextKitItem('decision', `Decision: ${resp.decision || 'Local Decision'}`, `Suggested: ${resp.suggestedDirection ? resp.suggestedDirection.option : ''}\nRationale: ${resp.suggestedDirection ? resp.suggestedDirection.rationale : ''}\nFocus: ${resp.decisionFocus || ''}`);
            });
          }

          const decPrepareReview = turnDiv.querySelector(`[data-dec-action="prepare-review"]`);
          if (decPrepareReview) {
            decPrepareReview.addEventListener('click', () => {
              selectAgentManually('local_review_agent');
              byId('prompt-input').value = `Review the following proposed decision and tradeoffs:\nDecision: ${resp.decision || 'Untitled'}\nSuggested Direction: ${resp.suggestedDirection ? resp.suggestedDirection.option : ''}\nTradeoffs: ${(resp.tradeoffs || []).join('; ')}`;
              byId('prompt-input').focus();
              triggerReadinessEvaluation();
              showToast('Prepared Review Agent with decision details.');
              byId('composer').scrollIntoView({ behavior: 'smooth' });
            });
          }

          // Follow-up chips
          turnDiv.querySelectorAll('.followup-chip').forEach(chip => {
            chip.addEventListener('click', () => {
              const text = chip.getAttribute('data-insert-prompt');
              const input = byId('prompt-input');
              input.value = (input.value.trim() ? `${input.value.trim()}\n\n${text}` : text).trim();
              input.focus();
              triggerReadinessEvaluation();
              showToast('Inserted follow-up query into prompt.');
              byId('composer').scrollIntoView({ behavior: 'smooth' });
            });
          });

          // Toggle Action Bridge
          const toggleBridgeBtn = turnDiv.querySelector(`[data-action="toggle-action-bridge"]`);
          if (toggleBridgeBtn) {
            toggleBridgeBtn.addEventListener('click', () => {
              turn.actionBridgeOpen = !turn.actionBridgeOpen;
              if (turn.actionBridgeOpen && !turn.selectedProject && sessionState.projects && sessionState.projects.length === 1) {
                turn.selectedProject = sessionState.projects[0].name;
              }
              if (turn.actionBridgeOpen) {
                updatePolicyPreview(index);
              }
              renderTranscript();
            });
          }

          // Form change events
          const typeSelect = turnDiv.querySelector(`#action-type-select-${index}`);
          if (typeSelect) {
            typeSelect.addEventListener('change', () => {
              turn.selectedActionType = typeSelect.value;
              if ((turn.selectedActionType === 'read_project_text_files' || turn.selectedActionType === 'modify_project_files_with_codex') && turn.selectedProject && !turn.availableProjectFiles) {
                loadProjectFiles(index, turn.selectedProject);
              }
              updatePolicyPreview(index);
              renderTranscript();
            });
          }
          const projSelect = turnDiv.querySelector(`#action-project-select-${index}`);
          if (projSelect) {
            projSelect.addEventListener('change', () => {
              turn.selectedProject = projSelect.value;
              turn.availableProjectFiles = null;
              turn.selectedRelativePaths = [];
              if ((turn.selectedActionType === 'read_project_text_files' || turn.selectedActionType === 'modify_project_files_with_codex') && turn.selectedProject) {
                loadProjectFiles(index, turn.selectedProject);
              }
              updatePolicyPreview(index);
            });
          }

          // Catalog filter & refresh
          const filterInput = turnDiv.querySelector(`#file-catalog-search-${index}`);
          if (filterInput) {
            filterInput.addEventListener('input', (e) => {
              turn.fileCatalogFilter = e.target.value;
              const listEl = byId(`file-catalog-list-${index}`);
              if (listEl) {
                listEl.innerHTML = renderFileCatalogItems(index, turn);
                bindCatalogCheckboxes(turnDiv, index, turn);
              }
            });
          }
          const refreshCatalogBtn = turnDiv.querySelector(`[data-action="refresh-file-catalog"]`);
          if (refreshCatalogBtn) {
            refreshCatalogBtn.addEventListener('click', () => {
              if (turn.selectedProject) {
                loadProjectFiles(index, turn.selectedProject);
              }
            });
          }

          bindCatalogCheckboxes(turnDiv, index, turn);

          const titleInput = turnDiv.querySelector(`#report-title-input-${index}`);
          if (titleInput) {
            titleInput.addEventListener('input', () => {
              turn.reportTitle = titleInput.value;
            });
          }
          const contentInput = turnDiv.querySelector(`#report-content-input-${index}`);
          if (contentInput) {
            contentInput.addEventListener('input', () => {
              turn.reportContent = contentInput.value;
            });
          }

          // Coding inputs
          const goalInput = turnDiv.querySelector(`#coding-goal-${index}`);
          if (goalInput) {
            goalInput.addEventListener('input', () => {
              turn.codingGoal = goalInput.value;
            });
          }
          const scopeInput = turnDiv.querySelector(`#coding-scope-${index}`);
          if (scopeInput) {
            scopeInput.addEventListener('input', () => {
              turn.codingScope = scopeInput.value;
            });
          }
          const nonGoalsInput = turnDiv.querySelector(`#coding-non-goals-${index}`);
          if (nonGoalsInput) {
            nonGoalsInput.addEventListener('input', () => {
              turn.codingNonGoals = nonGoalsInput.value;
            });
          }

          // Coding action buttons
          const prepPlanBtn = turnDiv.querySelector(`[data-action="prepare-coding-plan"]`);
          if (prepPlanBtn) {
            prepPlanBtn.addEventListener('click', () => prepareCodingPlan(index));
          }
          const appPlanBtn = turnDiv.querySelector(`[data-action="approve-coding-plan"]`);
          if (appPlanBtn) {
            appPlanBtn.addEventListener('click', () => approveCodingPlan(index));
          }
          const rejPlanBtn = turnDiv.querySelector(`[data-action="reject-coding-plan"]`);
          if (rejPlanBtn) {
            rejPlanBtn.addEventListener('click', () => rejectCodingPlan(index));
          }
          const execPlanBtn = turnDiv.querySelector(`[data-action="execute-coding-plan"]`);
          if (execPlanBtn) {
            execPlanBtn.addEventListener('click', () => executeCodingPlan(index));
          }
          const cancelExecBtn = turnDiv.querySelector(`[data-action="cancel-coding-execution"]`);
          if (cancelExecBtn) {
            cancelExecBtn.addEventListener('click', () => cancelCodingExecution(index));
          }
          const reviewChangedBtn = turnDiv.querySelector(`[data-action="review-changed-files"]`);
          if (reviewChangedBtn) {
            reviewChangedBtn.addEventListener('click', () => {
              const res = turn.codingExecutionResult;
              if (res && res.changedFiles) {
                turn.selectedActionType = 'read_project_text_files';
                turn.selectedRelativePaths = res.changedFiles.slice(0, 5);
                turn.readExecutionResult = null;
                turn.dryRunResult = null;
                loadProjectFiles(index, turn.selectedProject);
                updatePolicyPreview(index);
                renderTranscript();
                showToast('Staged changed files into Project Source Reader for review.');
              }
            });
          }

          // Submit dry run
          const submitDryRunBtn = turnDiv.querySelector(`[data-action="submit-dry-run"]`);
          if (submitDryRunBtn) {
            submitDryRunBtn.addEventListener('click', () => submitDryRun(index));
          }

          // Execute read-only inspection
          const execReadOnlyBtn = turnDiv.querySelector(`[data-action="execute-read-only"]`);
          if (execReadOnlyBtn) {
            execReadOnlyBtn.addEventListener('click', () => submitExecuteReadOnly(index));
          }

          // Execute project text read
          const execProjectTextReadBtn = turnDiv.querySelector(`[data-action="execute-project-text-read"]`);
          if (execProjectTextReadBtn) {
            execProjectTextReadBtn.addEventListener('click', () => submitExecuteProjectTextRead(index));
          }

          // Execute write report
          const execReportBtn = turnDiv.querySelector(`[data-action="execute-report"]`);
          if (execReportBtn) {
            execReportBtn.addEventListener('click', () => submitExecuteReport(index));
          }

          // Use inspection result as prior context
          const useInspPriorBtn = turnDiv.querySelector(`[data-action="use-inspection-prior"]`);
          if (useInspPriorBtn) {
            useInspPriorBtn.addEventListener('click', () => {
              const res = turn.realExecutionResult;
              const insp = res.inspectionResult || {};
              const docList = (insp.docsDetected || []).map(d => d.relativePath || d.filename).join(', ') || 'none';
              const summaryText = `Inspected project ${res.projectName}: Scanned ${insp.scannedFiles} files, ${insp.protectedSkippedFiles} protected files skipped. Documentation: ${docList}. File types: ${JSON.stringify(insp.fileTypeCounts || {})}.`;
              setStagedPriorContext({
                agentId: 'filesystem_tool',
                agentName: 'Filesystem Tool (Inspection)',
                responseId: res.receiptId || res.taskId,
                summary: summaryText,
              });
              byId('composer').scrollIntoView({ behavior: 'smooth' });
              showToast('Staged read-only inspection result as prior context.');
            });
          }

          // Add inspection result to board
          const addInspectBoardBtn = turnDiv.querySelector(`[data-action="add-inspect-board"]`);
          if (addInspectBoardBtn && turn.realExecutionResult) {
            addInspectBoardBtn.addEventListener('click', () => {
              const res = turn.realExecutionResult;
              const ins = res.inspectionResult || {};
              addToResultBoard({
                sourceType: 'inspection_result',
                agentId: 'inspect_project',
                route: { selected_display_name: 'Project Inspector', category: 'Coding/Core', confidence_tier: 'high' },
                timestamp: turn.timestamp,
                response: {
                  summary: `Inspected project ${res.projectName}: scanned ${ins.scannedFiles || 0} files, ${ins.protectedSkippedFiles || 0} protected skipped.`,
                  keyPoints: [`Scanned Files: ${ins.scannedFiles || 0}`, `Skipped Dirs: ${ins.skippedDirs || 0}`],
                  safetyNotes: ['Read-only inspection. No files modified.'],
                },
                actionResult: res,
              });
            });
          }

          // Use source content as prior context
          const useSourcePriorBtn = turnDiv.querySelector(`[data-action="use-source-prior"]`);
          if (useSourcePriorBtn) {
            useSourcePriorBtn.addEventListener('click', () => {
              const res = turn.readExecutionResult;
              const rRes = res.readResult || {};
              const files = rRes.files || [];
              let summaryText = `Read source files from project ${res.projectName} (${files.length} files, ${rRes.totalBytes || 0} bytes):\n`;
              files.forEach(f => {
                summaryText += `\n--- ${f.relativePath} (${f.lineCount} lines) ---\n${f.content.slice(0, 4000)}\n`;
              });
              setStagedPriorContext({
                agentId: 'filesystem_tool',
                agentName: 'Filesystem Tool (Source Reader)',
                responseId: res.receiptId || res.taskId,
                summary: summaryText.slice(0, 16000),
              });
              byId('composer').scrollIntoView({ behavior: 'smooth' });
              showToast('Staged selected source content as prior context.');
            });
          }

          // Add source read result to board
          const addReadBoardBtn = turnDiv.querySelector(`[data-action="add-read-board"]`);
          if (addReadBoardBtn && turn.readExecutionResult) {
            addReadBoardBtn.addEventListener('click', () => {
              const res = turn.readExecutionResult;
              const rRes = res.readResult || {};
              const fileCount = rRes.totalFiles || (rRes.files ? rRes.files.length : 0);
              addToResultBoard({
                sourceType: 'source_read_result',
                agentId: 'read_project_text_files',
                route: { selected_display_name: 'Project Source Reader', category: 'Coding/Core', confidence_tier: 'high' },
                timestamp: turn.timestamp,
                response: {
                  summary: `Read ${fileCount} source files from ${res.projectName} (${rRes.totalBytes || 0} bytes).`,
                  keyPoints: (rRes.files ? rRes.files.map(f => `${f.relativePath} (${f.lineCount} lines)`) : []),
                  safetyNotes: ['Read-only source access. No protected files or secrets read.'],
                },
                actionResult: res,
              });
            });
          }

          // Use report summary as prior context
          const useReportPriorBtn = turnDiv.querySelector(`[data-action="use-report-prior"]`);
          if (useReportPriorBtn) {
            useReportPriorBtn.addEventListener('click', () => {
              const res = turn.reportExecutionResult;
              const rep = res.reportResult || {};
              const summaryText = `Created local Markdown report '${rep.filename}' (${rep.title}) for project ${res.projectName}. File size: ${rep.charCount} characters. Saved to Jarvis reports directory (${rep.relativeReportPath}).`;
              setStagedPriorContext({
                agentId: 'report_tool',
                agentName: 'Report Tool',
                responseId: res.receiptId || res.taskId,
                summary: summaryText,
              });
              byId('composer').scrollIntoView({ behavior: 'smooth' });
              showToast('Staged report summary as prior context.');
            });
          }

          // Add report result to board
          const addReportBoardBtn = turnDiv.querySelector(`[data-action="add-report-board"]`);
          if (addReportBoardBtn && turn.reportExecutionResult) {
            addReportBoardBtn.addEventListener('click', () => {
              const res = turn.reportExecutionResult;
              const rep = res.reportResult || {};
              addToResultBoard({
                sourceType: 'report_result',
                agentId: 'write_report',
                route: { selected_display_name: 'Report Tool', category: 'Coding/Core', confidence_tier: 'high' },
                timestamp: turn.timestamp,
                response: {
                  summary: `Created report '${rep.filename || 'report.md'}' for project ${res.projectName}.`,
                  keyPoints: [`Path: ${rep.relativeReportPath || ''}`, `Size: ${rep.charCount || 0} chars`],
                  safetyNotes: ['Non-destructive Markdown creation in reports directory.'],
                },
                actionResult: res,
              });
            });
          }

          // Add Codex execution result to board
          const addCodexBoardBtn = turnDiv.querySelector(`[data-action="add-codex-board"]`);
          if (addCodexBoardBtn && turn.codingExecutionResult) {
            addCodexBoardBtn.addEventListener('click', () => {
              const res = turn.codingExecutionResult;
              addToResultBoard({
                sourceType: 'codex_result',
                agentId: 'modify_project_files_with_codex',
                route: { selected_display_name: 'Controlled Codex Coding', category: 'Coding/Core', confidence_tier: 'high' },
                timestamp: turn.timestamp,
                response: {
                  summary: `Controlled Codex execution: ${res.status || 'completed'} on project ${turn.selectedProject}. Changed files: ${res.changedFileCount || 0}.`,
                  keyPoints: [
                    `Changed: ${res.changedFileCount || 0} files (+${res.addedLines || 0}/-${res.deletedLines || 0})`,
                    `Execution ID: ${res.executionId || ''}`,
                  ],
                  safetyNotes: ['Supervised conservative single-run Codex execution. No automatic commits.'],
                },
                actionResult: res,
              });
            });
          }
        }
      }

      container.append(turnDiv);
    });

    // Auto scroll to bottom
    container.lastElementChild?.scrollIntoView({ behavior: 'smooth' });
  }

  function bindCatalogCheckboxes(turnDiv, turnIdx, turn) {
    const checkboxes = turnDiv.querySelectorAll(`input[data-file-rel]`);
    const maxAllowed = turn.selectedActionType === 'modify_project_files_with_codex' ? 10 : 5;
    checkboxes.forEach(cb => {
      cb.addEventListener('change', () => {
        const rel = cb.getAttribute('data-file-rel');
        if (!turn.selectedRelativePaths) turn.selectedRelativePaths = [];
        if (cb.checked) {
          if (turn.selectedRelativePaths.length >= maxAllowed) {
            cb.checked = false;
            alert(`You can select a maximum of ${maxAllowed} files for this action.`);
            return;
          }
          if (!turn.selectedRelativePaths.includes(rel)) {
            turn.selectedRelativePaths.push(rel);
          }
        } else {
          turn.selectedRelativePaths = turn.selectedRelativePaths.filter(p => p !== rel);
        }
        renderTranscript();
      });
    });
  }

  function renderFileCatalogItems(turnIdx, turn) {
    if (turn.loadingProjectFiles) {
      return '<div class="muted" style="padding:10px; text-align:center; font-size:0.82rem;">Scanning project for safe text files...</div>';
    }
    const files = turn.availableProjectFiles || [];
    if (!files.length) {
      return '<div class="muted" style="padding:10px; text-align:center; font-size:0.82rem;">No eligible text files loaded. Click Refresh or select a project.</div>';
    }
    const filter = (turn.fileCatalogFilter || '').toLowerCase();
    const filtered = filter ? files.filter(f => f.relativePath.toLowerCase().includes(filter)) : files;
    if (!filtered.length) {
      return `<div class="muted" style="padding:10px; text-align:center; font-size:0.82rem;">No files matching "${escapeHtml(filter)}".</div>`;
    }
    const selected = new Set(turn.selectedRelativePaths || []);
    return filtered.slice(0, 150).map(f => {
      const isChecked = selected.has(f.relativePath);
      const sizeKb = (f.sizeBytes / 1024).toFixed(1);
      return `
        <label style="display:flex; align-items:center; gap:8px; padding:4px 6px; border-bottom:1px solid #f1f5f9; cursor:pointer; font-size:0.82rem;">
          <input type="checkbox" data-turn-idx="${turnIdx}" data-file-rel="${escapeHtml(f.relativePath)}" ${isChecked ? 'checked' : ''} />
          <span style="font-family:Consolas, Monaco, 'Courier New', monospace; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escapeHtml(f.relativePath)}</span>
          <span class="muted" style="font-size:0.75rem;">${escapeHtml(sizeKb)} KB</span>
          <span class="pill inactive" style="font-size:0.7rem; padding:1px 5px;">${escapeHtml(f.category || f.extension)}</span>
        </label>
      `;
    }).join('');
  }

  async function loadProjectFiles(turnIdx, projectName) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn || !projectName) return;
    turn.loadingProjectFiles = true;
    try {
      const files = await apiFetch(`/api/assistant/actions/project-files?projectName=${encodeURIComponent(projectName)}`);
      turn.availableProjectFiles = files;
      turn.loadingProjectFiles = false;
      renderTranscript();
    } catch (err) {
      turn.loadingProjectFiles = false;
      turn.availableProjectFiles = [];
      showToast(`Error loading project files: ${err.message}`);
      renderTranscript();
    }
  }

  // Update policy preview for a specific turn
  async function updatePolicyPreview(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn) return;
    const typeSelect = byId(`action-type-select-${turnIdx}`);
    const projSelect = byId(`action-project-select-${turnIdx}`);
    if (typeSelect) turn.selectedActionType = typeSelect.value;
    if (projSelect) turn.selectedProject = projSelect.value;

    const actionType = turn.selectedActionType || 'inspect_project';
    const projectName = turn.selectedProject || '';

    if (!projectName) {
      turn.policyStatus = 'needs_project';
      turn.policyReason = 'Select a registered project target to preview policy status.';
      const pill = byId(`policy-status-pill-${turnIdx}`);
      const reason = byId(`policy-reason-${turnIdx}`);
      if (pill) { pill.className = 'pill inactive'; pill.textContent = 'NEEDS PROJECT'; }
      if (reason) reason.textContent = turn.policyReason;
      return;
    }

    if ((actionType === 'read_project_text_files' || actionType === 'modify_project_files_with_codex') && !turn.availableProjectFiles && !turn.loadingProjectFiles) {
      loadProjectFiles(turnIdx, projectName);
    }

    try {
      const preview = await apiFetch('/api/assistant/actions/policy-preview', {
        method: 'POST',
        body: JSON.stringify({ actionType: actionType, projectName: projectName })
      });
      turn.policyStatus = preview.status;
      turn.policyReason = preview.reason;
      const pill = byId(`policy-status-pill-${turnIdx}`);
      const reason = byId(`policy-reason-${turnIdx}`);
      if (pill) {
        const cls = preview.status === 'allowed' ? 'succeeded' : (preview.status === 'blocked' ? 'blocked' : 'waiting_for_approval');
        pill.className = `pill ${cls}`;
        pill.textContent = preview.status.toUpperCase();
      }
      if (reason) reason.textContent = preview.reason;
    } catch (err) {
      turn.policyStatus = 'error';
      turn.policyReason = err.message;
    }
  }

  // Submit dry run for a specific turn
  async function submitDryRun(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn) return;
    const actionType = turn.selectedActionType || 'inspect_project';
    const projectName = turn.selectedProject;

    if (!projectName) {
      alert('Please select a registered project target before validating.');
      return;
    }

    if (actionType === 'read_project_text_files' && (!turn.selectedRelativePaths || turn.selectedRelativePaths.length === 0)) {
      alert('Please select 1 to 5 safe project files to read before validating dry run.');
      return;
    }

    const resp = turn.response || {};
    const responseId = (resp.responseContext && resp.responseContext.responseId) || (resp.generation && resp.generation.responseId) || null;

    try {
      const result = await apiFetch('/api/assistant/actions/validate-dry-run', {
        method: 'POST',
        body: JSON.stringify({
          actionType: actionType,
          projectName: projectName,
          selectedRelativePaths: turn.selectedRelativePaths || [],
          sourceAgentId: turn.agentId || 'unified_assistant',
          sourceResponseId: responseId,
          actor: 'local_user'
        })
      });
      turn.dryRunResult = result;
      showToast(result.summary || 'Dry run validated. No local action was executed.');
      renderTranscript();
    } catch (err) {
      alert(`Dry run validation failed: ${err.message}`);
    }
  }

  // Execute real read-only inspection
  async function submitExecuteReadOnly(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn || !turn.dryRunResult) return;
    const dryRunTask = turn.dryRunResult.task;
    const projectName = turn.selectedProject || dryRunTask.project_name;
    const expectedReceiptId = (turn.dryRunResult.receipts && turn.dryRunResult.receipts.length)
      ? turn.dryRunResult.receipts[0].receipt_id
      : null;

    const resp = turn.response || {};
    const responseId = (resp.responseContext && resp.responseContext.responseId) || (resp.generation && resp.generation.responseId) || null;

    try {
      const result = await apiFetch('/api/assistant/actions/execute-read-only', {
        method: 'POST',
        body: JSON.stringify({
          dryRunTaskId: dryRunTask.task_id,
          projectName: projectName,
          expectedReceiptId: expectedReceiptId,
          confirmation: 'EXECUTE READ-ONLY INSPECTION',
          sourceAgentId: turn.agentId || 'unified_assistant',
          sourceResponseId: responseId,
          sourceTurnIndex: turnIdx,
          actor: 'local_user'
        })
      });
      turn.realExecutionResult = result;
      showToast('Read-only project inspection executed successfully.');
      renderTranscript();
    } catch (err) {
      alert(`Read-only inspection failed: ${err.message}`);
    }
  }

  // Execute real project text read
  async function submitExecuteProjectTextRead(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn || !turn.dryRunResult) return;
    const dryRunTask = turn.dryRunResult.task;
    const projectName = turn.selectedProject || dryRunTask.project_name;
    const relativePaths = turn.selectedRelativePaths || [];

    if (!relativePaths.length) {
      alert('Please select at least 1 file to read.');
      return;
    }

    const expectedReceiptId = (turn.dryRunResult.receipts && turn.dryRunResult.receipts.length)
      ? turn.dryRunResult.receipts[0].receipt_id
      : null;

    const resp = turn.response || {};
    const responseId = (resp.responseContext && resp.responseContext.responseId) || (resp.generation && resp.generation.responseId) || null;

    try {
      const result = await apiFetch('/api/assistant/actions/execute-project-text-read', {
        method: 'POST',
        body: JSON.stringify({
          dryRunTaskId: dryRunTask.task_id,
          projectName: projectName,
          relativePaths: relativePaths,
          expectedReceiptId: expectedReceiptId,
          confirmation: 'READ LOCAL PROJECT FILES',
          sourceAgentId: turn.agentId || 'unified_assistant',
          sourceResponseId: responseId,
          sourceTurnIndex: turnIdx,
          actor: 'local_user'
        })
      });
      turn.readExecutionResult = result;
      showToast('Project source files read successfully.');
      renderTranscript();
    } catch (err) {
      alert(`Project source read failed: ${err.message}`);
    }
  }

  // Execute real report creation
  async function submitExecuteReport(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn || !turn.dryRunResult) return;
    const dryRunTask = turn.dryRunResult.task;
    const projectName = turn.selectedProject || dryRunTask.project_name;
    const expectedReceiptId = (turn.dryRunResult.receipts && turn.dryRunResult.receipts.length)
      ? turn.dryRunResult.receipts[0].receipt_id
      : null;

    const resp = turn.response || {};
    const primaryText = resp.generatedResponse ? resp.generatedResponse.response : (resp.summary || resp.brief || resp.plan || resp.draft || resp.response || '');

    const titleInput = byId(`report-title-input-${turnIdx}`);
    const contentInput = byId(`report-content-input-${turnIdx}`);
    const title = (titleInput ? titleInput.value : (turn.reportTitle || `${projectName} Summary Report`)).trim();
    const content = (contentInput ? contentInput.value : (turn.reportContent !== undefined ? turn.reportContent : primaryText)).trim();

    if (!title) {
      alert('Please provide a report title.');
      return;
    }
    if (!content) {
      alert('Please provide report content before creating.');
      return;
    }

    const responseId = (resp.responseContext && resp.responseContext.responseId) || (resp.generation && resp.generation.responseId) || null;

    try {
      const result = await apiFetch('/api/assistant/actions/execute-report', {
        method: 'POST',
        body: JSON.stringify({
          dryRunTaskId: dryRunTask.task_id,
          projectName: projectName,
          title: title,
          content: content,
          expectedReceiptId: expectedReceiptId,
          confirmation: 'WRITE NEW LOCAL REPORT',
          sourceAgentId: turn.agentId || 'unified_assistant',
          sourceResponseId: responseId,
          sourceTurnIndex: turnIdx,
          actor: 'local_user'
        })
      });
      turn.reportExecutionResult = result;
      showToast('Local Markdown report created successfully.');
      renderTranscript();
    } catch (err) {
      alert(`Report creation failed: ${err.message}`);
    }
  }

  // Prepare conservative coding plan
  async function prepareCodingPlan(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn) return;
    if (!turn.selectedProject) {
      alert('Please select a registered target project.');
      return;
    }
    if (!turn.selectedRelativePaths || turn.selectedRelativePaths.length === 0) {
      alert('Please select 1 to 10 existing files for this conservative plan.');
      return;
    }
    const goalInput = byId(`coding-goal-${turnIdx}`);
    const scopeInput = byId(`coding-scope-${turnIdx}`);
    const nonGoalsInput = byId(`coding-non-goals-${turnIdx}`);
    const goal = (goalInput ? goalInput.value : turn.codingGoal) || turn.prompt || 'Code modification';
    const scope = (scopeInput ? scopeInput.value : turn.codingScope) || 'Modify specified files as requested';
    const nonGoals = (nonGoalsInput ? nonGoalsInput.value : turn.codingNonGoals) || 'Do not touch unapproved files or dependencies.';

    const resp = turn.response || {};
    const responseId = (resp.responseContext && resp.responseContext.responseId) || (resp.generation && resp.generation.responseId) || null;

    try {
      showToast('Preparing conservative Codex plan with scope manifest...');
      const planSummary = await apiFetch('/api/assistant/coding/prepare', {
        method: 'POST',
        body: JSON.stringify({
          projectName: turn.selectedProject,
          allowedFiles: turn.selectedRelativePaths,
          taskGoal: goal,
          exactScope: scope,
          nonGoals: nonGoals,
          sourceResponseId: responseId,
          sourceTurnIndex: turnIdx,
          actor: 'local_user'
        })
      });
      turn.codingPlan = planSummary;
      turn.codingExecutionResult = null;
      showToast('Conservative plan prepared. Scope manifest locked.');
      renderTranscript();
    } catch (err) {
      alert(`Plan preparation failed: ${err.message}`);
    }
  }

  // Approve conservative coding plan
  async function approveCodingPlan(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn || !turn.codingPlan) return;
    const confirmText = prompt('Type "APPROVE CONSERVATIVE CODEX PLAN" to approve this plan for future execution:');
    if (confirmText !== 'APPROVE CONSERVATIVE CODEX PLAN') {
      if (confirmText !== null) alert('Approval cancelled: confirmation string did not match exactly.');
      return;
    }
    try {
      const updated = await apiFetch('/api/assistant/coding/approve', {
        method: 'POST',
        body: JSON.stringify({
          planId: turn.codingPlan.planId,
          confirmation: confirmText,
          actor: 'local_user'
        })
      });
      turn.codingPlan = updated;
      showToast('Plan approved for future execution.');
      renderTranscript();
    } catch (err) {
      alert(`Approval failed: ${err.message}`);
    }
  }

  // Reject conservative coding plan
  async function rejectCodingPlan(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn || !turn.codingPlan) return;
    if (!confirm('Reject this Codex plan?')) return;
    try {
      const updated = await apiFetch('/api/assistant/coding/reject', {
        method: 'POST',
        body: JSON.stringify({
          planId: turn.codingPlan.planId,
          actor: 'local_user'
        })
      });
      turn.codingPlan = updated;
      showToast('Plan rejected.');
      renderTranscript();
    } catch (err) {
      alert(`Rejection failed: ${err.message}`);
    }
  }

  // Execute approved conservative coding plan
  async function executeCodingPlan(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn || !turn.codingPlan) return;
    const confirmText = prompt('Type "EXECUTE APPROVED CODEX CHANGE" to execute this approved single-run change:');
    if (confirmText !== 'EXECUTE APPROVED CODEX CHANGE') {
      if (confirmText !== null) alert('Execution cancelled: confirmation string did not match exactly.');
      return;
    }
    turn.codingActive = true;
    renderTranscript();
    try {
      showToast('Starting supervised Codex execution (single run mode)...');
      const result = await apiFetch('/api/assistant/coding/execute', {
        method: 'POST',
        body: JSON.stringify({
          planId: turn.codingPlan.planId,
          projectName: turn.selectedProject,
          confirmation: confirmText,
          actor: 'local_user'
        })
      });
      turn.codingActive = false;
      turn.codingExecutionResult = result;
      if (turn.codingPlan) turn.codingPlan.status = 'execution_consumed';
      showToast(result.message || 'Execution finished.');
      renderTranscript();
    } catch (err) {
      turn.codingActive = false;
      alert(`Execution failed: ${err.message}`);
      renderTranscript();
    }
  }

  // Cancel active coding execution
  async function cancelCodingExecution(turnIdx) {
    const turn = sessionState.transcript[turnIdx];
    if (!turn) return;
    const confirmText = prompt('Type "STOP CODEX EXECUTION" to stop the active child process:');
    if (confirmText !== 'STOP CODEX EXECUTION') {
      if (confirmText !== null) alert('Cancellation aborted: confirmation string did not match exactly.');
      return;
    }
    try {
      const res = await apiFetch('/api/codex/execution/cancel', {
        method: 'POST',
        body: JSON.stringify({
          confirmation: confirmText,
          actor: 'local_user'
        })
      });
      showToast(res.message || 'Cancellation requested.');
    } catch (err) {
      alert(`Stop failed: ${err.message}`);
    }
  }

  // ==========================================
  // Structured Decision Result Card Renderer
  // ==========================================

  function renderDecisionResultHtml(turn, resp, index) {
    if (!resp || (!resp.comparisonMatrix && !resp.suggestedDirection && !resp.decision && !resp.decisionFocus)) return '';

    const decisionTitle = resp.decision || 'Local Decision Analysis';
    const decisionStyle = resp.decisionStyle || 'balanced';
    const focusText = resp.decisionFocus || '';
    const suggested = resp.suggestedDirection || { option: 'Undetermined', rationale: '', certainty: 'low' };
    const matrix = Array.isArray(resp.comparisonMatrix) ? resp.comparisonMatrix : [];
    const tradeoffs = Array.isArray(resp.tradeoffs) ? resp.tradeoffs : [];
    const assumptions = Array.isArray(resp.assumptions) ? resp.assumptions : [];
    const risks = Array.isArray(resp.risks) ? resp.risks : [];
    const missingInfo = Array.isArray(resp.missingInformation) ? resp.missingInformation : [];
    const reviewQuestions = Array.isArray(resp.reviewQuestions) ? resp.reviewQuestions : [];
    const isHs = !!(resp.safety && resp.safety.high_stakes) || !!(turn.route && turn.route.is_high_stakes);

    let matrixRowsHtml = '';
    matrix.forEach(row => {
      const fitClass = row.fit || 'not_comparable';
      const criteriaStr = (row.criteriaNotes || []).join('; ');
      const constraintStr = (row.constraintNotes || []).join('; ');
      const priorityStr = (row.priorityNotes || []).join('; ');
      matrixRowsHtml += `
        <tr>
          <td><strong>${escapeHtml(row.option || '')}</strong></td>
          <td><span class="fit-pill ${fitClass}">${escapeHtml(row.fit || 'provisional')}</span></td>
          <td>${escapeHtml(criteriaStr || '—')}</td>
          <td>${escapeHtml(constraintStr || '—')}</td>
          <td>${escapeHtml(priorityStr || '—')}</td>
          <td>${escapeHtml(row.styleNote || '—')}</td>
        </tr>
      `;
    });

    let missingChipsHtml = '';
    missingInfo.forEach(info => {
      missingChipsHtml += `<button type="button" class="followup-chip" data-insert-prompt="${escapeHtml(info)}">+ ${escapeHtml(info)}</button>`;
    });

    let questionChipsHtml = '';
    reviewQuestions.forEach(q => {
      questionChipsHtml += `<button type="button" class="followup-chip" data-insert-prompt="${escapeHtml(q)}">❓ ${escapeHtml(q)}</button>`;
    });

    return `
      <div class="decision-result-card">
        <div class="decision-header-row">
          <div>
            <span class="pill override" style="font-size:0.75rem; margin-bottom:4px;">🎯 Structured Decision Analysis</span>
            <h4 style="margin:2px 0 0; color:#0f766e; font-size:1.05rem;">${escapeHtml(decisionTitle)}</h4>
          </div>
          <div style="display:flex; align-items:center; gap:6px;">
            <span class="pill" style="background:#e0f2fe; color:#0369a1; font-weight:600;">Style: ${escapeHtml(decisionStyle)}</span>
            <span class="pill active" style="font-size:0.78rem;">Confidence: ${escapeHtml(resp.confidence || 'standard')}</span>
          </div>
        </div>

        ${focusText ? `<div class="decision-focus-banner"><strong>Decision Focus:</strong> ${escapeHtml(focusText)}</div>` : ''}

        <div class="suggested-direction-box">
          <div class="direction-title">
            <span>💡 Agent's suggested direction:</span>
            <span style="color:#115e59; font-weight:700; text-decoration:underline;">${escapeHtml(suggested.option || 'Undetermined')}</span>
            <span class="pill" style="font-size:0.72rem; padding:1px 6px;">Certainty: ${escapeHtml(suggested.certainty || 'low')}</span>
          </div>
          <div style="font-size:0.88rem; color:#334155; line-height:1.4;">${escapeHtml(suggested.rationale || '')}</div>
          ${isHs ? `<div class="muted" style="font-size:0.8rem; color:#c2410c; margin-top:4px;">⚠️ <strong>High-Stakes Decision:</strong> Review important facts and sources before acting. Local informational guidance only.</div>` : ''}
        </div>

        ${matrix.length ? `
          <div>
            <h5 style="margin:0 0 4px; font-size:0.88rem; color:#0f766e;">Option Comparison Matrix:</h5>
            <div style="overflow-x:auto; border:1px solid #e2e8f0; border-radius:6px;">
              <table class="decision-matrix-table">
                <thead>
                  <tr>
                    <th>Option</th>
                    <th>Fit</th>
                    <th>Criteria Notes</th>
                    <th>Constraints</th>
                    <th>Priorities</th>
                    <th>Style Note</th>
                  </tr>
                </thead>
                <tbody>${matrixRowsHtml}</tbody>
              </table>
            </div>
          </div>
        ` : ''}

        ${tradeoffs.length ? `
          <div>
            <h5 style="margin:0 0 4px; font-size:0.88rem; color:#0f766e;">Tradeoffs Considered:</h5>
            <ul style="margin:0; padding-left:18px; font-size:0.85rem; line-height:1.4;">
              ${tradeoffs.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          ${assumptions.length ? `
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:8px;">
              <strong style="font-size:0.82rem; color:#475569;">Key Assumptions:</strong>
              <ul style="margin:4px 0 0; padding-left:16px; font-size:0.8rem; line-height:1.3;">
                ${assumptions.map(a => `<li>${escapeHtml(a)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${risks.length ? `
            <div style="background:#fff7ed; border:1px solid #fed7aa; border-radius:6px; padding:8px;">
              <strong style="font-size:0.82rem; color:#9a3412;">Key Risks:</strong>
              <ul style="margin:4px 0 0; padding-left:16px; font-size:0.8rem; line-height:1.3; color:#9a3412;">
                ${risks.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>

        ${(missingChipsHtml || questionChipsHtml) ? `
          <div style="background:#f0fdfa; border:1px solid #ccfbf1; border-radius:6px; padding:8px 10px;">
            <strong style="font-size:0.82rem; color:#0f766e;">Suggested Follow-Up Inquiries (Click to insert into composer):</strong>
            <div class="followup-chips">
              ${missingChipsHtml}
              ${questionChipsHtml}
            </div>
          </div>
        ` : ''}

        <div style="display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding-top:6px; border-top:1px solid #ccfbf1;">
          <button class="secondary small" type="button" data-dec-action="use-prior" data-turn-idx="${index}">Use Decision as Prior Context</button>
          <button class="secondary small" type="button" data-dec-action="add-board" data-turn-idx="${index}">Add Decision to Result Board</button>
          <button class="secondary small" type="button" data-dec-action="add-kit" data-turn-idx="${index}">Add Decision to Context Kit</button>
          <button class="secondary small" type="button" data-dec-action="prepare-review" data-turn-idx="${index}">Prepare Review of Decision</button>
        </div>
      </div>
    `;
  }

  // ==========================================
  // Enhanced Result Board (v0.1E Pass 10)
  // ==========================================

  const MAX_RESULT_BOARD_SIZE = 20;
  sessionState.resultBoard = [];
  sessionState.rbViewMode = 'expanded'; // 'compact' | 'expanded'
  sessionState.activeDetailItem = null;
  sessionState.decisionComposerOptions = [];

  function addToResultBoard(source) {
    if (sessionState.resultBoard.length >= MAX_RESULT_BOARD_SIZE) {
      alert(`Result Board is full (maximum ${MAX_RESULT_BOARD_SIZE} entries). Please remove unneeded items before adding more.`);
      return;
    }

    const resp = source.response || (source.fullResponse ? source.fullResponse : {});
    const primaryText = resp.generatedResponse ? resp.generatedResponse.response : (resp.summary || resp.brief || resp.plan || resp.draft || resp.response || resp.decision || source.text || '');
    const keyPoints = resp.keyPoints || (resp.generatedResponse && resp.generatedResponse.keyPoints) || resp.tradeoffs || [];
    const citations = resp.citations || resp.sources || (resp.generatedResponse && resp.generatedResponse.citations) || [];
    const limitations = resp.limitations || (resp.generatedResponse && resp.generatedResponse.limitations) || [];
    const safetyNotes = resp.safetyNotes || (resp.safety && resp.safety.notes) || [];
    const isHighStakes = !!(source.route && source.route.is_high_stakes) || !!(resp.safety && resp.safety.high_stakes) || !!source.isHighStakes;
    const routeConfidence = (source.route && source.route.confidence_tier) || source.confidenceTier || 'standard';
    const genMode = (resp.generation && resp.generation.mode) || source.generationMode || source.turnType || 'deterministic';

    const entry = {
      id: 'rb_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
      sourceTurnIndex: source.index !== undefined ? source.index : -1,
      sourceType: source.sourceType || 'assistant_turn',
      agentId: source.agentId || 'unknown_agent',
      agentDisplayName: source.route ? source.route.selected_display_name : (source.agentName || source.agentDisplayName || source.agentId || 'Agent'),
      category: source.route ? source.route.category : (source.category || 'General'),
      confidenceTier: routeConfidence,
      timestamp: source.timestamp || new Date().toLocaleTimeString(),
      primaryText: primaryText,
      keyPoints: Array.isArray(keyPoints) ? keyPoints : [],
      citations: Array.isArray(citations) ? citations : [],
      limitations: Array.isArray(limitations) ? limitations : [],
      safetyNotes: Array.isArray(safetyNotes) ? safetyNotes : [],
      isHighStakes: isHighStakes,
      actionMetadata: source.actionResult || null,
      generationMode: genMode,
      cancellationStatus: resp.cancelled ? 'cancelled' : 'completed',
      fullResponse: resp,
      selected: false,
      disagreementFlag: false,
    };

    sessionState.resultBoard.push(entry);
    updateResultBoardCounters();
    showToast(`Added "${entry.agentDisplayName}" result to session Result Board.`);
    renderResultBoard();
    populateResultBoardFilters();
  }

  function updateResultBoardCounters() {
    const count = sessionState.resultBoard.length;
    const countSpan = byId('result-board-count');
    const totalSpan = byId('rb-total-count');
    const tabSpan = byId('rb-tab-count');
    if (countSpan) countSpan.textContent = count;
    if (totalSpan) totalSpan.textContent = count;
    if (tabSpan) tabSpan.textContent = count;
  }

  function populateResultBoardFilters() {
    const agentSelect = byId('rb-agent-filter');
    const catSelect = byId('rb-category-filter');
    if (!agentSelect || !catSelect) return;

    const currentAgent = agentSelect.value;
    const currentCat = catSelect.value;

    const distinctAgents = new Set();
    const distinctCats = new Set();
    sessionState.resultBoard.forEach(item => {
      if (item.agentDisplayName) distinctAgents.add(item.agentDisplayName);
      if (item.category) distinctCats.add(item.category);
    });

    agentSelect.innerHTML = '<option value="">All Agents</option>';
    distinctAgents.forEach(a => {
      const opt = document.createElement('option');
      opt.value = a;
      opt.textContent = a;
      if (a === currentAgent) opt.selected = true;
      agentSelect.append(opt);
    });

    catSelect.innerHTML = '<option value="">All Categories</option>';
    distinctCats.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      if (c === currentCat) opt.selected = true;
      catSelect.append(opt);
    });
  }

  function renderResultBoard() {
    const container = byId('rb-cards-container');
    const legacyContainer = byId('result-board-items');
    if (!container) return;

    const query = (byId('rb-search-input')?.value || '').toLowerCase().trim();
    const agentFilter = byId('rb-agent-filter')?.value || '';
    const catFilter = byId('rb-category-filter')?.value || '';
    const hsOnly = byId('rb-high-stakes-filter')?.checked || false;
    const evidenceOnly = byId('rb-evidence-filter')?.checked || false;

    const filtered = sessionState.resultBoard.filter(item => {
      if (agentFilter && item.agentDisplayName !== agentFilter) return false;
      if (catFilter && item.category !== catFilter) return false;
      if (hsOnly && !item.isHighStakes) return false;
      if (evidenceOnly && !item.citations.length) return false;
      if (query) {
        const hay = `${item.agentDisplayName} ${item.category} ${item.primaryText} ${(item.keyPoints || []).join(' ')}`.toLowerCase();
        if (!hay.includes(query)) return false;
      }
      return true;
    });

    const selectedCount = sessionState.resultBoard.filter(i => i.selected).length;
    const selectedSpan = byId('rb-selected-count');
    const cmpTabSpan = byId('cmp-tab-count');
    if (selectedSpan) selectedSpan.textContent = selectedCount;
    if (cmpTabSpan) cmpTabSpan.textContent = selectedCount;

    if (!sessionState.resultBoard.length) {
      container.innerHTML = '<div class="empty-state" style="padding:24px;">No results on board yet. Click "Add to Result Board" on any Assistant response or action result.</div>';
      if (legacyContainer) legacyContainer.innerHTML = '<div class="empty-state" style="padding:20px;">No results added to Result Board yet.</div>';
      return;
    }

    if (!filtered.length) {
      container.innerHTML = '<div class="empty-state" style="padding:24px;">No saved results match the active filter criteria.</div>';
      return;
    }

    container.replaceChildren();
    filtered.forEach((item, idx) => {
      const isSelected = !!item.selected;
      const isCompact = sessionState.rbViewMode === 'compact';
      const card = document.createElement('div');
      card.className = `rb-card ${isSelected ? 'selected' : ''} ${item.isHighStakes ? 'high-stakes-card' : ''}`;
      card.innerHTML = `
        <div class="rb-card-top">
          <div style="display:flex; align-items:center; gap:8px;">
            <input type="checkbox" class="rb-item-cb" data-item-id="${item.id}" ${isSelected ? 'checked' : ''} style="cursor:pointer;" />
            <strong>${escapeHtml(item.agentDisplayName)}</strong>
            <span class="muted" style="font-size:0.78rem;">[${escapeHtml(item.category)}]</span>
            ${item.isHighStakes ? '<span class="cc-badge hs">High Stakes</span>' : ''}
          </div>
          <div class="rb-card-meta">
            <span class="pill" style="font-size:0.72rem;">${escapeHtml(item.sourceType)}</span>
            <span class="muted">${escapeHtml(item.timestamp)}</span>
          </div>
        </div>

        <div class="rb-card-body ${isCompact ? '' : 'expanded'}">${escapeHtml(item.primaryText)}</div>

        ${!isCompact && item.keyPoints && item.keyPoints.length ? `
          <div style="font-size:0.82rem; color:var(--muted);">
            <strong>Key Points:</strong> ${item.keyPoints.slice(0, 3).map(kp => `<span>• ${escapeHtml(kp)}</span>`).join(' ')}
          </div>
        ` : ''}

        <div class="rb-card-meta" style="margin-top:2px;">
          <span class="evidence-item-tag ${item.citations.length ? 'source' : 'none'}">
            ${item.citations.length ? `Reviewed / Citations: ${item.citations.length}` : 'No Citations'}
          </span>
          ${item.limitations.length ? `<span class="muted" style="font-size:0.75rem; color:#92400e;">Limitations: ${item.limitations.length}</span>` : ''}
          ${item.disagreementFlag ? '<span class="diff-badge" style="background:#fee2e2; color:#991b1b;">⚠️ Marked for Review</span>' : ''}
        </div>

        <div class="rb-card-actions">
          <button class="small" type="button" data-action="inspect-detail" data-item-id="${item.id}">🔍 Inspect Details</button>
          <button class="secondary small" type="button" data-action="use-prior" data-item-id="${item.id}">Use as Prior Context</button>
          <button class="secondary small" type="button" data-action="add-kit" data-item-id="${item.id}">Add to Context Kit</button>
          <button class="secondary small" type="button" data-action="toggle-flag" data-item-id="${item.id}">
            ${item.disagreementFlag ? '🚩 Unflag' : '🚩 Flag Review'}
          </button>
          <button class="secondary small danger" type="button" data-action="remove-item" data-item-id="${item.id}">Remove</button>
        </div>
      `;

      // Event bindings on card
      const cb = card.querySelector(`.rb-item-cb`);
      cb.addEventListener('change', (e) => {
        item.selected = e.target.checked;
        renderResultBoard();
      });

      card.querySelector(`[data-action="inspect-detail"]`).addEventListener('click', () => openResultDetailInspector(item));
      card.querySelector(`[data-action="use-prior"]`).addEventListener('click', () => {
        setStagedPriorContext({
          agentId: item.agentId,
          agentName: item.agentDisplayName,
          responseId: (item.fullResponse.responseContext && item.fullResponse.responseContext.responseId) || '',
          summary: item.primaryText,
        });
        byId('composer').scrollIntoView({ behavior: 'smooth' });
      });
      card.querySelector(`[data-action="add-kit"]`).addEventListener('click', () => {
        addContextKitItem('result_board', `${item.agentDisplayName} Result`, item.primaryText);
      });
      card.querySelector(`[data-action="toggle-flag"]`).addEventListener('click', () => {
        item.disagreementFlag = !item.disagreementFlag;
        renderResultBoard();
      });
      card.querySelector(`[data-action="remove-item"]`).addEventListener('click', () => {
        sessionState.resultBoard = sessionState.resultBoard.filter(i => i.id !== item.id);
        updateResultBoardCounters();
        renderResultBoard();
        populateResultBoardFilters();
      });

      container.append(card);
    });
  }

  // Result Board toolbar event listeners
  byId('rb-search-input')?.addEventListener('input', renderResultBoard);
  byId('rb-agent-filter')?.addEventListener('change', renderResultBoard);
  byId('rb-category-filter')?.addEventListener('change', renderResultBoard);
  byId('rb-high-stakes-filter')?.addEventListener('change', renderResultBoard);
  byId('rb-evidence-filter')?.addEventListener('change', renderResultBoard);

  byId('rb-view-mode-btn')?.addEventListener('click', () => {
    sessionState.rbViewMode = sessionState.rbViewMode === 'compact' ? 'expanded' : 'compact';
    byId('rb-view-mode-btn').textContent = sessionState.rbViewMode === 'compact' ? 'Expanded View' : 'Compact View';
    renderResultBoard();
  });

  byId('rb-select-all-visible')?.addEventListener('change', (e) => {
    const isChecked = e.target.checked;
    sessionState.resultBoard.forEach(i => { i.selected = isChecked; });
    renderResultBoard();
  });

  byId('rb-remove-selected-btn')?.addEventListener('click', () => {
    const selected = sessionState.resultBoard.filter(i => i.selected);
    if (!selected.length) {
      alert('No entries selected.');
      return;
    }
    if (confirm(`Remove ${selected.length} selected entries from the Result Board?`)) {
      sessionState.resultBoard = sessionState.resultBoard.filter(i => !i.selected);
      updateResultBoardCounters();
      renderResultBoard();
      populateResultBoardFilters();
      showToast(`Removed ${selected.length} entries.`);
    }
  });

  byId('rb-clear-btn')?.addEventListener('click', () => {
    if (!sessionState.resultBoard.length) return;
    if (confirm('Clear all saved results from this session? (In-memory state will be reset)')) {
      sessionState.resultBoard = [];
      updateResultBoardCounters();
      renderResultBoard();
      populateResultBoardFilters();
      showToast('Result Board cleared.');
    }
  });

  byId('rb-to-kit-btn')?.addEventListener('click', () => {
    const selected = sessionState.resultBoard.filter(i => i.selected);
    if (!selected.length) {
      alert('Select at least one entry on the Result Board.');
      return;
    }
    selected.forEach(item => {
      addContextKitItem('result_board', `${item.agentDisplayName} Result`, item.primaryText);
    });
    showToast(`Added ${selected.length} selected entries to Context Kit.`);
  });

  byId('rb-compare-btn')?.addEventListener('click', () => {
    const selected = sessionState.resultBoard.filter(i => i.selected);
    if (selected.length < 2 || selected.length > 6) {
      alert(`Please select between 2 and 6 entries to compare (currently ${selected.length} selected).`);
      return;
    }
    openComparisonWorkspace(selected);
  });

  byId('rb-review-packet-btn')?.addEventListener('click', () => {
    const selected = sessionState.resultBoard.filter(i => i.selected);
    if (!selected.length) {
      alert('Select at least one entry to compose a Review Packet.');
      return;
    }
    openReviewPacketComposer(selected);
  });

  byId('rb-to-decision-btn')?.addEventListener('click', () => {
    const selected = sessionState.resultBoard.filter(i => i.selected);
    if (!selected.length) {
      alert('Select at least one entry to populate Decision Composer options.');
      return;
    }
    openDecisionComposer(selected);
  });

  byId('rb-to-report-btn')?.addEventListener('click', () => {
    const selected = sessionState.resultBoard.filter(i => i.selected);
    if (!selected.length) {
      alert('Select at least one entry to prepare a report.');
      return;
    }
    prepareReportFromSelected(selected);
  });

  // ==========================================
  // Result Detail / Evidence Inspector
  // ==========================================

  function openResultDetailInspector(item) {
    sessionState.activeDetailItem = item;
    const modal = byId('drawer-result-detail');
    if (!modal) return;

    byId('detail-agent-name').textContent = `${item.agentDisplayName} — Result Details`;
    byId('detail-meta-subtitle').textContent = `Category: ${item.category} · Mode: ${item.generationMode} · Confidence: ${item.confidenceTier} · Saved: ${item.timestamp}`;
    byId('detail-primary-text').textContent = item.primaryText;

    const kpSec = byId('detail-keypoints-sec');
    const kpList = byId('detail-keypoints-list');
    if (item.keyPoints && item.keyPoints.length) {
      kpSec.style.display = 'block';
      kpList.innerHTML = item.keyPoints.map(kp => `<li>${escapeHtml(kp)}</li>`).join('');
    } else {
      kpSec.style.display = 'none';
    }

    // Evidence Ledger Breakdown
    const ledger = byId('detail-evidence-ledger');
    ledger.replaceChildren();

    const hasCitations = item.citations && item.citations.length;
    const sourceBreakdown = document.createElement('div');
    sourceBreakdown.innerHTML = `
      <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:6px;">
        <span class="evidence-item-tag ${hasCitations ? 'source' : 'none'}">
          ${hasCitations ? `Referenced Evidence: ${item.citations.length} item(s)` : 'No Reviewed Evidence'}
        </span>
        <span class="evidence-item-tag ${item.sourceType === 'assistant_turn' ? 'prior' : 'knowledge'}">
          Origin: ${escapeHtml(item.sourceType)}
        </span>
        <span class="evidence-item-tag citation">Not independently verified</span>
      </div>
    `;
    ledger.append(sourceBreakdown);

    if (hasCitations) {
      const citList = document.createElement('ul');
      citList.style.margin = '4px 0 0';
      citList.style.paddingLeft = '18px';
      item.citations.forEach(c => {
        const li = document.createElement('li');
        li.textContent = c;
        citList.append(li);
      });
      ledger.append(citList);
    }

    const limSec = byId('detail-limitations-sec');
    const limList = byId('detail-limitations-list');
    if (item.limitations && item.limitations.length) {
      limSec.style.display = 'block';
      limList.innerHTML = item.limitations.map(l => `<li>${escapeHtml(l)}</li>`).join('');
    } else {
      limSec.style.display = 'none';
    }

    const safeSec = byId('detail-safety-sec');
    const safeList = byId('detail-safety-list');
    if (item.safetyNotes && item.safetyNotes.length) {
      safeSec.style.display = 'block';
      safeList.innerHTML = item.safetyNotes.map(s => `<li>${escapeHtml(s)}</li>`).join('');
    } else {
      safeSec.style.display = 'none';
    }

    byId('detail-json-viewer').textContent = JSON.stringify(item.fullResponse || item, null, 2);
    byId('detail-json-panel').style.display = 'none';

    modal.classList.add('open');
  }

  byId('close-detail-btn')?.addEventListener('click', () => {
    byId('drawer-result-detail')?.classList.remove('open');
  });
  byId('drawer-result-detail')?.addEventListener('click', (e) => {
    if (e.target === byId('drawer-result-detail')) byId('drawer-result-detail').classList.remove('open');
  });

  byId('detail-toggle-json-btn')?.addEventListener('click', () => {
    const p = byId('detail-json-panel');
    p.style.display = p.style.display === 'none' ? 'block' : 'none';
  });

  byId('detail-use-prior-btn')?.addEventListener('click', () => {
    const item = sessionState.activeDetailItem;
    if (!item) return;
    setStagedPriorContext({
      agentId: item.agentId,
      agentName: item.agentDisplayName,
      responseId: (item.fullResponse.responseContext && item.fullResponse.responseContext.responseId) || '',
      summary: item.primaryText,
    });
    byId('drawer-result-detail')?.classList.remove('open');
    byId('composer').scrollIntoView({ behavior: 'smooth' });
  });

  byId('detail-add-kit-btn')?.addEventListener('click', () => {
    const item = sessionState.activeDetailItem;
    if (!item) return;
    addContextKitItem('result_board', `${item.agentDisplayName} Result`, item.primaryText);
    byId('drawer-result-detail')?.classList.remove('open');
  });

  // ==========================================
  // Multi-Result Comparison Workspace
  // ==========================================

  function openComparisonWorkspace(entries) {
    sessionState.activeComparisonEntries = entries;
    const wrap = byId('comparison-table-wrap');
    if (!wrap) return;

    // Asymmetry and high-stakes checks
    const asymBanner = byId('cmp-asymmetry-banner');
    const hsBanner = byId('cmp-high-stakes-banner');

    const sourceCounts = entries.map(e => (e.citations || []).length);
    const maxSources = Math.max(...sourceCounts);
    const minSources = Math.min(...sourceCounts);
    if (maxSources > 0 && minSources === 0) {
      asymBanner.style.display = 'block';
      asymBanner.innerHTML = `<strong>Evidence Asymmetry Notice:</strong> Evidence coverage differs between options (${maxSources} items vs 0 items). Lower-evidence options may need additional context before deciding.`;
    } else {
      asymBanner.style.display = 'none';
    }

    const anyHs = entries.some(e => e.isHighStakes);
    if (anyHs) {
      hsBanner.style.display = 'block';
      hsBanner.innerHTML = `<strong>High-Stakes Decision Domain:</strong> One or more candidate options touch sensitive areas (health, finance, legal, security). Review safety boundaries and independently verify critical details.`;
    } else {
      hsBanner.style.display = 'none';
    }

    // Differences detection
    const agentsDiffer = new Set(entries.map(e => e.agentDisplayName)).size > 1;
    const categoriesDiffer = new Set(entries.map(e => e.category)).size > 1;
    const modesDiffer = new Set(entries.map(e => e.generationMode)).size > 1;
    const hsDiffer = new Set(entries.map(e => e.isHighStakes)).size > 1;
    const evDiffer = new Set(sourceCounts).size > 1;

    let tableHtml = `
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Attribute</th>
            ${entries.map((e, idx) => `
              <th class="col-header">
                Option ${idx + 1}: ${escapeHtml(e.agentDisplayName)}
                ${e.isHighStakes ? '<span class="cc-badge hs" style="margin-left:4px;">High Stakes</span>' : ''}
              </th>
            `).join('')}
          </tr>
        </thead>
        <tbody>
          <tr>
            <th>Agent & Category ${agentsDiffer || categoriesDiffer ? '<span class="diff-badge">diff</span>' : ''}</th>
            ${entries.map(e => `<td><strong>${escapeHtml(e.agentDisplayName)}</strong><br><span class="muted">[${escapeHtml(e.category)}]</span></td>`).join('')}
          </tr>
          <tr>
            <th>Primary Answer</th>
            ${entries.map(e => `<td><div style="max-height:160px; overflow-y:auto; font-size:0.84rem; white-space:pre-wrap;">${escapeHtml(e.primaryText)}</div></td>`).join('')}
          </tr>
          <tr>
            <th>Key Points</th>
            ${entries.map(e => `
              <td>
                ${(e.keyPoints && e.keyPoints.length) ? `<ul style="margin:0; padding-left:16px; font-size:0.8rem;">${e.keyPoints.slice(0, 4).map(kp => `<li>${escapeHtml(kp)}</li>`).join('')}</ul>` : '<span class="muted">None listed</span>'}
              </td>
            `).join('')}
          </tr>
          <tr>
            <th>Evidence Breakdown ${evDiffer ? '<span class="diff-badge">diff</span>' : ''}</th>
            ${entries.map(e => `
              <td>
                <span class="evidence-item-tag ${e.citations.length ? 'source' : 'none'}">${e.citations.length ? `${e.citations.length} Citation(s)` : 'No Citations'}</span>
                ${e.citations.length ? `<ul style="margin:4px 0 0; padding-left:14px; font-size:0.75rem;">${e.citations.slice(0, 3).map(c => `<li>${escapeHtml(c)}</li>`).join('')}</ul>` : ''}
              </td>
            `).join('')}
          </tr>
          <tr>
            <th>Limitations</th>
            ${entries.map(e => `
              <td style="color:#92400e; font-size:0.8rem;">
                ${(e.limitations && e.limitations.length) ? e.limitations.join('; ') : 'None specified'}
              </td>
            `).join('')}
          </tr>
          <tr>
            <th>High-Stakes Status ${hsDiffer ? '<span class="diff-badge">diff</span>' : ''}</th>
            ${entries.map(e => `<td>${e.isHighStakes ? '<span class="pill blocked">High Stakes</span>' : '<span class="pill allowed">Standard</span>'}</td>`).join('')}
          </tr>
          <tr>
            <th>Generation Mode ${modesDiffer ? '<span class="diff-badge">diff</span>' : ''}</th>
            ${entries.map(e => `<td><code>${escapeHtml(e.generationMode || 'deterministic')}</code></td>`).join('')}
          </tr>
          <tr>
            <th>Manual Review Flag</th>
            ${entries.map(e => `
              <td>
                <button type="button" class="flag-btn ${e.disagreementFlag ? 'flagged' : ''}" data-cmp-flag="${e.id}">
                  ${e.disagreementFlag ? '🚩 Marked for Review' : '🏳️ Mark Review'}
                </button>
              </td>
            `).join('')}
          </tr>
        </tbody>
      </table>
    `;

    wrap.innerHTML = tableHtml;

    // Bind flags
    wrap.querySelectorAll('[data-cmp-flag]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-cmp-flag');
        const it = sessionState.resultBoard.find(i => i.id === id);
        if (it) {
          it.disagreementFlag = !it.disagreementFlag;
          openComparisonWorkspace(sessionState.activeComparisonEntries);
          renderResultBoard();
        }
      });
    });

    switchProductivityTab('panel-comparison');
  }

  byId('cmp-close-btn')?.addEventListener('click', () => {
    switchProductivityTab('panel-result-board');
  });

  byId('cmp-to-kit-btn')?.addEventListener('click', () => {
    if (!sessionState.activeComparisonEntries || !sessionState.activeComparisonEntries.length) return;
    const summary = sessionState.activeComparisonEntries.map((e, idx) => `[Option ${idx + 1}: ${e.agentDisplayName}]\n${e.primaryText.slice(0, 500)}`).join('\n\n');
    addContextKitItem('comparison_summary', `Comparison (${sessionState.activeComparisonEntries.length} Options)`, summary);
    showToast('Added comparison summary to Context Kit.');
  });

  byId('cmp-to-review-btn')?.addEventListener('click', () => {
    if (!sessionState.activeComparisonEntries || !sessionState.activeComparisonEntries.length) return;
    openReviewPacketComposer(sessionState.activeComparisonEntries);
  });

  byId('cmp-to-decision-btn')?.addEventListener('click', () => {
    if (!sessionState.activeComparisonEntries || !sessionState.activeComparisonEntries.length) return;
    openDecisionComposer(sessionState.activeComparisonEntries);
  });

  // ==========================================
  // Review Packet Composer
  // ==========================================

  const MAX_PACKET_CHARS = 16000;

  function openReviewPacketComposer(entries) {
    sessionState.activePacketEntries = entries;
    const modal = byId('drawer-review-packet');
    if (!modal) return;

    byId('packet-entry-count').textContent = entries.length;
    const list = byId('packet-entries-list');
    list.replaceChildren();

    entries.forEach((e, idx) => {
      const row = document.createElement('div');
      row.style.cssText = 'background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px; padding:6px 8px; font-size:0.82rem; display:flex; justify-content:space-between; align-items:center;';
      row.innerHTML = `
        <div>
          <strong>${idx + 1}. ${escapeHtml(e.agentDisplayName)}</strong> <span class="muted">[${escapeHtml(e.category)}]</span>
          <div class="muted" style="font-size:0.75rem; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:400px;">${escapeHtml(e.primaryText.slice(0, 80))}...</div>
        </div>
        <span class="muted" style="font-size:0.75rem;">${e.primaryText.length} chars</span>
      `;
      list.append(row);
    });

    updateReviewPacketBudget();
    modal.classList.add('open');
  }

  function updateReviewPacketBudget() {
    const question = byId('packet-question-input')?.value || '';
    const notes = byId('packet-notes-input')?.value || '';
    const unresolved = byId('packet-unresolved-input')?.value || '';
    const entries = sessionState.activePacketEntries || [];

    const approxText = `${question}\n${notes}\n${unresolved}\n` + entries.map(e => e.primaryText).join('\n');
    const totalChars = approxText.length;

    const budgetText = byId('packet-budget-text');
    const budgetBar = byId('packet-budget-bar');
    const insertBtn = byId('packet-insert-composer-btn');

    if (budgetText) budgetText.textContent = `${totalChars.toLocaleString()} / ${MAX_PACKET_CHARS.toLocaleString()} chars`;
    if (budgetBar) {
      const pct = Math.min(100, Math.round((totalChars / MAX_PACKET_CHARS) * 100));
      budgetBar.style.width = pct + '%';
      if (pct > 90) budgetBar.className = 'budget-bar-fill danger';
      else if (pct > 70) budgetBar.className = 'budget-bar-fill warning';
      else budgetBar.className = 'budget-bar-fill';
    }

    if (insertBtn) {
      if (totalChars > MAX_PACKET_CHARS) {
        insertBtn.disabled = true;
        insertBtn.title = 'Review packet exceeds character limit. Reduce notes or entries.';
      } else {
        insertBtn.disabled = false;
        insertBtn.title = '';
      }
    }
  }

  byId('packet-question-input')?.addEventListener('input', updateReviewPacketBudget);
  byId('packet-notes-input')?.addEventListener('input', updateReviewPacketBudget);
  byId('packet-unresolved-input')?.addEventListener('input', updateReviewPacketBudget);

  byId('close-review-packet-btn')?.addEventListener('click', () => {
    byId('drawer-review-packet')?.classList.remove('open');
  });
  byId('drawer-review-packet')?.addEventListener('click', (e) => {
    if (e.target === byId('drawer-review-packet')) byId('drawer-review-packet').classList.remove('open');
  });

  function buildReviewPacketMarkdown() {
    const question = (byId('packet-question-input')?.value || '').trim() || 'Review and synthesize selected responses';
    const notes = (byId('packet-notes-input')?.value || '').trim();
    const unresolved = (byId('packet-unresolved-input')?.value || '').trim();
    const entries = sessionState.activePacketEntries || [];

    let md = `# Review Packet: ${question}\n\n**Selected Responses:** ${entries.length}\n`;
    if (notes) md += `\n## Reviewer Notes\n${notes}\n`;
    md += `\n## Candidate Summaries\n`;
    entries.forEach((e, idx) => {
      md += `\n### [${idx + 1}] ${e.agentDisplayName} (${e.category})\n${e.primaryText}\n`;
      if (e.keyPoints && e.keyPoints.length) md += `**Key Points:**\n${e.keyPoints.map(kp => `- ${kp}`).join('\n')}\n`;
      if (e.citations && e.citations.length) md += `**Evidence / Citations:** ${e.citations.join('; ')}\n`;
    });
    if (unresolved) md += `\n## Unresolved Questions\n${unresolved}\n`;
    return md.trim();
  }

  byId('packet-insert-composer-btn')?.addEventListener('click', () => {
    const md = buildReviewPacketMarkdown();
    const input = byId('prompt-input');
    input.value = (input.value.trim() ? `${input.value.trim()}\n\n${md}` : md).trim();
    input.focus();
    triggerReadinessEvaluation();
    byId('drawer-review-packet')?.classList.remove('open');
    showToast('Inserted Review Packet into prompt composer.');
    byId('composer').scrollIntoView({ behavior: 'smooth' });
  });

  byId('packet-stage-prior-btn')?.addEventListener('click', () => {
    const md = buildReviewPacketMarkdown();
    setStagedPriorContext({
      agentId: 'review_packet',
      agentName: 'Review Packet Composer',
      responseId: 'packet_' + Date.now(),
      summary: md.slice(0, 16000),
    });
    byId('drawer-review-packet')?.classList.remove('open');
    showToast('Staged Review Packet as prior context.');
    byId('composer').scrollIntoView({ behavior: 'smooth' });
  });

  byId('packet-add-kit-btn')?.addEventListener('click', () => {
    const md = buildReviewPacketMarkdown();
    addContextKitItem('review_packet', 'Structured Review Packet', md);
    byId('drawer-review-packet')?.classList.remove('open');
  });

  // ==========================================
  // Decision Composer
  // ==========================================

  function openDecisionComposer(prefillEntries = null) {
    const modal = byId('drawer-decision-composer');
    if (!modal) return;

    if (prefillEntries && prefillEntries.length) {
      sessionState.decisionComposerOptions = prefillEntries.map(e => e.agentDisplayName || 'Candidate Option');
      const excerpts = prefillEntries.map(e => `[${e.agentDisplayName}]: ${e.primaryText.slice(0, 200)}`).join('\n\n');
      if (byId('dec-notes-input') && !byId('dec-notes-input').value.trim()) {
        byId('dec-notes-input').value = excerpts;
      }
    } else if (!sessionState.decisionComposerOptions.length) {
      sessionState.decisionComposerOptions = ['Option A', 'Option B'];
    }

    renderDecisionOptionsList();
    evaluateDecisionComposerReadiness();
    modal.classList.add('open');
  }

  function renderDecisionOptionsList() {
    const list = byId('dec-options-list');
    if (!list) return;
    list.replaceChildren();

    sessionState.decisionComposerOptions.forEach((opt, idx) => {
      const row = document.createElement('div');
      row.style.cssText = 'display:flex; align-items:center; gap:6px;';
      row.innerHTML = `
        <span class="muted" style="font-size:0.8rem; width:20px;">${idx + 1}.</span>
        <input type="text" class="dec-opt-input" data-opt-idx="${idx}" value="${escapeHtml(opt)}" style="flex:1; padding:4px 8px; font-size:0.85rem; border:1px solid #cbd5e1; border-radius:4px;" />
        <button type="button" class="secondary small danger" data-opt-remove="${idx}" title="Remove Option" ${sessionState.decisionComposerOptions.length <= 2 ? 'disabled' : ''}>✕</button>
      `;

      row.querySelector('.dec-opt-input').addEventListener('input', (e) => {
        sessionState.decisionComposerOptions[idx] = e.target.value;
        evaluateDecisionComposerReadiness();
      });

      row.querySelector(`[data-opt-remove="${idx}"]`).addEventListener('click', () => {
        sessionState.decisionComposerOptions.splice(idx, 1);
        renderDecisionOptionsList();
        evaluateDecisionComposerReadiness();
      });

      list.append(row);
    });
  }

  byId('dec-add-option-btn')?.addEventListener('click', () => {
    sessionState.decisionComposerOptions.push(`Option ${String.fromCharCode(65 + sessionState.decisionComposerOptions.length)}`);
    renderDecisionOptionsList();
    evaluateDecisionComposerReadiness();
  });

  function evaluateDecisionComposerReadiness() {
    const question = (byId('dec-question-input')?.value || '').trim();
    const options = sessionState.decisionComposerOptions.map(o => o.trim()).filter(Boolean);
    const criteria = (byId('dec-criteria-input')?.value || '').trim();
    const priorities = (byId('dec-priorities-input')?.value || '').trim();
    const notes = (byId('dec-notes-input')?.value || '').trim();

    const card = byId('dec-readiness-card');
    const pill = byId('dec-readiness-pill');
    const reason = byId('dec-readiness-reason');
    const prepBtn = byId('dec-prepare-btn');

    if (!card || !pill || !reason) return;

    if (!question) {
      pill.className = 'pill inactive';
      pill.textContent = 'Needs Question';
      reason.textContent = 'Enter a clear decision question or goal above.';
      card.className = 'readiness-coach-card';
      if (prepBtn) prepBtn.disabled = false;
      return;
    }

    if (options.length < 2) {
      pill.className = 'pill blocked';
      pill.textContent = 'Needs Options';
      reason.textContent = 'Local Decision Agent requires at least 2 distinct candidate options.';
      card.className = 'readiness-coach-card needs_options';
      if (prepBtn) prepBtn.disabled = true;
      return;
    }

    const unique = new Set(options.map(o => o.toLowerCase()));
    if (unique.size < options.length) {
      pill.className = 'pill moderate';
      pill.textContent = 'Duplicate Options';
      reason.textContent = 'Two or more options appear identical. Clarify option names.';
      card.className = 'readiness-coach-card';
      if (prepBtn) prepBtn.disabled = true;
      return;
    }

    if (!criteria && !priorities && notes.length < 30) {
      pill.className = 'pill waiting_for_approval';
      pill.textContent = 'Thin Criteria';
      reason.textContent = 'No explicit criteria or priorities provided. Fit ratings will be provisional.';
      card.className = 'readiness-coach-card';
      if (prepBtn) prepBtn.disabled = false;
      return;
    }

    pill.className = 'pill succeeded';
    pill.textContent = 'Ready to Prepare';
    reason.textContent = `Well-formed decision structure ready for Local Decision Agent (${options.length} options).`;
    card.className = 'readiness-coach-card ready';
    if (prepBtn) prepBtn.disabled = false;
  }

  byId('dec-question-input')?.addEventListener('input', evaluateDecisionComposerReadiness);
  byId('dec-criteria-input')?.addEventListener('input', evaluateDecisionComposerReadiness);
  byId('dec-priorities-input')?.addEventListener('input', evaluateDecisionComposerReadiness);
  byId('dec-constraints-input')?.addEventListener('input', evaluateDecisionComposerReadiness);
  byId('dec-notes-input')?.addEventListener('input', evaluateDecisionComposerReadiness);
  byId('dec-style-select')?.addEventListener('change', evaluateDecisionComposerReadiness);

  byId('close-decision-composer-btn')?.addEventListener('click', () => {
    byId('drawer-decision-composer')?.classList.remove('open');
  });
  byId('drawer-decision-composer')?.addEventListener('click', (e) => {
    if (e.target === byId('drawer-decision-composer')) byId('drawer-decision-composer').classList.remove('open');
  });

  byId('dec-prepare-btn')?.addEventListener('click', () => {
    const question = (byId('dec-question-input')?.value || '').trim() || 'Compare these options';
    const options = sessionState.decisionComposerOptions.map(o => o.trim()).filter(Boolean);
    const criteria = (byId('dec-criteria-input')?.value || '').trim();
    const priorities = (byId('dec-priorities-input')?.value || '').trim();
    const constraints = (byId('dec-constraints-input')?.value || '').trim();
    const style = byId('dec-style-select')?.value || 'balanced';
    const notes = (byId('dec-notes-input')?.value || '').trim();

    if (options.length < 2) {
      alert('Please provide at least 2 candidate options.');
      return;
    }

    let prompt = `Decision: ${question}\nOptions: ${options.join(', ')}`;
    if (criteria) prompt += `\nCriteria: ${criteria}`;
    if (priorities) prompt += `\nPriorities: ${priorities}`;
    if (constraints) prompt += `\nConstraints: ${constraints}`;
    if (style && style !== 'balanced') prompt += `\nDecision Style: ${style}`;
    if (notes) prompt += `\n\nContext Notes:\n${notes}`;

    selectAgentManually('local_decision_agent');
    byId('prompt-input').value = prompt;
    byId('prompt-input').focus();
    triggerReadinessEvaluation();
    byId('drawer-decision-composer')?.classList.remove('open');
    showToast('Prepared Decision Request in composer. Click Send to run.');
    byId('composer').scrollIntoView({ behavior: 'smooth' });
  });

  // ==========================================
  // Report Preparation from Selected Results
  // ==========================================

  function prepareReportFromSelected(entries) {
    let reportMd = `# Session Results Analysis Report\n\nGenerated on: ${new Date().toLocaleString()}\n\n`;
    entries.forEach((e, idx) => {
      reportMd += `## ${idx + 1}. ${e.agentDisplayName} (${e.category})\n\n${e.primaryText}\n\n`;
      if (e.keyPoints && e.keyPoints.length) {
        reportMd += `### Key Takeaways\n${e.keyPoints.map(kp => `- ${kp}`).join('\n')}\n\n`;
      }
      if (e.citations && e.citations.length) {
        reportMd += `### Referenced Evidence\n${e.citations.map(c => `- ${c}`).join('\n')}\n\n`;
      }
    });

    const lastIdx = sessionState.transcript.length - 1;
    if (lastIdx >= 0) {
      const turn = sessionState.transcript[lastIdx];
      turn.actionBridgeOpen = true;
      turn.selectedActionType = 'write_report';
      turn.reportTitle = 'Session Results Analysis Report';
      turn.reportContent = reportMd;
      renderTranscript();
      showToast('Opened Report Tool bridge with drafted report content. Inspect and run dry-run to proceed.');
      byId(`action-bridge-${lastIdx}`)?.scrollIntoView({ behavior: 'smooth' });
    } else {
      setStagedPriorContext({
        agentId: 'report_tool',
        agentName: 'Report Tool Preparation',
        responseId: 'rep_prep_' + Date.now(),
        summary: reportMd.slice(0, 4000),
      });
      showToast('Staged drafted report content as prior context.');
      byId('composer').scrollIntoView({ behavior: 'smooth' });
    }
  }

  // ==========================================
  // Productivity Layer: Tabs & Command Center
  // ==========================================

  sessionState.pinnedAgentIds = new Set();
  sessionState.recentAgentIds = [];
  sessionState.contextKit = [];
  sessionState.activePlaybookId = 'plan_review_decision';
  sessionState.playbookSteps = [];
  sessionState.builtInPlaybooks = [];
  sessionState.readinessDebounceTimer = null;
  sessionState.activeBoundariesAgent = null;
  sessionState.activeSuggestion = null;

  function switchProductivityTab(tabId) {
    const tabs = [
      'panel-command-center',
      'panel-playbooks',
      'panel-context-kit',
      'panel-result-board',
      'panel-comparison'
    ];
    if (tabId === 'panel-decision-composer-wrap') {
      openDecisionComposer();
      return;
    }
    tabs.forEach(id => {
      const panel = byId(id);
      const btn = document.querySelector(`[data-panel="${id}"]`);
      if (!panel || !btn) return;
      if (id === tabId) {
        const isOpen = panel.classList.contains('open');
        if (isOpen) {
          panel.classList.remove('open');
          btn.classList.remove('active');
        } else {
          panel.classList.add('open');
          btn.classList.add('active');
          if (id === 'panel-result-board') renderResultBoard();
        }
      } else {
        panel.classList.remove('open');
        btn.classList.remove('active');
      }
    });
  }

  document.querySelectorAll('.prod-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetPanel = btn.getAttribute('data-panel');
      switchProductivityTab(targetPanel);
    });
  });

  function renderCommandCenter() {
    const grid = byId('cc-agent-grid');
    if (!grid) return;
    const query = (byId('cc-search-input').value || '').toLowerCase().trim();
    const catFilter = byId('cc-category-filter').value;
    const hsOnly = byId('cc-high-stakes-filter').checked;
    const pinnedOnly = byId('cc-pinned-filter').checked;

    const filtered = sessionState.catalogAgents.filter(agent => {
      const agentId = agent.agentId || agent.agent_id;
      const name = (agent.displayName || agent.name || '').toLowerCase();
      const cat = (agent.category || '').toLowerCase();
      const useWhen = (agent.useWhen || agent.use_when || '').toLowerCase();
      const keywords = (agent.keywords || []).join(' ').toLowerCase();
      const isHs = !!(agent.isHighStakes || agent.high_stakes);
      const isPinned = sessionState.pinnedAgentIds.has(agentId);

      if (pinnedOnly && !isPinned) return false;
      if (hsOnly && !isHs) return false;
      if (catFilter && agent.category !== catFilter) return false;
      if (query) {
        const matches = name.includes(query) || cat.includes(query) || useWhen.includes(query) || keywords.includes(query) || agentId.includes(query);
        if (!matches) return false;
      }
      return true;
    });

    if (!filtered.length) {
      grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1; padding:24px;">No response agents match the active filter criteria.</div>';
      return;
    }

    grid.replaceChildren();
    filtered.forEach(agent => {
      const agentId = agent.agentId || agent.agent_id;
      const isPinned = sessionState.pinnedAgentIds.has(agentId);
      const isHs = !!(agent.isHighStakes || agent.high_stakes);
      const card = document.createElement('div');
      card.className = `cc-agent-card ${isHs ? 'high-stakes-card' : ''}`;
      card.innerHTML = `
        <div class="cc-card-top">
          <div class="cc-card-name">${escapeHtml(agent.displayName || agent.name)}</div>
          <button class="secondary small pin-btn" data-pin-id="${escapeHtml(agentId)}" style="padding:1px 6px; font-size:0.75rem;" title="${isPinned ? 'Unpin' : 'Pin to quick access'}">
            ${isPinned ? '★ Pinned' : '☆ Pin'}
          </button>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="cc-card-cat">${escapeHtml(agent.category || 'General')}</span>
          <span class="muted" style="font-size:0.75rem;">${escapeHtml(agent.responseMode || 'response_only')}</span>
        </div>
        <div class="cc-card-desc">${escapeHtml(agent.useWhen || 'Specialized response agent.')}</div>
        <div class="cc-card-badges">
          <span class="cc-badge">Local-Only</span>
          <span class="cc-badge">Manual-Input</span>
          ${isHs ? '<span class="cc-badge hs">High Stakes</span>' : ''}
        </div>
        <div class="cc-card-actions">
          <button type="button" class="small" data-action="use" data-agent-id="${escapeHtml(agentId)}">Use Agent</button>
          <button type="button" class="secondary small" data-action="starter" data-agent-id="${escapeHtml(agentId)}">Load Starter</button>
          <button type="button" class="secondary small" data-action="add-workflow" data-agent-id="${escapeHtml(agentId)}">Add to Workflow</button>
          <button type="button" class="secondary small" data-action="boundaries" data-agent-id="${escapeHtml(agentId)}">Boundaries</button>
        </div>
      `;

      card.querySelector(`[data-pin-id="${agentId}"]`).addEventListener('click', () => togglePin(agentId));
      card.querySelector(`[data-action="use"]`).addEventListener('click', () => selectAgentManually(agentId));
      card.querySelector(`[data-action="starter"]`).addEventListener('click', () => loadAgentStarter(agentId));
      card.querySelector(`[data-action="add-workflow"]`).addEventListener('click', () => addAgentToWorkflow(agentId));
      card.querySelector(`[data-action="boundaries"]`).addEventListener('click', () => showAgentBoundaries(agentId));

      grid.append(card);
    });
  }

  function togglePin(agentId) {
    if (sessionState.pinnedAgentIds.has(agentId)) {
      sessionState.pinnedAgentIds.delete(agentId);
      showToast('Unpinned agent.');
    } else {
      sessionState.pinnedAgentIds.add(agentId);
      showToast('Pinned agent to quick access.');
    }
    renderPinnedRow();
    renderCommandCenter();
  }

  function renderPinnedRow() {
    const row = byId('cc-pinned-chips');
    const sec = byId('cc-pinned-section');
    if (!sessionState.pinnedAgentIds.size) {
      sec.style.display = 'none';
      return;
    }
    sec.style.display = 'flex';
    row.replaceChildren();
    sessionState.pinnedAgentIds.forEach(agentId => {
      const agent = sessionState.catalogAgents.find(a => (a.agentId || a.agent_id) === agentId);
      const name = agent ? (agent.displayName || agent.name) : agentId;
      const chip = document.createElement('span');
      chip.className = 'cc-chip pinned';
      chip.innerHTML = `
        <span>★ ${escapeHtml(name)}</span>
        <span class="unpin-icon" title="Unpin">✕</span>
      `;
      chip.querySelector('span:first-child').addEventListener('click', () => selectAgentManually(agentId));
      chip.querySelector('.unpin-icon').addEventListener('click', (e) => {
        e.stopPropagation();
        togglePin(agentId);
      });
      row.append(chip);
    });
  }

  function recordRecentAgent(agentId) {
    if (!agentId) return;
    sessionState.recentAgentIds = [agentId, ...sessionState.recentAgentIds.filter(id => id !== agentId)].slice(0, 6);
    renderRecentRow();
  }

  function renderRecentRow() {
    const row = byId('cc-recent-chips');
    const sec = byId('cc-recent-section');
    if (!sessionState.recentAgentIds.length) {
      sec.style.display = 'none';
      return;
    }
    sec.style.display = 'flex';
    row.replaceChildren();
    sessionState.recentAgentIds.forEach(agentId => {
      const agent = sessionState.catalogAgents.find(a => (a.agentId || a.agent_id) === agentId);
      const name = agent ? (agent.displayName || agent.name) : agentId;
      const chip = document.createElement('span');
      chip.className = 'cc-chip';
      chip.textContent = name;
      chip.addEventListener('click', () => selectAgentManually(agentId));
      row.append(chip);
    });
  }

  function selectAgentManually(agentId) {
    const select = byId('opt-agent-override');
    select.value = agentId;
    recordRecentAgent(agentId);
    updateManualOverrideIndicator();
    triggerReadinessEvaluation();
    showToast(`Manual route set to: ${getAgentDisplayName(agentId)}`);
    byId('composer').scrollIntoView({ behavior: 'smooth' });
  }

  function clearManualAgentOverride() {
    const select = byId('opt-agent-override');
    select.value = '';
    updateManualOverrideIndicator();
    triggerReadinessEvaluation();
    showToast('Manual route cleared. Auto-routing active.');
  }

  function updateManualOverrideIndicator() {
    const select = byId('opt-agent-override');
    const val = select.value;
    const indicator = byId('manual-override-indicator');
    const nameSpan = byId('manual-override-agent-name');
    if (val) {
      nameSpan.textContent = getAgentDisplayName(val);
      indicator.style.display = 'inline-flex';
    } else {
      indicator.style.display = 'none';
    }
  }

  byId('clear-manual-override-btn').addEventListener('click', clearManualAgentOverride);
  byId('opt-agent-override').addEventListener('change', () => {
    const val = byId('opt-agent-override').value;
    if (val) recordRecentAgent(val);
    updateManualOverrideIndicator();
    triggerReadinessEvaluation();
  });

  function getAgentDisplayName(agentId) {
    const agent = sessionState.catalogAgents.find(a => (a.agentId || a.agent_id) === agentId);
    return agent ? (agent.displayName || agent.name) : agentId;
  }

  function loadAgentStarter(agentId) {
    const agent = sessionState.catalogAgents.find(a => (a.agentId || a.agent_id) === agentId);
    if (!agent) return;
    const example = (agent.examples && agent.examples[0]) || agent.exampleRequestBody;
    let starterText = '';
    if (example) {
      if (example.topic) starterText = `Topic: ${example.topic}\nNotes: ${example.notes || ''}`;
      else if (example.goal) starterText = `Goal: ${example.goal}`;
      else if (example.request) starterText = `Request: ${example.request}`;
      else if (example.problem) starterText = `Problem symptom: ${example.problem}`;
      else if (example.content) starterText = `Content:\n"""\n${example.content}\n"""`;
      else if (example.situation) starterText = `Situation: ${example.situation}`;
      else if (example.careerGoal) starterText = `Career Goal: ${example.careerGoal}`;
      else if (example.financialGoal) starterText = `Financial Goal: ${example.financialGoal}`;
      else if (example.academicGoal) starterText = `Academic Goal: ${example.academicGoal}`;
      else if (example.businessIdea) starterText = `Business Idea: ${example.businessIdea}`;
      else if (example.primaryGoal) starterText = `Primary Goal: ${example.primaryGoal}`;
      else if (example.decision) starterText = `Decision: ${example.decision}\nOptions: ${(example.options || []).join(', ')}`;
      else starterText = `Explore ${agent.displayName || agent.name}`;
    } else {
      starterText = `Help me with ${agent.displayName || agent.name}`;
    }

    byId('prompt-input').value = starterText;
    selectAgentManually(agentId);
    byId('prompt-input').focus();
    showToast(`Loaded starter template for ${getAgentDisplayName(agentId)}`);
  }

  function showAgentBoundaries(agentId) {
    const agent = sessionState.catalogAgents.find(a => (a.agentId || a.agent_id) === agentId);
    if (!agent) return;
    sessionState.activeBoundariesAgent = agent;
    const modal = byId('agent-boundaries-modal');
    byId('modal-agent-name').textContent = `${agent.displayName || agent.name} — Guardrails & Scope`;

    const badgesContainer = byId('modal-agent-badges');
    badgesContainer.replaceChildren();
    (agent.badges || ['local-only', 'manual-input', 'non-persistent']).forEach(b => {
      const span = document.createElement('span');
      span.className = 'pill inactive';
      span.textContent = b;
      badgesContainer.append(span);
    });

    byId('modal-agent-usewhen').innerHTML = `<strong>Intended Use:</strong> ${escapeHtml(agent.useWhen || 'Specialized response agent.')}`;

    const notesList = byId('modal-safety-notes');
    notesList.replaceChildren();
    (agent.safetyNotes || ['Local execution only. No external services or connectors.']).forEach(n => {
      const li = document.createElement('li');
      li.textContent = n;
      notesList.append(li);
    });

    const hsSec = byId('modal-high-stakes-section');
    if (agent.isHighStakes || agent.high_stakes) {
      hsSec.style.display = 'block';
      byId('modal-high-stakes-text').textContent = 'This agent operates in a high-stakes decision domain. Jarvis provides local informational guidance only; no professional certification, live filings, or financial transactions are performed.';
    } else {
      hsSec.style.display = 'none';
    }

    modal.classList.add('open');
  }

  byId('close-modal-btn').addEventListener('click', () => {
    byId('agent-boundaries-modal').classList.remove('open');
  });
  byId('agent-boundaries-modal').addEventListener('click', (e) => {
    if (e.target === byId('agent-boundaries-modal')) {
      byId('agent-boundaries-modal').classList.remove('open');
    }
  });

  byId('cc-search-input').addEventListener('input', renderCommandCenter);
  byId('cc-category-filter').addEventListener('change', renderCommandCenter);
  byId('cc-high-stakes-filter').addEventListener('change', renderCommandCenter);
  byId('cc-pinned-filter').addEventListener('change', renderCommandCenter);

  // ==========================================
  // Productivity Layer: Playbooks & Workflows
  // ==========================================

  async function loadPlaybooks() {
    try {
      const playbooks = await apiFetch('/api/assistant/productivity/playbooks');
      if (Array.isArray(playbooks)) {
        sessionState.builtInPlaybooks = playbooks;
        populatePlaybooksDropdown(playbooks);
        if (playbooks.length) {
          selectPlaybook(playbooks[0].id);
        }
      }
    } catch (err) {
      console.warn('Failed to load playbooks from server:', err);
    }
  }

  function populatePlaybooksDropdown(playbooks) {
    const select = byId('playbook-select');
    if (!select) return;
    select.replaceChildren();
    playbooks.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      select.append(opt);
    });
    const customOpt = document.createElement('option');
    customOpt.value = 'custom';
    customOpt.textContent = 'Custom Workflow';
    select.append(customOpt);
  }

  function populateAddStepAgentDropdown(agents) {
    const select = byId('add-step-agent-select');
    if (!select) return;
    select.replaceChildren();
    agents.forEach(agent => {
      const opt = document.createElement('option');
      opt.value = agent.agentId || agent.agent_id;
      opt.textContent = `${agent.displayName || agent.name} [${agent.category || 'General'}]`;
      select.append(opt);
    });
  }

  function selectPlaybook(playbookId) {
    sessionState.activePlaybookId = playbookId;
    byId('playbook-select').value = playbookId;
    if (playbookId === 'custom') {
      byId('playbook-description').textContent = 'Custom multi-step workflow. Add steps using the selector below.';
      if (!sessionState.playbookSteps.length) {
        sessionState.playbookSteps = [];
      }
    } else {
      const pb = sessionState.builtInPlaybooks.find(p => p.id === playbookId);
      if (pb) {
        byId('playbook-description').textContent = pb.description;
        sessionState.playbookSteps = pb.steps.map((s, idx) => ({
          stepIndex: idx,
          agentId: s.agentId,
          name: s.name || getAgentDisplayName(s.agentId),
          purpose: s.purpose,
          suggestedPrompt: s.suggestedPrompt || '',
          status: 'not_started',
        }));
      }
    }
    renderPlaybookSteps();
  }

  byId('playbook-select').addEventListener('change', (e) => {
    selectPlaybook(e.target.value);
  });

  byId('reset-playbook-btn').addEventListener('click', () => {
    selectPlaybook(sessionState.activePlaybookId);
    showToast('Reset active playbook steps.');
  });

  function renderPlaybookSteps() {
    const list = byId('playbook-steps-list');
    if (!list) return;
    if (!sessionState.playbookSteps.length) {
      list.innerHTML = '<div class="muted" style="text-align:center; padding:16px;">No steps in this workflow. Insert steps below.</div>';
      return;
    }
    list.replaceChildren();
    sessionState.playbookSteps.forEach((step, idx) => {
      const card = document.createElement('div');
      card.className = `playbook-step-card ${step.status === 'in_progress' ? 'active-step' : (step.status === 'done' ? 'completed-step' : '')}`;
      card.innerHTML = `
        <div class="step-left">
          <div class="step-num-badge">${idx + 1}</div>
          <div class="step-details">
            <div class="step-name">${escapeHtml(step.name || getAgentDisplayName(step.agentId))}</div>
            <div class="step-purpose">${escapeHtml(step.purpose || 'Execute step')}</div>
          </div>
        </div>
        <div class="step-right">
          <select class="cc-filter-select" data-step-status="${idx}" style="font-size:0.8rem; padding:4px 6px;">
            <option value="not_started" ${step.status === 'not_started' ? 'selected' : ''}>Not Started</option>
            <option value="in_progress" ${step.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
            <option value="done" ${step.status === 'done' ? 'selected' : ''}>Completed</option>
          </select>
          <button type="button" class="small" data-prepare-step="${idx}">Prepare Step</button>
          <button type="button" class="secondary small" data-step-up="${idx}" ${idx === 0 ? 'disabled' : ''} title="Move Up">↑</button>
          <button type="button" class="secondary small" data-step-down="${idx}" ${idx === sessionState.playbookSteps.length - 1 ? 'disabled' : ''} title="Move Down">↓</button>
          <button type="button" class="secondary small" data-step-remove="${idx}" title="Remove Step">✕</button>
        </div>
      `;

      card.querySelector(`[data-step-status="${idx}"]`).addEventListener('change', (e) => {
        step.status = e.target.value;
        renderPlaybookSteps();
      });
      card.querySelector(`[data-prepare-step="${idx}"]`).addEventListener('click', () => preparePlaybookStep(idx));
      card.querySelector(`[data-step-up="${idx}"]`).addEventListener('click', () => movePlaybookStep(idx, -1));
      card.querySelector(`[data-step-down="${idx}"]`).addEventListener('click', () => movePlaybookStep(idx, 1));
      card.querySelector(`[data-step-remove="${idx}"]`).addEventListener('click', () => removePlaybookStep(idx));

      list.append(card);
    });
  }

  function preparePlaybookStep(stepIndex) {
    const step = sessionState.playbookSteps[stepIndex];
    if (!step) return;
    step.status = 'in_progress';
    selectAgentManually(step.agentId);
    const input = byId('prompt-input');
    if (!input.value.trim() && step.suggestedPrompt) {
      input.value = step.suggestedPrompt;
    }
    input.focus();
    renderPlaybookSteps();
    showToast(`Prepared Step ${stepIndex + 1}: ${step.name}`);
  }

  function movePlaybookStep(index, direction) {
    const target = index + direction;
    if (target < 0 || target >= sessionState.playbookSteps.length) return;
    const temp = sessionState.playbookSteps[index];
    sessionState.playbookSteps[index] = sessionState.playbookSteps[target];
    sessionState.playbookSteps[target] = temp;
    renderPlaybookSteps();
  }

  function removePlaybookStep(index) {
    sessionState.playbookSteps.splice(index, 1);
    renderPlaybookSteps();
  }

  function addAgentToWorkflow(agentId) {
    const name = getAgentDisplayName(agentId);
    sessionState.playbookSteps.push({
      stepIndex: sessionState.playbookSteps.length,
      agentId: agentId,
      name: name,
      purpose: `Process with ${name}`,
      suggestedPrompt: `Task for ${name}: `,
      status: 'not_started',
    });
    switchProductivityTab('panel-playbooks');
    renderPlaybookSteps();
    showToast(`Added ${name} to workflow steps.`);
  }

  byId('add-step-btn').addEventListener('click', () => {
    const select = byId('add-step-agent-select');
    const agentId = select.value;
    if (agentId) addAgentToWorkflow(agentId);
  });

  // ==========================================
  // Productivity Layer: Context Kit Builder
  // ==========================================

  const MAX_KIT_CHARS = 16000;

  function addContextKitItem(type, label, content) {
    const text = String(content || '').trim();
    if (!text) {
      alert('Content is empty.');
      return;
    }
    const currentTotal = getContextKitTotalChars();
    if (currentTotal + text.length > MAX_KIT_CHARS) {
      alert(`Adding this item (${text.length} chars) would exceed the Context Kit budget of ${MAX_KIT_CHARS.toLocaleString()} characters.`);
      return;
    }

    const item = {
      id: 'kit_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
      type: type || 'note',
      label: label || 'Context Note',
      content: text,
      charCount: text.length,
    };
    sessionState.contextKit.push(item);
    renderContextKit();
    triggerReadinessEvaluation();
    showToast(`Added "${item.label}" to Context Kit.`);
  }

  function removeContextKitItem(itemId) {
    sessionState.contextKit = sessionState.contextKit.filter(item => item.id !== itemId);
    renderContextKit();
    triggerReadinessEvaluation();
  }

  function getContextKitTotalChars() {
    return sessionState.contextKit.reduce((sum, item) => sum + (item.charCount || 0), 0);
  }

  function renderContextKit() {
    const list = byId('kit-items-list');
    const countSpan = byId('kit-item-count');
    const budgetText = byId('kit-budget-text');
    const budgetBar = byId('kit-budget-bar');

    const totalChars = getContextKitTotalChars();
    if (countSpan) countSpan.textContent = sessionState.contextKit.length;
    if (budgetText) budgetText.textContent = `${totalChars.toLocaleString()} / ${MAX_KIT_CHARS.toLocaleString()} chars`;

    if (budgetBar) {
      const pct = Math.min(100, Math.round((totalChars / MAX_KIT_CHARS) * 100));
      budgetBar.style.width = pct + '%';
      if (pct > 90) budgetBar.className = 'budget-bar-fill danger';
      else if (pct > 70) budgetBar.className = 'budget-bar-fill warning';
      else budgetBar.className = 'budget-bar-fill';
    }

    if (!list) return;
    if (!sessionState.contextKit.length) {
      list.innerHTML = '<div class="muted" style="text-align:center; padding:16px; font-size:0.88rem;">No items in Context Kit. Add custom notes above or click "Add to Context Kit" on answers.</div>';
      return;
    }

    list.replaceChildren();
    sessionState.contextKit.forEach(item => {
      const row = document.createElement('div');
      row.className = 'context-kit-item';
      row.innerHTML = `
        <div style="display:grid; gap:2px; flex:1 1 auto; overflow:hidden;">
          <div style="display:flex; align-items:center; gap:8px;">
            <strong>${escapeHtml(item.label)}</strong>
            <span class="muted" style="font-size:0.75rem;">[${escapeHtml(item.type)}]</span>
            <span class="muted" style="font-size:0.75rem;">${item.charCount.toLocaleString()} chars</span>
          </div>
          <div class="muted" style="font-size:0.8rem; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">${escapeHtml(item.content.slice(0, 120))}</div>
        </div>
        <button class="secondary small" data-remove-kit="${item.id}" type="button">✕ Remove</button>
      `;
      row.querySelector(`[data-remove-kit="${item.id}"]`).addEventListener('click', () => removeContextKitItem(item.id));
      list.append(row);
    });
  }

  byId('add-kit-note-btn').addEventListener('click', () => {
    const labelInput = byId('kit-note-label');
    const contentInput = byId('kit-note-content');
    const label = labelInput.value.trim() || 'User Note';
    const content = contentInput.value.trim();
    if (!content) {
      alert('Please enter note content.');
      contentInput.focus();
      return;
    }
    addContextKitItem('note', label, content);
    labelInput.value = '';
    contentInput.value = '';
  });

  byId('clear-kit-btn').addEventListener('click', () => {
    sessionState.contextKit = [];
    renderContextKit();
    triggerReadinessEvaluation();
    showToast('Context Kit cleared.');
  });

  byId('insert-kit-btn').addEventListener('click', () => {
    if (!sessionState.contextKit.length) {
      alert('Context Kit is empty.');
      return;
    }
    const formatted = sessionState.contextKit.map(item => `### [${item.label}]\n${item.content}`).join('\n\n');
    const wrapper = `\n\n[Context Kit]\n${formatted}\n[/Context Kit]\n\n`;
    const input = byId('prompt-input');
    input.value = (input.value.trim() + wrapper).trim();
    input.focus();
    triggerReadinessEvaluation();
    showToast('Inserted Context Kit into prompt.');
    byId('composer').scrollIntoView({ behavior: 'smooth' });
  });

  byId('stage-kit-btn').addEventListener('click', () => {
    if (!sessionState.contextKit.length) {
      alert('Context Kit is empty.');
      return;
    }
    const formatted = sessionState.contextKit.map(item => `[${item.label}]: ${item.content}`).join(' | ');
    setStagedPriorContext({
      agentId: 'context_kit',
      agentName: 'Context Kit Builder',
      responseId: 'kit_' + Date.now(),
      summary: formatted.slice(0, 500),
    });
    showToast('Staged Context Kit as prior context.');
    byId('composer').scrollIntoView({ behavior: 'smooth' });
  });

  // ==========================================
  // Productivity Layer: Request Readiness Coach
  // ==========================================

  function triggerReadinessEvaluation() {
    if (sessionState.readinessDebounceTimer) {
      clearTimeout(sessionState.readinessDebounceTimer);
    }
    sessionState.readinessDebounceTimer = setTimeout(runReadinessEvaluation, 200);
  }

  async function runReadinessEvaluation() {
    const input = byId('prompt-input');
    if (!input) return;
    const text = input.value.trim();
    const explicitAgentId = byId('opt-agent-override') ? byId('opt-agent-override').value || null : null;
    const kitChars = getContextKitTotalChars();

    const charIndicator = byId('char-budget-indicator');
    if (charIndicator) charIndicator.textContent = `${text.length} chars`;

    try {
      const res = await apiFetch('/api/assistant/productivity/readiness', {
        method: 'POST',
        body: JSON.stringify({
          text: text,
          selectedAgentId: explicitAgentId,
          contextKitChars: kitChars,
          hasReviewedSources: false,
          sourceCount: 0,
          selectedProject: null,
        })
      });

      sessionState.currentReadiness = res;
      updateReadinessUI(res);
    } catch (err) {
      console.warn('Readiness check failed:', err);
    }
  }

  function updateReadinessUI(readiness) {
    const card = byId('readiness-coach-card');
    const pill = byId('readiness-status-pill');
    const reason = byId('readiness-reason-text');
    const hsBanner = byId('coach-high-stakes-banner');
    const sugBox = byId('readiness-suggestion-box');
    const sugText = byId('readiness-suggestion-text');

    if (!card || !pill || !reason) return;

    card.className = `readiness-coach-card ${readiness.status || 'ready'}`;
    pill.className = `pill ${readiness.badgeClass || 'succeeded'}`;
    pill.textContent = readiness.statusDisplay || 'Ready';
    reason.textContent = readiness.reason || '';

    if (readiness.isHighStakes) {
      hsBanner.style.display = 'block';
      hsBanner.innerHTML = `<strong>High-Stakes Category (${escapeHtml(readiness.highStakesCategory || 'Sensitive')}):</strong> ${escapeHtml(readiness.highStakesWarning || 'Review safety boundaries before acting.')}`;
    } else {
      hsBanner.style.display = 'none';
    }

    if (readiness.suggestion) {
      sugBox.style.display = 'flex';
      sugText.textContent = `Suggestion: ${readiness.suggestion.slice(0, 160)}...`;
      sessionState.activeSuggestion = readiness.suggestion;
    } else {
      sugBox.style.display = 'none';
      sessionState.activeSuggestion = null;
    }
  }

  byId('apply-suggestion-btn').addEventListener('click', () => {
    if (!sessionState.activeSuggestion) return;
    const input = byId('prompt-input');
    const current = input.value.trim();
    if (current) {
      input.value = `${current}\n\n${sessionState.activeSuggestion}`;
    } else {
      input.value = sessionState.activeSuggestion;
    }
    input.focus();
    triggerReadinessEvaluation();
    showToast('Applied scaffolding suggestion to prompt.');
  });

  byId('prompt-input').addEventListener('input', triggerReadinessEvaluation);

  // ==========================================
  // System Status & Initialization
  // ==========================================

  // Load system, generation status, and registered projects
  async function loadSystemStatus() {
    try {
      const genStatus = await apiFetch('/api/generation/status');
      sessionState.generationStatus = genStatus;
      const pill = byId('generation-pill');
      if (genStatus.enabled) {
        pill.className = 'pill active';
        pill.textContent = `Local Generation: Active (${genStatus.modelName || 'Ollama'})`;
      } else {
        pill.className = 'pill inactive';
        pill.textContent = 'Local Generation: Off (Deterministic)';
      }
    } catch (err) {
      byId('generation-pill').textContent = 'Local Generation: Unavailable';
    }

    try {
      const catalog = await apiFetch('/api/assistant/productivity/agents');
      if (Array.isArray(catalog) && catalog.length) {
        sessionState.catalogAgents = catalog;
        populateAgentOverrideDropdown(catalog);
        populateAddStepAgentDropdown(catalog);
        renderCommandCenter();
        byId('agents-pill').textContent = `${catalog.length} Response Agents Ready`;
      } else {
        const fallbackCatalog = await apiFetch('/agents/local-response-agents/discovery');
        if (fallbackCatalog && fallbackCatalog.agents) {
          sessionState.catalogAgents = fallbackCatalog.agents;
          populateAgentOverrideDropdown(fallbackCatalog.agents);
          populateAddStepAgentDropdown(fallbackCatalog.agents);
          renderCommandCenter();
          byId('agents-pill').textContent = `${fallbackCatalog.agents.length} Response Agents Ready`;
        }
      }
    } catch (err) {
      byId('agents-pill').textContent = 'Agents Discovery Error';
    }

    try {
      const projects = await apiFetch('/projects');
      if (Array.isArray(projects)) {
        sessionState.projects = projects;
      }
    } catch (err) {
      sessionState.projects = [];
    }

    await loadPlaybooks();
    triggerReadinessEvaluation();
  }

  // Handle composer submission
  async function handleSubmit(previewOnly = false) {
    if (sessionState.isGenerating) return;
    const input = byId('prompt-input');
    const promptText = input.value.trim();
    if (!promptText) {
      alert('Please enter a request.');
      input.focus();
      return;
    }

    try {
      byId('submit-btn').disabled = true;
      byId('preview-route-btn').disabled = true;

      const analysis = await analyzeRoute(promptText);

      if (previewOnly || analysis.route.is_ambiguous || !analysis.readiness.is_ready) {
        showStagingDrawer(analysis);
      } else {
        // Direct transparent execution
        await runAgent(promptText, analysis.route.selected_agent_id, analysis.route, analysis.prepared_payload);
      }
    } catch (err) {
      alert(`Routing analysis failed: ${err.message}`);
    } finally {
      if (!sessionState.isGenerating) {
        byId('submit-btn').disabled = false;
        byId('preview-route-btn').disabled = false;
      }
    }
  }

  byId('submit-btn').addEventListener('click', () => handleSubmit(false));
  byId('preview-route-btn').addEventListener('click', () => handleSubmit(true));

  // Enter to send (Shift+Enter for newline)
  byId('prompt-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(false);
    }
  });

  // Starter chips
  document.querySelectorAll('.starter-chip').forEach(btn => {
    btn.addEventListener('click', () => {
      byId('prompt-input').value = btn.getAttribute('data-prompt');
      byId('prompt-input').focus();
      triggerReadinessEvaluation();
    });
  });

  // Initialization
  loadSystemStatus();
})();
</script>
</body>
</html>"""
    html = html.replace("/* PRODUCTIVITY_STYLES_PLACEHOLDER */", productivity_styles() + "\n" + results_dashboard_styles())
    html = html.replace("<!-- PRODUCTIVITY_PANELS_PLACEHOLDER -->", productivity_html_panels() + "\n" + results_dashboard_html_panels())
    html = html.replace("<!-- PRODUCTIVITY_READINESS_COACH_PLACEHOLDER -->", productivity_readiness_coach_html())
    return html
