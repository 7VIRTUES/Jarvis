from __future__ import annotations


def results_dashboard_styles() -> str:
    return """
    /* ========================================================
       Assistant Result & Decision Workspace Styles (v0.1E Pass 10)
       ======================================================== */

    /* Result Board Enhanced Styles */
    .rb-toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 12px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 7px;
    }
    .rb-filter-group {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
    }
    .rb-selection-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 8px 12px;
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 6px;
      font-size: 0.86rem;
    }
    .rb-cards-container {
      display: grid;
      gap: 10px;
      max-height: 500px;
      overflow-y: auto;
      padding-right: 4px;
    }
    .rb-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      display: grid;
      gap: 8px;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      position: relative;
    }
    .rb-card:hover {
      border-color: var(--accent);
      box-shadow: 0 2px 8px rgba(15, 35, 55, 0.08);
    }
    .rb-card.selected {
      border-color: var(--accent);
      background: #f8fbfe;
      box-shadow: 0 0 0 2px var(--accent-light);
    }
    .rb-card.high-stakes-card {
      border-left: 5px solid #ea580c;
    }
    .rb-card-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .rb-card-meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
      font-size: 0.78rem;
    }
    .rb-card-body {
      font-size: 0.88rem;
      line-height: 1.5;
      color: #1e293b;
      max-height: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: pre-wrap;
    }
    .rb-card-body.expanded {
      max-height: none;
    }
    .rb-card-actions {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
      padding-top: 6px;
      border-top: 1px solid #f1f5f9;
    }
    .rb-card-actions button {
      padding: 3px 8px;
      font-size: 0.78rem;
    }

    /* Comparison Workspace Styles */
    .comparison-table-wrap {
      overflow-x: auto;
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fff;
    }
    .comparison-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.86rem;
    }
    .comparison-table th, .comparison-table td {
      padding: 10px 14px;
      border: 1px solid #e2e8f0;
      vertical-align: top;
      text-align: left;
    }
    .comparison-table th {
      background: #f8fafc;
      font-weight: 700;
      color: var(--accent-dark);
      width: 160px;
      white-space: nowrap;
    }
    .comparison-table .col-header {
      background: #f1f5f9;
      font-weight: 700;
      font-size: 0.92rem;
    }
    .diff-badge {
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
      font-size: 0.72rem;
      padding: 1px 5px;
      border-radius: 4px;
      font-weight: 600;
      margin-left: 6px;
    }
    .flag-btn {
      background: #fff;
      border: 1px solid #cbd5e1;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.75rem;
      cursor: pointer;
    }
    .flag-btn.flagged {
      background: #fef2f2;
      border-color: #fca5a5;
      color: #991b1b;
      font-weight: 600;
    }

    /* Evidence Ledger Styles */
    .evidence-ledger {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 12px;
      display: grid;
      gap: 6px;
      font-size: 0.84rem;
    }
    .evidence-item-tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.78rem;
      font-weight: 600;
    }
    .evidence-item-tag.source { background: #dcfce7; color: #14532d; }
    .evidence-item-tag.knowledge { background: #e0e7ff; color: #3730a3; }
    .evidence-item-tag.memory { background: #f3e8ff; color: #6b21a8; }
    .evidence-item-tag.prior { background: #fef3c7; color: #92400e; }
    .evidence-item-tag.citation { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
    .evidence-item-tag.none { background: #fee2e2; color: #991b1b; }

    /* Structured Decision Result Card Styles */
    .decision-result-card {
      background: #ffffff;
      border: 2px solid #0d9488;
      border-radius: 9px;
      padding: 18px;
      display: grid;
      gap: 14px;
      box-shadow: 0 4px 12px rgba(13, 148, 136, 0.08);
      margin-top: 8px;
    }
    .decision-header-row {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding-bottom: 10px;
      border-bottom: 1px solid #e2e8f0;
    }
    .decision-focus-banner {
      background: #f0fdfa;
      border: 1px solid #99f6e4;
      border-left: 5px solid #0d9488;
      padding: 10px 14px;
      border-radius: 6px;
      font-size: 0.9rem;
      color: #115e59;
    }
    .suggested-direction-box {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      padding: 14px;
      display: grid;
      gap: 8px;
    }
    .direction-title {
      font-weight: 700;
      font-size: 1.05rem;
      color: #0d9488;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .decision-matrix-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.84rem;
      margin-top: 6px;
    }
    .decision-matrix-table th, .decision-matrix-table td {
      padding: 8px 10px;
      border: 1px solid #e2e8f0;
      text-align: left;
    }
    .decision-matrix-table th {
      background: #f1f5f9;
      font-weight: 700;
      color: #334155;
    }
    .fit-pill {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.76rem;
      font-weight: 600;
    }
    .fit-pill.strong_initial_candidate { background: #dcfce7; color: #14532d; }
    .fit-pill.comparison_candidate { background: #dbeafe; color: #1e40af; }
    .fit-pill.secondary_candidate { background: #fef3c7; color: #92400e; }
    .fit-pill.not_comparable { background: #fee2e2; color: #991b1b; }

    /* Interactive follow-up chips */
    .followup-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 4px;
    }
    .followup-chip {
      background: #ffffff;
      border: 1px solid #99f6e4;
      color: #0f766e;
      padding: 4px 10px;
      border-radius: 16px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .followup-chip:hover {
      background: #f0fdfa;
      border-color: #0d9488;
      color: #115e59;
    }

    /* Modals & Drawers */
    .results-modal-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      z-index: 210;
      align-items: center;
      justify-content: center;
      padding: 16px;
    }
    .results-modal-backdrop.open {
      display: flex;
    }
    .results-modal-card {
      background: #ffffff;
      border-radius: 9px;
      max-width: 760px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      padding: 20px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
      display: grid;
      gap: 14px;
    }
    """


