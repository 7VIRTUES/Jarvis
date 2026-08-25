from __future__ import annotations


def assistant_actions_dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jarvis Action Center</title>
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
    .panel, section {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 9px;
      padding: 18px;
      box-shadow: 0 2px 8px rgba(15, 35, 55, 0.05);
    }
    .banner {
      border-left: 6px solid var(--warn);
      background: var(--warn-bg);
      padding: 14px 18px;
      border-radius: 6px;
      font-size: 0.92rem;
    }
    .banner h2 { margin: 0 0 6px; font-size: 1.05rem; color: var(--warn); }
    .banner p { margin: 0; }
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
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
    }
    .metric {
      background: var(--soft);
      border: 1px solid var(--border);
      border-radius: 7px;
      padding: 12px 14px;
      display: grid;
      gap: 4px;
    }
    .metric span { font-size: 0.82rem; color: var(--muted); font-weight: 600; }
    .metric strong { font-size: 1.4rem; color: var(--text); }
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      border-radius: 12px;
      font-weight: 600;
      font-size: 0.8rem;
    }
    .pill.succeeded, .pill.allowed, .pill.approved { background: #dcfce7; color: #14532d; }
    .pill.blocked, .pill.danger, .pill.rejected { background: #fee2e2; color: #991b1b; }
    .pill.waiting_for_approval, .pill.approval_required, .pill.pending { background: #fef3c7; color: #92400e; }
    .pill.running, .pill.queued { background: #dbeafe; color: #1e40af; }
    .pill.canceled, .pill.inactive { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
    .pill.dry-run { background: #f3e8ff; color: #6b21a8; font-weight: 700; }
    .controls-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }
    .filter-group {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }
    select, input[type="text"] {
      font: inherit;
      padding: 6px 10px;
      border: 1px solid #94a3b8;
      border-radius: 5px;
      background: #fff;
      font-size: 0.88rem;
    }
    button, .button {
      font: inherit;
      border: 1px solid var(--accent);
      background: var(--accent);
      color: #fff;
      padding: 7px 13px;
      border-radius: 5px;
      font-weight: 600;
      font-size: 0.88rem;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      text-decoration: none;
    }
    button:hover:not(:disabled) { background: var(--accent-dark); }
    button.secondary { background: #fff; color: var(--accent); border-color: var(--border); }
    button.secondary:hover:not(:disabled) { background: #f1f5f9; }
    button.danger { background: var(--danger); border-color: var(--danger); }
    button.danger:hover:not(:disabled) { background: #881b1b; }
    button.small { padding: 3px 8px; font-size: 0.8rem; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    .table-container {
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
      text-align: left;
    }
    th, td {
      padding: 10px 12px;
      border-bottom: 1px solid #e2e8f0;
      vertical-align: middle;
    }
    th {
      background: #f8fafc;
      font-weight: 700;
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }
    tr:hover td {
      background: #f8fafc;
    }
    .card-list {
      display: grid;
      gap: 10px;
    }
    .item-card {
      border: 1px solid var(--border);
      border-radius: 7px;
      padding: 12px 16px;
      background: #fff;
      display: grid;
      gap: 6px;
    }
    .item-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .muted { color: var(--muted); font-size: 0.85rem; }
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
  </style>
</head>
<body>
<header>
  <div class="header-inner">
    <div>
      <h1>Jarvis Action Center</h1>
      <p class="tagline">Supervised action proposal bridge · Policy previews · Auditable dry-run validation</p>
    </div>
    <nav class="header-nav">
      <a href="/assistant">Assistant</a>
      <a href="/dashboard">Dashboard</a>
      <a href="/actions" class="active">Action Center</a>
      <a href="/memory">Memory Center</a>
      <a href="/knowledge">Knowledge Library</a>
      <a href="/models">Models Center</a>
    </nav>
  </div>
</header>

<main>
  <!-- Strategic Boundary Banner -->
  <section class="banner" role="region" aria-label="Action boundary notice">
    <h2>Supervised Action Center</h2>
    <p>Action Center manages supervised action proposals, policy previews, and execution receipts. <strong><code>inspect_project</code> (read-only metadata inspection), <code>read_project_text_files</code> (bounded source/text reading, max 5 files), <code>write_report</code> (non-destructive Markdown report creation), and <code>modify_project_files_with_codex</code> (controlled coding via conservative Codex execution, max 10 existing files, 1 run, 0 checks, 0 repairs, no auto commit/push) all support explicit supervised execution on registered projects.</strong> No arbitrary shell commands or external network actions are executed.</p>
  </section>

  <!-- Summary Metrics Grid -->
  <section>
    <div class="controls-row">
      <h2 style="margin:0; font-size:1.15rem;">Action Pipeline Summary</h2>
      <button id="refresh-all-btn" class="secondary" type="button">Refresh All</button>
    </div>
    <div class="grid" id="summary-metrics">
      <div class="metric"><span>Total Supervised Tasks</span><strong id="metric-tasks-count">—</strong></div>
      <div class="metric"><span>Real Actions Executed</span><strong id="metric-executed-count">—</strong></div>
      <div class="metric"><span>Dry-Run Validated</span><strong id="metric-succeeded-count">—</strong></div>
      <div class="metric"><span>Policy Blocked</span><strong id="metric-blocked-count">—</strong></div>
      <div class="metric"><span>Action Receipts</span><strong id="metric-receipts-count">—</strong></div>
    </div>
  </section>

  <!-- Supervised Tasks Section -->
  <section>
    <div class="controls-row">
      <div>
        <h2 style="margin:0; font-size:1.15rem;">Supervised Tasks</h2>
        <p class="muted" style="margin:2px 0 0;">Tasks dispatched through TaskQueue. Real execution tasks and dry-run validations are auditable below.</p>
      </div>
      <div class="filter-group">
        <select id="filter-task-status" aria-label="Filter task status">
          <option value="">All Statuses</option>
          <option value="succeeded">Succeeded</option>
          <option value="blocked">Blocked</option>
          <option value="waiting_for_approval">Waiting for Approval</option>
          <option value="running">Running</option>
          <option value="canceled">Canceled</option>
        </select>
        <select id="filter-task-project" aria-label="Filter task project">
          <option value="">All Projects</option>
        </select>
      </div>
    </div>
    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>Task ID</th>
            <th>Project</th>
            <th>Source Agent</th>
            <th>Type</th>
            <th>Status</th>
            <th>Mode</th>
            <th>Summary / Result</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="tasks-table-body">
          <tr><td colspan="9" class="muted" style="text-align:center; padding:20px;">Loading tasks...</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- Action Receipts Section -->
  <section>
    <div class="controls-row">
      <div>
        <h2 style="margin:0; font-size:1.15rem;">Safe Action Runtime Receipts</h2>
        <p class="muted" style="margin:2px 0 0;">Auditable receipts generated by policy validation during dry-run executions.</p>
      </div>
      <div class="filter-group">
        <select id="filter-receipt-status" aria-label="Filter receipt status">
          <option value="">All Outcomes</option>
          <option value="allowed">Allowed</option>
          <option value="blocked">Blocked</option>
          <option value="approval_required">Approval Required</option>
        </select>
      </div>
    </div>
    <div class="card-list" id="receipts-list">
      <div class="muted" style="text-align:center; padding:20px;">Loading receipts...</div>
    </div>
  </section>

  <!-- Approvals Section -->
  <section>
    <div class="controls-row">
      <div>
        <h2 style="margin:0; font-size:1.15rem;">Policy Approvals Queue</h2>
        <p class="muted" style="margin:2px 0 0;">Approvals represent authorization records only and never trigger automated execution.</p>
      </div>
      <div class="filter-group">
        <select id="filter-approval-status" aria-label="Filter approval status">
          <option value="">All Statuses</option>
          <option value="pending" selected>Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>
    </div>
    <div class="card-list" id="approvals-list">
      <div class="muted" style="text-align:center; padding:20px;">Loading approvals...</div>
    </div>
  </section>

  <!-- Codex Controlled Coding Plans Section -->
  <section>
    <div class="controls-row">
      <div>
        <h2 style="margin:0; font-size:1.15rem;">Conservative Codex Plans</h2>
        <p class="muted" style="margin:2px 0 0;">Machine scope manifests and approval states for controlled Codex modifications.</p>
      </div>
    </div>
    <div class="card-list" id="codex-plans-list">
      <div class="muted" style="text-align:center; padding:20px;">Loading Codex plans...</div>
    </div>
  </section>
</main>

<div class="toast" id="toast" role="alert"></div>

<script>
(function() {
  const byId = (id) => document.getElementById(id);

  let state = {
    tasks: [],
    receipts: [],
    approvals: [],
    projects: [],
    codexPlans: [],
  };

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

  async function loadData() {
    try {
      const [tasksRes, receiptsRes, approvalsRes, projectsRes, codexPlansRes] = await Promise.all([
        apiFetch('/tasks'),
        apiFetch('/api/action-receipts'),
        apiFetch('/approvals'),
        apiFetch('/projects'),
        apiFetch('/codex/plans').catch(() => []),
      ]);

      state.tasks = Array.isArray(tasksRes) ? tasksRes : [];
      state.receipts = Array.isArray(receiptsRes) ? receiptsRes : [];
      state.approvals = Array.isArray(approvalsRes) ? approvalsRes : [];
      state.projects = Array.isArray(projectsRes) ? projectsRes : [];
      state.codexPlans = Array.isArray(codexPlansRes) ? codexPlansRes : [];

      updateProjectFilter();
      updateMetrics();
      renderTasks();
      renderReceipts();
      renderApprovals();
      renderCodexPlans();
    } catch (err) {
      showToast('Error loading action center data: ' + err.message);
    }
  }

  function updateProjectFilter() {
    const select = byId('filter-task-project');
    const curVal = select.value;
    select.replaceChildren();
    const allOpt = document.createElement('option');
    allOpt.value = '';
    allOpt.textContent = 'All Projects';
    select.append(allOpt);

    state.projects.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.name;
      opt.textContent = p.name;
      select.append(opt);
    });
    select.value = curVal;
  }

  function updateMetrics() {
    byId('metric-tasks-count').textContent = state.tasks.length;
    byId('metric-executed-count').textContent = state.tasks.filter(t => !t.dry_run && t.status === 'succeeded').length;
    byId('metric-succeeded-count').textContent = state.tasks.filter(t => t.dry_run && t.status === 'succeeded').length;
    byId('metric-blocked-count').textContent = state.tasks.filter(t => t.status === 'blocked').length;
    byId('metric-receipts-count').textContent = state.receipts.length;
  }

  function renderTasks() {
    const tbody = byId('tasks-table-body');
    const statusFilter = byId('filter-task-status').value;
    const projectFilter = byId('filter-task-project').value;

    let filtered = state.tasks;
    if (statusFilter) filtered = filtered.filter(t => t.status === statusFilter);
    if (projectFilter) filtered = filtered.filter(t => t.project_name === projectFilter);

    if (!filtered.length) {
      tbody.innerHTML = '<tr><td colspan="9" class="muted" style="text-align:center; padding:24px;">No supervised tasks matching criteria.</td></tr>';
      return;
    }

    // Sort descending by created_at
    filtered = [...filtered].reverse();

    tbody.replaceChildren();
    filtered.forEach(task => {
      const tr = document.createElement('tr');
      const shortId = (task.task_id || '').slice(0, 8);
      const isTerminal = ['succeeded', 'failed', 'blocked', 'canceled'].includes(task.status);
      const modePill = task.dry_run
        ? '<span class="pill dry-run">dry-run</span>'
        : (task.write_capable ? '<span class="pill active">real (write)</span>' : '<span class="pill active">real (read-only)</span>');

      tr.innerHTML = `
        <td><code title="${escapeHtml(task.task_id)}">${escapeHtml(shortId)}...</code></td>
        <td><strong>${escapeHtml(task.project_name || '—')}</strong></td>
        <td><span class="muted">${escapeHtml(task.agent_id || '—')}</span></td>
        <td>${escapeHtml(task.task_type || '—')}</td>
        <td><span class="pill ${escapeHtml(task.status)}">${escapeHtml(task.status)}</span></td>
        <td>${modePill}</td>
        <td>${escapeHtml(task.summary || task.error || (task.dry_run ? 'Validated without execution' : 'Executed'))}</td>
        <td class="muted" style="font-size:0.8rem;">${escapeHtml(task.created_at || '—')}</td>
        <td>
          ${!isTerminal ? `<button class="danger small" data-cancel-id="${escapeHtml(task.task_id)}">Cancel</button>` : '<span class="muted">—</span>'}
        </td>
      `;

      const cancelBtn = tr.querySelector(`[data-cancel-id="${task.task_id}"]`);
      if (cancelBtn) {
        cancelBtn.addEventListener('click', async () => {
          if (!confirm(`Cancel supervised task ${shortId}?`)) return;
          try {
            await apiFetch(`/tasks/${task.task_id}/cancel`, { method: 'POST' });
            showToast(`Task ${shortId} canceled.`);
            loadData();
          } catch (err) {
            showToast(`Cancel failed: ${err.message}`);
          }
        });
      }

      tbody.append(tr);
    });
  }

  function renderReceipts() {
    const list = byId('receipts-list');
    const statusFilter = byId('filter-receipt-status').value;

    let filtered = state.receipts;
    if (statusFilter === 'allowed') filtered = filtered.filter(r => r.approved && !r.blocked);
    if (statusFilter === 'blocked') filtered = filtered.filter(r => r.blocked);
    if (statusFilter === 'approval_required') filtered = filtered.filter(r => r.approval_required);

    if (!filtered.length) {
      list.innerHTML = '<div class="muted" style="text-align:center; padding:20px;">No action receipts matching criteria.</div>';
      return;
    }

    // Sort descending by finished_at
    filtered = [...filtered].reverse();

    list.replaceChildren();
    filtered.slice(0, 30).forEach(receipt => {
      const card = document.createElement('div');
      card.className = 'item-card';

      let statusBadge = '';
      if (receipt.result === 'executed_read_only') statusBadge = '<span class="pill active">Executed Read-Only</span>';
      else if (receipt.result === 'executed_write_report') statusBadge = '<span class="pill active">Created Local Report</span>';
      else if (receipt.result === 'execution_failed') statusBadge = '<span class="pill blocked">Execution Failed</span>';
      else if (receipt.blocked) statusBadge = '<span class="pill blocked">Blocked</span>';
      else if (receipt.approval_required) statusBadge = '<span class="pill approval_required">Approval Required</span>';
      else if (receipt.approved) statusBadge = '<span class="pill allowed">Allowed</span>';
      else statusBadge = `<span class="pill inactive">${escapeHtml(receipt.result || 'unknown')}</span>`;

      card.innerHTML = `
        <div class="item-header">
          <div style="display:flex; align-items:center; gap:8px;">
            <strong>Action: ${escapeHtml(receipt.action_type)}</strong>
            <span class="muted">· Tool: ${escapeHtml(receipt.tool_id)}</span>
            <span class="muted">· Target: <strong>${escapeHtml(receipt.target || '—')}</strong></span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            ${statusBadge}
            <span class="pill inactive">Risk: ${escapeHtml(receipt.risk_level)}</span>
            <span class="muted" style="font-size:0.8rem;">${escapeHtml(receipt.finished_at || receipt.started_at)}</span>
          </div>
        </div>
        <div style="font-size:0.86rem; color:var(--muted);">
          Reason: ${escapeHtml(receipt.reason || 'None provided')}
          <span style="margin-left:12px;">Receipt ID: <code>${escapeHtml(receipt.receipt_id)}</code></span>
          ${receipt.task_id ? `<span style="margin-left:8px;">Task: <code>${escapeHtml(receipt.task_id.slice(0, 8))}...</code></span>` : ''}
        </div>
      `;
      list.append(card);
    });
  }

  function renderApprovals() {
    const list = byId('approvals-list');
    const statusFilter = byId('filter-approval-status').value;

    let filtered = state.approvals;
    if (statusFilter) filtered = filtered.filter(a => a.status === statusFilter);

    if (!filtered.length) {
      list.innerHTML = '<div class="muted" style="text-align:center; padding:20px;">No approvals matching criteria.</div>';
      return;
    }

    // Sort descending by requested_at
    filtered = [...filtered].reverse();

    list.replaceChildren();
    filtered.forEach(approval => {
      const card = document.createElement('div');
      card.className = 'item-card';

      card.innerHTML = `
        <div class="item-header">
          <div style="display:flex; align-items:center; gap:8px;">
            <strong>${escapeHtml(approval.action_type)}</strong>
            <span class="muted">· Project: <strong>${escapeHtml(approval.project_name || '—')}</strong></span>
            <span class="pill ${escapeHtml(approval.status)}">${escapeHtml(approval.status)}</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="pill inactive">Risk: ${escapeHtml(approval.risk_level)}</span>
            <span class="muted" style="font-size:0.8rem;">${escapeHtml(approval.requested_at || '—')}</span>
          </div>
        </div>
        <div style="font-size:0.86rem; color:var(--muted);">
          Reason: ${escapeHtml(approval.reason || 'None provided')}
          <span style="margin-left:12px;">Approval ID: <code>${escapeHtml(approval.approval_id)}</code></span>
        </div>
        ${approval.status === 'pending' ? `
          <div style="display:flex; align-items:center; justify-content:space-between; margin-top:8px; padding-top:8px; border-top:1px solid #e2e8f0;">
            <span class="muted" style="font-size:0.82rem;">Note: Approval authorises policy check only — does not execute any local action.</span>
            <div style="display:flex; gap:8px;">
              <button class="secondary small" data-reject-id="${escapeHtml(approval.approval_id)}">Reject</button>
              <button class="small" data-approve-id="${escapeHtml(approval.approval_id)}">Approve Policy State</button>
            </div>
          </div>
        ` : (approval.resolved_by ? `
          <div class="muted" style="font-size:0.8rem; margin-top:4px;">
            Resolved by ${escapeHtml(approval.resolved_by)} at ${escapeHtml(approval.resolved_at || '—')}
            ${approval.resolution_note ? `· Note: ${escapeHtml(approval.resolution_note)}` : ''}
          </div>
        ` : '')}
      `;

      const approveBtn = card.querySelector(`[data-approve-id="${approval.approval_id}"]`);
      if (approveBtn) {
        approveBtn.addEventListener('click', async () => {
          try {
            await apiFetch(`/approvals/${approval.approval_id}/approve`, {
              method: 'POST',
              body: JSON.stringify({ resolvedBy: 'local_user', resolutionNote: 'Approved via Action Center' })
            });
            showToast('Approval updated — no action has been executed.');
            loadData();
          } catch (err) {
            showToast(`Approve failed: ${err.message}`);
          }
        });
      }

      const rejectBtn = card.querySelector(`[data-reject-id="${approval.approval_id}"]`);
      if (rejectBtn) {
        rejectBtn.addEventListener('click', async () => {
          try {
            await apiFetch(`/approvals/${approval.approval_id}/reject`, {
              method: 'POST',
              body: JSON.stringify({ resolvedBy: 'local_user', resolutionNote: 'Rejected via Action Center' })
            });
            showToast('Approval rejected.');
            loadData();
          } catch (err) {
            showToast(`Reject failed: ${err.message}`);
          }
        });
      }

      list.append(card);
    });
  }

  function renderCodexPlans() {
    const list = byId('codex-plans-list');
    if (!list) return;
    if (!state.codexPlans || !state.codexPlans.length) {
      list.innerHTML = '<div class="muted" style="text-align:center; padding:20px;">No conservative Codex plans created yet.</div>';
      return;
    }

    const sorted = [...state.codexPlans].reverse();
    list.replaceChildren();
    sorted.forEach(plan => {
      const card = document.createElement('div');
      card.className = 'item-card';
      const statusCls = plan.status === 'approved_for_future_execution'
        ? 'succeeded'
        : (plan.status === 'execution_consumed' ? 'inactive' : (plan.status === 'waiting_for_approval' ? 'waiting_for_approval' : 'blocked'));

      card.innerHTML = `
        <div class="item-header">
          <div style="display:flex; align-items:center; gap:8px;">
            <strong>Codex Plan: <code>${escapeHtml((plan.plan_id || '').slice(0, 8))}...</code></strong>
            <span class="muted">· Project: <strong>${escapeHtml(plan.project_name || '—')}</strong></span>
            <span class="pill ${escapeHtml(statusCls)}">${escapeHtml((plan.status || '').toUpperCase())}</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span class="pill inactive">Sandbox: ${escapeHtml(plan.sandbox_mode || 'workspace-write')}</span>
            <span class="muted" style="font-size:0.8rem;">${escapeHtml(plan.created_at || '—')}</span>
          </div>
        </div>
        <div style="font-size:0.86rem; color:var(--muted); margin-top:4px;">
          Task ID: <code>${escapeHtml(plan.task_id || '—')}</code>
          ${plan.approval_id ? `<span style="margin-left:12px;">Approval ID: <code>${escapeHtml(plan.approval_id)}</code></span>` : ''}
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:6px; font-size:0.75rem; margin-top:6px;">
          <span class="pill allowed">1 Run Max</span>
          <span class="pill allowed">0 Auto Checks</span>
          <span class="pill allowed">0 Auto Repairs</span>
          <span class="pill allowed">No Auto Commit/Push</span>
        </div>
      `;
      list.append(card);
    });
  }

  byId('refresh-all-btn').addEventListener('click', loadData);
  byId('filter-task-status').addEventListener('change', renderTasks);
  byId('filter-task-project').addEventListener('change', renderTasks);
  byId('filter-receipt-status').addEventListener('change', renderReceipts);
  byId('filter-approval-status').addEventListener('change', renderApprovals);

  loadData();
})();
</script>
</body>
</html>"""
