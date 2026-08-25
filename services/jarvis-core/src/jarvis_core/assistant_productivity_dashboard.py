from __future__ import annotations


def productivity_styles() -> str:
    return """
    /* ========================================================
       Assistant Productivity Layer Styles (v0.1E Pass 9)
       ======================================================== */
    .prod-toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 8px 12px;
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 2px;
    }
    .prod-tabs {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .prod-tab-btn {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      color: #334155;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }
    .prod-tab-btn:hover {
      background: #f1f5f9;
      border-color: var(--accent);
      color: var(--accent);
    }
    .prod-tab-btn.active {
      background: var(--accent);
      border-color: var(--accent-dark);
      color: #ffffff;
    }

    /* Collapsible Productivity Panels */
    .productivity-panel {
      display: none;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: 0 2px 8px rgba(15, 35, 55, 0.05);
      animation: fadeIn 0.18s ease-in-out;
    }
    .productivity-panel.open {
      display: grid;
      gap: 14px;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Command Center Styles */
    .cc-filter-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 7px;
    }
    .cc-search-input {
      flex: 1 1 200px;
      padding: 6px 10px;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      font: inherit;
      font-size: 0.88rem;
      background: #fff;
    }
    .cc-filter-select {
      padding: 6px 8px;
      border: 1px solid #cbd5e1;
      border-radius: 5px;
      font: inherit;
      font-size: 0.88rem;
      background: #fff;
    }
    .cc-pinned-section, .cc-recent-section {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: #f1f5f9;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      font-size: 0.84rem;
    }
    .cc-chip-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }
    .cc-chip {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      padding: 3px 8px;
      border-radius: 14px;
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text);
      display: inline-flex;
      align-items: center;
      gap: 5px;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .cc-chip:hover {
      background: var(--accent-light);
      border-color: var(--accent);
      color: var(--accent-dark);
    }
    .cc-chip.pinned {
      background: #fffbeb;
      border-color: #fde68a;
      color: #92400e;
    }
    .cc-chip .unpin-icon {
      font-size: 0.75rem;
      color: #94a3b8;
      cursor: pointer;
    }
    .cc-chip .unpin-icon:hover {
      color: var(--danger);
    }

    /* Agent Grid */
    .cc-agent-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 12px;
      max-height: 480px;
      overflow-y: auto;
      padding-right: 4px;
    }
    .cc-agent-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 7px;
      padding: 12px;
      display: grid;
      gap: 8px;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .cc-agent-card:hover {
      border-color: var(--accent);
      box-shadow: 0 2px 6px rgba(21, 94, 155, 0.12);
    }
    .cc-agent-card.high-stakes-card {
      border-left: 4px solid #ea580c;
    }
    .cc-card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 6px;
    }
    .cc-card-name {
      font-weight: 700;
      font-size: 0.92rem;
      color: var(--accent-dark);
    }
    .cc-card-cat {
      font-size: 0.76rem;
      color: var(--muted);
      background: #f1f5f9;
      padding: 2px 6px;
      border-radius: 4px;
      white-space: nowrap;
    }
    .cc-card-desc {
      font-size: 0.83rem;
      color: #334155;
      line-height: 1.4;
    }
    .cc-card-badges {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      font-size: 0.74rem;
    }
    .cc-badge {
      background: #e2e8f0;
      color: #475569;
      padding: 1px 5px;
      border-radius: 3px;
    }
    .cc-badge.hs {
      background: #ffedd5;
      color: #9a3412;
      font-weight: 600;
    }
    .cc-card-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
      margin-top: 4px;
      padding-top: 6px;
      border-top: 1px solid #f1f5f9;
    }
    .cc-card-actions button {
      padding: 3px 8px;
      font-size: 0.78rem;
    }

    /* Playbooks Styles */
    .playbook-steps-list {
      display: grid;
      gap: 10px;
    }
    .playbook-step-card {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 7px;
      padding: 12px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .playbook-step-card.active-step {
      background: #eff6ff;
      border-color: #93c5fd;
      border-left: 5px solid var(--accent);
    }
    .playbook-step-card.completed-step {
      background: #f0fdf4;
      border-color: #bbf7d0;
      border-left: 5px solid #16a34a;
    }
    .step-left {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1 1 300px;
    }
    .step-num-badge {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--accent);
      color: #fff;
      font-weight: 700;
      font-size: 0.85rem;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .step-details {
      display: grid;
      gap: 2px;
    }
    .step-name {
      font-weight: 700;
      font-size: 0.92rem;
      color: var(--text);
    }
    .step-purpose {
      font-size: 0.82rem;
      color: var(--muted);
    }
    .step-right {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }

    /* Context Kit Builder Styles */
    .context-kit-items-list {
      display: grid;
      gap: 8px;
      max-height: 260px;
      overflow-y: auto;
    }
    .context-kit-item {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      padding: 8px 12px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      font-size: 0.86rem;
    }
    .kit-budget-meter {
      display: grid;
      gap: 4px;
      font-size: 0.84rem;
      color: var(--muted);
    }
    .budget-bar-track {
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      overflow: hidden;
    }
    .budget-bar-fill {
      height: 100%;
      background: var(--accent);
      width: 0%;
      transition: width 0.2s ease, background 0.2s ease;
    }
    .budget-bar-fill.warning {
      background: #f59e0b;
    }
    .budget-bar-fill.danger {
      background: #ef4444;
    }

    /* Request Readiness Coach Bar */
    .readiness-coach-card {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 7px;
      padding: 10px 14px;
      display: grid;
      gap: 8px;
      margin-bottom: 8px;
      transition: border-color 0.2s ease;
    }
    .readiness-coach-card.ready {
      border-left: 5px solid #16a34a;
      background: #f0fdf4;
    }
    .readiness-coach-card.needs_context, .readiness-coach-card.ambiguous_route {
      border-left: 5px solid #d97706;
      background: #fffbeb;
    }
    .readiness-coach-card.needs_input, .readiness-coach-card.needs_project {
      border-left: 5px solid #dc2626;
      background: #fef2f2;
    }
    .readiness-coach-card.high_stakes_source_gap {
      border-left: 5px solid #ea580c;
      background: #fff7ed;
    }
    .readiness-top-row {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      font-size: 0.86rem;
    }
    .readiness-reason-text {
      font-size: 0.88rem;
      color: #1e293b;
      line-height: 1.4;
    }
    .readiness-suggestion-box {
      background: #ffffff;
      border: 1px dashed #cbd5e1;
      border-radius: 5px;
      padding: 8px 10px;
      font-size: 0.84rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }

    /* Boundaries Modal */
    .boundaries-modal-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      z-index: 200;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .boundaries-modal-backdrop.open {
      display: flex;
    }
    .boundaries-modal-card {
      background: #ffffff;
      border-radius: 9px;
      max-width: 600px;
      width: 100%;
      max-height: 85vh;
      overflow-y: auto;
      padding: 20px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
      display: grid;
      gap: 14px;
    }
    """


