from __future__ import annotations

import jarvis_core.app as app_module

from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.memory_dashboard import memory_dashboard_html


def page_text() -> str:
    return memory_dashboard_html()


def test_memory_page_route_returns_dedicated_page_and_uses_lan_guard():
    page = app_module.memory_center_page()
    text = page.body.decode("utf-8")
    routes = [
        route
        for route in app_module.app.routes
        if getattr(route, "path", None) == "/memory"
    ]

    assert "Jarvis Memory Center" in text
    assert len(routes) == 1
    dependency_calls = {
        dependency.call for dependency in routes[0].dependant.dependencies
    }
    assert require_dashboard_lan_access in dependency_calls


def test_page_has_header_navigation_and_complete_safety_banner():
    text = page_text()

    assert 'href="/dashboard"' in text
    assert "Local · User-controlled · Approval-gated · Auditable" in text
    assert 'class="safety-banner"' in text
    for statement in (
        "Memory is stored locally in Jarvis SQLite.",
        "New memories begin as pending",
        "Only approved, unexpired memories can be active.",
        "does not automatically save conversations",
        "does not automatically approve memory",
        "Memory retrieval is opt-in for exactly six representative pilot agents.",
        "Private-session state is temporary and page-local.",
        "Obvious credentials and secrets are rejected",
    ):
        assert statement in text


def test_summary_private_session_and_accessible_status_regions_exist():
    text = page_text()

    for element_id in (
        "summary-total",
        "summary-pending",
        "summary-active",
        "summary-approved",
        "summary-disabled",
        "summary-rejected",
        "summary-expired",
        "summary-inactive",
        "summary-loading",
        "summary-empty",
        "summary-error",
        "private-session-toggle",
        "private-session-policy-status",
        "memory-action-status",
    ):
        assert f'id="{element_id}"' in text
    assert 'role="switch"' in text
    assert 'aria-live="polite"' in text
    assert "let privateSession = false;" in text
    assert "privateSession = event.currentTarget.checked;" in text


def test_manual_proposal_form_has_exact_controlled_options_and_counter():
    text = page_text()

    assert 'id="proposal-form"' in text
    assert 'id="proposal-content"' in text
    assert 'maxlength="4000"' in text
    assert 'id="proposal-content-count"' in text
    for value in (
        "preference",
        "personal_fact",
        "goal",
        "constraint",
        "project_fact",
        "decision",
        "routine",
        "terminology",
        "agent_instruction",
    ):
        assert f'<option value="{value}">{value}</option>' in text
    assert '<option value="manual">manual</option>' in text
    proposal_form = text[text.index('id="proposal-form"'):text.index('id="stored-memory-title"')]
    assert "agent_proposal" not in proposal_form
    assert "migration" not in proposal_form
    assert 'sourceType: "manual"' in text
    assert 'actor: "local_user"' in text


def test_search_filters_pagination_and_manual_refresh_controls_exist():
    text = page_text()

    for element_id in (
        "memory-search-query",
        "memory-status-filter",
        "memory-type-filter",
        "memory-scope-filter",
        "memory-scope-value-filter",
        "memory-page-size",
        "memory-clear-filters-button",
        "memory-list-refresh-button",
        "memory-previous-button",
        "memory-next-button",
        "memory-range-status",
        "memory-list-loading",
        "memory-list-empty",
        "memory-list-error",
    ):
        assert f'id="{element_id}"' in text
    assert 'params.set("query", value)' not in text
    assert "Object.entries(values)" in text
    assert 'params.set("limit"' in text
    assert 'params.set("offset"' in text
    assert 'addEventListener("input", loadMemories)' not in text


def test_review_lifecycle_and_two_step_delete_controls_exist():
    text = page_text()

    for element_id in (
        "memory-detail",
        "memory-detail-content",
        "memory-detail-fields",
        "memory-lifecycle-actions",
        "approval-confirmation",
        "approval-confirm-checkbox",
        "rejection-confirmation",
        "rejection-reason",
        "memory-edit-section",
        "memory-edit-form",
        "edit-reapproval-warning",
        "disable-confirmation",
        "enable-confirmation",
        "delete-confirmation",
        "delete-confirm-input",
        "delete-final-button",
    ):
        assert f'id="{element_id}"' in text
    assert "Substantive changes will return this memory to pending and require approval again." in text
    assert "Type DELETE to continue" in text
    assert 'event.currentTarget.value !== "DELETE"' in text
    assert "Memory content will be removed from the memories table." in text
    assert "The action cannot be undone through Jarvis." in text


