from __future__ import annotations


def workflows_dashboard_styles() -> str:
    return """
    /* ========================================================
       Manual Multi-Agent Workflow Workspace Styles (v0.1E Pass 13)
       ======================================================== */

    .wf-progress-container {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 12px 14px;
      display: grid;
      gap: 10px;
    }
    .wf-metric-grid {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      font-size: 0.84rem;
    }
    .wf-metric-pill {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 16px;
      padding: 3px 10px;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      color: #334155;
    }
    .wf-metric-pill strong {
      color: var(--accent-dark);
    }
    .wf-progress-bar-track {
      background: #e2e8f0;
      height: 7px;
      border-radius: 4px;
      overflow: hidden;
      width: 100%;
    }
    .wf-progress-bar-fill {
      background: #10b981;
      height: 100%;
      width: 0%;
      transition: width 0.2s ease;
    }
    .wf-steps-list {
      display: grid;
      gap: 12px;
      margin-top: 4px;
    }
    .wf-step-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px;
      display: grid;
      gap: 10px;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
      position: relative;
      overflow-wrap: break-word;
      word-break: break-word;
    }
    .wf-step-card.current {
      border-color: #3b82f6;
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    .wf-step-card.completed {
      border-color: #86efac;
      background: #fcfdfc;
    }
    .wf-step-card.needs-review {
      border-color: #fca5a5;
      background: #fffafa;
    }
    .wf-step-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }
    .wf-step-title-row {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }
    .wf-step-num {
      background: var(--accent-dark);
      color: #ffffff;
      font-weight: 700;
      font-size: 0.8rem;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    .wf-step-name {
      font-weight: 700;
      font-size: 0.96rem;
      color: var(--accent-dark);
    }
    .wf-config-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 10px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 10px 12px;
    }
    .wf-field {
      display: grid;
      gap: 4px;
      font-size: 0.82rem;
    }
    .wf-field label {
      font-weight: 600;
      color: #475569;
    }
    .wf-notes-input {
      width: 100%;
      box-sizing: border-box;
      padding: 6px 8px;
      font-size: 0.82rem;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      resize: vertical;
      font-family: inherit;
      min-height: 52px;
    }
    .wf-flags-row {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      font-size: 0.8rem;
    }
    .wf-attached-card {
      background: #f0fdf4;
      border: 1px solid #86efac;
      border-radius: 6px;
      padding: 10px 12px;
      display: grid;
      gap: 6px;
      font-size: 0.84rem;
    }
    .wf-attached-card.mismatch {
      border-color: #f59e0b;
      background: #fffbeb;
    }
    .wf-attached-card.stale {
      border-color: #f87171;
      background: #fff5f5;
    }
    .wf-attached-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;
    }
    .wf-step-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      padding-top: 8px;
      border-top: 1px solid #f1f5f9;
    }
    .wf-artifacts-summary {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 7px;
      padding: 12px 14px;
      font-size: 0.84rem;
      display: grid;
      gap: 8px;
      margin-top: 10px;
    }
    """


def workflows_dashboard_html() -> str:
    return """
  <!-- PANEL 2: Playbooks & Manual Workflows -->
  <section class="productivity-panel" id="panel-playbooks">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
      <div>
        <h3 style="margin:0; font-size:1.05rem; color:var(--accent-dark);">Manual Workflow Playbooks (<span id="wf-step-count">0</span> / 8 steps)</h3>
        <p class="muted" style="margin:2px 0 0; font-size:0.84rem;">Multi-step deliberate thinking patterns. Step execution, input staging, and output attachment are strictly manual.</p>
      </div>
      <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
        <select id="playbook-select" class="cc-filter-select" aria-label="Select Workflow Playbook">
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
        <select id="add-step-agent-select" class="cc-filter-select" aria-label="Select Agent to Insert as Workflow Step">
          <!-- 37 agents list injected via JS -->
        </select>
        <button id="add-step-btn" class="secondary small" type="button">+ Add Step</button>
      </div>
      <span class="muted" style="font-size:0.82rem;">Manual advancement only · Zero automated chaining</span>
    </div>
  </section>

  <!-- MODAL: Attach Transcript Turn to Workflow Step -->
  <div class="results-modal-backdrop" id="modal-attach-workflow">
    <div class="results-modal-card" style="max-width:540px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h3 style="margin:0; color:var(--accent-dark);">Attach Result to Workflow Step</h3>
        <button id="close-attach-modal-btn" class="secondary small" type="button">✕ Close</button>
      </div>

      <div style="display:grid; gap:10px; font-size:0.86rem;">
        <div>
          <span class="muted">Attaching Turn:</span> <strong id="attach-turn-agent-name"></strong>
          <span class="muted" id="attach-turn-meta"></span>
        </div>
        <div id="attach-turn-preview" class="source-excerpt-box" style="max-height:80px;"></div>

        <div id="attach-mismatch-warning" class="banner warning" style="display:none; margin:0; font-size:0.82rem;"></div>

        <div>
          <label style="font-weight:600; color:var(--text); margin-bottom:6px; display:block;">Select Target Workflow Step:</label>
          <div id="attach-steps-radio-list" style="display:grid; gap:6px; max-height:220px; overflow-y:auto; padding-right:4px;">
            <!-- Injected via JavaScript -->
          </div>
        </div>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:8px; padding-top:8px; border-top:1px solid #e2e8f0;">
        <button id="cancel-attach-btn" class="secondary small" type="button">Cancel</button>
        <button id="confirm-attach-btn" class="small" type="button" style="background:#15803d; border-color:#15803d;">Attach Output</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Select Target Step Picker (Replaces prompt() for Step Linkage) -->
  <div class="results-modal-backdrop" id="modal-step-target-selector">
    <div class="results-modal-card" style="max-width:520px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h3 id="step-target-modal-title" style="margin:0; color:var(--accent-dark);">Select Target Workflow Step</h3>
        <button id="close-step-target-modal-btn" class="secondary small" type="button">✕ Close</button>
      </div>

      <div style="display:grid; gap:10px; font-size:0.86rem;">
        <p id="step-target-modal-desc" class="muted" style="margin:0; font-size:0.84rem;"></p>
        <div id="step-target-radio-list" style="display:grid; gap:6px; max-height:240px; overflow-y:auto; padding-right:4px;">
          <!-- Injected via JavaScript -->
        </div>
      </div>

      <div style="display:flex; justify-content:flex-end; gap:8px; padding-top:8px; border-top:1px solid #e2e8f0;">
        <button id="cancel-step-target-btn" class="secondary small" type="button">Cancel</button>
        <button id="confirm-step-target-btn" class="small" type="button">Confirm Selection</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Workflow Packet Composer -->
  <div class="results-modal-backdrop" id="drawer-workflow-packet">
    <div class="results-modal-card" style="max-width:760px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <h3 style="margin:0; color:var(--accent-dark);">Workflow Review &amp; Synthesis Packet</h3>
          <span class="muted" style="font-size:0.82rem;">Assemble attached workflow outputs into a bounded synthesis context.</span>
        </div>
        <button id="close-wf-packet-btn" class="secondary small" type="button">✕ Close</button>
      </div>

      <div style="display:grid; gap:12px;">
        <!-- Budget meter -->
        <div class="kit-budget-meter" style="margin:0;">
          <div style="display:flex; justify-content:space-between; font-size:0.84rem;">
            <span>Packet Budget (Max 16,000 chars):</span>
            <strong id="wf-packet-budget-text">0 / 16,000 chars</strong>
          </div>
          <div class="budget-bar-track">
            <div class="budget-bar-fill" id="wf-packet-budget-bar"></div>
          </div>
        </div>

        <div id="wf-packet-oversized-warning" class="banner warning" style="display:none; font-size:0.82rem;">
          <strong>Packet Budget Exceeded:</strong> Total characters exceed 16,000. Transfer actions are disabled until you uncheck steps or shorten notes.
        </div>

        <div>
          <div style="font-weight:600; font-size:0.84rem; margin-bottom:6px; color:#334155;">Included Attached Steps:</div>
          <div id="wf-packet-steps-selector" style="display:grid; gap:6px; max-height:160px; overflow-y:auto; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:8px;">
            <!-- Injected via JavaScript -->
          </div>
        </div>

        <div>
          <label style="font-weight:600; font-size:0.82rem; color:#334155;">Generated Packet Preview:</label>
          <pre id="wf-packet-preview-text" class="json-viewer" style="max-height:220px; white-space:pre-wrap; font-size:0.82rem; background:#1e293b; color:#f8fafc; padding:10px; border-radius:6px; overflow:auto;"></pre>
        </div>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; padding-top:8px; border-top:1px solid #e2e8f0;">
        <span class="muted" style="font-size:0.78rem;">Manual staging only · Never executes automatically</span>
        <div style="display:flex; flex-wrap:wrap; gap:6px;">
          <button id="wf-packet-to-kit-btn" class="secondary small" type="button">🧰 Add to Context Kit</button>
          <button id="wf-packet-to-prior-btn" class="secondary small" type="button">Stage as Prior Context</button>
          <button id="wf-packet-to-composer-btn" class="secondary small" type="button">Insert into Request</button>
          <button id="wf-packet-prepare-review-btn" class="small" type="button">🔍 Prepare Review Request</button>
          <button id="wf-packet-prepare-decision-btn" class="small" type="button" style="background:#0284c7; border-color:#0284c7;">🎯 Prepare Decision Request</button>
        </div>
      </div>
    </div>
  </div>
    """