def productivity_html_panels() -> str:
    return """
  <!-- Productivity Layer Toolbar (Tabs) -->
  <section class="prod-toolbar" aria-label="Productivity workspace helpers">
    <div class="prod-tabs">
      <button type="button" class="prod-tab-btn" id="tab-command-center" data-panel="panel-command-center">
        ⚡ Command Center (37)
      </button>
      <button type="button" class="prod-tab-btn" id="tab-playbooks" data-panel="panel-playbooks">
        📋 Playbooks
      </button>
      <button type="button" class="prod-tab-btn" id="tab-context-kit" data-panel="panel-context-kit">
        🧰 Context Kit (<span id="kit-item-count">0</span>)
      </button>
      <button type="button" class="prod-tab-btn" id="tab-result-board" data-panel="panel-result-board">
        📊 Result Board (<span id="rb-tab-count">0</span>)
      </button>
      <button type="button" class="prod-tab-btn" id="tab-comparison" data-panel="panel-comparison">
        ⚖️ Comparison (<span id="cmp-tab-count">0</span>)
      </button>
      <button type="button" class="prod-tab-btn" id="tab-sources" data-panel="panel-sources">
        🌐 Sources (<span id="sources-tab-count">0</span>)
      </button>
      <button type="button" class="prod-tab-btn" id="tab-decision-composer" data-panel="panel-decision-composer-wrap">
        🎯 Decision Composer
      </button>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
      <span id="manual-override-indicator" class="pill override" style="display:none;">
        Manual Route: <strong id="manual-override-agent-name"></strong>
        <button id="clear-manual-override-btn" class="secondary small" style="margin-left:4px; padding:1px 5px;" type="button">✕ Auto</button>
      </span>
    </div>
  </section>

  <!-- PANEL 1: Agent Command Center -->
  <section class="productivity-panel" id="panel-command-center">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Agent Command Center</h3>
      <span class="muted" style="font-size:0.84rem;">Exposing all 37 canonical response agents · Local-only · Manual input only</span>
    </div>

    <!-- Filter & Search Bar -->
    <div class="cc-filter-bar">
      <input type="search" id="cc-search-input" class="cc-search-input" placeholder="Search by name, category, capabilities, keywords...">
      <select id="cc-category-filter" class="cc-filter-select">
        <option value="">All Categories</option>
        <option value="Coding/Core">Coding / Core (12)</option>
        <option value="Health/Food/Home">Health / Food / Home (3)</option>
        <option value="Safety/Emergency">Safety / Emergency (3)</option>
        <option value="Creativity/Hobbies">Creativity / Hobbies (3)</option>
        <option value="Knowledge/Coordinator">Knowledge / Coordinator (2)</option>
        <option value="Life/Admin">Life / Admin (4)</option>
        <option value="Social/Family">Social / Family (4)</option>
        <option value="School/Career">School / Career (4)</option>
        <option value="Finance/Housing/Travel">Finance / Housing / Travel (2)</option>
      </select>
      <label class="toggle-label" style="font-size:0.85rem;">
        <input type="checkbox" id="cc-high-stakes-filter">
        <span>High-Stakes Only</span>
      </label>
      <label class="toggle-label" style="font-size:0.85rem;">
        <input type="checkbox" id="cc-pinned-filter">
        <span>Pinned Only</span>
      </label>
    </div>

    <!-- Pinned Agents Quick Row -->
    <div class="cc-pinned-section" id="cc-pinned-section" style="display:none;">
      <strong>📌 Pinned Agents:</strong>
      <div class="cc-chip-row" id="cc-pinned-chips"></div>
    </div>

    <!-- Recent Agents Quick Row -->
    <div class="cc-recent-section" id="cc-recent-section" style="display:none;">
      <strong>🕒 Recent Agents:</strong>
      <div class="cc-chip-row" id="cc-recent-chips"></div>
    </div>

    <!-- Agent Cards Grid -->
    <div class="cc-agent-grid" id="cc-agent-grid">
      <!-- Injected via JavaScript from canonical discovery catalog -->
    </div>
  </section>

  <!-- PANEL 2: Playbooks & Manual Workflows -->
  <section class="productivity-panel" id="panel-playbooks">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <div>
        <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Manual Workflow Playbooks (<span id="wf-step-count">0</span> / 8 steps)</h3>
        <p class="muted" style="margin:2px 0 0; font-size:0.84rem;">Multi-step deliberate thinking patterns. Step execution, input staging, and output attachment are strictly manual.</p>
      </div>
      <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
        <select id="playbook-select" class="cc-filter-select">
          <!-- Built-in playbooks injected via JS -->
        </select>
        <button id="reset-playbook-btn" class="secondary small" type="button">Reset Playbook</button>
        <button id="open-wf-packet-btn" class="small" type="button">📋 Workflow Packet</button>
      </div>
    </div>

    <!-- Workflow Progress & Status Header -->
    <div class="wf-progress-container">
      <div id="playbook-description" class="muted" style="font-size:0.88rem;"></div>

      <div class="wf-metric-grid">
        <span class="wf-metric-pill">Total: <strong id="wf-stat-total">0</strong></span>
        <span class="wf-metric-pill">Completed: <strong id="wf-stat-completed">0</strong></span>
        <span class="wf-metric-pill">In Progress: <strong id="wf-stat-in-progress">0</strong></span>
        <span class="wf-metric-pill">Not Started: <strong id="wf-stat-not-started">0</strong></span>
        <span class="wf-metric-pill">Needs Review: <strong id="wf-stat-needs-review">0</strong></span>
        <span class="wf-metric-pill">Outputs Attached: <strong id="wf-stat-attached">0</strong></span>
        <span class="wf-metric-pill">Current: <strong id="wf-current-step-label">None</strong></span>
        <span class="wf-metric-pill">Session Sources: <strong id="wf-stat-sources">0</strong></span>
        <span class="wf-metric-pill">Context Kit: <strong id="wf-stat-kit">0</strong></span>
      </div>

      <div class="wf-progress-bar-track">
        <div class="wf-progress-bar-fill" id="wf-progress-bar"></div>
      </div>

      <div id="wf-completed-banner" class="banner allowed" style="display:none; font-size:0.84rem; margin:0; padding:8px 12px;">
        <strong>Workflow marked complete for this session.</strong> All steps have been manually marked Completed. Use the Workflow Packet or Decision Composer to synthesize final actions.
      </div>
    </div>

    <!-- Steps List Container -->
    <div class="wf-steps-list" id="playbook-steps-list">
      <!-- Injected via JavaScript -->
    </div>

    <!-- Workflow Artifacts Summary -->
    <div id="wf-artifacts-summary" class="wf-artifacts-summary"></div>

    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; padding-top:6px; border-top:1px solid #e2e8f0;">
      <div style="display:flex; align-items:center; gap:8px;">
        <span>Insert Step (Max 8):</span>
        <select id="add-step-agent-select" class="cc-filter-select">
          <!-- 37 agents list injected via JS -->
        </select>
        <button id="add-step-btn" class="secondary small" type="button">+ Add Step</button>
      </div>
      <span class="muted" style="font-size:0.82rem;">Manual advancement only · Zero automated chaining</span>
    </div>
  </section>

  <!-- PANEL 3: Context Kit Builder -->
  <section class="productivity-panel" id="panel-context-kit">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Session Context Kit Builder</h3>
        <p class="muted" style="margin:2px 0 0; font-size:0.84rem;">Assemble and preview transparent context items before dispatching to an agent. In-memory only.</p>
      </div>
      <button id="clear-kit-btn" class="secondary small" type="button">Clear Kit</button>
    </div>

    <!-- Context Budget Meter -->
    <div class="kit-budget-meter">
      <div style="display:flex; justify-content:space-between;">
        <span>Total Context Kit Budget:</span>
        <strong id="kit-budget-text">0 / 16,000 chars</strong>
      </div>
      <div class="budget-bar-track">
        <div class="budget-bar-fill" id="kit-budget-bar"></div>
      </div>
    </div>

    <!-- Add Custom Note Input -->
    <div style="display:grid; gap:6px; background:#f8fafc; padding:10px 12px; border-radius:6px; border:1px solid #e2e8f0;">
      <label style="font-weight:600; font-size:0.84rem; color:#334155;">Add User Context Note / Background Item:</label>
      <div style="display:flex; gap:8px;">
        <input type="text" id="kit-note-label" placeholder="Item Label (e.g. 'Project Requirements', 'User Constraints')" style="flex:1 1 180px; padding:6px 8px; border:1px solid #cbd5e1; border-radius:4px; font-size:0.86rem;">
        <input type="text" id="kit-note-content" placeholder="Content text / key details..." style="flex:2 1 300px; padding:6px 8px; border:1px solid #cbd5e1; border-radius:4px; font-size:0.86rem;">
        <button id="add-kit-note-btn" class="secondary small" type="button">+ Add to Kit</button>
      </div>
    </div>

    <!-- Items List -->
    <div class="context-kit-items-list" id="kit-items-list">
      <div class="muted" style="text-align:center; padding:16px; font-size:0.88rem;">No items in Context Kit. Add custom notes above or click "Add to Kit" on previous answers.</div>
    </div>

    <!-- Kit Actions -->
    <div style="display:flex; justify-content:flex-end; gap:8px; padding-top:6px; border-top:1px solid #e2e8f0;">
      <button id="kit-to-workflow-btn" class="secondary small" type="button">Use in Current Workflow Step</button>
      <button id="stage-kit-btn" class="secondary" type="button">Stage as Prior Context</button>
      <button id="insert-kit-btn" type="button">Insert into Request</button>
    </div>
  </section>

  <!-- Boundaries & Safety Modal -->
  <div class="boundaries-modal-backdrop" id="agent-boundaries-modal">
    <div class="boundaries-modal-card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h3 id="modal-agent-name" style="margin:0; color:var(--accent-dark);">Agent Safety & Boundaries</h3>
        <button id="close-modal-btn" class="secondary small" type="button">✕ Close</button>
      </div>
      <div id="modal-agent-badges" style="display:flex; flex-wrap:wrap; gap:6px;"></div>
      <div id="modal-agent-usewhen" style="font-size:0.88rem; background:#f8fafc; padding:10px; border-radius:6px; border:1px solid #e2e8f0;"></div>
      <div>
        <h4 style="margin:0 0 6px; font-size:0.9rem; color:var(--accent);">Safety Notes & Guardrails:</h4>
        <ul id="modal-safety-notes" style="margin:0; padding-left:20px; font-size:0.86rem; line-height:1.5;"></ul>
      </div>
      <div id="modal-high-stakes-section" style="display:none; background:#fff7ed; border:1px solid #fed7aa; padding:10px; border-radius:6px; font-size:0.86rem; color:#9a3412;">
        <strong>High-Stakes Boundary:</strong>
        <p id="modal-high-stakes-text" style="margin:4px 0 0;"></p>
      </div>
    </div>
  </div>
    """


