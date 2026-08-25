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
      flex-wrap: nowrap;
      overflow-x: auto;
      gap: 6px;
      padding-bottom: 2px;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: thin;
    }
    .prod-tab-btn {
      flex-shrink: 0;
      white-space: nowrap;
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
      align-items: center;
      gap: 8px;
      font-size: 0.84rem;
      flex-wrap: wrap;
    }
    .cc-chip-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .cc-agent-chip {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      padding: 2px 10px;
      font-size: 0.8rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      transition: all 0.12s ease;
    }
    .cc-agent-chip:hover {
      border-color: var(--accent);
      background: #f0fdf4;
    }
    .cc-agent-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 12px;
      margin-top: 4px;
    }
    .cc-agent-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 14px;
      display: grid;
      gap: 8px;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      cursor: pointer;
    }
    .cc-agent-card:hover {
      border-color: var(--accent);
      box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    }
    .cc-agent-card.selected {
      border-color: var(--accent);
      background: #f0fdf4;
    }
    .cc-agent-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 6px;
    }
    .cc-agent-name {
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--accent-dark);
    }
    .cc-agent-category {
      font-size: 0.72rem;
      text-transform: uppercase;
      font-weight: 700;
      letter-spacing: 0.5px;
      padding: 2px 6px;
      border-radius: 4px;
      background: #e2e8f0;
      color: #475569;
    }
    .cc-agent-desc {
      font-size: 0.84rem;
      color: #475569;
      line-height: 1.35;
    }
    .cc-agent-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 4px;
      font-size: 0.8rem;
    }

    /* Context Kit Styles */
    .kit-budget-meter {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 12px;
      display: grid;
      gap: 6px;
      font-size: 0.86rem;
    }
    .budget-bar-track {
      background: #e2e8f0;
      height: 8px;
      border-radius: 4px;
      overflow: hidden;
      width: 100%;
    }
    .budget-bar-fill {
      background: var(--accent);
      height: 100%;
      width: 0%;
      transition: width 0.2s ease;
    }
    .budget-bar-fill.warning {
      background: #f59e0b;
    }
    .budget-bar-fill.danger {
      background: #ef4444;
    }
    .context-kit-items-list {
      display: grid;
      gap: 8px;
    }
    .context-kit-item-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 10px 12px;
      display: grid;
      gap: 6px;
      font-size: 0.85rem;
    }
    .context-kit-item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .context-kit-item-type {
      font-weight: 700;
      color: var(--accent-dark);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .context-kit-item-content {
      font-size: 0.82rem;
      color: #334155;
      background: #f8fafc;
      padding: 6px 8px;
      border-radius: 4px;
      max-height: 80px;
      overflow-y: auto;
      white-space: pre-wrap;
    }

    /* Boundaries Modal */
    .boundaries-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.5);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 999;
      padding: 16px;
    }
    .boundaries-modal-backdrop.open {
      display: flex;
    }
    .boundaries-modal-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      width: 100%;
      max-width: 580px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
      display: grid;
      gap: 12px;
    }
    """


def productivity_html_toolbar() -> str:
    return """
  <!-- Productivity Workspace Toolbar Strip -->
  <div class="prod-toolbar" id="prod-toolbar">
    <div class="prod-tabs" role="tablist" aria-label="Productivity Workspaces">
      <button class="prod-tab-btn" data-prod-tab="panel-command-center" role="tab" aria-selected="false" type="button">
        ⚡ Command Center (<span id="tab-count-agents">37</span>)
      </button>
      <button class="prod-tab-btn" data-prod-tab="panel-playbooks" role="tab" aria-selected="false" type="button">
        📚 Playbooks &amp; Workflows
      </button>
      <button class="prod-tab-btn" data-prod-tab="panel-sources" role="tab" aria-selected="false" type="button">
        🌐 Reviewed Sources (<span id="tab-count-sources">0</span>)
      </button>
      <button class="prod-tab-btn" data-prod-tab="panel-context-kit" role="tab" aria-selected="false" type="button">
        🧰 Context Kit (<span id="tab-count-kit">0</span>)
      </button>
      <button class="prod-tab-btn" data-prod-tab="panel-result-board" role="tab" aria-selected="false" type="button">
        📊 Result Board (<span id="tab-count-results">0</span>)
      </button>
      <button class="prod-tab-btn" data-prod-tab="panel-comparison" role="tab" aria-selected="false" type="button">
        ⚖️ Multi-Result Compare (<span id="tab-count-compare">0</span>)
      </button>
    </div>
    <div style="font-size:0.8rem; color:#64748b;">
      <span id="prod-session-status">Local-only · In-memory session</span>
    </div>
  </div>
    """


def productivity_html_panels() -> str:
    return """
  <!-- PANEL 1: Command Center -->
  <section class="productivity-panel" id="panel-command-center">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <div>
        <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Local Response Agent Command Center</h3>
        <p class="muted" style="margin:2px 0 0; font-size:0.84rem;">Select from 37 canonical single-turn local response agents. Fully manual selection and dispatch.</p>
      </div>
      <div style="display:flex; align-items:center; gap:8px;">
        <span class="pill" id="cc-total-count-pill" style="font-size:0.8rem;">37 Agents Available</span>
      </div>
    </div>

    <!-- Filter & Search Bar -->
    <div class="cc-filter-bar">
      <input type="search" id="cc-search-input" class="cc-search-input" placeholder="Search agents by name, tag, or description...">
      <select id="cc-category-filter" class="cc-filter-select">
        <option value="all">All Categories</option>
        <option value="General">General / Orchestration</option>
        <option value="Coding">Coding & Architecture</option>
        <option value="Research">Research & Synthesis</option>
        <option value="Review">Review & Hardening</option>
        <option value="High-Stakes">High-Stakes Analysis</option>
      </select>
      <select id="cc-sort-select" class="cc-filter-select">
        <option value="default">Default Catalog Order</option>
        <option value="name_asc">Name (A-Z)</option>
        <option value="name_desc">Name (Z-A)</option>
        <option value="category">Category</option>
      </select>
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
      <div class="empty-state" style="padding:16px;">No items in Context Kit. Add custom notes above or click "Add to Kit" on previous answers. Context Kit is session-only and never stored permanently.</div>
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
