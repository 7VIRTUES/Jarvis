from __future__ import annotations


def sources_dashboard_styles() -> str:
    return """
    /* ========================================================
       Assistant Reviewed Sources & Evidence Styles (v0.1E Pass 11)
       ======================================================== */

    .sources-toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 7px;
    }
    .sources-url-bar {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      width: 100%;
    }
    .sources-url-input {
      flex: 1 1 320px;
      padding: 7px 12px;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font: inherit;
      font-size: 0.88rem;
      background: #ffffff;
    }
    .sources-grid {
      display: grid;
      gap: 12px;
      max-height: 540px;
      overflow-y: auto;
      padding-right: 4px;
    }
    .source-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      display: grid;
      gap: 10px;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      position: relative;
    }
    .source-card:hover {
      border-color: var(--accent);
      box-shadow: 0 2px 8px rgba(15, 35, 55, 0.08);
    }
    .source-card.included {
      border-color: #10b981;
      background: #f0fdf4;
      box-shadow: 0 0 0 1px #86efac;
    }
    .source-card.blocked, .source-card.failed {
      border-color: #fca5a5;
      background: #fff5f5;
    }
    .source-card-header {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    .source-card-title {
      font-weight: 700;
      font-size: 0.95rem;
      color: var(--accent-dark);
      word-break: break-word;
    }
    .source-card-url {
      font-family: Consolas, Monaco, monospace;
      font-size: 0.78rem;
      color: #64748b;
      word-break: break-all;
    }
    .source-card-meta {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 6px;
      font-size: 0.78rem;
    }
    .source-excerpt-box {
      font-size: 0.84rem;
      line-height: 1.45;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 5px;
      padding: 8px 10px;
      max-height: 110px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
      color: #334155;
    }
    .source-card-notes {
      display: grid;
      gap: 4px;
    }
    .source-card-notes textarea {
      width: 100%;
      box-sizing: border-box;
      padding: 5px 8px;
      font-size: 0.8rem;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      resize: vertical;
      font-family: inherit;
    }
    .source-card-actions {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding-top: 8px;
      border-top: 1px solid #e2e8f0;
    }

    /* Turn Reviewed Source Evidence & Trace Styles */
    .turn-sources-card {
      background: #f8fafc;
      border: 1px solid #cbd5e1;
      border-radius: 7px;
      padding: 12px;
      margin-top: 10px;
      display: grid;
      gap: 8px;
      font-size: 0.86rem;
    }
    .turn-sources-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 700;
      color: var(--accent-dark);
    }
    .trace-item {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 5px;
      padding: 8px 10px;
      font-size: 0.82rem;
      display: grid;
      gap: 4px;
    }
    .trace-item.unmatched {
      border-color: #fca5a5;
      background: #fff8f8;
    }
    .trace-match-row {
      display: flex;
      align-items: baseline;
      gap: 6px;
      flex-wrap: wrap;
    }
    """


