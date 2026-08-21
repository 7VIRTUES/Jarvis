from __future__ import annotations


def unified_assistant_html() -> str:
    return """<!doctype html>
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
      max-width: 860px;
      margin: 0 auto;
    }
    .starter-chip {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 6px 14px;
      font-size: 0.88rem;
      cursor: pointer;
      color: var(--accent-dark);
      font-weight: 500;
      transition: all 0.15s ease;
    }
    .starter-chip:hover {
      background: var(--accent-light);
      border-color: var(--accent);
      transform: translateY(-1px);
    }
    .turn {
      display: grid;
      gap: 12px;
      padding: 16px;
      border-radius: 9px;
      border: 1px solid var(--border);
      background: var(--surface);
    }
    .turn.user-turn {
      background: #f8fafc;
      border-color: #cbd5e1;
      border-left: 5px solid #64748b;
    }
    .turn.jarvis-turn {
      background: var(--surface);
      border-left: 5px solid var(--accent);
    }
    .turn-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-size: 0.85rem;
      color: var(--muted);
      border-bottom: 1px solid #edf2f7;
      padding-bottom: 8px;
    }
    .turn-title {
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .turn-body {
      font-size: 1rem;
      line-height: 1.6;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }
    .route-info-card {
      background: #f0f7ff;
      border: 1px solid #bfdbfe;
      border-radius: 6px;
      padding: 10px 14px;
      display: grid;
      gap: 6px;
      font-size: 0.9rem;
    }
    .route-info-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }
    .route-rationale {
      color: #334155;
      font-size: 0.88rem;
    }
    .response-section {
      margin-top: 10px;
    }
    .response-section h4 {
      margin: 12px 0 6px;
      font-size: 0.95rem;
      color: var(--accent-dark);
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .key-points-list {
      margin: 6px 0;
      padding-left: 20px;
    }
    .key-points-list li {
      margin-bottom: 4px;
    }
    .citations-card {
      background: #fafaf9;
      border: 1px solid #e7e5e4;
      border-radius: 6px;
      padding: 10px 14px;
      margin-top: 10px;
      font-size: 0.88rem;
    }
    .turn-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid #edf2f7;
    }
    button, .button {
      font: inherit;
      border: 1px solid var(--accent);
      border-radius: 5px;
      padding: 8px 14px;
      background: var(--accent);
      color: #fff;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 0.9rem;
      transition: background 0.15s ease;
    }
    button:hover {
      background: var(--accent-dark);
    }
    button.secondary {
      background: #fff;
      color: var(--accent);
      border-color: var(--border);
    }
    button.secondary:hover {
      background: #f8fafc;
      border-color: var(--accent);
    }
    button.small {
      padding: 4px 9px;
      font-size: 0.82rem;
    }
    button.warning {
      background: var(--warn);
      border-color: var(--warn);
    }
    button:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }
    .composer-panel {
      position: sticky;
      bottom: 12px;
      background: var(--surface);
      border: 2px solid #b4c9de;
      border-radius: 9px;
      padding: 14px;
      box-shadow: 0 6px 20px rgba(15, 35, 55, 0.12);
      display: grid;
      gap: 10px;
      z-index: 5;
    }
    .composer-textarea {
      width: 100%;
      min-height: 80px;
      max-height: 220px;
      resize: vertical;
      padding: 10px 12px;
      border: 1px solid #94a3b8;
      border-radius: 6px;
      font: inherit;
      line-height: 1.45;
    }
    .composer-textarea:focus {
      outline: 3px solid var(--focus);
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
      gap: 5px;
      cursor: pointer;
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
    .staged-context-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 6px;
      padding: 6px 12px;
      font-size: 0.85rem;
      color: #166534;
    }
    .drawer {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 16px;
      display: grid;
      gap: 12px;
      margin-top: 10px;
    }
    .alternatives-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 8px;
    }
    .alt-card {
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 10px;
      background: var(--soft);
      display: grid;
      gap: 4px;
      font-size: 0.86rem;
    }
    .alt-card strong {
      color: var(--accent-dark);
    }
    details summary {
      cursor: pointer;
      font-weight: 600;
      color: var(--accent);
      padding: 4px 0;
    }
    pre.json-viewer {
      background: var(--code-bg);
      color: #e2e8f0;
      padding: 12px;
      border-radius: 6px;
      font-size: 0.82rem;
      overflow-x: auto;
      max-height: 320px;
      margin: 8px 0 0;
    }
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #1e293b;
      color: #fff;
      padding: 12px 18px;
      border-radius: 7px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.25);
      z-index: 100;
      font-size: 0.9rem;
      display: none;
      align-items: center;
      gap: 8px;
    }
    .toast.show { display: flex; }
    @media (max-width: 768px) {
      .composer-options { flex-direction: column; align-items: stretch; }
      .options-left, .options-right { width: 100%; justify-content: space-between; }
    }
  </style>
</head>
<body>
<header>
  <div class="header-inner">
    <div>
      <h1>Jarvis Unified Assistant</h1>
      <div class="tagline">Deterministic routing & execution over 37 local response agents · Session-only memory</div>
    </div>
    <nav class="header-nav" aria-label="Main Navigation">
      <a class="active" href="/assistant">Assistant</a>
      <a href="/dashboard">Dashboard</a>
      <a href="/dashboard#local-response-agents-workbench">Workbench</a>
      <a href="/memory">Memory Center</a>
      <a href="/knowledge">Knowledge Library</a>
      <a href="/models">Models Center</a>
    </nav>
  </div>
</header>

<main>
  <div class="status-bar" id="system-status-bar">
    <div style="display:flex; flex-wrap:wrap; align-items:center; gap:8px;">
      <span class="pill active" id="session-pill">Session-Only: In-Memory</span>
      <span class="pill inactive" id="generation-pill">Local Generation: Checking...</span>
      <span class="pill inactive" id="agents-pill">37 Response Agents Ready</span>
    </div>
    <div>
      <span class="muted" style="font-size:0.84rem;">No persistent DB transcript · No external APIs · Auditable</span>
    </div>
  </div>

  <div class="banner warning" id="boundary-banner" style="display:block;">
    <strong>Safe Local Supervisor Boundary:</strong>
    Jarvis provides manual-input, response-only assistance using deterministic and local Ollama execution.
    No automatic actions, account access, booking, purchases, email/calendar posting, or emergency filings are performed.
  </div>

  <section class="panel" style="padding:14px;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
      <h2 style="margin:0; font-size:1.15rem; color:var(--accent-dark);">Conversation</h2>
      <div style="display:flex; gap:8px;">
        <button id="clear-session-btn" class="secondary small" type="button">Clear Transcript</button>
        <button id="view-result-board-btn" class="secondary small" type="button">Session Result Board (<span id="result-board-count">0</span>)</button>
      </div>
    </div>

    <div class="chat-container" id="chat-container">
      <div class="empty-state" id="empty-state">
        <h3>How can Jarvis assist you today?</h3>
        <p>Enter a natural language question or request. Jarvis will deterministically select the most suitable local agent from its 37 specialized capabilities, prepare the request payload, and execute it under your supervision.</p>
        <div class="starter-chips">
          <button class="starter-chip" data-prompt="Draft a weekly meal plan and grocery list for quick healthy dinners">Meal & Grocery Plan</button>
          <button class="starter-chip" data-prompt="Organize my document checklist and questions for an upcoming visa/immigration appointment">Immigration Checklist</button>
          <button class="starter-chip" data-prompt="Help me brainstorm and compare 3 monetization ideas for a local software tool">Business Tradeoffs</button>
          <button class="starter-chip" data-prompt="Create a beginner home workout routine focusing on mobility and strength">Home Workout Routine</button>
          <button class="starter-chip" data-prompt="Create an emergency preparedness car kit checklist for winter travel">Car Emergency Kit</button>
          <button class="starter-chip" data-prompt="Review this project description for clarity and safety wording">Draft Review</button>
          <button class="starter-chip" data-prompt="Troubleshoot why my local database connection timed out">Troubleshooting Triage</button>
          <button class="starter-chip" data-prompt="Create a study roadmap to learn Python for robotics in 8 weeks">Study Roadmap</button>
        </div>
      </div>
    </div>
  </section>

  <!-- Route Preview / Execution Staging Drawer -->
  <div class="drawer" id="staging-drawer" style="display:none;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Route Preview & Readiness Review</h3>
      <button class="secondary small" id="close-drawer-btn" type="button">Close Preview</button>
    </div>

    <div id="drawer-high-stakes" style="display:none;" class="banner danger"></div>

    <div class="route-info-card" id="drawer-route-card">
      <div class="route-info-header">
        <strong>Recommended Agent:</strong>
        <span id="drawer-agent-name" style="font-weight:700;"></span>
        <span class="pill" id="drawer-confidence-pill"></span>
        <span class="muted" id="drawer-category"></span>
      </div>
      <div class="route-rationale" id="drawer-rationale"></div>
    </div>

    <div id="drawer-ambiguity-notice" class="banner warning" style="display:none;">
      <strong>Ambiguous Route:</strong> Several agents matched this request closely. Review alternative agents below or choose one explicitly.
    </div>

    <div id="drawer-alternatives-container" style="display:grid; gap:6px;">
      <div style="font-weight:600; font-size:0.88rem; color:var(--muted);">Alternative Agent Candidates:</div>
      <div class="alternatives-grid" id="drawer-alternatives-grid"></div>
    </div>

    <div style="display:flex; align-items:center; gap:8px; font-size:0.9rem;">
      <strong>Payload Readiness:</strong>
      <span class="pill" id="drawer-readiness-pill">Ready</span>
      <span class="muted" id="drawer-readiness-notes"></span>
    </div>

    <details id="drawer-payload-details">
      <summary>Inspect / Edit Prepared Agent Request Payload (JSON)</summary>
      <textarea id="drawer-payload-editor" style="width:100%; min-height:140px; font-family:monospace; font-size:0.85rem; padding:8px; margin-top:8px; border:1px solid #cbd5e1; border-radius:5px;"></textarea>
      <div style="font-size:0.82rem; color:var(--muted); margin-top:4px;">You can modify the JSON payload before executing.</div>
    </details>

    <div style="display:flex; justify-content:flex-end; gap:8px; margin-top:8px;">
      <button id="drawer-cancel-btn" class="secondary" type="button">Cancel</button>
      <button id="drawer-execute-btn" type="button">Execute Selected Agent</button>
    </div>
  </div>

  <!-- Session Result Board Drawer -->
  <div class="drawer" id="result-board-drawer" style="display:none;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Session Result Board (In-Memory)</h3>
      <button class="secondary small" id="close-result-board-btn" type="button">Close</button>
    </div>
    <p class="muted" style="margin:0; font-size:0.88rem;">Results saved during this active browser session for comparison. Cleared upon page refresh.</p>
    <div id="result-board-items" style="display:grid; gap:10px; max-height:400px; overflow-y:auto;">
      <div class="empty-state" style="padding:20px;">No results added to Result Board yet.</div>
    </div>
  </div>

  <!-- Composer Area -->
  <div class="composer-panel" id="composer">
    <div id="staged-prior-context-bar" class="staged-context-bar" style="display:none;">
      <span><strong>Prior Context Attached:</strong> <span id="staged-prior-summary"></span></span>
      <button id="clear-prior-context-btn" class="secondary small" type="button" style="padding:2px 6px;">Remove</button>
    </div>

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
    generationStatus: null,
    stagedAnalysis: null,
  };

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

  // Load system and generation status
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

  // Core execution flow
  async function runAgent(promptText, agentId, routeInfo, payload) {
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

    // Disable composer during execution
    byId('submit-btn').disabled = true;
    byId('preview-route-btn').disabled = true;
    byId('prompt-input').disabled = true;

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
      };
      sessionState.transcript.push(jarvisTurn);

      // Consume staged prior context after successful use
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
      byId('submit-btn').disabled = false;
      byId('preview-route-btn').disabled = false;
      byId('prompt-input').disabled = false;
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
          const gen = resp.generation || resp.generatedResponse || {};
          const isGenerated = !!resp.generatedResponse || (resp.actualMode && resp.actualMode !== 'deterministic');
          const primaryText = resp.generatedResponse ? resp.generatedResponse.response : (resp.summary || resp.brief || resp.plan || resp.draft || resp.response || JSON.stringify(resp, null, 2));

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
                ${resp.actualMode ? `<span class="pill ${resp.actualMode === 'deterministic' ? 'inactive' : 'active'}">${escapeHtml(resp.actualMode)}</span>` : ''}
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

            <div class="turn-body">${escapeHtml(primaryText)}</div>

            ${keyPointsHtml}
            ${citationsHtml}
            ${safetyNotesHtml}

            <div class="turn-actions">
              <button class="secondary small" type="button" data-action="use-prior" data-turn-idx="${index}">Use as prior context for next message</button>
              <button class="secondary small" type="button" data-action="add-board" data-turn-idx="${index}">Add to Result Board</button>
              <button class="secondary small" type="button" data-action="toggle-json" data-turn-idx="${index}">Inspect Metadata & JSON</button>
            </div>

            <div class="json-panel" id="json-panel-${index}" style="display:none; margin-top:8px;">
              <pre class="json-viewer">${escapeHtml(JSON.stringify(resp, null, 2))}</pre>
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

          turnDiv.querySelector(`[data-action="toggle-json"]`).addEventListener('click', () => {
            const p = byId(`json-panel-${index}`);
            p.style.display = p.style.display === 'none' ? 'block' : 'none';
          });
        }
      }

      container.append(turnDiv);
    });

    // Auto scroll to bottom
    container.lastElementChild?.scrollIntoView({ behavior: 'smooth' });
  }

  // Result Board in session memory
  function addToResultBoard(jarvisTurn) {
    const resp = jarvisTurn.response || {};
    const primaryText = resp.generatedResponse ? resp.generatedResponse.response : (resp.summary || resp.brief || resp.plan || resp.draft || resp.response || '');
    const entry = {
      id: 'rb_' + Date.now(),
      timestamp: jarvisTurn.timestamp,
      agentId: jarvisTurn.agentId,
      agentName: jarvisTurn.route ? jarvisTurn.route.selected_display_name : jarvisTurn.agentId,
      category: jarvisTurn.route ? jarvisTurn.route.category : 'General',
      text: primaryText,
      fullResponse: resp,
    };
    sessionState.resultBoard.push(entry);
    byId('result-board-count').textContent = sessionState.resultBoard.length;
    showToast(`Added result from ${entry.agentName} to session Result Board.`);
    renderResultBoard();
  }

  function renderResultBoard() {
    const container = byId('result-board-items');
    if (!sessionState.resultBoard.length) {
      container.innerHTML = '<div class="empty-state" style="padding:20px;">No results added to Result Board yet.</div>';
      return;
    }
    container.replaceChildren();
    sessionState.resultBoard.forEach((item, idx) => {
      const card = document.createElement('div');
      card.className = 'panel';
      card.style.padding = '10px';
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <strong>${escapeHtml(item.agentName)} <span class="muted" style="font-size:0.8rem;">[${escapeHtml(item.category)}]</span></strong>
          <span class="muted" style="font-size:0.8rem;">${escapeHtml(item.timestamp)}</span>
        </div>
        <div style="font-size:0.88rem; max-height:100px; overflow-y:auto; white-space:pre-wrap;">${escapeHtml(item.text)}</div>
        <div style="margin-top:8px; display:flex; gap:6px;">
          <button class="secondary small" data-rb-prior="${idx}">Use as Prior Context</button>
          <button class="secondary small" data-rb-remove="${idx}">Remove</button>
        </div>
      `;
      card.querySelector(`[data-rb-prior="${idx}"]`).addEventListener('click', () => {
        setStagedPriorContext({
          agentId: item.agentId,
          agentName: item.agentName,
          responseId: (item.fullResponse.responseContext && item.fullResponse.responseContext.responseId) || '',
          summary: item.text,
        });
        byId('result-board-drawer').style.display = 'none';
        byId('composer').scrollIntoView({ behavior: 'smooth' });
      });
      card.querySelector(`[data-rb-remove="${idx}"]`).addEventListener('click', () => {
        sessionState.resultBoard.splice(idx, 1);
        byId('result-board-count').textContent = sessionState.resultBoard.length;
        renderResultBoard();
      });
      container.append(card);
    });
  }

  byId('view-result-board-btn').addEventListener('click', () => {
    const drawer = byId('result-board-drawer');
    drawer.style.display = drawer.style.display === 'none' ? 'grid' : 'none';
    if (drawer.style.display === 'grid') renderResultBoard();
  });
  byId('close-result-board-btn').addEventListener('click', () => {
    byId('result-board-drawer').style.display = 'none';
  });

  byId('clear-session-btn').addEventListener('click', () => {
    if (confirm('Clear the current conversation transcript from memory? (This cannot be undone)')) {
      sessionState.transcript = [];
      setStagedPriorContext(null);
      renderTranscript();
      showToast('Conversation transcript cleared.');
    }
  });

  // Handle composer submission
  async function handleSubmit(previewOnly = false) {
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
      byId('submit-btn').disabled = false;
      byId('preview-route-btn').disabled = false;
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
    });
  });

  // Initialization
  loadSystemStatus();
})();
</script>
</body>
</html>"""