def workflows_dashboard_scripts() -> str:
    return """
  // ==========================================
  // Manual Multi-Agent Workflow Workspace (v0.1E Pass 13)
  // ==========================================

  const MAX_WORKFLOW_STEPS = 8;
  const MAX_WORKFLOW_PACKET_CHARS = 16000;

  sessionState.currentWorkflowStepId = null;
  sessionState.pendingAttachTurn = null;
  sessionState.pendingStepTargetCallback = null;

  function createWorkflowStep(agentId, name, purpose, suggestedPrompt) {
    const dName = name || getAgentDisplayName(agentId);
    return {
      stepId: 'wf_step_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
      agentId: agentId,
      name: dName,
      purpose: purpose || `Process with ${dName}`,
      suggestedPrompt: suggestedPrompt || '',
      status: 'not_started', // 'not_started' | 'in_progress' | 'completed' | 'needs_review'
      userNotes: '', // max 2,000 chars

      // Explicit input mode
      inputMode: 'none', // 'none' | 'prev_step_output' | 'specific_step_output' | 'result_board' | 'context_kit' | 'custom_notes'
      inputRef: null, // stepId or resultBoardId
      inputLabel: '',

      // Attached Assistant output reference-first (A4)
      attachedOutputRef: null,

      // Manual review flags
      reviewFlags: {
        needsReview: false,
        potentialConflict: false,
        blockedOnInput: false,
      },

      preparedAt: null,
    };
  }

  async function loadPlaybooks() {
    try {
      const playbooks = await apiFetch('/api/assistant/productivity/playbooks');
      if (Array.isArray(playbooks)) {
        sessionState.builtInPlaybooks = playbooks;
        populatePlaybooksDropdown(playbooks);
        if (playbooks.length) {
          selectPlaybook(playbooks[0].id, true);
        }
      }
    } catch (err) {
      console.warn('Failed to load playbooks from server:', err);
    }
  }

  function populatePlaybooksDropdown(playbooks) {
    const select = byId('playbook-select');
    if (!select) return;
    select.replaceChildren();
    playbooks.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.name;
      select.append(opt);
    });
    const customOpt = document.createElement('option');
    customOpt.value = 'custom';
    customOpt.textContent = 'Custom Workflow';
    select.append(customOpt);
  }

  function populateAddStepAgentDropdown(agents) {
    const select = byId('add-step-agent-select');
    if (!select) return;
    select.replaceChildren();
    agents.forEach(agent => {
      const opt = document.createElement('option');
      opt.value = agent.agentId || agent.agent_id;
      opt.textContent = `${agent.displayName || agent.name} [${agent.category || 'General'}]`;
      select.append(opt);
    });
  }

  // Complete Workflow Dirty-State Detection (A2)
  function hasWorkflowDirtyState() {
    if (!sessionState.playbookSteps || !sessionState.playbookSteps.length) {
      return false;
    }
    if (sessionState.activePlaybookId === 'custom') {
      return sessionState.playbookSteps.length > 0;
    }
    const pb = sessionState.builtInPlaybooks?.find(p => p.id === sessionState.activePlaybookId);
    if (pb && sessionState.playbookSteps.length !== pb.steps.length) {
      return true;
    }
    return sessionState.playbookSteps.some(s =>
      s.attachedOutputRef != null ||
      (s.userNotes && s.userNotes.trim().length > 0) ||
      s.status !== 'not_started' ||
      s.inputMode !== 'none' ||
      s.inputRef !== null ||
      s.reviewFlags.needsReview ||
      s.reviewFlags.potentialConflict ||
      s.reviewFlags.blockedOnInput
    );
  }

  // Clean Custom Initialization & Reset Semantics (A1)
  function selectPlaybook(playbookId, skipConfirm = false) {
    if (!skipConfirm && hasWorkflowDirtyState()) {
      if (!confirm('Switching playbooks will discard current step notes and attached outputs for this session. Continue?')) {
        byId('playbook-select').value = sessionState.activePlaybookId;
        return;
      }
    }

    sessionState.activePlaybookId = playbookId;
    sessionState.currentWorkflowStepId = null;
    byId('playbook-select').value = playbookId;

    if (playbookId === 'custom') {
      byId('playbook-description').textContent = 'Custom multi-step workflow. Add up to 8 agent steps manually.';
      sessionState.playbookSteps = [];
    } else {
      const pb = sessionState.builtInPlaybooks?.find(p => p.id === playbookId);
      if (pb) {
        byId('playbook-description').textContent = pb.description;
        sessionState.playbookSteps = pb.steps.map((s) => createWorkflowStep(
          s.agentId,
          s.name,
          s.purpose,
          s.suggestedPrompt
        ));
      }
    }
    renderPlaybookSteps();
  }

  // Reference-First Output Content Resolution (A4 & A5)
  function resolveWorkflowAttachedOutputContent(attachedRef) {
    if (!attachedRef) return { text: '', isStale: false, excerpt: '' };
    if (attachedRef.turnIndex !== null && attachedRef.turnIndex !== undefined && sessionState.transcript) {
      const turn = sessionState.transcript[attachedRef.turnIndex];
      if (turn && turn.response) {
        const resp = turn.response;
        const primaryText = resp.summary || resp.decision || resp.response || resp.plan || (typeof resp === 'string' ? resp : JSON.stringify(resp));
        if (primaryText) {
          return { text: primaryText, isStale: false, excerpt: primaryText.slice(0, 300) };
        }
      }
    }
    // If transcript turn is missing or empty, handle as stale
    return { text: '', isStale: true, excerpt: attachedRef.excerpt || '' };
  }

  function resolveStepInputContext(step) {
    if (!step || step.inputMode === 'none') {
      return { text: '', label: 'Fresh Request (No prior input)', valid: true };
    }

    if (step.inputMode === 'prev_step_output') {
      const stepIdx = sessionState.playbookSteps.findIndex(s => s.stepId === step.stepId);
      if (stepIdx <= 0) {
        return { text: '', label: 'No previous step exists', valid: false };
      }
      for (let i = stepIdx - 1; i >= 0; i--) {
        const prev = sessionState.playbookSteps[i];
        if (prev.attachedOutputRef) {
          const resolved = resolveWorkflowAttachedOutputContent(prev.attachedOutputRef);
          if (resolved.isStale) {
            return { text: '', label: `Previous Attached Output (Step ${i + 1}) is no longer available in transcript`, valid: false };
          }
          if (resolved.text) {
            return {
              text: resolved.text,
              label: `Previous Attached Output (Step ${i + 1}: ${prev.attachedOutputRef.agentName})`,
              agentName: prev.attachedOutputRef.agentName,
              agentId: prev.attachedOutputRef.agentId,
              responseId: prev.attachedOutputRef.responseId,
              valid: true,
            };
          }
        }
      }
      return { text: '', label: 'No previous attached workflow output is available.', valid: false };
    }

    if (step.inputMode === 'specific_step_output') {
      if (!step.inputRef) return { text: '', label: 'No specific step selected', valid: false };
      const targetStep = sessionState.playbookSteps.find(s => s.stepId === step.inputRef);
      if (!targetStep || !targetStep.attachedOutputRef) {
        return { text: '', label: 'Referenced workflow step has no attached output.', valid: false };
      }
      const resolved = resolveWorkflowAttachedOutputContent(targetStep.attachedOutputRef);
      if (resolved.isStale) {
        return { text: '', label: `Attached output from ${targetStep.name} is no longer available in transcript.`, valid: false };
      }
      return {
        text: resolved.text,
        label: `Attached Output from ${targetStep.name}`,
        agentName: targetStep.attachedOutputRef.agentName,
        agentId: targetStep.attachedOutputRef.agentId,
        responseId: targetStep.attachedOutputRef.responseId,
        valid: true,
      };
    }

    if (step.inputMode === 'result_board') {
      if (!step.inputRef) return { text: '', label: 'No Result Board item selected', valid: false };
      const rbItem = sessionState.resultBoard?.find(r => r.id === step.inputRef);
      if (!rbItem) {
        return { text: '', label: 'Referenced Result Board item is no longer available in this session.', valid: false };
      }
      return {
        text: rbItem.primaryText || '',
        label: `Result Board: ${rbItem.agentDisplayName} [${rbItem.category || 'Result'}]`,
        agentName: rbItem.agentDisplayName,
        agentId: rbItem.agentId,
        responseId: rbItem.fullResponse?.responseContext?.responseId || '',
        valid: true,
      };
    }

    if (step.inputMode === 'context_kit') {
      const items = sessionState.contextKit || [];
      if (!items.length) {
        return { text: '', label: 'Context Kit is currently empty', valid: false };
      }
      const combined = items.map(it => `[${it.label}]\n${it.content}`).join('\\n\\n');
      return {
        text: combined,
        label: `Context Kit (${items.length} items, ${combined.length} chars)`,
        valid: true,
      };
    }

    if (step.inputMode === 'custom_notes') {
      const notes = (step.userNotes || '').trim();
      return {
        text: notes,
        label: `Step Notes (${notes.length} chars)`,
        valid: notes.length > 0,
      };
    }

    return { text: '', label: 'Unknown input mode', valid: false };
  }

  function renderPlaybookSteps() {
    const list = byId('playbook-steps-list');
    const totalCountSpan = byId('wf-step-count');
    const statTotal = byId('wf-stat-total');
    const statCompleted = byId('wf-stat-completed');
    const statInProgress = byId('wf-stat-in-progress');
    const statNotStarted = byId('wf-stat-not-started');
    const statNeedsReview = byId('wf-stat-needs-review');
    const statAttached = byId('wf-stat-attached');
    const statSources = byId('wf-stat-sources');
    const statKit = byId('wf-stat-kit');
    const currentLabel = byId('wf-current-step-label');
    const progressBar = byId('wf-progress-bar');
    const completedBanner = byId('wf-completed-banner');
    const artifactsSummary = byId('wf-artifacts-summary');

    const steps = sessionState.playbookSteps;
    const total = steps.length;
    const completed = steps.filter(s => s.status === 'completed').length;
    const inProgress = steps.filter(s => s.status === 'in_progress').length;
    const notStarted = steps.filter(s => s.status === 'not_started').length;
    const needsReview = steps.filter(s => s.status === 'needs_review' || s.reviewFlags.needsReview).length;
    const attached = steps.filter(s => s.attachedOutputRef).length;
    const activeSourcesCount = typeof getIncludedReviewedSources === 'function' ? getIncludedReviewedSources().length : 0;
    const kitCount = sessionState.contextKit?.length || 0;

    if (totalCountSpan) totalCountSpan.textContent = total;
    if (statTotal) statTotal.textContent = total;
    if (statCompleted) statCompleted.textContent = completed;
    if (statInProgress) statInProgress.textContent = inProgress;
    if (statNotStarted) statNotStarted.textContent = notStarted;
    if (statNeedsReview) statNeedsReview.textContent = needsReview;
    if (statAttached) statAttached.textContent = attached;
    if (statSources) statSources.textContent = activeSourcesCount;
    if (statKit) statKit.textContent = kitCount;

    const currentStep = steps.find(s => s.stepId === sessionState.currentWorkflowStepId);
    if (currentLabel) {
      if (currentStep) {
        const cIdx = steps.findIndex(s => s.stepId === currentStep.stepId);
        currentLabel.textContent = `Step ${cIdx + 1}: ${currentStep.name}`;
      } else {
        currentLabel.textContent = 'None';
      }
    }

    if (progressBar) {
      const pct = total > 0 ? Math.round((completed / total) * 100) : 0;
      progressBar.style.width = pct + '%';
    }

    if (completedBanner) {
      if (total > 0 && completed === total) {
        completedBanner.style.display = 'block';
      } else {
        completedBanner.style.display = 'none';
      }
    }

    // Artifacts Summary Box
    if (artifactsSummary) {
      artifactsSummary.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="color:var(--accent-dark);">Workflow Artifacts &amp; Evidence Summary</strong>
          <span class="pill ${completed === total && total > 0 ? 'succeeded' : 'inactive'}">
            ${completed} / ${total} Completed
          </span>
        </div>
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:6px; font-size:0.8rem;">
          <div>• <strong>${attached}</strong> step(s) have attached Assistant outputs</div>
          <div>• <strong>${total - attached}</strong> step(s) missing attached outputs</div>
          <div>• <strong>${activeSourcesCount}</strong> reviewed public source(s) attached to session</div>
          <div>• <strong>${kitCount}</strong> item(s) in Context Kit (${(typeof getContextKitTotalChars === 'function' ? getContextKitTotalChars() : 0).toLocaleString()} chars)</div>
          ${needsReview > 0 ? `<div style="color:#b91c1c;">• <strong>${needsReview}</strong> step(s) flagged for review / potential conflict</div>` : '<div class="muted">• 0 steps flagged for review</div>'}
        </div>
      `;
    }

    if (!list) return;
    if (!steps.length) {
      list.innerHTML = `
        <div class="empty-state" style="padding:24px;">
          No workflow steps yet. Choose a built-in playbook above or add an existing response agent manually. Nothing runs automatically.
        </div>
      `;
      return;
    }

    list.replaceChildren();
    steps.forEach((step, idx) => {
      const card = document.createElement('div');
      const isCurrent = step.stepId === sessionState.currentWorkflowStepId;
      card.className = `wf-step-card ${isCurrent ? 'current' : ''} ${step.status === 'completed' ? 'completed' : (step.status === 'needs_review' || step.reviewFlags.needsReview ? 'needs-review' : '')}`;

      const resolvedInput = resolveStepInputContext(step);

      // Workflow High-Stakes Visibility (Part K)
      const agentMeta = sessionState.catalogAgents?.find(a => (a.agentId || a.agent_id) === step.agentId);
      const isAgentHighStakes = !!(agentMeta && (agentMeta.category === 'High-Stakes' || agentMeta.highStakes || (agentMeta.metadata && agentMeta.metadata.high_stakes)));
      const isAttachedHighStakes = !!(step.attachedOutputRef && step.attachedOutputRef.highStakes);
      const isHighStakes = isAgentHighStakes || isAttachedHighStakes;

      // Stale Attached Output check (A4 & A5)
      let resolvedOutput = null;
      if (step.attachedOutputRef) {
        resolvedOutput = resolveWorkflowAttachedOutputContent(step.attachedOutputRef);
      }

      card.innerHTML = `
        <div class="wf-step-header">
          <div class="wf-step-title-row">
            <span class="wf-step-num">${idx + 1}</span>
            <span class="wf-step-name">${escapeHtml(step.name)}</span>
            ${isCurrent ? '<span class="pill active">Current Step</span>' : ''}
            ${step.attachedOutputRef ? (resolvedOutput && resolvedOutput.isStale ? '<span class="pill danger">Output Stale</span>' : '<span class="pill succeeded">Output Attached</span>') : '<span class="pill inactive">Awaiting Output</span>'}
            ${isHighStakes ? '<span class="diff-badge" style="background:#fee2e2; color:#991b1b;">High Stakes</span>' : ''}
          </div>
          <div style="display:flex; align-items:center; gap:6px;">
            <select class="cc-filter-select" data-wf-status="${step.stepId}" style="font-size:0.8rem; padding:3px 6px;" aria-label="Step status">
              <option value="not_started" ${step.status === 'not_started' ? 'selected' : ''}>Not Started</option>
              <option value="in_progress" ${step.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
              <option value="needs_review" ${step.status === 'needs_review' ? 'selected' : ''}>Needs Review</option>
              <option value="completed" ${step.status === 'completed' ? 'selected' : ''}>Completed</option>
            </select>
          </div>
        </div>

        <div style="font-size:0.86rem; color:#334155;">
          <strong>Purpose:</strong> ${escapeHtml(step.purpose)}
        </div>

        ${isHighStakes && activeSourcesCount === 0 && isCurrent ? `
          <div class="banner warning" style="margin:2px 0 0; font-size:0.8rem; padding:6px 10px;">
            <strong>High-Stakes Step:</strong> 0 reviewed public sources attached to session. High-stakes requests are safer when validated against verified external evidence.
          </div>
        ` : ''}

        <!-- Input Source Configuration -->
        <div class="wf-config-row">
          <div class="wf-field">
            <label>Input Source for Step:</label>
            <select class="cc-filter-select" data-wf-input-mode="${step.stepId}" aria-label="Input mode for step">
              <option value="none" ${step.inputMode === 'none' ? 'selected' : ''}>None / Fresh Request</option>
              <option value="prev_step_output" ${step.inputMode === 'prev_step_output' ? 'selected' : ''}>Previous Workflow Step Output</option>
              <option value="specific_step_output" ${step.inputMode === 'specific_step_output' ? 'selected' : ''}>Specific Workflow Step Output</option>
              <option value="result_board" ${step.inputMode === 'result_board' ? 'selected' : ''}>Result Board Entry</option>
              <option value="context_kit" ${step.inputMode === 'context_kit' ? 'selected' : ''}>Context Kit</option>
              <option value="custom_notes" ${step.inputMode === 'custom_notes' ? 'selected' : ''}>Custom Step Notes</option>
            </select>
          </div>

          <!-- Specific Step Output Picker (conditional) -->
          ${step.inputMode === 'specific_step_output' ? `
            <div class="wf-field">
              <label>Select Attached Step Output:</label>
              <select class="cc-filter-select" data-wf-specific-step="${step.stepId}">
                <option value="">-- Choose Step --</option>
                ${steps.filter(s => s.stepId !== step.stepId && s.attachedOutputRef).map(s => `
                  <option value="${s.stepId}" ${step.inputRef === s.stepId ? 'selected' : ''}>
                    Step ${steps.indexOf(s) + 1}: ${escapeHtml(s.name)} (${escapeHtml(s.attachedOutputRef.agentName)})
                  </option>
                `).join('')}
              </select>
            </div>
          ` : ''}

          <!-- Result Board Picker (conditional) -->
          ${step.inputMode === 'result_board' ? `
            <div class="wf-field">
              <label>Select Result Board Entry:</label>
              <select class="cc-filter-select" data-wf-rb-select="${step.stepId}">
                <option value="">-- Choose Result Board Item --</option>
                ${(sessionState.resultBoard || []).map(r => `
                  <option value="${r.id}" ${step.inputRef === r.id ? 'selected' : ''}>
                    ${escapeHtml(r.agentDisplayName)} [${escapeHtml(r.category || 'Result')}] — ${escapeHtml(r.primaryText.slice(0, 40))}...
                  </option>
                `).join('')}
              </select>
            </div>
          ` : ''}

          <div class="wf-field" style="grid-column: 1 / -1;">
            <div style="font-size:0.8rem; color:${resolvedInput.valid ? '#15803d' : '#b91c1c'}; font-weight:600;">
              ${resolvedInput.valid ? '✓ Input Context:' : '⚠️ Input Notice:'} ${escapeHtml(resolvedInput.label)}
            </div>
          </div>
        </div>

        <!-- Step Notes & Review Flags -->
        <div style="display:grid; gap:6px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <label style="font-weight:600; font-size:0.8rem; color:#475569;">Step Notes / Instructions (Max 2,000 chars, session-only):</label>
            <span class="muted" style="font-size:0.75rem;">${(step.userNotes || '').length} / 2,000</span>
          </div>
          <textarea class="wf-notes-input" data-wf-notes="${step.stepId}" placeholder="Enter specific instructions, constraints, or focus areas for this step...">${escapeHtml(step.userNotes || '')}</textarea>
        </div>

        <div class="wf-flags-row">
          <span class="muted" style="font-weight:600;">Manual Flags:</span>
          <label style="display:inline-flex; align-items:center; gap:4px; cursor:pointer;">
            <input type="checkbox" data-wf-flag="needsReview" data-step-id="${step.stepId}" ${step.reviewFlags.needsReview ? 'checked' : ''}>
            <span>Needs Review</span>
          </label>
          <label style="display:inline-flex; align-items:center; gap:4px; cursor:pointer;">
            <input type="checkbox" data-wf-flag="potentialConflict" data-step-id="${step.stepId}" ${step.reviewFlags.potentialConflict ? 'checked' : ''}>
            <span>Potential Conflict</span>
          </label>
          <label style="display:inline-flex; align-items:center; gap:4px; cursor:pointer;">
            <input type="checkbox" data-wf-flag="blockedOnInput" data-step-id="${step.stepId}" ${step.reviewFlags.blockedOnInput ? 'checked' : ''}>
            <span>Blocked on Input</span>
          </label>
        </div>

        <!-- Attached Output Card (if present) -->
        ${step.attachedOutputRef ? `
          <div class="wf-attached-card ${resolvedOutput && resolvedOutput.isStale ? 'stale' : (step.attachedOutputRef.agentId !== step.agentId ? 'mismatch' : '')}">
            <div class="wf-attached-header">
              <div>
                <strong>Attached Output:</strong> ${escapeHtml(step.attachedOutputRef.agentName)}
                ${step.attachedOutputRef.agentId !== step.agentId ? `<span class="diff-badge" style="background:#fef3c7; color:#92400e; margin-left:4px;">Different Agent than Step Assigned</span>` : ''}
              </div>
              <div style="display:flex; align-items:center; gap:6px;">
                <span class="muted" style="font-size:0.75rem;">Turn #${step.attachedOutputRef.turnIndex !== null ? step.attachedOutputRef.turnIndex + 1 : 'Ref'}</span>
                ${step.attachedOutputRef.sourceCount > 0 ? `<span class="pill allowed" style="font-size:0.7rem;">${step.attachedOutputRef.sourceCount} Sources</span>` : ''}
              </div>
            </div>

            ${resolvedOutput && resolvedOutput.isStale ? `
              <div class="banner warning" style="margin:0; font-size:0.8rem; padding:6px 8px;">
                ⚠️ Attached result is no longer available in this session transcript.
              </div>
            ` : `
              <div style="font-size:0.82rem; color:#334155; line-height:1.4; background:rgba(255,255,255,0.7); padding:6px 8px; border-radius:4px; max-height:80px; overflow-y:auto;">
                ${escapeHtml(resolvedOutput ? resolvedOutput.excerpt : step.attachedOutputRef.excerpt)}
              </div>
            `}

            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:6px; margin-top:2px;">
              <div style="display:flex; gap:6px;">
                ${resolvedOutput && !resolvedOutput.isStale ? `
                  <button class="secondary small" type="button" data-wf-attached-action="view" data-step-id="${step.stepId}">🔍 View Result</button>
                  <button class="secondary small" type="button" data-wf-attached-action="add-board" data-step-id="${step.stepId}">📊 Add to Result Board</button>
                  <button class="secondary small" type="button" data-wf-attached-action="use-input" data-step-id="${step.stepId}">➡️ Use as Input for Another Step</button>
                ` : ''}
              </div>
              <button class="secondary small danger" type="button" data-wf-attached-action="detach" data-step-id="${step.stepId}">Detach</button>
            </div>
          </div>
        ` : ''}

        <!-- Step Action Controls -->
        <div class="wf-step-actions">
          <div style="display:flex; flex-wrap:wrap; gap:6px;">
            <button class="small" type="button" data-wf-action="prepare" data-step-id="${step.stepId}">⚡ Prepare Step</button>
            ${idx < steps.length - 1 ? `
              <button class="secondary small" type="button" data-wf-action="prepare-next" data-step-idx="${idx}">Manual Prepare Next Step ➔</button>
            ` : ''}
            <button class="secondary small" type="button" data-wf-action="set-current" data-step-id="${step.stepId}">
              ${isCurrent ? 'Current Step Active' : 'Set as Current Step'}
            </button>
          </div>
          <div style="display:flex; gap:4px;">
            <button class="secondary small" type="button" data-wf-action="up" data-step-idx="${idx}" ${idx === 0 ? 'disabled' : ''} aria-label="Move Step Up" title="Move Step Up">↑</button>
            <button class="secondary small" type="button" data-wf-action="down" data-step-idx="${idx}" ${idx === steps.length - 1 ? 'disabled' : ''} aria-label="Move Step Down" title="Move Step Down">↓</button>
            <button class="secondary small danger" type="button" data-wf-action="remove" data-step-idx="${idx}" aria-label="Remove Step" title="Remove Step">✕</button>
          </div>
        </div>
      `;

      // Event bindings
      card.querySelector(`[data-wf-status="${step.stepId}"]`)?.addEventListener('change', (e) => {
        step.status = e.target.value;
        renderPlaybookSteps();
      });

      card.querySelector(`[data-wf-input-mode="${step.stepId}"]`)?.addEventListener('change', (e) => {
        step.inputMode = e.target.value;
        step.inputRef = null;
        renderPlaybookSteps();
      });

      card.querySelector(`[data-wf-specific-step="${step.stepId}"]`)?.addEventListener('change', (e) => {
        step.inputRef = e.target.value || null;
        renderPlaybookSteps();
      });

      card.querySelector(`[data-wf-rb-select="${step.stepId}"]`)?.addEventListener('change', (e) => {
        step.inputRef = e.target.value || null;
        renderPlaybookSteps();
      });

      const notesEl = card.querySelector(`[data-wf-notes="${step.stepId}"]`);
      if (notesEl) {
        notesEl.addEventListener('input', (e) => {
          step.userNotes = e.target.value.slice(0, 2000);
        });
      }

      card.querySelectorAll(`[data-wf-flag]`).forEach(cb => {
        cb.addEventListener('change', (e) => {
          const fName = cb.getAttribute('data-wf-flag');
          step.reviewFlags[fName] = e.target.checked;
          renderPlaybookSteps();
        });
      });

      // Attached Output Actions
      card.querySelector(`[data-wf-attached-action="view"]`)?.addEventListener('click', () => {
        if (step.attachedOutputRef && step.attachedOutputRef.turnIndex !== null) {
          const turnDiv = document.querySelectorAll('.chat-container .turn')[step.attachedOutputRef.turnIndex];
          if (turnDiv) {
            turnDiv.scrollIntoView({ behavior: 'smooth' });
            turnDiv.style.outline = '2px solid #3b82f6';
            setTimeout(() => { turnDiv.style.outline = ''; }, 1800);
          } else {
            alert('Referenced transcript turn is no longer in active view.');
          }
        }
      });

      card.querySelector(`[data-wf-attached-action="add-board"]`)?.addEventListener('click', () => {
        if (step.attachedOutputRef && step.attachedOutputRef.turnIndex !== null) {
          const turn = sessionState.transcript?.[step.attachedOutputRef.turnIndex];
          if (turn && typeof addToResultBoard === 'function') {
            addToResultBoard(turn);
          } else {
            showToast('Result Board entry updated.');
          }
        }
      });

      // Non-prompt modal picker for Step Input linkage (Part J)
      card.querySelector(`[data-wf-attached-action="use-input"]`)?.addEventListener('click', () => {
        openTargetStepPickerForOutput(step.stepId);
      });

      card.querySelector(`[data-wf-attached-action="detach"]`)?.addEventListener('click', () => {
        if (confirm(`Detach attached result from Step ${idx + 1}?`)) {
          step.attachedOutputRef = null;
          renderPlaybookSteps();
          showToast(`Detached output from Step ${idx + 1}.`);
        }
      });

      // Step Actions
      card.querySelector(`[data-wf-action="prepare"]`)?.addEventListener('click', () => prepareWorkflowStep(step.stepId));
      card.querySelector(`[data-wf-action="prepare-next"]`)?.addEventListener('click', () => prepareNextWorkflowStep(idx));
      card.querySelector(`[data-wf-action="set-current"]`)?.addEventListener('click', () => {
        sessionState.currentWorkflowStepId = step.stepId;
        renderPlaybookSteps();
      });
      card.querySelector(`[data-wf-action="up"]`)?.addEventListener('click', () => moveWorkflowStep(idx, -1));
      card.querySelector(`[data-wf-action="down"]`)?.addEventListener('click', () => moveWorkflowStep(idx, 1));
      card.querySelector(`[data-wf-action="remove"]`)?.addEventListener('click', () => removeWorkflowStep(idx));

      list.append(card);
    });
  }

  function prepareWorkflowStep(stepId) {
    const stepIdx = sessionState.playbookSteps.findIndex(s => s.stepId === stepId);
    if (stepIdx < 0) return;
    const step = sessionState.playbookSteps[stepIdx];

    sessionState.currentWorkflowStepId = step.stepId;
    if (typeof selectAgentManually === 'function') {
      selectAgentManually(step.agentId);
    }

    const resolvedInput = resolveStepInputContext(step);
    const pbName = byId('playbook-select')?.selectedOptions?.[0]?.textContent || 'Workflow Playbook';

    // Bounded context check
    if (resolvedInput.text && resolvedInput.text.length > MAX_WORKFLOW_PACKET_CHARS) {
      alert(`The selected input source (${resolvedInput.text.length.toLocaleString()} chars) exceeds the 16,000 character maximum budget. Please choose a smaller input source or reduce Context Kit items.`);
      return;
    }

    // Build transparent workflow scaffold
    let scaffold = `[Workflow Step]\n`;
    scaffold += `Playbook: ${pbName}\n`;
    scaffold += `Step: ${stepIdx + 1} of ${sessionState.playbookSteps.length}\n`;
    scaffold += `Agent: ${step.name}\n`;
    scaffold += `Purpose: ${step.purpose}\n`;

    if (step.userNotes && step.userNotes.trim()) {
      scaffold += `\nStep Notes:\n${step.userNotes.trim()}\n`;
    }

    if (resolvedInput.text && resolvedInput.text.trim()) {
      scaffold += `\nInput Context (${escapeHtml(resolvedInput.label)}):\n${resolvedInput.text.trim()}\n`;
    }
    scaffold += `[/Workflow Step]\n\n`;

    if (step.suggestedPrompt) {
      scaffold += `${step.suggestedPrompt}`;
    }

    const input = byId('prompt-input');
    if (input) {
      input.value = scaffold;
      input.focus();
    }

    // Stage prior context if single prior result is resolved
    if (resolvedInput.agentId && resolvedInput.text && typeof setStagedPriorContext === 'function') {
      setStagedPriorContext({
        agentId: resolvedInput.agentId,
        agentName: resolvedInput.agentName || getAgentDisplayName(resolvedInput.agentId),
        responseId: resolvedInput.responseId || '',
        summary: resolvedInput.text.slice(0, 4000),
      });
    }

    step.preparedAt = new Date().toISOString();
    renderPlaybookSteps();
    if (typeof triggerReadinessEvaluation === 'function') {
      triggerReadinessEvaluation();
    }
    showToast(`Prepared Step ${stepIdx + 1}: ${step.name} in prompt composer.`);
    byId('composer')?.scrollIntoView({ behavior: 'smooth' });
  }

  function prepareNextWorkflowStep(currentIndex) {
    if (currentIndex + 1 < sessionState.playbookSteps.length) {
      const nextStep = sessionState.playbookSteps[currentIndex + 1];
      prepareWorkflowStep(nextStep.stepId);
    }
  }

  function moveWorkflowStep(index, direction) {
    const target = index + direction;
    if (target < 0 || target >= sessionState.playbookSteps.length) return;
    const temp = sessionState.playbookSteps[index];
    sessionState.playbookSteps[index] = sessionState.playbookSteps[target];
    sessionState.playbookSteps[target] = temp;
    renderPlaybookSteps();
  }

  function removeWorkflowStep(index) {
    sessionState.playbookSteps.splice(index, 1);
    renderPlaybookSteps();
  }

  function addAgentToWorkflow(agentId) {
    if (sessionState.playbookSteps.length >= MAX_WORKFLOW_STEPS) {
      alert(`Maximum ${MAX_WORKFLOW_STEPS} steps allowed in a session workflow. Remove an existing step before adding another.`);
      return;
    }
    const name = getAgentDisplayName(agentId);
    const newStep = createWorkflowStep(agentId, name, `Process with ${name}`, `Task for ${name}: `);
    sessionState.playbookSteps.push(newStep);
    switchProductivityTab('panel-playbooks');
    renderPlaybookSteps();
    showToast(`Added ${name} to workflow steps.`);
  }

  // ==========================================
  // Attach Transcript Turn to Workflow Modal
  // ==========================================

  function openAttachToWorkflowModal(turnIndex) {
    const turn = sessionState.transcript?.[turnIndex];
    if (!turn) return;

    sessionState.pendingAttachTurn = { turnIndex, turn };
    const modal = byId('modal-attach-workflow');
    if (!modal) return;

    const agentName = turn.route ? turn.route.selected_display_name : turn.agentId;
    byId('attach-turn-agent-name').textContent = agentName;
    byId('attach-turn-meta').textContent = `(Turn #${turnIndex + 1} · ${turn.timestamp || ''})`;

    const resp = turn.response || {};
    const primaryText = resp.summary || resp.decision || resp.response || resp.plan || (typeof resp === 'string' ? resp : JSON.stringify(resp));
    byId('attach-turn-preview').textContent = primaryText.slice(0, 300);

    const radioList = byId('attach-steps-radio-list');
    radioList.replaceChildren();

    if (!sessionState.playbookSteps.length) {
      radioList.innerHTML = '<div class="muted" style="padding:8px;">No steps in current workflow. Create or select a playbook first.</div>';
      byId('confirm-attach-btn').disabled = true;
    } else {
      byId('confirm-attach-btn').disabled = false;
      sessionState.playbookSteps.forEach((s, sIdx) => {
        const row = document.createElement('label');
        row.style.display = 'flex';
        row.style.alignItems = 'center';
        row.style.gap = '8px';
        row.style.padding = '6px 8px';
        row.style.background = '#f8fafc';
        row.style.border = '1px solid #e2e8f0';
        row.style.borderRadius = '5px';
        row.style.cursor = 'pointer';

        row.innerHTML = `
          <input type="radio" name="attach-target-step" value="${s.stepId}" ${sIdx === 0 ? 'checked' : ''}>
          <span style="flex:1;">
            <strong>Step ${sIdx + 1}: ${escapeHtml(s.name)}</strong>
            <span class="muted" style="font-size:0.78rem;">(${escapeHtml(s.status)})</span>
            ${s.attachedOutputRef ? `<span class="pill" style="font-size:0.7rem; margin-left:4px;">Has Output</span>` : ''}
          </span>
        `;

        row.querySelector('input').addEventListener('change', () => {
          updateAttachMismatchWarning(turn.agentId, s.agentId, s.name, agentName);
        });

        radioList.append(row);
      });

      // Initial check
      const firstStep = sessionState.playbookSteps[0];
      updateAttachMismatchWarning(turn.agentId, firstStep.agentId, firstStep.name, agentName);
    }

    if (typeof openOverlayModal === 'function') {
      openOverlayModal('modal-attach-workflow');
    } else {
      modal.classList.add('open');
    }
  }

  function updateAttachMismatchWarning(turnAgentId, stepAgentId, stepName, turnAgentName) {
    const warn = byId('attach-mismatch-warning');
    if (!warn) return;
    if (turnAgentId && stepAgentId && turnAgentId !== stepAgentId) {
      warn.style.display = 'block';
      warn.innerHTML = `<strong>Agent Mismatch Notice:</strong> This response came from <strong>${escapeHtml(turnAgentName)}</strong>, while this workflow step is assigned to <strong>${escapeHtml(stepName)}</strong>. Attachment is allowed and will be clearly disclosed on the step card.`;
    } else {
      warn.style.display = 'none';
    }
  }

  function confirmAttachTurnToWorkflow() {
    if (!sessionState.pendingAttachTurn) return;
    const { turnIndex, turn } = sessionState.pendingAttachTurn;
    const selectedRadio = document.querySelector('input[name="attach-target-step"]:checked');
    if (!selectedRadio) return;

    const stepId = selectedRadio.value;
    const step = sessionState.playbookSteps.find(s => s.stepId === stepId);
    if (!step) return;

    const resp = turn.response || {};
    const primaryText = resp.summary || resp.decision || resp.response || resp.plan || (typeof resp === 'string' ? resp : JSON.stringify(resp));
    const agentName = turn.route ? turn.route.selected_display_name : turn.agentId;
    const sourceCount = (resp.source_evidence && resp.source_evidence.length) || (turn.preparedPayload?.web_context?.length) || 0;

    // Reference-first storage: do not duplicate full response body
    step.attachedOutputRef = {
      turnIndex: turnIndex,
      responseId: (resp.responseContext && resp.responseContext.responseId) || (resp.generation && resp.generation.responseId) || null,
      agentId: turn.agentId,
      agentName: agentName,
      displayLabel: `Turn #${turnIndex + 1} (${agentName})`,
      excerpt: primaryText.slice(0, 300),
      highStakes: !!(turn.route && turn.route.high_stakes),
      sourceCount: sourceCount,
      generationMode: resp.actualMode || 'standard',
      attachedAt: new Date().toISOString(),
    };

    if (typeof closeOverlayModal === 'function') {
      closeOverlayModal('modal-attach-workflow');
    } else {
      byId('modal-attach-workflow')?.classList.remove('open');
    }
    sessionState.pendingAttachTurn = null;
    renderPlaybookSteps();
    showToast(`Attached Turn #${turnIndex + 1} to "${step.name}".`);
  }

  // ==========================================
  // Modal Step Target Selector (Part J - Eliminates prompt())
  // ==========================================

  function openTargetStepModal(title, description, availableSteps, onConfirm) {
    const modal = byId('modal-step-target-selector');
    if (!modal) return;

    byId('step-target-modal-title').textContent = title || 'Select Target Step';
    byId('step-target-modal-desc').textContent = description || 'Choose which workflow step should receive this input:';

    const radioList = byId('step-target-radio-list');
    radioList.replaceChildren();

    if (!availableSteps.length) {
      radioList.innerHTML = '<div class="muted" style="padding:10px;">No compatible workflow steps available.</div>';
      byId('confirm-step-target-btn').disabled = true;
    } else {
      byId('confirm-step-target-btn').disabled = false;
      availableSteps.forEach((s, idx) => {
        const row = document.createElement('label');
        row.style.display = 'flex';
        row.style.alignItems = 'center';
        row.style.gap = '8px';
        row.style.padding = '8px 10px';
        row.style.background = '#f8fafc';
        row.style.border = '1px solid #e2e8f0';
        row.style.borderRadius = '5px';
        row.style.cursor = 'pointer';

        row.innerHTML = `
          <input type="radio" name="target-step-pick" value="${s.stepId}" ${idx === 0 ? 'checked' : ''}>
          <div style="flex:1;">
            <strong>Step ${sessionState.playbookSteps.indexOf(s) + 1}: ${escapeHtml(s.name)}</strong>
            <div class="muted" style="font-size:0.78rem;">${escapeHtml(s.purpose)}</div>
          </div>
        `;
        radioList.append(row);
      });
    }

    sessionState.pendingStepTargetCallback = onConfirm;

    if (typeof openOverlayModal === 'function') {
      openOverlayModal('modal-step-target-selector');
    } else {
      modal.classList.add('open');
    }
  }

  function assignResultBoardToWorkflow(rbItemId) {
    if (!sessionState.playbookSteps.length) {
      alert('No steps in current workflow. Select or create a playbook first.');
      return;
    }
    const rbItem = sessionState.resultBoard?.find(r => r.id === rbItemId);
    const label = rbItem ? `${rbItem.agentDisplayName} Result` : 'Result Board entry';

    openTargetStepModal(
      'Assign Result Board Entry to Step',
      `Select which workflow step will receive ${label} as its input:`,
      sessionState.playbookSteps,
      (targetStepId) => {
        const targetStep = sessionState.playbookSteps.find(s => s.stepId === targetStepId);
        if (targetStep) {
          targetStep.inputMode = 'result_board';
          targetStep.inputRef = rbItemId;
          switchProductivityTab('panel-playbooks');
          renderPlaybookSteps();
          showToast(`Assigned Result Board entry as input for "${targetStep.name}".`);
        }
      }
    );
  }

  function openTargetStepPickerForOutput(fromStepId) {
    const fromStep = sessionState.playbookSteps.find(s => s.stepId === fromStepId);
    const eligibleSteps = sessionState.playbookSteps.filter(s => s.stepId !== fromStepId);

    if (!eligibleSteps.length) {
      alert('No other workflow steps exist to receive this output as input.');
      return;
    }

    openTargetStepModal(
      'Use Output as Input for Another Step',
      `Select which workflow step should receive the output from "${fromStep ? fromStep.name : 'this step'}":`,
      eligibleSteps,
      (targetStepId) => {
        const targetStep = sessionState.playbookSteps.find(s => s.stepId === targetStepId);
        if (targetStep) {
          targetStep.inputMode = 'specific_step_output';
          targetStep.inputRef = fromStepId;
          renderPlaybookSteps();
          showToast(`Configured "${targetStep.name}" input to receive output from "${fromStep ? fromStep.name : 'Step'}".`);
        }
      }
    );
  }

  function assignContextKitToCurrentWorkflow() {
    if (!sessionState.currentWorkflowStepId) {
      if (sessionState.playbookSteps.length > 0) {
        sessionState.currentWorkflowStepId = sessionState.playbookSteps[0].stepId;
      } else {
        alert('No workflow steps available.');
        return;
      }
    }
    const step = sessionState.playbookSteps.find(s => s.stepId === sessionState.currentWorkflowStepId);
    if (step) {
      step.inputMode = 'context_kit';
      switchProductivityTab('panel-playbooks');
      renderPlaybookSteps();
      showToast(`Assigned Context Kit as input for "${step.name}".`);
    }
  }

  // ==========================================
  // Workflow Packet Drawer & Composer
  // ==========================================

  function openWorkflowPacketDrawer() {
    const drawer = byId('drawer-workflow-packet');
    if (!drawer) return;

    const selector = byId('wf-packet-steps-selector');
    selector.replaceChildren();

    const stepsWithOutputs = sessionState.playbookSteps.filter(s => s.attachedOutputRef);
    if (!stepsWithOutputs.length) {
      selector.innerHTML = '<div class="muted" style="padding:6px;">No steps currently have attached outputs. Attach outputs to workflow steps first.</div>';
    } else {
      stepsWithOutputs.forEach((s) => {
        const resolved = resolveWorkflowAttachedOutputContent(s.attachedOutputRef);
        const row = document.createElement('label');
        row.style.display = 'flex';
        row.style.alignItems = 'center';
        row.style.gap = '8px';
        row.style.fontSize = '0.84rem';
        row.style.cursor = 'pointer';

        row.innerHTML = `
          <input type="checkbox" class="wf-packet-step-cb" value="${s.stepId}" ${resolved.isStale ? '' : 'checked'}>
          <span>
            <strong>${escapeHtml(s.name)}</strong> — ${escapeHtml(s.attachedOutputRef.agentName)}
            ${resolved.isStale ? '<span class="pill danger" style="font-size:0.7rem; margin-left:4px;">Stale</span>' : `<span class="muted" style="font-size:0.75rem;">(${resolved.text.length} chars)</span>`}
          </span>
        `;

        row.querySelector('input').addEventListener('change', updateWorkflowPacketPreview);
        selector.append(row);
      });
    }

    updateWorkflowPacketPreview();
    if (typeof openOverlayModal === 'function') {
      openOverlayModal('drawer-workflow-packet');
    } else {
      drawer.classList.add('open');
    }
  }

  function buildWorkflowPacketText() {
    const checkedStepIds = Array.from(document.querySelectorAll('.wf-packet-step-cb:checked')).map(cb => cb.value);
    const pbName = byId('playbook-select')?.selectedOptions?.[0]?.textContent || 'Workflow Playbook';

    let text = `==================================================\n`;
    text += `WORKFLOW REVIEW & SYNTHESIS PACKET\n`;
    text += `Playbook: ${pbName}\n`;
    text += `Compiled: ${new Date().toLocaleTimeString()}\n`;
    text += `==================================================\n\n`;

    sessionState.playbookSteps.forEach((s, idx) => {
      if (!checkedStepIds.includes(s.stepId) || !s.attachedOutputRef) return;
      const resolved = resolveWorkflowAttachedOutputContent(s.attachedOutputRef);
      if (resolved.isStale || !resolved.text) return;

      text += `--------------------------------------------------\n`;
      text += `STEP ${idx + 1}: ${s.name}\n`;
      text += `Assigned Agent: ${s.agentId}\n`;
      text += `Responding Agent: ${s.attachedOutputRef.agentName}\n`;
      text += `Purpose: ${s.purpose}\n`;
      if (s.userNotes) text += `Step Notes: ${s.userNotes}\n`;
      if (s.attachedOutputRef.sourceCount > 0) text += `Reviewed Sources Attached: ${s.attachedOutputRef.sourceCount}\n`;
      if (s.attachedOutputRef.highStakes) text += `High-Stakes Category: YES\n`;
      if (s.reviewFlags.needsReview) text += `Flag: NEEDS REVIEW\n`;
      if (s.reviewFlags.potentialConflict) text += `Flag: POTENTIAL CONFLICT\n`;
      text += `\nOutput Content:\n${resolved.text}\n`;
      text += `--------------------------------------------------\n\n`;
    });

    return text.trim();
  }

  function updateWorkflowPacketPreview() {
    const packetText = buildWorkflowPacketText();
    const charCount = packetText.length;

    const budgetText = byId('wf-packet-budget-text');
    const budgetBar = byId('wf-packet-budget-bar');
    const previewEl = byId('wf-packet-preview-text');
    const warnEl = byId('wf-packet-oversized-warning');

    if (budgetText) budgetText.textContent = `${charCount.toLocaleString()} / ${MAX_WORKFLOW_PACKET_CHARS.toLocaleString()} chars`;
    if (previewEl) previewEl.textContent = packetText || 'No attached steps selected.';

    const isOver = charCount > MAX_WORKFLOW_PACKET_CHARS;
    if (budgetBar) {
      const pct = Math.min(100, Math.round((charCount / MAX_WORKFLOW_PACKET_CHARS) * 100));
      budgetBar.style.width = pct + '%';
      budgetBar.className = isOver ? 'budget-bar-fill danger' : (pct > 75 ? 'budget-bar-fill warning' : 'budget-bar-fill');
    }

    if (warnEl) warnEl.style.display = isOver ? 'block' : 'none';

    // Disable all action buttons fail-closed if oversized or empty
    const disabled = isOver || charCount === 0;
    byId('wf-packet-to-kit-btn').disabled = disabled;
    byId('wf-packet-to-prior-btn').disabled = disabled;
    byId('wf-packet-to-composer-btn').disabled = disabled;
    byId('wf-packet-prepare-review-btn').disabled = disabled;
    byId('wf-packet-prepare-decision-btn').disabled = disabled;
  }

  function handleWorkflowPacketAction(actionType) {
    const packetText = buildWorkflowPacketText();
    if (!packetText || packetText.length > MAX_WORKFLOW_PACKET_CHARS) {
      alert('Packet is empty or exceeds the 16,000 character maximum budget.');
      return;
    }

    if (actionType === 'add_kit') {
      if (typeof addContextKitItem === 'function') {
        addContextKitItem('workflow_packet', 'Workflow Synthesis Packet', packetText);
        if (typeof closeOverlayModal === 'function') closeOverlayModal('drawer-workflow-packet');
        else byId('drawer-workflow-packet')?.classList.remove('open');
      }
    } else if (actionType === 'stage_prior') {
      // Full packet staged without silent 4k slice (Part A3)
      if (typeof setStagedPriorContext === 'function') {
        setStagedPriorContext({
          agentId: 'workflow_synthesis',
          agentName: 'Workflow Synthesis Packet',
          responseId: 'wf_packet_' + Date.now(),
          summary: packetText,
        });
        if (typeof closeOverlayModal === 'function') closeOverlayModal('drawer-workflow-packet');
        else byId('drawer-workflow-packet')?.classList.remove('open');
        showToast('Staged full Workflow Packet as prior context.');
        byId('composer')?.scrollIntoView({ behavior: 'smooth' });
      }
    } else if (actionType === 'insert_composer') {
      const input = byId('prompt-input');
      if (input) {
        input.value = (input.value.trim() ? `${input.value.trim()}\n\n${packetText}` : packetText).trim();
        input.focus();
        if (typeof triggerReadinessEvaluation === 'function') triggerReadinessEvaluation();
        if (typeof closeOverlayModal === 'function') closeOverlayModal('drawer-workflow-packet');
        else byId('drawer-workflow-packet')?.classList.remove('open');
        showToast('Inserted Workflow Packet into prompt composer.');
        byId('composer')?.scrollIntoView({ behavior: 'smooth' });
      }
    } else if (actionType === 'prepare_review') {
      if (typeof selectAgentManually === 'function') {
        selectAgentManually('local_review_agent');
      }
      const prompt = `Review this compiled multi-agent workflow packet for gaps, contradictions, unaddressed risks, and logical inconsistencies:\n\n${packetText}`;
      const input = byId('prompt-input');
      if (input) {
        input.value = prompt;
        input.focus();
        if (typeof triggerReadinessEvaluation === 'function') triggerReadinessEvaluation();
      }
      if (typeof closeOverlayModal === 'function') closeOverlayModal('drawer-workflow-packet');
      else byId('drawer-workflow-packet')?.classList.remove('open');
      showToast('Prepared Review Agent request with Workflow Packet.');
      byId('composer')?.scrollIntoView({ behavior: 'smooth' });
    } else if (actionType === 'prepare_decision') {
      if (typeof closeOverlayModal === 'function') closeOverlayModal('drawer-workflow-packet');
      else byId('drawer-workflow-packet')?.classList.remove('open');
      if (typeof openDecisionComposer === 'function') {
        openDecisionComposer();
        const pbInput = byId('dec-problem-input');
        if (pbInput && !pbInput.value.trim()) {
          pbInput.value = 'Evaluate tradeoffs and synthesize final direction across workflow findings.';
        }
        showToast('Opened Decision Composer for workflow synthesis.');
      }
    }
  }

  function initWorkflowsDashboardEventHandlers() {
    byId('playbook-select')?.addEventListener('change', (e) => {
      selectPlaybook(e.target.value);
    });

    byId('reset-playbook-btn')?.addEventListener('click', () => {
      if (hasWorkflowDirtyState()) {
        if (!confirm('Reset all step notes, attached outputs, and statuses for this playbook?')) return;
      }
      selectPlaybook(sessionState.activePlaybookId, true);
      showToast('Reset active playbook steps.');
    });

    byId('add-step-btn')?.addEventListener('click', () => {
      const select = byId('add-step-agent-select');
      const agentId = select?.value;
      if (agentId) addAgentToWorkflow(agentId);
    });

    // Attach modal bindings
    byId('close-attach-modal-btn')?.addEventListener('click', () => {
      if (typeof closeOverlayModal === 'function') closeOverlayModal('modal-attach-workflow');
      else byId('modal-attach-workflow')?.classList.remove('open');
      sessionState.pendingAttachTurn = null;
    });
    byId('cancel-attach-btn')?.addEventListener('click', () => {
      if (typeof closeOverlayModal === 'function') closeOverlayModal('modal-attach-workflow');
      else byId('modal-attach-workflow')?.classList.remove('open');
      sessionState.pendingAttachTurn = null;
    });
    byId('confirm-attach-btn')?.addEventListener('click', confirmAttachTurnToWorkflow);
    byId('modal-attach-workflow')?.addEventListener('click', (e) => {
      if (e.target === byId('modal-attach-workflow')) {
        if (typeof closeOverlayModal === 'function') closeOverlayModal('modal-attach-workflow');
        else byId('modal-attach-workflow').classList.remove('open');
        sessionState.pendingAttachTurn = null;
      }
    });

    // Step target modal bindings
    byId('close-step-target-modal-btn')?.addEventListener('click', () => {
      if (typeof closeOverlayModal === 'function') closeOverlayModal('modal-step-target-selector');
      else byId('modal-step-target-selector')?.classList.remove('open');
      sessionState.pendingStepTargetCallback = null;
    });
    byId('cancel-step-target-btn')?.addEventListener('click', () => {
      if (typeof closeOverlayModal === 'function') closeOverlayModal('modal-step-target-selector');
      else byId('modal-step-target-selector')?.classList.remove('open');
      sessionState.pendingStepTargetCallback = null;
    });
    byId('confirm-step-target-btn')?.addEventListener('click', () => {
      const selected = document.querySelector('input[name="target-step-pick"]:checked');
      if (selected && typeof sessionState.pendingStepTargetCallback === 'function') {
        const cb = sessionState.pendingStepTargetCallback;
        sessionState.pendingStepTargetCallback = null;
        if (typeof closeOverlayModal === 'function') closeOverlayModal('modal-step-target-selector');
        else byId('modal-step-target-selector')?.classList.remove('open');
        cb(selected.value);
      }
    });
    byId('modal-step-target-selector')?.addEventListener('click', (e) => {
      if (e.target === byId('modal-step-target-selector')) {
        if (typeof closeOverlayModal === 'function') closeOverlayModal('modal-step-target-selector');
        else byId('modal-step-target-selector').classList.remove('open');
        sessionState.pendingStepTargetCallback = null;
      }
    });

    // Workflow packet bindings
    byId('open-wf-packet-btn')?.addEventListener('click', openWorkflowPacketDrawer);
    byId('close-wf-packet-btn')?.addEventListener('click', () => {
      if (typeof closeOverlayModal === 'function') closeOverlayModal('drawer-workflow-packet');
      else byId('drawer-workflow-packet')?.classList.remove('open');
    });
    byId('drawer-workflow-packet')?.addEventListener('click', (e) => {
      if (e.target === byId('drawer-workflow-packet')) {
        if (typeof closeOverlayModal === 'function') closeOverlayModal('drawer-workflow-packet');
        else byId('drawer-workflow-packet').classList.remove('open');
      }
    });

    byId('wf-packet-to-kit-btn')?.addEventListener('click', () => handleWorkflowPacketAction('add_kit'));
    byId('wf-packet-to-prior-btn')?.addEventListener('click', () => handleWorkflowPacketAction('stage_prior'));
    byId('wf-packet-to-composer-btn')?.addEventListener('click', () => handleWorkflowPacketAction('insert_composer'));
    byId('wf-packet-prepare-review-btn')?.addEventListener('click', () => handleWorkflowPacketAction('prepare_review'));
    byId('wf-packet-prepare-decision-btn')?.addEventListener('click', () => handleWorkflowPacketAction('prepare_decision'));

    // Context kit integration button
    byId('kit-to-workflow-btn')?.addEventListener('click', assignContextKitToCurrentWorkflow);
  }
  """