def sources_dashboard_html() -> str:
    return """
  <!-- PANEL: Reviewed Public Sources Workspace -->
  <section class="productivity-panel" id="panel-sources">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <div>
        <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Reviewed Public Sources (<span id="src-total-count">0</span> / 5 included)</h3>
        <p class="muted" style="margin:2px 0 0; font-size:0.84rem;">Optional manual reviewed-public-source context for Unified Assistant requests. Session-only · Bounded excerpt · No auto-fetch.</p>
      </div>
      <div style="display:flex; align-items:center; gap:6px;">
        <button id="sources-clear-btn" class="secondary small" type="button">Clear Sources</button>
      </div>
    </div>

    <!-- URL Entry & Validation Toolbar -->
    <div class="sources-toolbar">
      <div class="sources-url-bar">
        <input type="url" id="source-url-input" class="sources-url-input" placeholder="Enter or paste public HTTP/HTTPS URL (e.g. https://example.org/article)..." />
        <button id="source-validate-btn" class="small" type="button">Validate URL</button>
      </div>
      <div id="source-url-feedback" style="display:none; width:100%; font-size:0.82rem; margin-top:2px;"></div>
    </div>

    <!-- Sources Grid Container -->
    <div class="sources-grid" id="sources-grid">
      <div class="empty-state" style="padding:24px;">
        No reviewed sources in this session. Add a public URL manually if your request would benefit from reviewed source context.
      </div>
    </div>
  </section>

  <!-- MODAL: Source Detail Drawer -->
  <div class="results-modal-backdrop" id="drawer-source-detail">
    <div class="results-modal-card">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h3 id="src-detail-title" style="margin:0; color:var(--accent-dark);">Reviewed Source Details</h3>
          <span id="src-detail-domain" class="muted" style="font-size:0.82rem;"></span>
        </div>
        <button id="close-source-detail-btn" class="secondary small" type="button">✕ Close</button>
      </div>

      <div style="display:grid; gap:12px;">
        <div style="display:flex; flex-wrap:wrap; gap:6px;">
          <span id="src-detail-status-pill" class="pill allowed">Included</span>
          <span id="src-detail-type-pill" class="pill">public_web_excerpt</span>
          <span id="src-detail-recency-pill" class="pill">Recency Unknown</span>
        </div>

        <div>
          <label style="font-weight:600; font-size:0.82rem; color:var(--muted);">Source URL:</label>
          <div id="src-detail-source-url" class="source-card-url" style="background:#f8fafc; padding:6px; border:1px solid #e2e8f0; border-radius:4px;"></div>
        </div>

        <div id="src-detail-final-url-sec" style="display:none;">
          <label style="font-weight:600; font-size:0.82rem; color:var(--muted);">Final Resolved URL:</label>
          <div id="src-detail-final-url" class="source-card-url" style="background:#f8fafc; padding:6px; border:1px solid #e2e8f0; border-radius:4px;"></div>
        </div>

        <div>
          <label style="font-weight:600; font-size:0.82rem; color:var(--muted);">Bounded Excerpt:</label>
          <div id="src-detail-excerpt" style="font-size:0.88rem; line-height:1.5; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:10px; max-height:220px; overflow-y:auto; white-space:pre-wrap;"></div>
        </div>

        <div id="src-detail-warnings-sec" style="display:none;">
          <label style="font-weight:600; font-size:0.82rem; color:#92400e;">Quality Warnings:</label>
          <ul id="src-detail-warnings-list" style="margin:4px 0 0; padding-left:18px; font-size:0.82rem; color:#92400e;"></ul>
        </div>

        <div id="src-detail-limitations-sec" style="display:none;">
          <label style="font-weight:600; font-size:0.82rem; color:var(--muted);">Limitations & Security Boundary:</label>
          <ul id="src-detail-limitations-list" style="margin:4px 0 0; padding-left:18px; font-size:0.82rem; color:var(--muted);"></ul>
        </div>

        <div id="src-detail-notes-sec">
          <label style="font-weight:600; font-size:0.82rem; color:var(--muted);">Reviewer Notes (Session-Only):</label>
          <div id="src-detail-notes" style="font-size:0.84rem; background:#f8fafc; padding:6px 8px; border:1px solid #e2e8f0; border-radius:4px; font-style:italic;"></div>
        </div>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:8px; padding-top:8px; border-top:1px solid #e2e8f0;">
        <button id="src-detail-add-kit-btn" class="secondary small" type="button">🧰 Add Excerpt to Context Kit</button>
        <button id="src-detail-insert-composer-btn" class="secondary small" type="button">📝 Use Excerpt in Request</button>
      </div>
    </div>
  </div>
    """


