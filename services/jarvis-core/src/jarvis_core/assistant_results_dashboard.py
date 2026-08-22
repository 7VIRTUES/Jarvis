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
    .evidence-item-tag.source { background: #dcfce7; color: #14532d; border: 1px solid #bbf7d0; }
    .evidence-item-tag.knowledge { background: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe; }
    .evidence-item-tag.memory { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }
    .evidence-item-tag.prior { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .evidence-item-tag.citation { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
    .evidence-item-tag.none { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

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
        <select id="rb-evidence-filter" class="cc-filter-select">
          <option value="">All Evidence Types</option>
          <option value="reviewed_sources">Has Reviewed Sources</option>
          <option value="model_citations">Has Model Citations</option>
          <option value="referenced_context">Has Referenced Context</option>
        </select>
        <label class="toggle-label" style="font-size:0.82rem;">
          <input type="checkbox" id="rb-high-stakes-filter">
          <span>High Stakes Only</span>
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


def results_dashboard_scripts() -> str:
    return """
  // ==========================================
  // Evidence Normalization & Result Board (v0.1E Pass 10B)
  // ==========================================

  const MAX_RESULT_BOARD_SIZE = 20;
  const MAX_PACKET_CHARS = 16000;

  sessionState.resultBoard = [];
  sessionState.rbViewMode = 'expanded'; // 'compact' | 'expanded'
  sessionState.activeDetailItem = null;
  sessionState.activePacketEntries = [];
  sessionState.decisionComposerOptions = [];
  sessionState.activeComparisonEntries = [];

  function extractEvidenceModel(source) {
    const resp = source.response || (source.fullResponse ? source.fullResponse : {});
    const rawPayload = (source.actionMetadata && source.actionMetadata.rawPayload) || source.rawPayload || {};
    const genResp = resp.generatedResponse || {};

    // Reviewed sources derived ONLY from explicitly supplied rawPayload.web_context
    const reviewedSources = [];
    const webContext = rawPayload.web_context || (resp.responseContext && resp.responseContext.webContext) || [];
    if (Array.isArray(webContext)) {
      webContext.forEach((src, idx) => {
        if (src && typeof src === 'object') {
          reviewedSources.push({
            citationLabel: src.citationLabel || src.label || `Source ${idx + 1}`,
            title: src.title || src.citationLabel || 'Reviewed Web Source',
            domain: src.domain || '',
            sourceType: src.sourceType || 'web_context',
            fetchedAt: src.fetchedAt || null,
            recencyNote: src.recencyNote || '',
            qualityWarnings: Array.isArray(src.qualityWarnings) ? src.qualityWarnings : [],
            limitations: Array.isArray(src.limitations) ? src.limitations : [],
            excerpt: typeof src.excerpt === 'string' ? src.excerpt.slice(0, 400) : '',
          });
        }
      });
    }

    // Model Citation Labels from generatedResponse.citations
    const modelCitationLabels = [];
    const rawCitations = genResp.citations || resp.citations || [];
    if (Array.isArray(rawCitations)) {
      rawCitations.forEach((cit, idx) => {
        if (typeof cit === 'string' && cit.trim()) {
          modelCitationLabels.push({
            label: cit.trim(),
            supports: 'Referenced in model response text',
          });
        } else if (cit && typeof cit === 'object') {
          modelCitationLabels.push({
            label: cit.label || `Citation ${idx + 1}`,
            supports: cit.supports || 'Model citation reference',
          });
        }
      });
    }

    // Context origin flags
    const knowledgeContext = [];
    if (rawPayload.knowledge && rawPayload.knowledge.enabled) {
      knowledgeContext.push({
        type: 'Referenced Knowledge Context',
        detail: 'Project Knowledge context was enabled in request assembly.',
      });
    }
    if (rawPayload.system_knowledge_summary) {
      knowledgeContext.push({
        type: 'System Knowledge Context',
        detail: 'System Knowledge context summary was provided.',
      });
    }

    const memoryContext = [];
    if (rawPayload.memory && rawPayload.memory.enabled) {
      memoryContext.push({
        type: 'Referenced Memory Context',
        detail: 'Local memory recall was active for this request.',
      });
    }

    const priorAgentContext = [];
    if (rawPayload.prior_agent_context || (resp.responseContext && resp.responseContext.priorContext)) {
      priorAgentContext.push({
        type: 'Prior Agent Context',
        detail: 'Staged prior context from another agent was supplied.',
      });
    }

    return {
      reviewedSources,
      modelCitationLabels,
      knowledgeContext,
      memoryContext,
      priorAgentContext,
    };
  }

  function addToResultBoard(source) {
    if (sessionState.resultBoard.length >= MAX_RESULT_BOARD_SIZE) {
      alert(`Result Board is full (maximum ${MAX_RESULT_BOARD_SIZE} entries). Please remove unneeded items before adding more.`);
      return;
    }

    const resp = source.response || (source.fullResponse ? source.fullResponse : {});
    const primaryText = resp.generatedResponse ? resp.generatedResponse.response : (resp.summary || resp.brief || resp.plan || resp.draft || resp.response || resp.decision || source.text || '');
    const keyPoints = resp.keyPoints || (resp.generatedResponse && resp.generatedResponse.keyPoints) || resp.tradeoffs || [];
    const limitations = resp.limitations || (resp.generatedResponse && resp.generatedResponse.limitations) || [];
    const safetyNotes = resp.safetyNotes || (resp.safety && resp.safety.notes) || [];
    
    // Canonical high-stakes boolean propagation
    const isHighStakes = !!(source.route && (source.route.high_stakes || source.route.is_high_stakes)) ||
                         !!(resp.safety && resp.safety.high_stakes) ||
                         !!source.isHighStakes;
    const routeConfidence = (source.route && source.route.confidence_tier) || source.confidenceTier || 'standard';
    const genMode = (resp.generation && resp.generation.mode) || source.generationMode || source.turnType || 'deterministic';

    const evidence = extractEvidenceModel(source);

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
      evidence: evidence,
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

  function getFilteredResultBoardEntries() {
    const query = (byId('rb-search-input')?.value || '').toLowerCase().trim();
    const agentFilter = byId('rb-agent-filter')?.value || '';
    const catFilter = byId('rb-category-filter')?.value || '';
    const hsOnly = byId('rb-high-stakes-filter')?.checked || false;
    const evidenceType = byId('rb-evidence-filter')?.value || '';

    return sessionState.resultBoard.filter(item => {
      if (agentFilter && item.agentDisplayName !== agentFilter) return false;
      if (catFilter && item.category !== catFilter) return false;
      if (hsOnly && !item.isHighStakes) return false;
      if (evidenceType === 'reviewed_sources' && (!item.evidence || !item.evidence.reviewedSources.length)) return false;
      if (evidenceType === 'model_citations' && (!item.evidence || !item.evidence.modelCitationLabels.length)) return false;
      if (evidenceType === 'referenced_context' && (!item.evidence || (!item.evidence.knowledgeContext.length && !item.evidence.memoryContext.length && !item.evidence.priorAgentContext.length))) return false;
      if (query) {
        const hay = `${item.agentDisplayName} ${item.category} ${item.primaryText} ${(item.keyPoints || []).join(' ')}`.toLowerCase();
        if (!hay.includes(query)) return false;
      }
      return true;
    });
  }

  function moveResultBoardEntry(itemId, direction) {
    const idx = sessionState.resultBoard.findIndex(i => i.id === itemId);
    if (idx === -1) return;
    const targetIdx = idx + direction;
    if (targetIdx < 0 || targetIdx >= sessionState.resultBoard.length) return;
    const item = sessionState.resultBoard.splice(idx, 1)[0];
    sessionState.resultBoard.splice(targetIdx, 0, item);
    renderResultBoard();
  }

  function renderResultBoard() {
    const container = byId('rb-cards-container');
    const legacyContainer = byId('result-board-items');
    if (!container) return;

    const filtered = getFilteredResultBoardEntries();
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
    filtered.forEach((item) => {
      const canonicalIdx = sessionState.resultBoard.findIndex(i => i.id === item.id);
      const isSelected = !!item.selected;
      const isCompact = sessionState.rbViewMode === 'compact';
      const card = document.createElement('div');
      card.className = `rb-card ${isSelected ? 'selected' : ''} ${item.isHighStakes ? 'high-stakes-card' : ''}`;
      
      const revCount = item.evidence?.reviewedSources?.length || 0;
      const citCount = item.evidence?.modelCitationLabels?.length || 0;
      const hasRefContext = !!(item.evidence?.knowledgeContext?.length || item.evidence?.memoryContext?.length || item.evidence?.priorAgentContext?.length);

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
            <div style="display:inline-flex; gap:2px; margin-left:4px;">
              <button class="secondary small" type="button" data-action="move-up" data-item-id="${item.id}" ${canonicalIdx === 0 ? 'disabled' : ''} style="padding:1px 5px; font-size:0.72rem;" title="Move Up in Board Order">↑</button>
              <button class="secondary small" type="button" data-action="move-down" data-item-id="${item.id}" ${canonicalIdx === sessionState.resultBoard.length - 1 ? 'disabled' : ''} style="padding:1px 5px; font-size:0.72rem;" title="Move Down in Board Order">↓</button>
            </div>
          </div>
        </div>

        <div class="rb-card-body ${isCompact ? '' : 'expanded'}">${escapeHtml(item.primaryText)}</div>

        ${!isCompact && item.keyPoints && item.keyPoints.length ? `
          <div style="font-size:0.82rem; color:var(--muted);">
            <strong>Key Points:</strong> ${item.keyPoints.slice(0, 3).map(kp => `<span>• ${escapeHtml(kp)}</span>`).join(' ')}
          </div>
        ` : ''}

        <div class="rb-card-meta" style="margin-top:2px;">
          ${revCount > 0 ? `<span class="evidence-item-tag source">Reviewed Sources: ${revCount}</span>` : '<span class="evidence-item-tag none">No Reviewed Sources</span>'}
          ${citCount > 0 ? `<span class="evidence-item-tag citation">Model Citations: ${citCount}</span>` : ''}
          ${hasRefContext ? `<span class="evidence-item-tag knowledge">Referenced Context</span>` : ''}
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

      card.querySelector(`[data-action="move-up"]`).addEventListener('click', () => moveResultBoardEntry(item.id, -1));
      card.querySelector(`[data-action="move-down"]`).addEventListener('click', () => moveResultBoardEntry(item.id, 1));
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

    const revSources = item.evidence?.reviewedSources || [];
    const modCitations = item.evidence?.modelCitationLabels || [];
    const knContext = item.evidence?.knowledgeContext || [];
    const memContext = item.evidence?.memoryContext || [];
    const priorContext = item.evidence?.priorAgentContext || [];

    const summaryBlock = document.createElement('div');
    summaryBlock.innerHTML = `
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:6px; margin-bottom:8px;">
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px; font-size:0.8rem;">
          <span class="muted">Reviewed Sources:</span> <strong>${revSources.length}</strong>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px; font-size:0.8rem;">
          <span class="muted">Model Citations:</span> <strong>${modCitations.length}</strong>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px; font-size:0.8rem;">
          <span class="muted">Knowledge Context:</span> <strong>${knContext.length ? 'Yes' : 'No'}</strong>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px; font-size:0.8rem;">
          <span class="muted">Memory Context:</span> <strong>${memContext.length ? 'Yes' : 'No'}</strong>
        </div>
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:4px; padding:6px; font-size:0.8rem;">
          <span class="muted">Prior Context:</span> <strong>${priorContext.length ? 'Yes' : 'No'}</strong>
        </div>
      </div>
    `;
    ledger.append(summaryBlock);

    if (revSources.length > 0) {
      const srcSec = document.createElement('div');
      srcSec.innerHTML = `<strong style="font-size:0.82rem; color:#166534;">Explicitly Reviewed Web Sources (${revSources.length}):</strong>`;
      const srcList = document.createElement('ul');
      srcList.style.cssText = 'margin:4px 0 8px; padding-left:18px; font-size:0.8rem;';
      revSources.forEach(s => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${escapeHtml(s.title || s.citationLabel)}</strong> ${s.domain ? `<span class="muted">(${escapeHtml(s.domain)})</span>` : ''} ${s.recencyNote ? `<span class="pill allowed" style="font-size:0.7rem;">${escapeHtml(s.recencyNote)}</span>` : ''}`;
        srcList.append(li);
      });
      srcSec.append(srcList);
      ledger.append(srcSec);
    } else {
      const noSrc = document.createElement('div');
      noSrc.style.cssText = 'font-size:0.8rem; color:#64748b; margin-bottom:6px;';
      noSrc.textContent = 'No independently reviewed external web/source context was supplied to this request.';
      ledger.append(noSrc);
    }

    if (modCitations.length > 0) {
      const citSec = document.createElement('div');
      citSec.innerHTML = `<strong style="font-size:0.82rem; color:#334155;">Model Citation Labels (${modCitations.length}):</strong>`;
      const citList = document.createElement('ul');
      citList.style.cssText = 'margin:4px 0 8px; padding-left:18px; font-size:0.8rem;';
      modCitations.forEach(c => {
        const li = document.createElement('li');
        li.innerHTML = `<code>${escapeHtml(c.label)}</code> <span class="muted">— supports: ${escapeHtml(c.supports)}</span>`;
        citList.append(li);
      });
      citSec.append(citList);
      ledger.append(citSec);
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

  // ==========================================
  // Multi-Result Comparison Workspace
  // ==========================================

  function openComparisonWorkspace(entries) {
    sessionState.activeComparisonEntries = entries;
    const wrap = byId('comparison-table-wrap');
    if (!wrap) return;

    // Evidence asymmetry calculated STRICTLY on reviewed source counts
    const asymBanner = byId('cmp-asymmetry-banner');
    const hsBanner = byId('cmp-high-stakes-banner');

    const revCounts = entries.map(e => (e.evidence?.reviewedSources || []).length);
    const maxRev = Math.max(...revCounts);
    const minRev = Math.min(...revCounts);
    if (maxRev > 0 && minRev === 0) {
      asymBanner.style.display = 'block';
      asymBanner.innerHTML = `<strong>Evidence Asymmetry Notice:</strong> Reviewed-source coverage differs between options (${maxRev} reviewed source(s) vs 0). Lower-evidence options may need additional verified context before deciding.`;
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
    const revDiffer = new Set(revCounts).size > 1;
    const citCounts = entries.map(e => (e.evidence?.modelCitationLabels || []).length);
    const citDiffer = new Set(citCounts).size > 1;

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
            <th>Reviewed Sources ${revDiffer ? '<span class="diff-badge">diff</span>' : ''}</th>
            ${entries.map(e => {
              const srcs = e.evidence?.reviewedSources || [];
              if (!srcs.length) return '<td><span class="evidence-item-tag none">No Reviewed Sources</span></td>';
              return `
                <td>
                  <span class="evidence-item-tag source">${srcs.length} Reviewed Source(s)</span>
                  <ul style="margin:4px 0 0; padding-left:14px; font-size:0.75rem;">
                    ${srcs.slice(0, 3).map(s => `<li>${escapeHtml(s.title || s.citationLabel)} ${s.domain ? `(${escapeHtml(s.domain)})` : ''}</li>`).join('')}
                  </ul>
                </td>
              `;
            }).join('')}
          </tr>
          <tr>
            <th>Model Citation Labels ${citDiffer ? '<span class="diff-badge">diff</span>' : ''}</th>
            ${entries.map(e => {
              const cits = e.evidence?.modelCitationLabels || [];
              if (!cits.length) return '<td class="muted" style="font-size:0.8rem;">None</td>';
              return `
                <td>
                  <span class="evidence-item-tag citation">${cits.length} Model Citation(s)</span>
                  <ul style="margin:4px 0 0; padding-left:14px; font-size:0.75rem;">
                    ${cits.slice(0, 3).map(c => `<li><code>${escapeHtml(c.label)}</code></li>`).join('')}
                  </ul>
                </td>
              `;
            }).join('')}
          </tr>
          <tr>
            <th>Referenced Context</th>
            ${entries.map(e => {
              const kn = e.evidence?.knowledgeContext?.length || 0;
              const mem = e.evidence?.memoryContext?.length || 0;
              const prior = e.evidence?.priorAgentContext?.length || 0;
              const flags = [];
              if (kn) flags.push('Knowledge');
              if (mem) flags.push('Memory');
              if (prior) flags.push('Prior Context');
              if (!flags.length) return '<td class="muted" style="font-size:0.8rem;">None</td>';
              return `<td><span class="evidence-item-tag knowledge">${flags.join(', ')}</span></td>`;
            }).join('')}
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

  // ==========================================
  // Review Packet Composer (Fail-Closed Budgeting)
  // ==========================================

  function openReviewPacketComposer(entries) {
    sessionState.activePacketEntries = [...entries];
    const modal = byId('drawer-review-packet');
    if (!modal) return;

    renderPacketEntriesList();
    updateReviewPacketBudget();
    modal.classList.add('open');
  }

  function renderPacketEntriesList() {
    const list = byId('packet-entries-list');
    if (!list) return;
    byId('packet-entry-count').textContent = sessionState.activePacketEntries.length;
    list.replaceChildren();

    sessionState.activePacketEntries.forEach((e, idx) => {
      const row = document.createElement('div');
      row.style.cssText = 'background:#f8fafc; border:1px solid #e2e8f0; border-radius:4px; padding:6px 8px; font-size:0.82rem; display:flex; justify-content:space-between; align-items:center;';
      row.innerHTML = `
        <div style="flex:1; margin-right:8px;">
          <strong>${idx + 1}. ${escapeHtml(e.agentDisplayName)}</strong> <span class="muted">[${escapeHtml(e.category)}]</span>
          <div class="muted" style="font-size:0.75rem; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:380px;">${escapeHtml(e.primaryText.slice(0, 80))}...</div>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
          <span class="muted" style="font-size:0.75rem;">${e.primaryText.length} chars</span>
          <button type="button" class="secondary small danger" data-remove-packet-idx="${idx}" title="Remove entry from packet" ${sessionState.activePacketEntries.length <= 1 ? 'disabled' : ''}>✕</button>
        </div>
      `;

      row.querySelector(`[data-remove-packet-idx="${idx}"]`).addEventListener('click', () => {
        sessionState.activePacketEntries.splice(idx, 1);
        renderPacketEntriesList();
        updateReviewPacketBudget();
      });

      list.append(row);
    });
  }

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
      if (e.keyPoints && e.keyPoints.length) {
        md += `\n**Key Points:**\n${e.keyPoints.map(kp => `- ${kp}`).join('\n')}\n`;
      }
      const revSrcs = e.evidence?.reviewedSources || [];
      if (revSrcs.length) {
        md += `\n**Reviewed Sources:**\n${revSrcs.map(s => `- ${s.title || s.citationLabel} (${s.domain || 'web_context'})`).join('\n')}\n`;
      }
      const modCits = e.evidence?.modelCitationLabels || [];
      if (modCits.length) {
        md += `\n**Model Citation Labels:**\n${modCits.map(c => `- ${c.label}: ${c.supports}`).join('\n')}\n`;
      }
      const refKn = e.evidence?.knowledgeContext || [];
      const refMem = e.evidence?.memoryContext || [];
      const refPrior = e.evidence?.priorAgentContext || [];
      if (refKn.length || refMem.length || refPrior.length) {
        const refs = [...refKn, ...refMem, ...refPrior];
        md += `\n**Referenced Context:**\n${refs.map(r => `- ${r.type}: ${r.detail}`).join('\n')}\n`;
      }
      if (e.limitations && e.limitations.length) {
        md += `\n**Limitations:**\n${e.limitations.map(l => `- ${l}`).join('\n')}\n`;
      }
    });
    if (unresolved) md += `\n## Unresolved Questions\n${unresolved}\n`;
    return md.trim();
  }

  function updateReviewPacketBudget() {
    const md = buildReviewPacketMarkdown();
    const totalChars = md.length;
    const isOver = totalChars > MAX_PACKET_CHARS;
    const overage = totalChars - MAX_PACKET_CHARS;

    const budgetText = byId('packet-budget-text');
    const budgetBar = byId('packet-budget-bar');
    const insertBtn = byId('packet-insert-composer-btn');
    const stageBtn = byId('packet-stage-prior-btn');
    const kitBtn = byId('packet-add-kit-btn');

    if (budgetText) {
      if (isOver) {
        budgetText.innerHTML = `<span style="color:#b91c1c; font-weight:700;">${totalChars.toLocaleString()} / ${MAX_PACKET_CHARS.toLocaleString()} chars (${overage.toLocaleString()} chars over limit)</span>`;
      } else {
        budgetText.textContent = `${totalChars.toLocaleString()} / ${MAX_PACKET_CHARS.toLocaleString()} chars`;
      }
    }
    if (budgetBar) {
      const pct = Math.min(100, Math.round((totalChars / MAX_PACKET_CHARS) * 100));
      budgetBar.style.width = pct + '%';
      budgetBar.className = isOver ? 'budget-bar-fill danger' : (pct > 75 ? 'budget-bar-fill warning' : 'budget-bar-fill');
    }

    [insertBtn, stageBtn, kitBtn].forEach(btn => {
      if (btn) {
        btn.disabled = isOver;
        btn.title = isOver ? `Review Packet exceeds ${MAX_PACKET_CHARS.toLocaleString()} char limit. Remove entries or trim notes.` : '';
      }
    });
  }

  // ==========================================
  // Decision Composer (Structured Request Format)
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
      if (prepBtn) prepBtn.disabled = true;
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

  function formatStructuredDecisionRequest() {
    const question = (byId('dec-question-input')?.value || '').trim() || 'Compare these options';
    const options = sessionState.decisionComposerOptions.map(o => o.trim()).filter(Boolean);
    const criteria = (byId('dec-criteria-input')?.value || '').trim();
    const priorities = (byId('dec-priorities-input')?.value || '').trim();
    const constraints = (byId('dec-constraints-input')?.value || '').trim();
    const style = byId('dec-style-select')?.value || 'balanced';
    const notes = (byId('dec-notes-input')?.value || '').trim();

    let block = `[Decision Request]\nDecision: ${question}\nDecision Style: ${style}\n\nOptions:\n`;
    options.forEach(opt => {
      block += `- ${opt}\n`;
    });

    if (criteria) {
      block += `\nCriteria:\n`;
      criteria.split(',').map(c => c.trim()).filter(Boolean).forEach(c => {
        block += `- ${c}\n`;
      });
    }

    if (constraints) {
      block += `\nConstraints:\n`;
      constraints.split(',').map(c => c.trim()).filter(Boolean).forEach(c => {
        block += `- ${c}\n`;
      });
    }

    if (priorities) {
      block += `\nPriorities:\n`;
      priorities.split(',').map(p => p.trim()).filter(Boolean).forEach(p => {
        block += `- ${p}\n`;
      });
    }

    if (notes) {
      block += `\nContext Notes:\n${notes}\n`;
    }

    block += `[/Decision Request]`;
    return block;
  }

  function prepareReportFromSelected(entries) {
    let reportMd = `# Session Results Analysis Report\n\nGenerated on: ${new Date().toLocaleString()}\n\n`;
    entries.forEach((e, idx) => {
      reportMd += `## ${idx + 1}. ${e.agentDisplayName} (${e.category})\n\n${e.primaryText}\n\n`;
      if (e.keyPoints && e.keyPoints.length) {
        reportMd += `### Key Takeaways\n${e.keyPoints.map(kp => `- ${kp}`).join('\n')}\n\n`;
      }
      const revSrcs = e.evidence?.reviewedSources || [];
      if (revSrcs.length) {
        reportMd += `### Reviewed Sources\n${revSrcs.map(s => `- ${s.title || s.citationLabel} (${s.domain || 'web_context'})`).join('\n')}\n\n`;
      }
      const modCits = e.evidence?.modelCitationLabels || [];
      if (modCits.length) {
        reportMd += `### Model Citation Labels\n${modCits.map(c => `- ${c.label}: ${c.supports}`).join('\n')}\n\n`;
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
  // Initialization of Result Dashboard Handlers
  // ==========================================

  function initResultsDashboardEventHandlers() {
    // Result Board toolbar event listeners
    byId('rb-search-input')?.addEventListener('input', renderResultBoard);
    byId('rb-agent-filter')?.addEventListener('change', renderResultBoard);
    byId('rb-category-filter')?.addEventListener('change', renderResultBoard);
    byId('rb-evidence-filter')?.addEventListener('change', renderResultBoard);
    byId('rb-high-stakes-filter')?.addEventListener('change', renderResultBoard);

    byId('rb-view-mode-btn')?.addEventListener('click', () => {
      sessionState.rbViewMode = sessionState.rbViewMode === 'compact' ? 'expanded' : 'compact';
      byId('rb-view-mode-btn').textContent = sessionState.rbViewMode === 'compact' ? 'Expanded View' : 'Compact View';
      renderResultBoard();
    });

    byId('rb-select-all-visible')?.addEventListener('change', (e) => {
      const isChecked = e.target.checked;
      const visible = getFilteredResultBoardEntries();
      const visibleIds = new Set(visible.map(i => i.id));
      sessionState.resultBoard.forEach(i => {
        if (visibleIds.has(i.id)) {
          i.selected = isChecked;
        }
      });
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

    // Inspector modal
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

    // Comparison workspace buttons
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

    // Review packet events
    byId('packet-question-input')?.addEventListener('input', updateReviewPacketBudget);
    byId('packet-notes-input')?.addEventListener('input', updateReviewPacketBudget);
    byId('packet-unresolved-input')?.addEventListener('input', updateReviewPacketBudget);
    byId('close-review-packet-btn')?.addEventListener('click', () => {
      byId('drawer-review-packet')?.classList.remove('open');
    });
    byId('drawer-review-packet')?.addEventListener('click', (e) => {
      if (e.target === byId('drawer-review-packet')) byId('drawer-review-packet').classList.remove('open');
    });
    byId('packet-insert-composer-btn')?.addEventListener('click', () => {
      const md = buildReviewPacketMarkdown();
      if (md.length > MAX_PACKET_CHARS) {
        alert(`Review Packet exceeds character limit (${md.length} / ${MAX_PACKET_CHARS}). Please remove entries or shorten notes.`);
        return;
      }
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
      if (md.length > MAX_PACKET_CHARS) {
        alert(`Review Packet exceeds character limit (${md.length} / ${MAX_PACKET_CHARS}). Please remove entries or shorten notes.`);
        return;
      }
      setStagedPriorContext({
        agentId: 'review_packet',
        agentName: 'Review Packet Composer',
        responseId: 'packet_' + Date.now(),
        summary: md,
      });
      byId('drawer-review-packet')?.classList.remove('open');
      showToast('Staged Review Packet as prior context.');
      byId('composer').scrollIntoView({ behavior: 'smooth' });
    });
    byId('packet-add-kit-btn')?.addEventListener('click', () => {
      const md = buildReviewPacketMarkdown();
      if (md.length > MAX_PACKET_CHARS) {
        alert(`Review Packet exceeds character limit (${md.length} / ${MAX_PACKET_CHARS}). Please remove entries or shorten notes.`);
        return;
      }
      addContextKitItem('review_packet', 'Structured Review Packet', md);
      byId('drawer-review-packet')?.classList.remove('open');
    });

    // Decision composer events
    byId('dec-add-option-btn')?.addEventListener('click', () => {
      sessionState.decisionComposerOptions.push(`Option ${String.fromCharCode(65 + sessionState.decisionComposerOptions.length)}`);
      renderDecisionOptionsList();
      evaluateDecisionComposerReadiness();
    });
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
      const options = sessionState.decisionComposerOptions.map(o => o.trim()).filter(Boolean);
      if (options.length < 2) {
        alert('Please provide at least 2 candidate options.');
        return;
      }
      const prompt = formatStructuredDecisionRequest();
      selectAgentManually('local_decision_agent');
      byId('prompt-input').value = prompt;
      byId('prompt-input').focus();
      triggerReadinessEvaluation();
      byId('drawer-decision-composer')?.classList.remove('open');
      showToast('Prepared Decision Request in composer. Click Send to run.');
      byId('composer').scrollIntoView({ behavior: 'smooth' });
    });
  }
  """