def productivity_readiness_coach_html() -> str:
    return """
  <!-- Deterministic Request Readiness Coach & High-Stakes Banner -->
  <section class="readiness-coach-card ready" id="readiness-coach-card">
    <div class="readiness-top-row">
      <div style="display:flex; align-items:center; gap:8px;">
        <strong style="color:var(--text);">Readiness Coach:</strong>
        <span class="pill succeeded" id="readiness-status-pill">Ready</span>
        <span class="pill" id="source-summary-pill" style="display:none;">Reviewed Sources: 0</span>
      </div>
      <span class="muted" style="font-size:0.8rem;" id="char-budget-indicator">0 chars</span>
    </div>

    <!-- High-Stakes Coach Banner (if applicable) -->
    <div id="coach-high-stakes-banner" class="banner high-stakes" style="display:none; font-size:0.84rem; padding:8px 12px;"></div>

    <div class="readiness-reason-text" id="readiness-reason-text">
      Enter your prompt below. Readiness is deterministically evaluated in real time.
    </div>

    <!-- Suggestion Action Box -->
    <div class="readiness-suggestion-box" id="readiness-suggestion-box" style="display:none;">
      <span style="font-style:italic; color:#475569;" id="readiness-suggestion-text"></span>
      <button id="apply-suggestion-btn" class="secondary small" type="button">Apply Scaffolding</button>
    </div>
  </section>
    """
