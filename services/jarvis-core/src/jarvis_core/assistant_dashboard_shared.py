from __future__ import annotations


def shared_dashboard_styles() -> str:
    return """
    /* ========================================================
       Shared Dashboard Accessibility, Modals & Responsive Tokens (v0.1E Pass 13)
       ======================================================== */

    /* Accessible Focus Indicators */
    button:focus-visible,
    input:focus-visible,
    select:focus-visible,
    textarea:focus-visible,
    a:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }

    /* Normalized Status Pills */
    .pill.ready { background: #dcfce7; color: #166534; }
    .pill.included { background: #dcfce7; color: #15803d; border-color: #86efac; }
    .pill.current { background: #dbeafe; color: #1e40af; border-color: #93c5fd; }
    .pill.completed { background: #dcfce7; color: #166534; border-color: #86efac; }
    .pill.needs-review { background: #fee2e2; color: #991b1b; border-color: #fca5a5; }
    .pill.high-stakes { background: #fee2e2; color: #991b1b; font-weight: 700; border-color: #f87171; }
    .pill.blocked { background: #fee2e2; color: #991b1b; }
    .pill.failed { background: #fef2f2; color: #b91c1c; }
    .pill.running { background: #e0e7ff; color: #3730a3; }
    .pill.skipped { background: #f1f5f9; color: #64748b; }

    /* Normalized Empty State Card */
    .empty-state {
      background: #f8fafc;
      border: 1px dashed #cbd5e1;
      border-radius: 8px;
      padding: 20px;
      text-align: center;
      color: #64748b;
      font-size: 0.88rem;
      line-height: 1.45;
    }

    /* Modal Backdrop & Dialog Shell */
    .results-modal-backdrop,
    .boundaries-modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(2px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 16px;
      animation: fadeIn 0.15s ease-out;
    }
    .results-modal-backdrop.open,
    .boundaries-modal-backdrop.open {
      display: flex;
    }
    .results-modal-card,
    .boundaries-modal-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px;
      width: 100%;
      max-width: 680px;
      max-height: 88vh;
      overflow-y: auto;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
      display: grid;
      gap: 14px;
      animation: slideUp 0.15s ease-out;
    }

    /* Responsive Viewport Overrides */
    @media (max-width: 840px) {
      .prod-toolbar {
        flex-direction: column;
        align-items: stretch;
      }
      .prod-tabs {
        overflow-x: auto;
        flex-wrap: nowrap;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
        padding-bottom: 4px;
      }
      .prod-tab-btn {
        flex-shrink: 0;
        white-space: nowrap;
      }
      .results-modal-card,
      .boundaries-modal-card {
        max-width: 95vw !important;
        max-height: 90vh !important;
        padding: 14px !important;
        margin: 8px !important;
      }
      .composer-options {
        flex-direction: column;
        align-items: stretch;
      }
      .wf-config-row {
        grid-template-columns: 1fr !important;
      }
    }
    """


def shared_dashboard_scripts() -> str:
    return """
  // ==========================================
  // Shared Dashboard Overlay & Keyboard Management (v0.1E Pass 13)
  // ==========================================

  const openModalsStack = [];

  function openOverlayModal(modalId, triggerEl = null) {
    const modal = byId(modalId);
    if (!modal) return;

    modal.classList.add('open');
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');

    openModalsStack.push({ modalId, triggerEl: triggerEl || document.activeElement });

    // Focus first meaningful interactive element
    const firstInput = modal.querySelector('input:not([type="hidden"]), select, textarea, button.small:not(.danger), button#close-modal-btn');
    if (firstInput) {
      setTimeout(() => { firstInput.focus(); }, 50);
    }
  }

  function closeOverlayModal(modalId) {
    const modal = byId(modalId);
    if (!modal) return;

    modal.classList.remove('open');

    const entryIdx = openModalsStack.findIndex(e => e.modalId === modalId);
    if (entryIdx >= 0) {
      const entry = openModalsStack.splice(entryIdx, 1)[0];
      if (entry && entry.triggerEl && typeof entry.triggerEl.focus === 'function') {
        setTimeout(() => {
          try { entry.triggerEl.focus(); } catch (e) { /* element may be unmounted */ }
        }, 50);
      }
    }
  }

  function closeTopmostOverlayModal() {
    if (!openModalsStack.length) return false;
    const top = openModalsStack[openModalsStack.length - 1];
    if (top && top.modalId) {
      // Check if modal has dirty unsaved state that needs confirmation
      if (top.modalId === 'drawer-decision-composer') {
        const q = (byId('dec-problem-input')?.value || '').trim();
        if (q && !confirm('Discard unsaved Decision Request draft?')) {
          return true; // handled, keep open
        }
      }
      closeOverlayModal(top.modalId);
      return true;
    }
    return false;
  }

  // Global Escape Key Listener for topmost non-destructive UI overlay
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      const closed = closeTopmostOverlayModal();
      if (closed) {
        e.preventDefault();
      }
    }
  });

  // Normalized User-Facing Error Messages
  function formatUserFriendlyError(err, category = 'Request failed') {
    if (!err) return `${category}: An unexpected error occurred.`;
    const msg = typeof err === 'string' ? err : (err.message || 'Unknown error');

    if (msg.includes('403') || msg.includes('Permission') || msg.includes('blocked')) {
      return `Blocked by policy: ${msg.replace(/403:?/, '').trim()}`;
    }
    if (msg.includes('Network') || msg.includes('Failed to fetch') || msg.includes('ECONNREFUSED')) {
      return `Unable to load: Jarvis Core service connection unavailable.`;
    }
    if (msg.includes('timeout') || msg.includes('timed out')) {
      return `Request timed out: Jarvis local worker did not complete in time.`;
    }
    return `${category}: ${msg}`;
  }
  """
