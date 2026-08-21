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

  <!-- Staged Prior Context Indicator -->
  <div id="staged-prior-context-bar" class="staged-prior-bar" style="display:none;">
    <span><strong>Staged Prior Context:</strong> <span id="staged-prior-summary"></span></span>
    <button id="clear-prior-context-btn" class="secondary small" style="border-color:#d8b4fe;" type="button">Dismiss</button>
  </div>

  <!-- Conversation Transcript Area -->
  <section id="chat-container" class="chat-container">
    <div id="empty-state" class="empty-state">
      <h3>Welcome to the Unified Jarvis Assistant</h3>
      <p>Enter any natural-language request below. Jarvis will deterministically inspect your request, recommend the best specialized response agent, explain the route transparently, and execute locally on your machine.</p>
      <div class="starter-chips">
        <button class="starter-chip" data-prompt="Help me plan a 3-month strength training and nutrition routine">Fitness & Nutrition Plan</button>
        <button class="starter-chip" data-prompt="Draft an executive summary of our Q3 product roadmap update">Drafting Executive Brief</button>
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
      };
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
    });
  });

  // Initialization
  loadSystemStatus();
})();
</script>
</body>
</html>"""