def results_dashboard_html_panels() -> str:
    return """
  <!-- PANEL: Enhanced Result Board -->
  <section class="productivity-panel" id="panel-result-board">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <div>
        <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Session Result Board (<span id="rb-total-count">0</span> / 20)</h3>
        <p class="muted" style="margin:2px 0 0; font-size:0.84rem;">Explicitly collected decisions, briefs, plans, and action outputs for comparison and review. In-memory only.</p>
      </div>
      <div style="display:flex; align-items:center; gap:6px;">
        <button id="rb-view-mode-btn" class="secondary small" type="button">Compact View</button>
        <button id="rb-clear-btn" class="secondary small" type="button">Clear Board</button>
      </div>
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="rb-toolbar">
      <input type="search" id="rb-search-input" class="cc-search-input" placeholder="Search saved results by keyword, agent, or content...">
      <div class="rb-filter-group">
        <select id="rb-agent-filter" class="cc-filter-select">
          <option value="">All Agents</option>
        </select>
        <select id="rb-category-filter" class="cc-filter-select">
          <option value="">All Categories</option>
        </select>
        <label class="toggle-label" style="font-size:0.82rem;">
          <input type="checkbox" id="rb-high-stakes-filter">
          <span>High Stakes Only</span>
        </label>
        <label class="toggle-label" style="font-size:0.82rem;">
          <input type="checkbox" id="rb-evidence-filter">
          <span>Evidence Present</span>
        </label>
      </div>
    </div>

    <!-- Batch Selection Actions Bar -->
    <div class="rb-selection-bar" id="rb-selection-bar">
      <div style="display:flex; align-items:center; gap:10px;">
        <label style="display:inline-flex; align-items:center; gap:6px; cursor:pointer; font-weight:600;">
          <input type="checkbox" id="rb-select-all-visible">
          <span>Select All Visible (<span id="rb-selected-count">0</span> selected)</span>
        </label>
      </div>
      <div style="display:flex; flex-wrap:wrap; align-items:center; gap:6px;">
        <button id="rb-compare-btn" class="small" type="button">⚖️ Compare Selected (2–6)</button>
        <button id="rb-review-packet-btn" class="secondary small" type="button">📋 Review Packet</button>
        <button id="rb-to-decision-btn" class="secondary small" type="button">🎯 Decision Options</button>
        <button id="rb-to-kit-btn" class="secondary small" type="button">🧰 Add to Context Kit</button>
        <button id="rb-to-report-btn" class="secondary small" type="button">📝 Prepare Report</button>
        <button id="rb-remove-selected-btn" class="secondary small danger" type="button">Remove Selected</button>
      </div>
    </div>

    <!-- Result Board Cards Grid -->
    <div class="rb-cards-container" id="rb-cards-container">
      <div class="empty-state" style="padding:24px;">No results on board yet. Click "Add to Result Board" on any Assistant response or action result.</div>
    </div>
  </section>

  <!-- PANEL: Multi-Result Comparison Workspace -->
  <section class="productivity-panel" id="panel-comparison">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <div>
        <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Multi-Result Comparison Workspace</h3>
        <p class="muted" style="margin:2px 0 0; font-size:0.84rem;">Side-by-side descriptive comparison across 2–6 selected responses. Zero fake scoring.</p>
      </div>
      <div style="display:flex; align-items:center; gap:6px;">
        <button id="cmp-to-kit-btn" class="secondary small" type="button">🧰 Add Summary to Context Kit</button>
        <button id="cmp-to-review-btn" class="secondary small" type="button">📋 Compose Review Packet</button>
        <button id="cmp-to-decision-btn" class="secondary small" type="button">🎯 Use as Decision Options</button>
        <button id="cmp-close-btn" class="secondary small" type="button">✕ Close</button>
      </div>
    </div>

    <!-- Evidence Asymmetry & High-Stakes Notice -->
    <div id="cmp-asymmetry-banner" class="banner warning" style="display:none; font-size:0.84rem; padding:8px 12px;"></div>
    <div id="cmp-high-stakes-banner" class="banner high-stakes" style="display:none; font-size:0.84rem; padding:8px 12px;"></div>

    <div class="comparison-table-wrap" id="comparison-table-wrap">
      <!-- Injected via JavaScript -->
    </div>
  </section>

  <!-- MODAL: Result Detail / Evidence Inspector -->
  <div class="results-modal-backdrop" id="drawer-result-detail">
    <div class="results-modal-card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h3 id="detail-agent-name" style="margin:0; color:var(--accent-dark);">Result Detail Inspector</h3>
          <span id="detail-meta-subtitle" class="muted" style="font-size:0.82rem;"></span>
        </div>
        <button id="close-detail-btn" class="secondary small" type="button">✕ Close</button>
      </div>

      <!-- Detail Sections -->
      <div style="display:grid; gap:12px;">
        <div>
          <h4 style="margin:0 0 4px; font-size:0.88rem; color:var(--accent);">Primary Response:</h4>
          <div id="detail-primary-text" style="font-size:0.9rem; line-height:1.5; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px; max-height:220px; overflow-y:auto; white-space:pre-wrap;"></div>
        </div>

        <div id="detail-keypoints-sec" style="display:none;">
          <h4 style="margin:0 0 4px; font-size:0.88rem; color:var(--accent);">Key Points:</h4>
          <ul id="detail-keypoints-list" style="margin:0; padding-left:18px; font-size:0.86rem; line-height:1.4;"></ul>
        </div>

        <!-- Evidence Ledger -->
        <div>
          <h4 style="margin:0 0 4px; font-size:0.88rem; color:var(--accent);">Evidence Ledger (Origin Breakdown):</h4>
          <div class="evidence-ledger" id="detail-evidence-ledger">
            <!-- Injected via JS -->
          </div>
        </div>

        <div id="detail-limitations-sec" style="display:none;">
          <h4 style="margin:0 0 4px; font-size:0.88rem; color:#92400e;">Limitations:</h4>
          <ul id="detail-limitations-list" style="margin:0; padding-left:18px; font-size:0.84rem; color:#92400e;"></ul>
        </div>

        <div id="detail-safety-sec" style="display:none;">
          <h4 style="margin:0 0 4px; font-size:0.88rem; color:var(--safe);">Safety Notes & Guardrails:</h4>
          <ul id="detail-safety-list" style="margin:0; padding-left:18px; font-size:0.84rem; color:var(--safe);"></ul>
        </div>

        <!-- Metadata & JSON Viewer Toggle -->
        <div>
          <button id="detail-toggle-json-btn" class="secondary small" type="button">View Raw Metadata JSON</button>
          <div class="json-panel" id="detail-json-panel" style="display:none; margin-top:6px;">
            <pre class="json-viewer" id="detail-json-viewer"></pre>
          </div>
        </div>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:8px; padding-top:8px; border-top:1px solid #e2e8f0;">
        <button id="detail-use-prior-btn" class="secondary small" type="button">Use as Prior Context</button>
        <button id="detail-add-kit-btn" class="secondary small" type="button">Add to Context Kit</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Review Packet Composer -->
  <div class="results-modal-backdrop" id="drawer-review-packet">
    <div class="results-modal-card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h3 style="margin:0; color:var(--accent-dark);">Review Packet Composer</h3>
          <span class="muted" style="font-size:0.82rem;">Assemble selected responses into a structured review package</span>
        </div>
        <button id="close-review-packet-btn" class="secondary small" type="button">✕ Close</button>
      </div>

      <!-- Budget Meter -->
      <div class="kit-budget-meter">
        <div style="display:flex; justify-content:space-between;">
          <span>Review Packet Budget:</span>
          <strong id="packet-budget-text">0 / 16,000 chars</strong>
        </div>
        <div class="budget-bar-track">
          <div class="budget-bar-fill" id="packet-budget-bar"></div>
        </div>
      </div>

      <div style="display:grid; gap:10px;">
        <div class="action-field">
          <label for="packet-question-input">Review Purpose / Core Question</label>
          <input type="text" id="packet-question-input" placeholder="e.g. 'Synthesize findings and identify risks across candidate approaches'" />
        </div>

        <div class="action-field">
          <label for="packet-notes-input">Reviewer Notes & Context</label>
          <textarea id="packet-notes-input" rows="3" class="composer-textarea" placeholder="Add custom background notes or constraints for the reviewer..."></textarea>
        </div>

        <div class="action-field">
          <label for="packet-unresolved-input">Unresolved Questions (one per line)</label>
          <textarea id="packet-unresolved-input" rows="2" class="composer-textarea" placeholder="What questions remain unanswered?"></textarea>
        </div>

        <div>
          <label style="font-weight:600; font-size:0.84rem; color:var(--muted);">Selected Responses Included (<span id="packet-entry-count">0</span>):</label>
          <div id="packet-entries-list" style="display:grid; gap:6px; margin-top:4px; max-height:140px; overflow-y:auto;"></div>
        </div>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:8px; padding-top:8px; border-top:1px solid #e2e8f0;">
        <button id="packet-stage-prior-btn" class="secondary" type="button">Stage as Prior Context</button>
        <button id="packet-add-kit-btn" class="secondary" type="button">Add to Context Kit</button>
        <button id="packet-insert-composer-btn" type="button">Insert into Request</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Decision Composer -->
  <div class="results-modal-backdrop" id="drawer-decision-composer">
    <div class="results-modal-card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h3 style="margin:0; color:var(--accent-dark);">Decision Composer</h3>
          <span class="muted" style="font-size:0.82rem;">Structure decision choices for Local Decision Agent</span>
        </div>
        <button id="close-decision-composer-btn" class="secondary small" type="button">✕ Close</button>
      </div>

      <!-- Decision Readiness Coach Card -->
      <div class="readiness-coach-card ready" id="dec-readiness-card" style="margin-bottom:0;">
        <div class="readiness-top-row">
          <div style="display:flex; align-items:center; gap:8px;">
            <strong style="color:var(--text);">Decision Readiness:</strong>
            <span class="pill succeeded" id="dec-readiness-pill">Ready to Prepare</span>
          </div>
        </div>
        <div class="readiness-reason-text" id="dec-readiness-reason">At least 2 distinct candidate options are required.</div>
      </div>

      <div style="display:grid; gap:10px;">
        <div class="action-field">
          <label for="dec-question-input">Decision Question / Goal *</label>
          <input type="text" id="dec-question-input" placeholder="e.g. 'Choose the best storage architecture for our local metadata cache'" />
        </div>

        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <label style="font-weight:600; font-size:0.84rem; color:var(--muted);">Candidate Options (At least 2 required) *</label>
            <button id="dec-add-option-btn" class="secondary small" type="button">+ Add Option</button>
          </div>
          <div id="dec-options-list" style="display:grid; gap:6px;"></div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          <div class="action-field">
            <label for="dec-criteria-input">Criteria (comma-separated)</label>
            <input type="text" id="dec-criteria-input" placeholder="e.g. Speed, Low RAM, Simplicity" />
          </div>
          <div class="action-field">
            <label for="dec-priorities-input">Priorities (comma-separated)</label>
            <input type="text" id="dec-priorities-input" placeholder="e.g. Data integrity, Zero network" />
          </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
          <div class="action-field">
            <label for="dec-constraints-input">Constraints (comma-separated)</label>
            <input type="text" id="dec-constraints-input" placeholder="e.g. Local-only, Single-threaded" />
          </div>
          <div class="action-field">
            <label for="dec-style-select">Decision Style</label>
            <select id="dec-style-select" class="cc-filter-select">
              <option value="balanced" selected>Balanced (Standard)</option>
              <option value="safest">Safest (Risk-Minimizing)</option>
              <option value="fastest">Fastest (Speed-Optimizing)</option>
              <option value="cheapest">Cheapest (Resource-Preserving)</option>
              <option value="highest_upside">Highest Upside (Opportunity-Seeking)</option>
            </select>
          </div>
        </div>

        <div class="action-field">
          <label for="dec-notes-input">Context Notes / Evidence Summaries</label>
          <textarea id="dec-notes-input" rows="3" class="composer-textarea" placeholder="Add supporting context, excerpt notes, or benchmarks..."></textarea>
        </div>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; padding-top:8px; border-top:1px solid #e2e8f0;">
        <span class="muted" style="font-size:0.8rem;">Populates composer for Local Decision Agent · Does not execute automatically</span>
        <button id="dec-prepare-btn" type="button">🎯 Prepare Decision Request</button>
      </div>
    </div>
  </div>
    """