def sources_dashboard_scripts() -> str:
    return """
  // ==========================================
  // Reviewed Public Sources Workspace (v0.1E Pass 11)
  // ==========================================

  const MAX_SESSION_SOURCES = 5;
  const MAX_INCLUDED_SOURCES = 5;

  sessionState.reviewedSources = [];
  sessionState.activeDetailSource = null;

  function buildIncludedWebContext() {
    const included = sessionState.reviewedSources.filter(s => s.included && s.fetched && s.excerpt);
    return included.slice(0, MAX_INCLUDED_SOURCES).map(s => ({
      source_url: s.sourceUrl,
      final_url: s.finalUrl || s.sourceUrl,
      title: s.title || '',
      domain: s.domain || '',
      excerpt: (s.excerpt || '').slice(0, 4000),
      content_type: s.contentType || 'text/plain',
      fetched: true,
      fetched_at: s.fetchedAt || '',
      user_notes: (s.userNotes || '').slice(0, 500),
      source_type: 'public_web_excerpt',
      limitations: Array.isArray(s.limitations) ? s.limitations : [],
    }));
  }

  function getIncludedReviewedSources() {
    return sessionState.reviewedSources.filter(s => s.included && s.fetched && s.excerpt);
  }

  function updateSourcesCounters() {
    const total = sessionState.reviewedSources.length;
    const included = getIncludedReviewedSources().length;

    const tabSpan = byId('sources-tab-count');
    const totalSpan = byId('src-total-count');
    const compBadge = byId('composer-sources-badge');

    if (tabSpan) tabSpan.textContent = included;
    if (totalSpan) totalSpan.textContent = included;

    if (compBadge) {
      if (included === 0) {
        compBadge.className = 'pill inactive';
        compBadge.textContent = 'No reviewed sources attached';
        compBadge.title = 'Click to open Reviewed Sources panel';
      } else {
        compBadge.className = 'pill allowed';
        compBadge.textContent = `Reviewed Sources: ${included} / 5 attached`;
        compBadge.title = `Click to view ${included} attached reviewed source(s)`;
      }
    }
  }

  async function handleValidateSourceUrl(rawUrl) {
    const fb = byId('source-url-feedback');
    if (!rawUrl || !rawUrl.trim()) {
      if (fb) {
        fb.style.display = 'block';
        fb.innerHTML = '<span style="color:#b91c1c;">Please enter a URL.</span>';
      }
      return;
    }

    if (sessionState.reviewedSources.length >= MAX_SESSION_SOURCES) {
      alert(`Maximum ${MAX_SESSION_SOURCES} session sources reached. Remove an existing source before adding another.`);
      return;
    }

    try {
      const btn = byId('source-validate-btn');
      if (btn) btn.disabled = true;

      const res = await apiFetch('/web-research/validate-url', {
        method: 'POST',
        body: JSON.stringify({ url: rawUrl.trim() })
      });

      if (fb) {
        fb.style.display = 'block';
        if (res.is_allowed) {
          fb.innerHTML = `<span style="color:#15803d; font-weight:600;">✓ Validated:</span> <code>${escapeHtml(res.normalized_url || rawUrl)}</code> <span class="muted">(${escapeHtml(res.domain || '')})</span>`;
        } else {
          fb.innerHTML = `<span style="color:#b91c1c; font-weight:600;">✕ Blocked:</span> ${escapeHtml(res.blocked_reason || (res.warnings || []).join(' ') || 'URL blocked by security boundary')}`;
        }
      }

      const newSource = {
        id: 'src_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
        sourceUrl: res.normalized_url || rawUrl.trim(),
        finalUrl: '',
        title: res.domain ? `Source from ${res.domain}` : 'Reviewed Public Source',
        domain: res.domain || '',
        excerpt: '',
        contentType: '',
        fetched: false,
        fetchedAt: null,
        userNotes: '',
        sourceType: 'public_web_excerpt',
        status: res.is_allowed ? 'validated' : 'blocked',
        included: false,
        validationResult: res,
        fetchResult: null,
        limitations: [],
        qualityWarnings: res.warnings || [],
        recencyNote: 'Recency Unknown',
        errorMessage: res.is_allowed ? null : (res.blocked_reason || 'URL blocked by security boundary'),
      };

      sessionState.reviewedSources.push(newSource);
      updateSourcesCounters();
      renderSourcesGrid();
      triggerReadinessEvaluation();

      // Clear input
      if (byId('source-url-input')) byId('source-url-input').value = '';
    } catch (err) {
      if (fb) {
        fb.style.display = 'block';
        fb.innerHTML = `<span style="color:#b91c1c;">Validation error: ${escapeHtml(err.message)}</span>`;
      }
    } finally {
      const btn = byId('source-validate-btn');
      if (btn) btn.disabled = false;
    }
  }

  async function handleFetchSource(sourceItem) {
    if (!sourceItem || !sourceItem.sourceUrl) return;

    try {
      sourceItem.status = 'fetching';
      renderSourcesGrid();

      const res = await apiFetch('/web-research/fetch-public-url', {
        method: 'POST',
        body: JSON.stringify({
          url: (sourceItem.validationResult && sourceItem.validationResult.normalized_url) || sourceItem.sourceUrl
        })
      });

      if (res.fetched) {
        sourceItem.fetched = true;
        sourceItem.status = 'fetched';
        sourceItem.title = res.title || sourceItem.title || 'Reviewed Public Source';
        sourceItem.domain = res.domain || sourceItem.domain || '';
        sourceItem.finalUrl = res.final_url || sourceItem.sourceUrl;
        sourceItem.contentType = res.content_type || 'text/plain';
        sourceItem.excerpt = res.excerpt || '';
        sourceItem.fetchedAt = res.fetched_at || new Date().toISOString();
        sourceItem.qualityWarnings = Array.isArray(res.quality_warnings) ? res.quality_warnings : [];
        sourceItem.limitations = Array.isArray(res.limitations) ? res.limitations : [];
        sourceItem.recencyNote = res.recency_note || 'Recency Unknown';
        sourceItem.fetchResult = res;
        sourceItem.errorMessage = null;
        showToast(`Fetched excerpt for "${sourceItem.title}". Review excerpt and click Include to attach.`);
      } else {
        sourceItem.fetched = false;
        sourceItem.status = 'failed';
        sourceItem.errorMessage = res.error || (res.warnings || []).join(' ') || 'Fetch failed or content blocked.';
        sourceItem.included = false;
        showToast(`Fetch unavailable: ${sourceItem.errorMessage}`);
      }
    } catch (err) {
      sourceItem.fetched = false;
      sourceItem.status = 'failed';
      sourceItem.errorMessage = err.message || 'Fetch request error';
      sourceItem.included = false;
    } finally {
      updateSourcesCounters();
      renderSourcesGrid();
      triggerReadinessEvaluation();
    }
  }

  function renderSourcesGrid() {
    const grid = byId('sources-grid');
    if (!grid) return;

    if (!sessionState.reviewedSources.length) {
      grid.innerHTML = `
        <div class="empty-state" style="padding:24px;">
          No reviewed sources in this session. Add a public URL manually if your request would benefit from reviewed source context.
        </div>
      `;
      return;
    }

    grid.replaceChildren();
    sessionState.reviewedSources.forEach((s) => {
      const card = document.createElement('div');
      card.className = `source-card ${s.included ? 'included' : ''} ${s.status === 'blocked' ? 'blocked' : (s.status === 'failed' ? 'failed' : '')}`;

      let statusBadge = '';
      if (s.status === 'draft') statusBadge = '<span class="pill inactive">Draft URL</span>';
      else if (s.status === 'validated') statusBadge = '<span class="pill waiting_for_approval">Validated · Ready to Fetch</span>';
      else if (s.status === 'fetching') statusBadge = '<span class="pill active">Fetching Excerpt...</span>';
      else if (s.status === 'fetched') {
        statusBadge = s.included ? '<span class="pill succeeded">✓ Included in Next Request</span>' : '<span class="pill moderate">Fetched — Review Required</span>';
      } else if (s.status === 'blocked') statusBadge = '<span class="pill blocked">Blocked by Policy</span>';
      else if (s.status === 'failed') statusBadge = '<span class="pill danger">Fetch Unavailable</span>';

      card.innerHTML = `
        <div class="source-card-header">
          <div>
            <div class="source-card-title">${escapeHtml(s.title || 'Untitled Source')}</div>
            <div class="source-card-url">${escapeHtml(s.sourceUrl)}</div>
            ${(s.finalUrl && s.finalUrl !== s.sourceUrl) ? `<div class="source-card-url" style="color:#0284c7;">↳ Final: ${escapeHtml(s.finalUrl)}</div>` : ''}
          </div>
          <div style="display:flex; align-items:center; gap:6px;">
            ${statusBadge}
          </div>
        </div>

        ${s.errorMessage ? `
          <div class="banner warning" style="margin:0; font-size:0.8rem; padding:6px 10px;">
            <strong>Notice:</strong> ${escapeHtml(s.errorMessage)}
          </div>
        ` : ''}

        ${s.fetched && s.excerpt ? `
          <div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
              <span class="muted" style="font-size:0.78rem; font-weight:600;">Bounded Excerpt (${s.excerpt.length} chars):</span>
              <span class="muted" style="font-size:0.75rem;">Type: ${escapeHtml(s.contentType || 'text/plain')}</span>
            </div>
            <div class="source-excerpt-box">${escapeHtml(s.excerpt)}</div>
          </div>
        ` : ''}

        <div class="source-card-meta">
          ${s.domain ? `<span class="pill" style="font-size:0.72rem;">${escapeHtml(s.domain)}</span>` : ''}
          ${s.fetchedAt ? `<span class="muted" style="font-size:0.72rem;">Fetched: ${escapeHtml(new Date(s.fetchedAt).toLocaleTimeString())}</span>` : ''}
          ${s.recencyNote ? `<span class="evidence-item-tag citation" style="font-size:0.72rem;">${escapeHtml(s.recencyNote)}</span>` : ''}
          ${(s.qualityWarnings && s.qualityWarnings.length) ? `<span class="diff-badge" style="background:#fef3c7; color:#92400e;">${s.qualityWarnings.length} Warning(s)</span>` : ''}
        </div>

        ${s.fetched ? `
          <div class="source-card-notes">
            <label style="font-size:0.78rem; font-weight:600; color:var(--muted);">Reviewer Notes / Purpose (Session-only, max 500 chars):</label>
            <textarea class="source-notes-input" placeholder="Explain why this source is relevant or what key facts to extract..." rows="2">${escapeHtml(s.userNotes || '')}</textarea>
          </div>
        ` : ''}

        <div class="source-card-actions">
          <div style="display:flex; gap:6px;">
            ${!s.fetched && s.status === 'validated' ? `
              <button class="small" type="button" data-src-action="fetch">📥 Fetch Reviewed Excerpt</button>
            ` : ''}
            ${s.fetched ? `
              <button class="${s.included ? 'secondary small' : 'small'}" type="button" data-src-action="toggle-include" style="${s.included ? '' : 'background:#15803d; border-color:#15803d;'}">
                ${s.included ? '✕ Exclude from Request' : '✓ Include in Next Request'}
              </button>
              <button class="secondary small" type="button" data-src-action="refetch" title="Perform a manual re-fetch of this URL">🔄 Re-fetch</button>
              <button class="secondary small" type="button" data-src-action="inspect">🔍 Inspect Detail</button>
            ` : ''}
          </div>
          <div>
            <button class="secondary small danger" type="button" data-src-action="remove">Remove</button>
          </div>
        </div>
      `;

      // Event bindings
      const notesInput = card.querySelector('.source-notes-input');
      if (notesInput) {
        notesInput.addEventListener('input', (e) => {
          s.userNotes = e.target.value.slice(0, 500);
        });
      }

      card.querySelector('[data-src-action="fetch"]')?.addEventListener('click', () => handleFetchSource(s));
      card.querySelector('[data-src-action="refetch"]')?.addEventListener('click', () => handleFetchSource(s));
      card.querySelector('[data-src-action="inspect"]')?.addEventListener('click', () => openSourceDetailDrawer(s));
      card.querySelector('[data-src-action="toggle-include"]')?.addEventListener('click', () => {
        if (!s.included && getIncludedReviewedSources().length >= MAX_INCLUDED_SOURCES) {
          alert(`Maximum ${MAX_INCLUDED_SOURCES} sources can be included in one request.`);
          return;
        }
        s.included = !s.included;
        updateSourcesCounters();
        renderSourcesGrid();
        triggerReadinessEvaluation();
      });
      card.querySelector('[data-src-action="remove"]')?.addEventListener('click', () => {
        sessionState.reviewedSources = sessionState.reviewedSources.filter(item => item.id !== s.id);
        updateSourcesCounters();
        renderSourcesGrid();
        triggerReadinessEvaluation();
      });

      grid.append(card);
    });
  }

  function openSourceDetailDrawer(s) {
    sessionState.activeDetailSource = s;
    const drawer = byId('drawer-source-detail');
    if (!drawer) return;

    byId('src-detail-title').textContent = s.title || 'Reviewed Public Source';
    byId('src-detail-domain').textContent = s.domain ? `Domain: ${s.domain}` : '';

    const statusPill = byId('src-detail-status-pill');
    if (statusPill) {
      statusPill.className = s.included ? 'pill succeeded' : 'pill moderate';
      statusPill.textContent = s.included ? 'Included in Request' : 'Excluded from Request';
    }

    byId('src-detail-type-pill').textContent = s.sourceType || 'public_web_excerpt';
    byId('src-detail-recency-pill').textContent = s.recencyNote || 'Recency Unknown';

    byId('src-detail-source-url').textContent = s.sourceUrl || '';
    
    const finSec = byId('src-detail-final-url-sec');
    if (s.finalUrl && s.finalUrl !== s.sourceUrl) {
      finSec.style.display = 'block';
      byId('src-detail-final-url').textContent = s.finalUrl;
    } else {
      finSec.style.display = 'none';
    }

    byId('src-detail-excerpt').textContent = s.excerpt || 'No excerpt fetched.';

    const warnSec = byId('src-detail-warnings-sec');
    const warnList = byId('src-detail-warnings-list');
    if (s.qualityWarnings && s.qualityWarnings.length) {
      warnSec.style.display = 'block';
      warnList.innerHTML = s.qualityWarnings.map(w => `<li>${escapeHtml(w)}</li>`).join('');
    } else {
      warnSec.style.display = 'none';
    }

    const limSec = byId('src-detail-limitations-sec');
    const limList = byId('src-detail-limitations-list');
    if (s.limitations && s.limitations.length) {
      limSec.style.display = 'block';
      limList.innerHTML = s.limitations.map(l => `<li>${escapeHtml(l)}</li>`).join('');
    } else {
      limSec.style.display = 'none';
    }

    const notesSec = byId('src-detail-notes-sec');
    const notesText = byId('src-detail-notes');
    if (s.userNotes) {
      notesSec.style.display = 'block';
      notesText.textContent = s.userNotes;
    } else {
      notesSec.style.display = 'none';
    }

    drawer.classList.add('open');
  }

  function initSourcesDashboardEventHandlers() {
    byId('source-validate-btn')?.addEventListener('click', () => {
      const val = byId('source-url-input')?.value || '';
      handleValidateSourceUrl(val);
    });

    byId('source-url-input')?.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const val = byId('source-url-input')?.value || '';
        handleValidateSourceUrl(val);
      }
    });

    byId('sources-clear-btn')?.addEventListener('click', () => {
      if (!sessionState.reviewedSources.length) return;
      if (sessionState.reviewedSources.length === 1 || confirm(`Remove all ${sessionState.reviewedSources.length} reviewed sources from this session?`)) {
        sessionState.reviewedSources = [];
        updateSourcesCounters();
        renderSourcesGrid();
        triggerReadinessEvaluation();
        showToast('Cleared session sources.');
      }
    });

    byId('close-source-detail-btn')?.addEventListener('click', () => {
      byId('drawer-source-detail')?.classList.remove('open');
    });
    byId('drawer-source-detail')?.addEventListener('click', (e) => {
      if (e.target === byId('drawer-source-detail')) byId('drawer-source-detail').classList.remove('open');
    });

    byId('src-detail-add-kit-btn')?.addEventListener('click', () => {
      const s = sessionState.activeDetailSource;
      if (!s || !s.excerpt) return;
      addContextKitItem('reviewed_source', `Reviewed Source — ${s.title || s.domain || 'Excerpt'}`, `Source URL: ${s.sourceUrl}\nDomain: ${s.domain}\n\nExcerpt:\n${s.excerpt}`);
      byId('drawer-source-detail')?.classList.remove('open');
    });

    byId('src-detail-insert-composer-btn')?.addEventListener('click', () => {
      const s = sessionState.activeDetailSource;
      if (!s || !s.excerpt) return;
      const snippet = `[Reviewed Source: ${s.title || s.domain}]\nURL: ${s.sourceUrl}\nExcerpt: ${s.excerpt}\n`;
      const input = byId('prompt-input');
      input.value = (input.value.trim() ? `${input.value.trim()}\n\n${snippet}` : snippet).trim();
      input.focus();
      triggerReadinessEvaluation();
      byId('drawer-source-detail')?.classList.remove('open');
      showToast('Inserted source excerpt into prompt composer.');
      byId('composer').scrollIntoView({ behavior: 'smooth' });
    });

    byId('composer-sources-badge')?.addEventListener('click', () => {
      switchProductivityTab('panel-sources');
    });
  }

  // ==========================================
  // Turn Source Evidence & Citation Trace Renderer
  // ==========================================

  function renderTurnSourceEvidenceHtml(turn, resp, index) {
    const sourceEvidence = resp.source_evidence || (resp.responseContext && resp.responseContext.sourceEvidence) || [];
    const rawCitations = (resp.generatedResponse && resp.generatedResponse.citations) || resp.citations || [];
    
    if (!sourceEvidence.length && !rawCitations.length && !resp.source_use_summary) {
      return '';
    }

    let html = `
      <div class="turn-sources-card">
        <div class="turn-sources-header">
          <span>🌐 Reviewed Source Evidence & Trace</span>
          <span class="pill ${sourceEvidence.length ? 'succeeded' : 'inactive'}" style="font-size:0.75rem;">
            ${sourceEvidence.length} Source(s) Supplied
          </span>
        </div>
    `;

    // 1. Trace of Model Citation Labels to Supplied Reviewed Sources
    if (rawCitations.length) {
      html += `
        <div style="margin-top:4px;">
          <strong style="font-size:0.82rem; color:#334155;">Model Citation Label Trace:</strong>
          <div style="display:grid; gap:4px; margin-top:4px;">
      `;

      rawCitations.forEach((cit, cIdx) => {
        const lbl = (typeof cit === 'object' && cit !== null) ? (cit.label || `Citation ${cIdx + 1}`) : String(cit);
        const supp = (typeof cit === 'object' && cit !== null) ? (cit.supports || 'Model reference') : 'Model reference';

        // Match citation label against response.source_evidence citation_label
        const matchedSource = sourceEvidence.find(s => s.citation_label === lbl || s.citationLabel === lbl || `[${s.citation_label}]` === lbl);

        if (matchedSource) {
          html += `
            <div class="trace-item">
              <div class="trace-match-row">
                <span class="pill allowed" style="font-size:0.72rem; padding:1px 5px;">${escapeHtml(lbl)}</span>
                <strong>${escapeHtml(matchedSource.title || matchedSource.citation_label)}</strong>
                <span class="muted" style="font-size:0.78rem;">(${escapeHtml(matchedSource.domain || matchedSource.source_type || 'web')})</span>
              </div>
              <div class="muted" style="font-size:0.78rem;">
                Model says it supports: <em>"${escapeHtml(supp)}"</em>
              </div>
              <div class="muted" style="font-size:0.75rem; font-style:italic;">
                Recency: ${escapeHtml(matchedSource.recency_note || 'Recency Unknown')} · Trace context only (not certified fact).
              </div>
            </div>
          `;
        } else {
          html += `
            <div class="trace-item unmatched">
              <div class="trace-match-row">
                <span class="diff-badge" style="background:#fee2e2; color:#991b1b;">⚠️ Unmatched Citation Label ${escapeHtml(lbl)}</span>
                <span class="muted" style="font-size:0.78rem;">— Model cited label not matched to supplied source evidence.</span>
              </div>
              <div class="muted" style="font-size:0.78rem;">
                Supports text: <em>"${escapeHtml(supp)}"</em>
              </div>
            </div>
          `;
        }
      });

      html += `</div></div>`;
    }

    // 2. Uncited Reviewed Sources
    if (sourceEvidence.length && rawCitations.length) {
      const uncited = sourceEvidence.filter(s => !rawCitations.some(c => {
        const l = (typeof c === 'object' && c !== null) ? c.label : String(c);
        return l === s.citation_label || l === `[${s.citation_label}]`;
      }));

      if (uncited.length) {
        html += `
          <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">
            <strong>Uncited Sources (${uncited.length}):</strong> ${uncited.map(u => `${escapeHtml(u.citation_label || u.title)}`).join(', ')} — supplied in request but not explicitly referenced by citation label.
          </div>
        `;
      }
    }

    // 3. Supplied Reviewed Sources list
    if (sourceEvidence.length) {
      html += `
        <div style="margin-top:6px;">
          <strong style="font-size:0.82rem; color:#166534;">Supplied Reviewed Sources (${sourceEvidence.length}):</strong>
          <div style="display:grid; gap:4px; margin-top:4px;">
      `;

      sourceEvidence.forEach((s, sIdx) => {
        html += `
          <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:4px; padding:6px 8px; font-size:0.8rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px;">
            <div>
              <span class="pill allowed" style="font-size:0.7rem; padding:1px 5px;">${escapeHtml(s.citation_label || `S${sIdx + 1}`)}</span>
              <strong>${escapeHtml(s.title || 'Reviewed Source')}</strong>
              <span class="muted">(${escapeHtml(s.domain || '')})</span>
              ${s.recency_note ? `<span class="pill" style="font-size:0.7rem;">${escapeHtml(s.recency_note)}</span>` : ''}
            </div>
            <div style="display:flex; align-items:center; gap:4px;">
              <button class="secondary small" type="button" data-turn-inspect-src="${index}" data-src-idx="${sIdx}" style="padding:1px 6px; font-size:0.72rem;">Inspect</button>
            </div>
          </div>
        `;
      });

      html += `</div></div>`;
    }

    // 4. Deterministic Source Trace Fields (if available)
    if (resp.source_use_summary || (resp.source_supported_points && resp.source_supported_points.length) || (resp.source_cautions && resp.source_cautions.length)) {
      html += `
        <details style="margin-top:6px; font-size:0.8rem; background:#ffffff; border:1px solid #e2e8f0; border-radius:4px; padding:6px 8px;">
          <summary style="cursor:pointer; font-weight:600; color:var(--accent-dark);">Deterministic Source Trace / Server Review Notes</summary>
          <div style="display:grid; gap:6px; margin-top:6px; padding-top:6px; border-top:1px solid #f1f5f9;">
            ${resp.source_use_summary ? `<div><strong>Summary of Source Use:</strong> ${escapeHtml(resp.source_use_summary)}</div>` : ''}
            ${(resp.source_supported_points && resp.source_supported_points.length) ? `
              <div>
                <strong>Source-Supported Points (Server Trace):</strong>
                <ul style="margin:2px 0 0; padding-left:16px;">
                  ${resp.source_supported_points.map(p => `<li>${escapeHtml(p)}</li>`).join('')}
                </ul>
              </div>
            ` : ''}
            ${(resp.source_cautions && resp.source_cautions.length) ? `
              <div style="color:#92400e;">
                <strong>Source Cautions:</strong>
                <ul style="margin:2px 0 0; padding-left:16px;">
                  ${resp.source_cautions.map(c => `<li>${escapeHtml(c)}</li>`).join('')}
                </ul>
              </div>
            ` : ''}
            ${(resp.source_followup_checks && resp.source_followup_checks.length) ? `
              <div>
                <strong>Follow-Up Checks Suggested:</strong>
                <ul style="margin:2px 0 0; padding-left:16px;">
                  ${resp.source_followup_checks.map(f => `<li>${escapeHtml(f)}</li>`).join('')}
                </ul>
              </div>
            ` : ''}
          </div>
        </details>
      `;
    }

    html += `</div>`;
    return html;
  }
  """
