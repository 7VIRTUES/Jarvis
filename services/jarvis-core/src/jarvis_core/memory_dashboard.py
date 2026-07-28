from __future__ import annotations


def memory_dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jarvis Memory Center</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #eef2f6;
      --surface: #ffffff;
      --surface-soft: #f7f9fc;
      --border: #cbd5e1;
      --text: #172033;
      --muted: #536174;
      --accent: #155e9b;
      --accent-dark: #0f4775;
      --safe: #176b45;
      --warn: #8a5200;
      --danger: #a12626;
      --focus: #ffbf47;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", system-ui, sans-serif;
      line-height: 1.5;
    }
    a { color: var(--accent); }
    a:hover { color: var(--accent-dark); }
    a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible,
    summary:focus-visible {
      outline: 3px solid var(--focus);
      outline-offset: 2px;
    }
    .skip-link {
      position: absolute;
      left: 12px;
      top: -80px;
      z-index: 10;
      padding: 10px 14px;
      background: #111827;
      color: white;
      border-radius: 4px;
    }
    .skip-link:focus { top: 12px; }
    header {
      background: #14263b;
      color: #ffffff;
      padding: 24px clamp(18px, 4vw, 48px);
      border-bottom: 4px solid #5e87ad;
    }
    header h1 { margin: 0 0 6px; font-size: clamp(1.65rem, 3vw, 2.4rem); }
    header p { margin: 0; color: #dce8f4; }
    header a { color: #ffffff; font-weight: 700; }
    main {
      width: min(1500px, 100%);
      margin: 0 auto;
      padding: 22px clamp(14px, 3vw, 36px) 48px;
      display: grid;
      gap: 18px;
    }
    section, .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 18px;
      box-shadow: 0 2px 8px rgba(15, 35, 55, 0.06);
    }
    h2, h3 { margin-top: 0; }
    .safety-banner {
      border-left: 6px solid var(--accent);
      background: #f2f7fc;
    }
    .safety-banner ul { columns: 2; column-gap: 32px; }
    .status-line {
      min-height: 44px;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: var(--surface-soft);
    }
    .status-line[data-tone="success"] { border-color: #70ad8e; background: #edf8f2; }
    .status-line[data-tone="warning"] { border-color: #d0a24d; background: #fff8e8; }
    .status-line[data-tone="error"] { border-color: #d38282; background: #fff1f1; }
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: 10px;
    }
    .metric {
      min-height: 86px;
      padding: 12px;
      border: 1px solid var(--border);
      border-radius: 7px;
      background: var(--surface-soft);
      display: grid;
      align-content: center;
      gap: 2px;
    }
    .metric span { color: var(--muted); }
    .metric strong { font-size: 1.55rem; }
    .layout-two {
      display: grid;
      grid-template-columns: minmax(310px, 0.9fr) minmax(420px, 1.4fr);
      gap: 18px;
      align-items: start;
    }
    .form-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    .field { display: grid; gap: 5px; }
    .field.full { grid-column: 1 / -1; }
    label, legend { font-weight: 650; }
    input, select, textarea, button {
      font: inherit;
    }
    input, select, textarea {
      width: 100%;
      border: 1px solid #9aa8b8;
      border-radius: 5px;
      padding: 9px 10px;
      background: #ffffff;
      color: var(--text);
    }
    textarea { min-height: 104px; resize: vertical; }
    .counter, .help, .muted { color: var(--muted); font-size: 0.92rem; }
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 9px;
      align-items: center;
    }
    button, .button-link {
      border: 1px solid var(--accent);
      border-radius: 5px;
      padding: 9px 13px;
      background: var(--accent);
      color: #ffffff;
      text-decoration: none;
      font-weight: 650;
      cursor: pointer;
    }
    button:hover, .button-link:hover { background: var(--accent-dark); color: #ffffff; }
    button.secondary { background: #ffffff; color: var(--accent); }
    button.warning { background: var(--warn); border-color: var(--warn); }
    button.danger { background: var(--danger); border-color: var(--danger); }
    button:disabled { opacity: 0.55; cursor: not-allowed; }
    .filter-grid {
      display: grid;
      grid-template-columns: 2fr repeat(4, minmax(120px, 1fr)) 110px;
      gap: 10px;
      align-items: end;
    }
    .list {
      display: grid;
      gap: 10px;
    }
    .memory-card, .event-card, .preview-card {
      border: 1px solid var(--border);
      border-radius: 7px;
      padding: 12px;
      background: var(--surface-soft);
      display: grid;
      gap: 7px;
    }
    .memory-card.selected { border: 2px solid var(--accent); background: #f2f7fc; }
    .chips { display: flex; flex-wrap: wrap; gap: 6px; }
    .chip {
      display: inline-flex;
      border: 1px solid #aebaca;
      border-radius: 999px;
      padding: 2px 8px;
      background: #ffffff;
      font-size: 0.84rem;
    }
    .content-preview, .content-full {
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      word-break: break-word;
    }
    .content-full {
      padding: 12px;
      border-left: 4px solid #7796b5;
      background: var(--surface-soft);
    }
    dl {
      display: grid;
      grid-template-columns: minmax(140px, 0.35fr) 1fr;
      gap: 7px 12px;
      margin: 0;
    }
    dt { font-weight: 700; color: #354357; }
    dd { margin: 0; overflow-wrap: anywhere; }
    .confirmation {
      margin-top: 12px;
      border: 2px solid #d0a24d;
      border-radius: 7px;
      padding: 13px;
      background: #fff9ea;
    }
    .confirmation.danger { border-color: #c45c5c; background: #fff2f2; }
    .inline-check {
      display: flex;
      gap: 8px;
      align-items: flex-start;
      font-weight: 500;
    }
    .inline-check input { width: auto; margin-top: 5px; }
    .empty-state {
      border: 1px dashed #9caabb;
      border-radius: 6px;
      padding: 16px;
      color: var(--muted);
      background: var(--surface-soft);
    }
    [hidden] { display: none !important; }
    .danger-text { color: var(--danger); font-weight: 700; }
    @media (max-width: 1000px) {
      .metrics { grid-template-columns: repeat(2, minmax(120px, 1fr)); }
      .layout-two { grid-template-columns: 1fr; }
      .filter-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 620px) {
      .metrics, .form-grid, .filter-grid { grid-template-columns: 1fr; }
      .field.full { grid-column: auto; }
      .safety-banner ul { columns: 1; }
      dl { grid-template-columns: 1fr; }
      dd { padding-bottom: 6px; }
      .actions > button, .actions > .button-link { width: 100%; text-align: center; }
    }
  </style>
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to Memory Center content</a>
  <header>
    <div class="actions">
      <div>
        <h1>Jarvis Memory Center</h1>
        <p>Local · User-controlled · Approval-gated · Auditable</p>
      </div>
      <a class="button-link" href="/dashboard">Back to Dashboard</a>
    </div>
  </header>
  <main id="main-content">
    <section class="safety-banner" aria-labelledby="memory-safety-title">
      <h2 id="memory-safety-title">Memory safety boundaries</h2>
      <ul>
        <li>Memory is stored locally in Jarvis SQLite.</li>
        <li>New memories begin as pending, and pending memories are inactive.</li>
        <li>Only approved, unexpired memories can be active.</li>
        <li>Jarvis does not automatically save conversations.</li>
        <li>Jarvis does not automatically approve memory.</li>
        <li>Memory retrieval is opt-in for exactly six representative pilot agents.</li>
        <li>Private-session state is temporary and page-local.</li>
        <li>Sensitive memories should be used sparingly.</li>
        <li>Obvious credentials and secrets are rejected before storage.</li>
      </ul>
    </section>

    <div id="memory-action-status" class="status-line" role="status" aria-live="polite">
      Memory Center ready. Administrative actions occur only when you select them.
    </div>

    <section aria-labelledby="summary-title">
      <div class="actions">
        <div>
          <h2 id="summary-title">Memory summary</h2>
          <p class="muted">Stored status and effective activity are shown separately.</p>
        </div>
        <button id="summary-refresh-button" type="button" class="secondary">Refresh summary</button>
      </div>
      <div id="summary-loading" class="muted" aria-live="polite">Loading memory summary...</div>
      <div id="summary-error" class="empty-state" hidden></div>
      <div id="summary-empty" class="empty-state" hidden>No stored memories yet. Create a pending proposal below.</div>
      <div id="summary-metrics" class="metrics" aria-busy="true">
        <div class="metric"><span>Total</span><strong id="summary-total">—</strong></div>
        <div class="metric"><span>Pending</span><strong id="summary-pending">—</strong></div>
        <div class="metric"><span>Active</span><strong id="summary-active">—</strong></div>
        <div class="metric"><span>Approved stored</span><strong id="summary-approved">—</strong></div>
        <div class="metric"><span>Disabled</span><strong id="summary-disabled">—</strong></div>
        <div class="metric"><span>Rejected</span><strong id="summary-rejected">—</strong></div>
        <div class="metric"><span>Expired</span><strong id="summary-expired">—</strong></div>
        <div class="metric"><span>Inactive</span><strong id="summary-inactive">—</strong></div>
      </div>
    </section>

    <section aria-labelledby="private-session-title">
      <h2 id="private-session-title">Private-session policy</h2>
      <label class="inline-check" for="private-session-toggle">
        <input id="private-session-toggle" type="checkbox" role="switch" aria-describedby="private-session-help">
        <span><strong>Private session</strong> — block memory use in manual and ranked previews from this page.</span>
      </label>
      <p id="private-session-help" class="help">
        This temporary page-only switch does not delete or hide stored memories. Administrative review remains
        available, while ranked retrieval is blocked without audit records or events.
      </p>
      <div id="private-session-policy-status" class="status-line" aria-live="polite">
        Private session is off. Manual and ranked previews may return approved, unexpired matches.
      </div>
    </section>

    <section aria-labelledby="proposal-title">
      <h2 id="proposal-title">Create a pending proposal</h2>
      <p>Manual creation always produces a pending, inactive proposal. Approval is a separate explicit action.</p>
      <form id="proposal-form">
        <div class="form-grid">
          <div class="field full">
            <label for="proposal-content">Memory content</label>
            <textarea id="proposal-content" maxlength="4000" required aria-describedby="proposal-content-help proposal-content-count"></textarea>
            <div id="proposal-content-help" class="help">Required. Maximum 4,000 characters; content is never silently truncated.</div>
            <div id="proposal-content-count" class="counter" aria-live="polite">4,000 characters remaining</div>
          </div>
          <div class="field">
            <label for="proposal-memory-type">Memory type</label>
            <select id="proposal-memory-type" required>
              <option value="preference">preference</option>
              <option value="personal_fact">personal_fact</option>
              <option value="goal">goal</option>
              <option value="constraint">constraint</option>
              <option value="project_fact">project_fact</option>
              <option value="decision">decision</option>
              <option value="routine">routine</option>
              <option value="terminology">terminology</option>
              <option value="agent_instruction">agent_instruction</option>
            </select>
          </div>
          <div class="field">
            <label for="proposal-scope-type">Scope type</label>
            <select id="proposal-scope-type" required>
              <option value="global">global</option>
              <option value="project">project</option>
              <option value="agent">agent</option>
            </select>
          </div>
          <div class="field">
            <label for="proposal-scope-value">Scope value</label>
            <input id="proposal-scope-value" type="text" maxlength="1000" aria-describedby="proposal-scope-help">
            <div id="proposal-scope-help" class="help">Required for project or agent scope. Agent scope requires an existing agent ID.</div>
          </div>
          <div class="field">
            <label for="proposal-source-type">Source type</label>
            <select id="proposal-source-type" required>
              <option value="manual">manual</option>
            </select>
          </div>
          <div class="field">
            <label for="proposal-confidence">Confidence</label>
            <select id="proposal-confidence" required>
              <option value="low">low</option>
              <option value="medium" selected>medium</option>
              <option value="high">high</option>
            </select>
          </div>
          <div class="field">
            <label for="proposal-sensitivity">Sensitivity</label>
            <select id="proposal-sensitivity" required>
              <option value="standard" selected>standard</option>
              <option value="sensitive">sensitive</option>
            </select>
          </div>
          <div class="field">
            <label for="proposal-expiration">Expiration</label>
            <input id="proposal-expiration" type="datetime-local">
          </div>
          <div class="field">
            <label for="proposal-source-reference">Source reference</label>
            <input id="proposal-source-reference" type="text" maxlength="1000">
          </div>
          <div class="field full">
            <label for="proposal-reason">Proposal reason</label>
            <textarea id="proposal-reason" maxlength="1000"></textarea>
          </div>
        </div>
        <div class="actions">
          <button id="proposal-submit-button" type="submit">Create pending proposal</button>
          <button id="proposal-reset-button" type="button" class="secondary">Reset form</button>
        </div>
      </form>
    </section>

    <section aria-labelledby="stored-memory-title">
      <h2 id="stored-memory-title">Stored memories</h2>
      <form id="memory-filter-form" class="filter-grid">
        <div class="field">
          <label for="memory-search-query">Search</label>
          <input id="memory-search-query" type="search" maxlength="200" placeholder="Content, type, scope, or provenance">
        </div>
        <div class="field">
          <label for="memory-status-filter">Status</label>
          <select id="memory-status-filter">
            <option value="">all</option>
            <option value="pending">pending</option>
            <option value="approved">approved</option>
            <option value="disabled">disabled</option>
            <option value="rejected">rejected</option>
          </select>
        </div>
        <div class="field">
          <label for="memory-type-filter">Memory type</label>
          <select id="memory-type-filter">
            <option value="">all</option>
            <option value="preference">preference</option>
            <option value="personal_fact">personal_fact</option>
            <option value="goal">goal</option>
            <option value="constraint">constraint</option>
            <option value="project_fact">project_fact</option>
            <option value="decision">decision</option>
            <option value="routine">routine</option>
            <option value="terminology">terminology</option>
            <option value="agent_instruction">agent_instruction</option>
          </select>
        </div>
        <div class="field">
          <label for="memory-scope-filter">Scope type</label>
          <select id="memory-scope-filter">
            <option value="">all</option>
            <option value="global">global</option>
            <option value="project">project</option>
            <option value="agent">agent</option>
          </select>
        </div>
        <div class="field">
          <label for="memory-scope-value-filter">Scope value</label>
          <input id="memory-scope-value-filter" type="text" maxlength="1000">
        </div>
        <div class="field">
          <label for="memory-page-size">Page size</label>
          <select id="memory-page-size">
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50" selected>50</option>
            <option value="100">100</option>
            <option value="200">200</option>
          </select>
        </div>
        <div class="actions field full">
          <button type="submit">Apply filters</button>
          <button id="memory-clear-filters-button" type="button" class="secondary">Clear filters</button>
          <button id="memory-list-refresh-button" type="button" class="secondary">Refresh list</button>
        </div>
      </form>
      <div class="actions">
        <button id="memory-previous-button" type="button" class="secondary">Previous page</button>
        <button id="memory-next-button" type="button" class="secondary">Next page</button>
        <span id="memory-range-status" class="muted" aria-live="polite">No records displayed.</span>
      </div>
      <div id="memory-list-loading" class="muted">Loading stored memories...</div>
      <div id="memory-list-error" class="empty-state" hidden></div>
      <div id="memory-list-empty" class="empty-state" hidden>No memories match the current filters.</div>
      <div id="memory-list" class="list" aria-busy="true"></div>
    </section>

    <div class="layout-two">
      <section aria-labelledby="review-title">
        <h2 id="review-title">Memory review</h2>
        <div id="memory-detail-empty" class="empty-state">Select Review on a stored memory to inspect its content, provenance, and lifecycle.</div>
        <div id="memory-detail-loading" class="muted" hidden>Loading selected memory...</div>
        <div id="memory-detail-error" class="empty-state" hidden></div>
        <div id="memory-detail" hidden>
          <h3>Full content</h3>
          <div id="memory-detail-content" class="content-full"></div>
          <h3>Record details</h3>
          <dl id="memory-detail-fields"></dl>
          <div id="memory-lifecycle-actions" class="actions"></div>
          <p id="memory-lifecycle-guidance" class="help"></p>
        </div>

        <div id="approval-confirmation" class="confirmation" hidden>
          <h3>Confirm approval</h3>
          <p id="approval-summary"></p>
          <p>Approval makes this memory eligible for future retrieval when it is unexpired and in scope.</p>
          <label class="inline-check" for="approval-confirm-checkbox">
            <input id="approval-confirm-checkbox" type="checkbox">
            <span>I reviewed the type, scope, and sensitivity and explicitly approve this memory.</span>
          </label>
          <div class="actions">
            <button id="approval-final-button" type="button" disabled>Approve memory</button>
            <button type="button" class="secondary confirmation-cancel">Cancel</button>
          </div>
        </div>

        <div id="rejection-confirmation" class="confirmation" hidden>
          <h3>Reject pending memory</h3>
          <p>Rejected memory remains stored but inactive.</p>
          <div class="field">
            <label for="rejection-reason">Optional rejection reason</label>
            <textarea id="rejection-reason" maxlength="1000"></textarea>
          </div>
          <div class="actions">
            <button id="rejection-final-button" type="button" class="warning">Reject memory</button>
            <button type="button" class="secondary confirmation-cancel">Cancel</button>
          </div>
        </div>

        <div id="disable-confirmation" class="confirmation" hidden>
          <h3>Confirm disable</h3>
          <p>Disabling keeps the record but prevents active use.</p>
          <label class="inline-check" for="disable-confirm-checkbox">
            <input id="disable-confirm-checkbox" type="checkbox">
            <span>I understand this approved memory will become inactive.</span>
          </label>
          <div class="actions">
            <button id="disable-final-button" type="button" class="warning" disabled>Disable memory</button>
            <button type="button" class="secondary confirmation-cancel">Cancel</button>
          </div>
        </div>

        <div id="enable-confirmation" class="confirmation" hidden>
          <h3>Confirm enable</h3>
          <p>Enabling restores approved status without changing content. An expired record remains expired.</p>
          <label class="inline-check" for="enable-confirm-checkbox">
            <input id="enable-confirm-checkbox" type="checkbox">
            <span>I explicitly want to restore approved status.</span>
          </label>
          <div class="actions">
            <button id="enable-final-button" type="button" disabled>Enable memory</button>
            <button type="button" class="secondary confirmation-cancel">Cancel</button>
          </div>
        </div>

        <div id="delete-confirmation" class="confirmation danger" hidden>
          <h3>Hard-delete memory</h3>
          <p class="danger-text">This action is destructive.</p>
          <ul>
            <li>Memory content will be removed from the memories table.</li>
            <li>Redacted audit metadata may remain.</li>
            <li>The action cannot be undone through Jarvis.</li>
          </ul>
          <div class="field">
            <label for="delete-confirm-input">Type DELETE to continue</label>
            <input id="delete-confirm-input" type="text" autocomplete="off">
          </div>
          <div class="actions">
            <button id="delete-final-button" type="button" class="danger" disabled>Delete permanently</button>
            <button type="button" class="secondary confirmation-cancel">Cancel</button>
          </div>
        </div>
      </section>

      <section id="memory-edit-section" aria-labelledby="edit-title" hidden>
        <h2 id="edit-title">Edit selected memory</h2>
        <p id="edit-reapproval-warning" class="status-line" hidden>
          Substantive changes will return this memory to pending and require approval again.
        </p>
        <form id="memory-edit-form">
          <div class="form-grid">
            <div class="field full">
              <label for="edit-content">Content</label>
              <textarea id="edit-content" maxlength="4000" required></textarea>
              <div id="edit-content-count" class="counter" aria-live="polite">4,000 characters remaining</div>
            </div>
            <div class="field">
              <label for="edit-memory-type">Memory type</label>
              <select id="edit-memory-type" required>
                <option value="preference">preference</option>
                <option value="personal_fact">personal_fact</option>
                <option value="goal">goal</option>
                <option value="constraint">constraint</option>
                <option value="project_fact">project_fact</option>
                <option value="decision">decision</option>
                <option value="routine">routine</option>
                <option value="terminology">terminology</option>
                <option value="agent_instruction">agent_instruction</option>
              </select>
            </div>
            <div class="field">
              <label for="edit-scope-type">Scope type</label>
              <select id="edit-scope-type" required>
                <option value="global">global</option>
                <option value="project">project</option>
                <option value="agent">agent</option>
              </select>
            </div>
            <div class="field">
              <label for="edit-scope-value">Scope value</label>
              <input id="edit-scope-value" type="text" maxlength="1000">
            </div>
            <div class="field">
              <label for="edit-source-type">Source type</label>
              <select id="edit-source-type" required>
                <option value="manual">manual</option>
                <option value="agent_proposal">agent_proposal</option>
                <option value="migration">migration</option>
              </select>
            </div>
            <div class="field">
              <label for="edit-source-agent-id">Source agent ID</label>
              <input id="edit-source-agent-id" type="text" maxlength="200">
            </div>
            <div class="field">
              <label for="edit-source-reference">Source reference</label>
              <input id="edit-source-reference" type="text" maxlength="1000">
            </div>
            <div class="field">
              <label for="edit-confidence">Confidence</label>
              <select id="edit-confidence" required>
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
              </select>
            </div>
            <div class="field">
              <label for="edit-sensitivity">Sensitivity</label>
              <select id="edit-sensitivity" required>
                <option value="standard">standard</option>
                <option value="sensitive">sensitive</option>
              </select>
            </div>
            <div class="field">
              <label for="edit-expiration">Expiration</label>
              <input id="edit-expiration" type="datetime-local">
            </div>
            <div class="field full">
              <label for="edit-proposal-reason">Proposal reason</label>
              <textarea id="edit-proposal-reason" maxlength="1000"></textarea>
            </div>
          </div>
          <div class="actions">
            <button id="edit-submit-button" type="submit">Apply memory edit</button>
            <button id="edit-cancel-button" type="button" class="secondary">Cancel editing</button>
          </div>
        </form>
        <div id="edit-result" class="status-line" aria-live="polite">No edit submitted.</div>
      </section>
    </div>

    <section aria-labelledby="event-history-title">
      <div class="actions">
        <div>
          <h2 id="event-history-title">Redacted event history</h2>
          <p class="muted">Safe transition metadata only; full memory content is not included.</p>
        </div>
        <button id="event-history-refresh-button" type="button" class="secondary" disabled>Refresh event history</button>
      </div>
      <div id="event-history-loading" class="muted" hidden>Loading redacted memory events...</div>
      <div id="event-history-error" class="empty-state" hidden></div>
      <div id="event-history-empty" class="empty-state">Select a memory to inspect its event history.</div>
      <div id="event-history-list" class="list" aria-busy="false"></div>
    </section>

    <section aria-labelledby="context-preview-title">
      <h2 id="context-preview-title">Manual context preview</h2>
      <div class="status-line">
        <strong>No agent was invoked · No relevance ranking · Not yet used in agent responses</strong>
      </div>
      <p>
        This administrative preview shows approved, unexpired memories that match the supplied scope context.
        It performs no injection, proposal generation, persistence, or response-agent execution.
      </p>
      <form id="context-preview-form">
        <div class="form-grid">
          <div class="field">
            <label for="context-project-name">Project name</label>
            <input id="context-project-name" type="text" maxlength="200">
          </div>
          <div class="field">
            <label for="context-agent-id">Agent ID</label>
            <input id="context-agent-id" type="text" maxlength="200">
          </div>
          <div class="field">
            <label for="context-limit">Result limit</label>
            <input id="context-limit" type="number" min="1" max="200" value="50" required>
          </div>
        </div>
        <button id="context-preview-button" type="submit">Run manual context preview</button>
      </form>
      <div id="context-preview-loading" class="muted" hidden>Loading manual context preview...</div>
      <div id="context-preview-error" class="empty-state" hidden></div>
      <div id="context-preview-empty" class="empty-state">No preview has been requested in this page session.</div>
      <div id="context-preview-result" hidden>
        <dl id="context-preview-policy"></dl>
        <h3>Matching memories</h3>
        <div id="context-preview-memories" class="list"></div>
        <h3>Limitations</h3>
        <ul id="context-preview-limitations"></ul>
      </div>
    </section>

    <section aria-labelledby="ranked-retrieval-title">
      <h2 id="ranked-retrieval-title">Ranked Retrieval Preview</h2>
      <div class="status-line"><strong>No agent is invoked · No memory is modified · Explicit click only</strong></div>
      <p>Search approved, unexpired, in-scope memories using FTS5 when available or the disclosed deterministic fallback.</p>
      <form id="ranked-retrieval-form">
        <div class="form-grid">
          <div class="field full">
            <label for="ranked-retrieval-query">Retrieval query</label>
            <input id="ranked-retrieval-query" type="text" maxlength="1000" required autocomplete="off">
          </div>
          <div class="field">
            <label for="ranked-retrieval-project">Project name</label>
            <input id="ranked-retrieval-project" type="text" maxlength="200" autocomplete="off">
          </div>
          <div class="field">
            <label for="ranked-retrieval-agent">Agent ID</label>
            <select id="ranked-retrieval-agent">
              <option value="">No agent scope</option>
              <option value="local_planning_agent">local_planning_agent</option>
              <option value="local_drafting_agent">local_drafting_agent</option>
              <option value="local_decision_agent">local_decision_agent</option>
              <option value="local_career_agent">local_career_agent</option>
              <option value="local_personal_knowledge_memory_organizer">local_personal_knowledge_memory_organizer</option>
              <option value="local_life_dashboard_cross_agent_coordinator">local_life_dashboard_cross_agent_coordinator</option>
            </select>
          </div>
          <div class="field">
            <label for="ranked-retrieval-max-items">Maximum results</label>
            <input id="ranked-retrieval-max-items" type="number" min="1" max="10" value="5" required>
          </div>
          <label class="inline-check" for="ranked-retrieval-sensitive">
            <input id="ranked-retrieval-sensitive" type="checkbox">
            <span>Include approved sensitive memories. These may contain personal information.</span>
          </label>
        </div>
        <button id="ranked-retrieval-button" type="submit">Run ranked retrieval preview</button>
      </form>
      <div id="ranked-retrieval-loading" class="muted" hidden>Loading ranked retrieval preview...</div>
      <div id="ranked-retrieval-error" class="empty-state" hidden></div>
      <div id="ranked-retrieval-empty" class="empty-state">No ranked preview has been requested in this page session.</div>
      <div id="ranked-retrieval-result" hidden>
        <dl id="ranked-retrieval-metadata"></dl>
        <div id="ranked-retrieval-items" class="list"></div>
        <h3>Limitations</h3>
        <ul id="ranked-retrieval-limitations"></ul>
      </div>
    </section>

    <section aria-labelledby="retrieval-audit-title">
      <h2 id="retrieval-audit-title">Retrieval Audit History</h2>
      <p class="muted">Redacted metadata only. Raw queries and historical memory content are not stored or displayed.</p>
      <div class="filter-grid">
        <div class="field">
          <label for="retrieval-audit-agent">Pilot-agent filter</label>
          <select id="retrieval-audit-agent">
            <option value="">All agents and manual previews</option>
            <option value="local_planning_agent">local_planning_agent</option>
            <option value="local_drafting_agent">local_drafting_agent</option>
            <option value="local_decision_agent">local_decision_agent</option>
            <option value="local_career_agent">local_career_agent</option>
            <option value="local_personal_knowledge_memory_organizer">local_personal_knowledge_memory_organizer</option>
            <option value="local_life_dashboard_cross_agent_coordinator">local_life_dashboard_cross_agent_coordinator</option>
          </select>
        </div>
        <div class="field">
          <label for="retrieval-audit-purpose">Purpose</label>
          <select id="retrieval-audit-purpose">
            <option value="">all</option>
            <option value="manual_preview">manual_preview</option>
            <option value="agent_response">agent_response</option>
          </select>
        </div>
        <div class="field">
          <label for="retrieval-audit-page-size">Page size</label>
          <select id="retrieval-audit-page-size"><option value="10">10</option><option value="25" selected>25</option><option value="50">50</option></select>
        </div>
      </div>
      <div class="actions">
        <button id="retrieval-audit-refresh" type="button">Refresh retrieval history</button>
        <button id="retrieval-audit-previous" type="button" class="secondary">Previous page</button>
        <button id="retrieval-audit-next" type="button" class="secondary">Next page</button>
        <span id="retrieval-audit-range" class="muted">No retrieval history loaded.</span>
      </div>
      <div id="retrieval-audit-error" class="empty-state" hidden></div>
      <div id="retrieval-audit-list" class="list"></div>
      <div id="retrieval-audit-detail" class="row stack muted">Select a retrieval to inspect redacted ranked item metadata.</div>
    </section>
  </main>

  <script>
    let privateSession = false;
    let selectedMemory = null;
    let currentRecords = [];
    let currentEvents = [];
    let currentOffset = 0;
    let retrievalOffset = 0;

    const byId = (id) => document.getElementById(id);

    function setActionStatus(message, tone = "info") {
      const target = byId("memory-action-status");
      target.textContent = message;
      target.dataset.tone = tone;
    }

    function setHidden(id, hidden) {
      byId(id).hidden = hidden;
    }

    function createElement(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined && text !== null) node.textContent = String(text);
      return node;
    }

    function addDefinition(list, label, value) {
      list.append(
        createElement("dt", "", label),
        createElement("dd", "", value === null || value === undefined || value === "" ? "Not provided" : value)
      );
    }

    function formatDate(value) {
      if (!value) return "Not set";
      const parsed = new Date(value);
      return Number.isNaN(parsed.getTime()) ? "Invalid timestamp" : parsed.toLocaleString();
    }

    function toUtcIso(localValue) {
      if (!localValue) return null;
      const parsed = new Date(localValue);
      if (Number.isNaN(parsed.getTime())) throw new Error("Expiration must be a valid local date and time.");
      return parsed.toISOString();
    }

    function toLocalInputValue(isoValue) {
      if (!isoValue) return "";
      const parsed = new Date(isoValue);
      if (Number.isNaN(parsed.getTime())) return "";
      const local = new Date(parsed.getTime() - parsed.getTimezoneOffset() * 60000);
      return local.toISOString().slice(0, 16);
    }

    function normalizedOrNull(value) {
      const normalized = String(value || "").trim();
      return normalized || null;
    }

    function scopeLabel(memory) {
      return memory.scopeType === "global"
        ? "global"
        : `${memory.scopeType}: ${memory.scopeValue || "missing scope value"}`;
    }

    async function requestJson(url, options = {}) {
      let response;
      try {
        response = await fetch(url, options);
      } catch {
        throw new Error("The local Jarvis request could not be reached.");
      }
      let data = null;
      try {
        const bodyText = await response.text();
        data = bodyText ? JSON.parse(bodyText) : null;
      } catch {
        data = null;
      }
      if (!response.ok) {
        const detail = data && typeof data.detail === "string"
          ? data.detail
          : "The local Jarvis request could not be completed.";
        throw new Error(detail);
      }
      return data;
    }

    async function loadSummary() {
      setHidden("summary-loading", false);
      setHidden("summary-error", true);
      byId("summary-metrics").setAttribute("aria-busy", "true");
      try {
        const summary = await requestJson("/api/memory/summary");
        const counts = summary.counts || {};
        byId("summary-total").textContent = String(summary.total || 0);
        byId("summary-pending").textContent = String(counts.pending || 0);
        byId("summary-active").textContent = String(summary.active || 0);
        byId("summary-approved").textContent = String(counts.approved || 0);
        byId("summary-disabled").textContent = String(counts.disabled || 0);
        byId("summary-rejected").textContent = String(counts.rejected || 0);
        byId("summary-expired").textContent = String(summary.expired || 0);
        byId("summary-inactive").textContent = String(summary.inactive || 0);
        setHidden("summary-empty", Number(summary.total || 0) !== 0);
      } catch (error) {
        byId("summary-error").textContent = error.message;
        setHidden("summary-error", false);
      } finally {
        setHidden("summary-loading", true);
        byId("summary-metrics").setAttribute("aria-busy", "false");
      }
    }

    function updateCounter(inputId, counterId) {
      const remaining = 4000 - byId(inputId).value.length;
      byId(counterId).textContent = `${remaining.toLocaleString()} characters remaining`;
    }

    function updateScopeRequirement(scopeId, valueId) {
      const requiresValue = byId(scopeId).value !== "global";
      byId(valueId).required = requiresValue;
      if (!requiresValue) byId(valueId).value = "";
    }

    async function submitProposal(event) {
      event.preventDefault();
      const form = event.currentTarget;
      if (!form.reportValidity()) return;
      updateScopeRequirement("proposal-scope-type", "proposal-scope-value");
      const scopeType = byId("proposal-scope-type").value;
      const scopeValue = normalizedOrNull(byId("proposal-scope-value").value);
      if (scopeType !== "global" && !scopeValue) {
        setActionStatus("Project and agent scopes require a scope value.", "error");
        byId("proposal-scope-value").focus();
        return;
      }
      const submitButton = byId("proposal-submit-button");
      submitButton.disabled = true;
      try {
        const created = await requestJson("/api/memories/proposals", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            memoryType: byId("proposal-memory-type").value,
            content: byId("proposal-content").value,
            scopeType,
            scopeValue,
            sourceType: "manual",
            sourceReference: normalizedOrNull(byId("proposal-source-reference").value),
            proposalReason: normalizedOrNull(byId("proposal-reason").value),
            confidence: byId("proposal-confidence").value,
            sensitivity: byId("proposal-sensitivity").value,
            expiresAt: toUtcIso(byId("proposal-expiration").value),
            actor: "local_user"
          })
        });
        form.reset();
        updateScopeRequirement("proposal-scope-type", "proposal-scope-value");
        updateCounter("proposal-content", "proposal-content-count");
        setActionStatus("Pending memory proposal created. It is inactive until explicitly approved.", "success");
        currentOffset = 0;
        await Promise.all([loadSummary(), loadMemories()]);
        await selectMemory(created.memoryId);
      } catch (error) {
        setActionStatus(error.message, "error");
      } finally {
        submitButton.disabled = false;
      }
    }

    function filterParameters() {
      const params = new URLSearchParams();
      const values = {
        query: byId("memory-search-query").value.trim(),
        status: byId("memory-status-filter").value,
        memoryType: byId("memory-type-filter").value,
        scopeType: byId("memory-scope-filter").value,
        scopeValue: byId("memory-scope-value-filter").value.trim()
      };
      Object.entries(values).forEach(([key, value]) => {
        if (value) params.set(key, value);
      });
      params.set("limit", byId("memory-page-size").value);
      params.set("offset", String(currentOffset));
      return params;
    }

    async function loadMemories() {
      setHidden("memory-list-loading", false);
      setHidden("memory-list-error", true);
      byId("memory-list").setAttribute("aria-busy", "true");
      try {
        const params = filterParameters();
        const records = await requestJson(`/api/memories?${params.toString()}`);
        currentRecords = records;
        renderMemoryList(records);
        const limit = Number(byId("memory-page-size").value);
        byId("memory-previous-button").disabled = currentOffset === 0;
        byId("memory-next-button").disabled = records.length < limit;
        const start = records.length ? currentOffset + 1 : 0;
        const end = currentOffset + records.length;
        byId("memory-range-status").textContent = records.length
          ? `Displaying ${start}–${end}.`
          : "No records displayed.";
        setHidden("memory-list-empty", records.length !== 0);
      } catch (error) {
        currentRecords = [];
        byId("memory-list").replaceChildren();
        byId("memory-list-error").textContent = error.message;
        setHidden("memory-list-error", false);
        setHidden("memory-list-empty", true);
      } finally {
        setHidden("memory-list-loading", true);
        byId("memory-list").setAttribute("aria-busy", "false");
      }
    }

    function renderMemoryList(records) {
      const list = byId("memory-list");
      list.replaceChildren();
      records.forEach((memory) => {
        const card = createElement("article", "memory-card");
        if (selectedMemory && selectedMemory.memoryId === memory.memoryId) card.classList.add("selected");
        const preview = createElement(
          "div",
          "content-preview",
          memory.content.length > 220 ? `${memory.content.slice(0, 220)}…` : memory.content
        );
        const chips = createElement("div", "chips");
        [
          memory.memoryType,
          `stored: ${memory.status}`,
          `effective: ${memory.effectiveStatus}`,
          memory.active ? "active" : "inactive",
          scopeLabel(memory),
          `confidence: ${memory.confidence}`,
          `sensitivity: ${memory.sensitivity}`,
          `source: ${memory.sourceType}`
        ].forEach((value) => chips.append(createElement("span", "chip", value)));
        const dates = createElement(
          "div",
          "muted",
          `Expiration: ${formatDate(memory.expiresAt)} · Updated: ${formatDate(memory.updatedAt)}`
        );
        const reviewButton = createElement("button", "secondary", "Review");
        reviewButton.type = "button";
        reviewButton.addEventListener("click", () => selectMemory(memory.memoryId));
        card.append(preview, chips, dates, reviewButton);
        list.append(card);
      });
    }

    async function selectMemory(memoryId) {
      hideConfirmationPanels();
      setHidden("memory-detail-empty", true);
      setHidden("memory-detail-error", true);
      setHidden("memory-detail-loading", false);
      try {
        selectedMemory = await requestJson(`/api/memories/${encodeURIComponent(memoryId)}`);
        renderMemoryDetail(selectedMemory);
        renderMemoryList(currentRecords);
        byId("event-history-refresh-button").disabled = false;
        await loadEventHistory();
      } catch (error) {
        selectedMemory = null;
        byId("memory-detail-error").textContent = error.message;
        setHidden("memory-detail-error", false);
      } finally {
        setHidden("memory-detail-loading", true);
      }
    }

    function renderMemoryDetail(memory) {
      setHidden("memory-detail", false);
      byId("memory-detail-content").textContent = memory.content;
      const details = byId("memory-detail-fields");
      details.replaceChildren();
      [
        ["Memory ID", memory.memoryId],
        ["Memory type", memory.memoryType],
        ["Stored status", memory.status],
        ["Effective status", memory.effectiveStatus],
        ["Active", memory.active ? "Yes" : "No"],
        ["Scope", scopeLabel(memory)],
        ["Source type", memory.sourceType],
        ["Source agent ID", memory.sourceAgentId],
        ["Source reference", memory.sourceReference],
        ["Proposal reason", memory.proposalReason],
        ["Confidence", memory.confidence],
        ["Sensitivity", memory.sensitivity],
        ["Expiration", formatDate(memory.expiresAt)],
        ["Created", formatDate(memory.createdAt)],
        ["Last updated", formatDate(memory.updatedAt)],
        ["Approved", formatDate(memory.approvedAt)],
        ["Approved by", memory.approvedBy],
        ["Last confirmed", formatDate(memory.lastConfirmedAt)],
        ["Disabled", formatDate(memory.disabledAt)],
        ["Rejected", formatDate(memory.rejectedAt)],
        ["Rejected by", memory.rejectedBy],
        ["Rejection reason", memory.rejectionReason]
      ].forEach(([label, value]) => addDefinition(details, label, value));
      renderLifecycleActions(memory);
    }

    function actionButton(label, action, className = "secondary") {
      const button = createElement("button", className, label);
      button.type = "button";
      button.addEventListener("click", action);
      return button;
    }

    function renderLifecycleActions(memory) {
      const actions = byId("memory-lifecycle-actions");
      actions.replaceChildren();
      const editLabel = memory.status === "rejected" ? "Edit and return to pending" : "Edit";
      if (memory.status === "pending") {
        actions.append(
          actionButton("Review approval", () => showConfirmation("approval-confirmation")),
          actionButton("Reject", () => showConfirmation("rejection-confirmation"), "warning"),
          actionButton(editLabel, openEditForm)
        );
      } else if (memory.status === "approved") {
        actions.append(
          actionButton("Disable", () => showConfirmation("disable-confirmation"), "warning"),
          actionButton(memory.effectiveStatus === "expired" ? "Edit to renew" : editLabel, openEditForm)
        );
      } else if (memory.status === "disabled") {
        actions.append(
          actionButton("Enable", () => showConfirmation("enable-confirmation")),
          actionButton(editLabel, openEditForm)
        );
      } else if (memory.status === "rejected") {
        actions.append(actionButton(editLabel, openEditForm));
      }
      actions.append(actionButton("Delete", () => showConfirmation("delete-confirmation"), "danger"));
      byId("memory-lifecycle-guidance").textContent =
        memory.status === "approved" && memory.effectiveStatus === "expired"
          ? "This memory is stored as approved but expired and inactive. Editing expiration requires reapproval."
          : "Substantive edits to approved or disabled memory return it to pending for reapproval.";
    }

    function hideConfirmationPanels() {
      ["approval-confirmation", "rejection-confirmation", "disable-confirmation", "enable-confirmation", "delete-confirmation"]
        .forEach((id) => setHidden(id, true));
      byId("approval-confirm-checkbox").checked = false;
      byId("approval-final-button").disabled = true;
      byId("disable-confirm-checkbox").checked = false;
      byId("disable-final-button").disabled = true;
      byId("enable-confirm-checkbox").checked = false;
      byId("enable-final-button").disabled = true;
      byId("delete-confirm-input").value = "";
      byId("delete-final-button").disabled = true;
      byId("rejection-reason").value = "";
    }

    function showConfirmation(id) {
      if (!selectedMemory) return;
      hideConfirmationPanels();
      setHidden(id, false);
      if (id === "approval-confirmation") {
        byId("approval-summary").textContent =
          `Type: ${selectedMemory.memoryType} · Scope: ${scopeLabel(selectedMemory)} · Sensitivity: ${selectedMemory.sensitivity}`;
      }
      byId(id).scrollIntoView({ block: "nearest" });
    }

    async function runSelectedAction(endpoint, body, successMessage) {
      if (!selectedMemory) return;
      const memoryId = selectedMemory.memoryId;
      try {
        const updated = await requestJson(`/api/memories/${encodeURIComponent(memoryId)}/${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body)
        });
        selectedMemory = updated;
        hideConfirmationPanels();
        setActionStatus(successMessage, "success");
        await Promise.all([loadSummary(), loadMemories()]);
        renderMemoryDetail(updated);
        await loadEventHistory();
      } catch (error) {
        setActionStatus(error.message, "error");
      }
    }

    function openEditForm() {
      if (!selectedMemory) return;
      hideConfirmationPanels();
      setHidden("memory-edit-section", false);
      byId("edit-content").value = selectedMemory.content;
      byId("edit-memory-type").value = selectedMemory.memoryType;
      byId("edit-scope-type").value = selectedMemory.scopeType;
      byId("edit-scope-value").value = selectedMemory.scopeValue || "";
      byId("edit-source-type").value = selectedMemory.sourceType;
      byId("edit-source-agent-id").value = selectedMemory.sourceAgentId || "";
      byId("edit-source-reference").value = selectedMemory.sourceReference || "";
      byId("edit-proposal-reason").value = selectedMemory.proposalReason || "";
      byId("edit-confidence").value = selectedMemory.confidence;
      byId("edit-sensitivity").value = selectedMemory.sensitivity;
      byId("edit-expiration").value = toLocalInputValue(selectedMemory.expiresAt);
      setHidden("edit-reapproval-warning", !["approved", "disabled"].includes(selectedMemory.status));
      updateScopeRequirement("edit-scope-type", "edit-scope-value");
      updateCounter("edit-content", "edit-content-count");
      byId("edit-result").textContent = "Review fields before applying an explicit edit.";
      byId("memory-edit-section").scrollIntoView({ block: "start" });
    }

    async function submitEdit(event) {
      event.preventDefault();
      if (!selectedMemory || !event.currentTarget.reportValidity()) return;
      updateScopeRequirement("edit-scope-type", "edit-scope-value");
      const scopeType = byId("edit-scope-type").value;
      const scopeValue = normalizedOrNull(byId("edit-scope-value").value);
      if (scopeType !== "global" && !scopeValue) {
        byId("edit-result").textContent = "Project and agent scopes require a scope value.";
        return;
      }
      const button = byId("edit-submit-button");
      button.disabled = true;
      try {
        const updated = await requestJson(`/api/memories/${encodeURIComponent(selectedMemory.memoryId)}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            memoryType: byId("edit-memory-type").value,
            content: byId("edit-content").value,
            scopeType,
            scopeValue,
            sourceType: byId("edit-source-type").value,
            sourceAgentId: normalizedOrNull(byId("edit-source-agent-id").value),
            sourceReference: normalizedOrNull(byId("edit-source-reference").value),
            proposalReason: normalizedOrNull(byId("edit-proposal-reason").value),
            confidence: byId("edit-confidence").value,
            sensitivity: byId("edit-sensitivity").value,
            expiresAt: toUtcIso(byId("edit-expiration").value),
            actor: "local_user"
          })
        });
        const changedFields = updated.changedFields || [];
        const message = changedFields.length
          ? `Changed fields: ${changedFields.join(", ")}. Status changed: ${updated.statusChanged ? "yes" : "no"}. Reapproval required: ${updated.reapprovalRequired ? "yes" : "no"}.`
          : "No fields changed. No save or status transition occurred.";
        byId("edit-result").textContent = message;
        setActionStatus(message, changedFields.length ? "success" : "info");
        selectedMemory = updated;
        await Promise.all([loadSummary(), loadMemories()]);
        renderMemoryDetail(updated);
        await loadEventHistory();
      } catch (error) {
        byId("edit-result").textContent = error.message;
        setActionStatus(error.message, "error");
      } finally {
        button.disabled = false;
      }
    }

    async function deleteSelectedMemory() {
      if (!selectedMemory || byId("delete-confirm-input").value !== "DELETE") return;
      const memoryId = selectedMemory.memoryId;
      byId("delete-final-button").disabled = true;
      try {
        await requestJson(`/api/memories/${encodeURIComponent(memoryId)}`, { method: "DELETE" });
        selectedMemory = null;
        currentRecords = [];
        currentEvents = [];
        hideConfirmationPanels();
        setHidden("memory-detail", true);
        setHidden("memory-detail-empty", false);
        setHidden("memory-edit-section", true);
        byId("event-history-list").replaceChildren();
        byId("event-history-empty").textContent = "Select a memory to inspect its event history.";
        setHidden("event-history-empty", false);
        byId("event-history-refresh-button").disabled = true;
        setActionStatus("Memory content was deleted. Redacted audit metadata may remain.", "success");
        await Promise.all([loadSummary(), loadMemories()]);
      } catch (error) {
        setActionStatus(error.message, "error");
      }
    }

    async function loadEventHistory() {
      if (!selectedMemory) return;
      setHidden("event-history-loading", false);
      setHidden("event-history-error", true);
      byId("event-history-list").setAttribute("aria-busy", "true");
      try {
        currentEvents = await requestJson(`/api/memories/${encodeURIComponent(selectedMemory.memoryId)}/events`);
        renderEventHistory(currentEvents);
        setHidden("event-history-empty", currentEvents.length !== 0);
        if (!currentEvents.length) byId("event-history-empty").textContent = "No redacted events are available.";
      } catch (error) {
        currentEvents = [];
        byId("event-history-list").replaceChildren();
        byId("event-history-error").textContent = error.message;
        setHidden("event-history-error", false);
        setHidden("event-history-empty", true);
      } finally {
        setHidden("event-history-loading", true);
        byId("event-history-list").setAttribute("aria-busy", "false");
      }
    }

    function renderEventHistory(events) {
      const list = byId("event-history-list");
      list.replaceChildren();
      events.forEach((event) => {
        const card = createElement("article", "event-card");
        const heading = createElement("strong", "", event.eventType);
        const meta = createElement("dl");
        addDefinition(meta, "Actor", event.actor);
        addDefinition(meta, "Timestamp", formatDate(event.createdAt));
        const safeMetadata = event.metadata || {};
        ["transition", "changedFields", "status", "memoryType", "scopeType", "sensitivity", "reasonCategory", "reapprovalRequired"]
          .forEach((key) => {
            if (safeMetadata[key] !== undefined) {
              const value = Array.isArray(safeMetadata[key]) ? safeMetadata[key].join(", ") : safeMetadata[key];
              addDefinition(meta, key, String(value));
            }
          });
        card.append(heading, meta);
        list.append(card);
      });
    }

    async function submitContextPreview(event) {
      event.preventDefault();
      if (!event.currentTarget.reportValidity()) return;
      const button = byId("context-preview-button");
      button.disabled = true;
      setHidden("context-preview-loading", false);
      setHidden("context-preview-error", true);
      setHidden("context-preview-empty", true);
      try {
        const result = await requestJson("/api/memory/context-preview", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            privateSession,
            projectName: normalizedOrNull(byId("context-project-name").value),
            agentId: normalizedOrNull(byId("context-agent-id").value),
            limit: Number(byId("context-limit").value)
          })
        });
        renderContextPreview(result);
        setHidden("context-preview-result", false);
      } catch (error) {
        byId("context-preview-error").textContent = error.message;
        setHidden("context-preview-error", false);
        setHidden("context-preview-result", true);
      } finally {
        setHidden("context-preview-loading", true);
        button.disabled = false;
      }
    }

    function renderContextPreview(result) {
      const policy = byId("context-preview-policy");
      policy.replaceChildren();
      addDefinition(policy, "Memory use allowed", result.policy.memoryUseAllowed ? "Yes" : "No");
      addDefinition(policy, "Private session", result.context.privateSession ? "On" : "Off");
      addDefinition(policy, "Project context", result.context.projectName);
      addDefinition(policy, "Agent context", result.context.agentId);
      addDefinition(policy, "Matching memories", String(result.count));
      const memories = byId("context-preview-memories");
      memories.replaceChildren();
      (result.memories || []).forEach((memory) => {
        const card = createElement("article", "preview-card");
        card.append(
          createElement("strong", "", `${memory.memoryType} · ${scopeLabel(memory)}`),
          createElement("div", "content-full", memory.content),
          createElement("div", "muted", `Status: ${memory.effectiveStatus} · Expiration: ${formatDate(memory.expiresAt)}`)
        );
        memories.append(card);
      });
      if (!(result.memories || []).length) {
        memories.append(createElement(
          "div",
          "empty-state",
          result.context.privateSession
            ? "Private session blocked memory use. Stored memories were not deleted or hidden from administrative review."
            : "No approved, unexpired memories matched this scope context."
        ));
      }
      const limitations = byId("context-preview-limitations");
      limitations.replaceChildren();
      (result.limitations || []).forEach((item) => limitations.append(createElement("li", "", item)));
    }

    function initializeMemoryCenter() {
    async function submitRankedRetrieval(event) {
      event.preventDefault();
      if (!event.currentTarget.reportValidity()) return;
      const button = byId("ranked-retrieval-button");
      button.disabled = true;
      setHidden("ranked-retrieval-loading", false);
      setHidden("ranked-retrieval-error", true);
      setHidden("ranked-retrieval-empty", true);
      try {
        const result = await requestJson("/api/memory/retrieval-preview", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: byId("ranked-retrieval-query").value,
            privateSession,
            projectName: normalizedOrNull(byId("ranked-retrieval-project").value),
            agentId: normalizedOrNull(byId("ranked-retrieval-agent").value),
            includeSensitive: byId("ranked-retrieval-sensitive").checked,
            maxItems: Number(byId("ranked-retrieval-max-items").value)
          })
        });
        renderRankedRetrieval(result);
        setHidden("ranked-retrieval-result", false);
      } catch (error) {
        byId("ranked-retrieval-error").textContent = error.message;
        setHidden("ranked-retrieval-error", false);
        setHidden("ranked-retrieval-result", true);
      } finally {
        setHidden("ranked-retrieval-loading", true);
        button.disabled = false;
      }
    }

    function renderRankedRetrieval(result) {
      const metadata = byId("ranked-retrieval-metadata");
      metadata.replaceChildren();
      addDefinition(metadata, "Blocked", result.blocked ? "Yes" : "No");
      addDefinition(metadata, "Block reason", result.blockReason);
      addDefinition(metadata, "FTS5 available", result.fts5Available ? "Yes" : "No");
      addDefinition(metadata, "Retrieval mode", result.retrievalMode);
      addDefinition(metadata, "Retrieval ID", result.retrievalId);
      addDefinition(metadata, "Normalized query", result.query);
      addDefinition(metadata, "Query term count", String(result.queryTermCount));
      addDefinition(metadata, "Candidates", String(result.candidateCount));
      addDefinition(metadata, "Selected", String(result.selectedCount));
      addDefinition(metadata, "No agent invoked", "Yes");
      addDefinition(metadata, "Memory modified", "No");
      const items = byId("ranked-retrieval-items");
      items.replaceChildren();
      (result.items || []).forEach((item) => {
        const card = createElement("article", "preview-card");
        card.append(
          createElement("strong", "", `#${item.rank} ${item.memoryType} · ${scopeLabel(item)}`),
          createElement("div", "content-full", item.content),
          createElement("div", "muted", `Text score ${item.textScore} · scope ${item.scopePriority} · type ${item.memoryTypePriority} · confidence ${item.confidencePriority}`)
        );
        const reasons = createElement("ul");
        (item.matchReasons || []).forEach((reason) => reasons.append(createElement("li", "", reason)));
        card.append(createElement("strong", "", "Match reasons"), reasons);
        items.append(card);
      });
      if (!(result.items || []).length) {
        items.append(createElement("div", "empty-state", result.blocked ? "Private session blocked ranked retrieval and audit creation." : "No approved, unexpired memories matched the query and exact scope."));
      }
      const limitations = byId("ranked-retrieval-limitations");
      limitations.replaceChildren();
      (result.limitations || []).forEach((item) => limitations.append(createElement("li", "", item)));
    }

    async function loadRetrievalHistory() {
      const limit = Number(byId("retrieval-audit-page-size").value);
      const parameters = new URLSearchParams({ limit: String(limit), offset: String(retrievalOffset) });
      const agentId = normalizedOrNull(byId("retrieval-audit-agent").value);
      const purpose = normalizedOrNull(byId("retrieval-audit-purpose").value);
      if (agentId) parameters.set("agentId", agentId);
      if (purpose) parameters.set("purpose", purpose);
      setHidden("retrieval-audit-error", true);
      try {
        const records = await requestJson(`/api/memory/retrievals?${parameters.toString()}`);
        renderRetrievalHistory(records);
        byId("retrieval-audit-range").textContent = records.length
          ? `Showing ${retrievalOffset + 1}-${retrievalOffset + records.length}.`
          : "No retrievals on this page.";
        byId("retrieval-audit-previous").disabled = retrievalOffset === 0;
        byId("retrieval-audit-next").disabled = records.length < limit;
      } catch (error) {
        byId("retrieval-audit-error").textContent = error.message;
        setHidden("retrieval-audit-error", false);
      }
    }

    function renderRetrievalHistory(records) {
      const list = byId("retrieval-audit-list");
      list.replaceChildren();
      (records || []).forEach((record) => {
        const card = createElement("article", "event-card");
        const heading = createElement("strong", "", `${record.purpose} · ${record.retrievalMode}`);
        const fields = createElement("dl");
        addDefinition(fields, "Retrieval ID", record.retrievalId);
        addDefinition(fields, "Agent", record.agentId);
        addDefinition(fields, "Project", record.projectName);
        addDefinition(fields, "Query hash", record.queryHash);
        addDefinition(fields, "Query term count", String(record.queryTermCount));
        addDefinition(fields, "Include sensitive", record.includeSensitive ? "Yes" : "No");
        addDefinition(fields, "Candidate / selected", `${record.candidateCount} / ${record.selectedCount}`);
        addDefinition(fields, "Timestamp", formatDate(record.createdAt));
        const button = createElement("button", "secondary", "Inspect redacted detail");
        button.type = "button";
        button.addEventListener("click", () => loadRetrievalDetail(record.retrievalId));
        card.append(heading, fields, button);
        list.append(card);
      });
      if (!(records || []).length) list.append(createElement("div", "empty-state", "No retrieval audit records match the current filters."));
    }

    async function loadRetrievalDetail(retrievalId) {
      const detail = byId("retrieval-audit-detail");
      detail.replaceChildren(createElement("div", "muted", "Loading redacted retrieval detail..."));
      try {
        const record = await requestJson(`/api/memory/retrievals/${encodeURIComponent(retrievalId)}`);
        renderRetrievalDetail(record);
      } catch (error) {
        detail.replaceChildren(createElement("div", "empty-state", error.message));
      }
    }

    function renderRetrievalDetail(record) {
      const detail = byId("retrieval-audit-detail");
      detail.className = "row stack";
      detail.replaceChildren(createElement("strong", "", "Redacted retrieval detail"));
      const metadata = createElement("dl");
      addDefinition(metadata, "Retrieval ID", record.retrievalId);
      addDefinition(metadata, "Purpose", record.purpose);
      addDefinition(metadata, "Agent", record.agentId);
      addDefinition(metadata, "Project present", record.projectPresent ? "Yes" : "No");
      addDefinition(metadata, "Project", record.projectName);
      addDefinition(metadata, "Retrieval mode", record.retrievalMode);
      addDefinition(metadata, "Query hash", record.queryHash);
      addDefinition(metadata, "Query term count", String(record.queryTermCount));
      addDefinition(metadata, "Include sensitive", record.includeSensitive ? "Yes" : "No");
      addDefinition(metadata, "Candidate / selected", `${record.candidateCount} / ${record.selectedCount}`);
      addDefinition(metadata, "Timestamp", formatDate(record.createdAt));
      detail.append(metadata);
      (record.items || []).forEach((item) => {
        const itemCard = createElement("article", "preview-card");
        itemCard.append(
          createElement("strong", "", `#${item.rank} ${item.memoryId}`),
          createElement("div", "muted", `${item.memoryType} · ${item.scopeType}`),
          createElement("div", "muted", `Text score ${item.textScore} · scope ${item.scopePriority} · confidence ${item.confidencePriority}`)
        );
        detail.append(itemCard);
      });
      if (!(record.items || []).length) detail.append(createElement("div", "empty-state", "No selected item metadata was recorded."));
    }

      byId("summary-refresh-button").addEventListener("click", loadSummary);
      byId("private-session-toggle").addEventListener("change", (event) => {
        privateSession = event.currentTarget.checked;
        byId("private-session-policy-status").textContent = privateSession
          ? "Private session is on. Manual and ranked previews return zero memories; ranked retrieval creates no audit records or events."
          : "Private session is off. Manual and ranked previews may return approved, unexpired matches.";
      });
      byId("proposal-content").addEventListener("input", () => updateCounter("proposal-content", "proposal-content-count"));
      byId("proposal-scope-type").addEventListener("change", () => updateScopeRequirement("proposal-scope-type", "proposal-scope-value"));
      byId("proposal-form").addEventListener("submit", submitProposal);
      byId("proposal-reset-button").addEventListener("click", () => {
        byId("proposal-form").reset();
        updateScopeRequirement("proposal-scope-type", "proposal-scope-value");
        updateCounter("proposal-content", "proposal-content-count");
      });
      byId("memory-filter-form").addEventListener("submit", (event) => {
        event.preventDefault();
        currentOffset = 0;
        loadMemories();
      });
      byId("memory-clear-filters-button").addEventListener("click", () => {
        byId("memory-filter-form").reset();
        currentOffset = 0;
        loadMemories();
      });
      byId("memory-list-refresh-button").addEventListener("click", loadMemories);
      byId("memory-previous-button").addEventListener("click", () => {
        currentOffset = Math.max(0, currentOffset - Number(byId("memory-page-size").value));
        loadMemories();
      });
      byId("memory-next-button").addEventListener("click", () => {
        currentOffset += Number(byId("memory-page-size").value);
        loadMemories();
      });
      byId("approval-confirm-checkbox").addEventListener("change", (event) => {
        byId("approval-final-button").disabled = !event.currentTarget.checked;
      });
      byId("approval-final-button").addEventListener("click", () => runSelectedAction(
        "approve",
        { resolution: "approve", approvedBy: "local_user" },
        "Memory approved. It is eligible for future retrieval only while active and in scope."
      ));
      byId("rejection-final-button").addEventListener("click", () => runSelectedAction(
        "reject",
        {
          resolution: "reject",
          rejectedBy: "local_user",
          rejectionReason: normalizedOrNull(byId("rejection-reason").value)
        },
        "Memory rejected and inactive."
      ));
      byId("disable-confirm-checkbox").addEventListener("change", (event) => {
        byId("disable-final-button").disabled = !event.currentTarget.checked;
      });
      byId("disable-final-button").addEventListener("click", () => runSelectedAction(
        "disable",
        { actor: "local_user" },
        "Memory disabled. The stored record remains available for administrative review."
      ));
      byId("enable-confirm-checkbox").addEventListener("change", (event) => {
        byId("enable-final-button").disabled = !event.currentTarget.checked;
      });
      byId("enable-final-button").addEventListener("click", () => runSelectedAction(
        "enable",
        { actor: "local_user" },
        "Approved status restored without changing content."
      ));
      byId("delete-confirm-input").addEventListener("input", (event) => {
        byId("delete-final-button").disabled = event.currentTarget.value !== "DELETE";
      });
      byId("delete-final-button").addEventListener("click", deleteSelectedMemory);
      document.querySelectorAll(".confirmation-cancel").forEach((button) => {
        button.addEventListener("click", hideConfirmationPanels);
      });
      byId("edit-content").addEventListener("input", () => updateCounter("edit-content", "edit-content-count"));
      byId("edit-scope-type").addEventListener("change", () => updateScopeRequirement("edit-scope-type", "edit-scope-value"));
      byId("memory-edit-form").addEventListener("submit", submitEdit);
      byId("edit-cancel-button").addEventListener("click", () => setHidden("memory-edit-section", true));
      byId("event-history-refresh-button").addEventListener("click", loadEventHistory);
      byId("context-preview-form").addEventListener("submit", submitContextPreview);
      byId("ranked-retrieval-form").addEventListener("submit", submitRankedRetrieval);
      byId("retrieval-audit-refresh").addEventListener("click", () => {
        retrievalOffset = 0;
        loadRetrievalHistory();
      });
      byId("retrieval-audit-previous").addEventListener("click", () => {
        retrievalOffset = Math.max(0, retrievalOffset - Number(byId("retrieval-audit-page-size").value));
        loadRetrievalHistory();
      });
      byId("retrieval-audit-next").addEventListener("click", () => {
        retrievalOffset += Number(byId("retrieval-audit-page-size").value);
        loadRetrievalHistory();
      });
      byId("retrieval-audit-previous").disabled = true;
      byId("retrieval-audit-next").disabled = true;
      updateScopeRequirement("proposal-scope-type", "proposal-scope-value");
      updateCounter("proposal-content", "proposal-content-count");
      Promise.all([loadSummary(), loadMemories()]);
    }

    document.addEventListener("DOMContentLoaded", initializeMemoryCenter);
  </script>
</body>
</html>"""