def test_event_history_and_context_preview_have_loading_empty_error_and_manual_controls():
    text = page_text()

    for element_id in (
        "event-history-refresh-button",
        "event-history-loading",
        "event-history-empty",
        "event-history-error",
        "event-history-list",
        "context-preview-form",
        "context-project-name",
        "context-agent-id",
        "context-limit",
        "context-preview-button",
        "context-preview-loading",
        "context-preview-empty",
        "context-preview-error",
        "context-preview-result",
        "context-preview-limitations",
    ):
        assert f'id="{element_id}"' in text
    assert "Manual context preview" in text
    assert "No agent was invoked" in text
    assert "No relevance ranking" in text
    assert "Not yet used in agent responses" in text
    assert 'requestJson("/api/memory/context-preview"' in text


def test_page_uses_no_external_or_persistent_browser_capabilities():
    text = page_text()
    forbidden = (
        "http://",
        "https://",
        "localStorage",
        "sessionStorage",
        "IndexedDB",
        "document.cookie",
        "serviceWorker",
        "caches.",
        "showOpenFilePicker",
        "showSaveFilePicker",
        "navigator.clipboard",
        "setInterval",
        "setTimeout",
        "queueMicrotask",
        'download=',
        ".download",
        "console.",
    )

    assert all(item not in text for item in forbidden)
    assert "<script src=" not in text
    assert "<link rel=" not in text


def test_dynamic_memory_text_uses_safe_dom_apis():
    text = page_text()

    assert ".innerHTML" not in text
    assert "replaceChildren" in text
    assert "document.createElement" in text
    assert ".textContent" in text
    assert 'addEventListener("click"' in text
    assert "onclick=" not in text
    assert "console." not in text
    assert "memory.content" in text
    assert "selectedMemory.content" in text
    assert "href=${memory.content" not in text
    assert "encodeURIComponent(memory.content" not in text
    assert "window.history" not in text


def test_page_has_no_automatic_agent_or_lifecycle_execution():
    text = page_text()

    assert "/agents/" not in text
    assert 'addEventListener("click", () => runSelectedAction(' in text
    assert 'addEventListener("submit", submitProposal)' in text
    assert 'addEventListener("submit", submitContextPreview)' in text
    assert "Promise.all([loadSummary(), loadMemories()])" in text
    assert "poll" not in text.lower()


def test_ranked_preview_and_retrieval_audit_panels_are_explicit_and_redacted():
    text = page_text()

    assert "Ranked Retrieval Preview" in text
    assert "Retrieval Audit History" in text
    for element_id in (
        "ranked-retrieval-form",
        "ranked-retrieval-query",
        "ranked-retrieval-project",
        "ranked-retrieval-agent",
        "ranked-retrieval-max-items",
        "ranked-retrieval-sensitive",
        "ranked-retrieval-button",
        "ranked-retrieval-result",
        "ranked-retrieval-items",
        "retrieval-audit-agent",
        "retrieval-audit-purpose",
        "retrieval-audit-refresh",
        "retrieval-audit-previous",
        "retrieval-audit-next",
        "retrieval-audit-list",
        "retrieval-audit-detail",
    ):
        assert f'id="{element_id}"' in text
    assert 'requestJson("/api/memory/retrieval-preview"' in text
    assert 'requestJson(`/api/memory/retrievals?' in text
    assert "No agent is invoked" in text
    assert "No memory is modified" in text
    assert "Raw queries and historical memory content are not stored or displayed." in text
    assert 'addEventListener("submit", submitRankedRetrieval)' in text
    assert "loadRetrievalHistory();" in text
    assert "setInterval" not in text
    assert "item.content" in text
    assert "encodeURIComponent(item.content" not in text
    assert ".innerHTML" not in text
    assert "Promise.all([loadSummary(), loadMemories()])" in text
    assert "Promise.all([loadSummary(), loadMemories(), loadRetrievalHistory()])" not in text
