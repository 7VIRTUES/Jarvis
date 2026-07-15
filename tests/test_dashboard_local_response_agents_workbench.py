import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


EXPECTED_ENDPOINTS = [
    "POST /agents/research/local-brief",
    "POST /agents/files/local-summary",
    "POST /agents/planning/local-plan",
    "POST /agents/drafting/local-draft",
    "POST /agents/review/local-review",
    "POST /agents/decision/local-decision",
    "POST /agents/troubleshooting/local-triage",
    "POST /agents/summarization/local-summary",
    "POST /agents/extraction/local-extract",
    "POST /agents/classification/local-classify",
    "POST /agents/transformation/local-transform",
    "POST /agents/business/local-brief",
    "POST /agents/health-fitness/local-plan",
    "POST /agents/food-cooking-grocery/local-plan",
    "POST /agents/home-room-living-space/local-plan",
    "POST /agents/legal-immigration-official/local-plan",
    "POST /agents/emergency-preparedness/local-plan",
    "POST /agents/culture-taste-high-class-lifestyle/local-plan",
    "POST /agents/hobbies-adventure/local-plan",
    "POST /agents/personal-knowledge-memory-organizer/local-plan",
    "POST /agents/life-dashboard-coordinator/local-plan",
    "POST /agents/everyday-life/local-plan",
    "POST /agents/online-presence/local-plan",
    "POST /agents/security-safety/local-review",
    "POST /agents/creator/local-plan",
    "POST /agents/school-robotics/local-plan",
    "POST /agents/career/local-plan",
    "POST /agents/finance-budget/local-plan",
    "POST /agents/housing-move-travel/local-plan",
    "POST /agents/projects-portfolio/local-plan",
    "POST /agents/learning-study/local-plan",
    "POST /agents/social-networking/local-plan",
    "POST /agents/personal-admin/local-plan",
    "POST /agents/vehicle-devices-gear/local-plan",
    "POST /agents/life-direction/local-plan",
    "POST /agents/relationships/local-plan",
    "POST /agents/emotional-reflection/local-reflect",
]


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return dashboard


def dashboard_page_text() -> str:
    return app_module.local_dashboard().body.decode("utf-8")


def local_response_agents_section() -> str:
    page_text = dashboard_page_text()
    start = page_text.index('id="local-response-agents-index"')
    end = page_text.index('id="vm-validation-prep-center"')
    return page_text[start:end]


def test_dashboard_html_includes_local_response_agents_workbench_controls(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    section = local_response_agents_section()

    assert "Local Response Agents Overview" in section
    assert "Categories" in section
    assert "Agent Details" in section
    assert "Request Template" in section
    assert "Sample Payload" in section
    assert "Use sample payload" in section
    assert "Route Preview" in section
    assert "Discovery catalog metadata pending." in section
    assert "Suggested only — not executed" in section
    assert "Route preview does not invoke agents" in section
    assert "Select manually before running a local response" in section
    assert "Manual Multi-Agent Workflow Builder" in section
    assert "Manual workflow only" in section
    assert "Steps are suggestions, not execution" in section
    assert "Run one selected agent at a time" in section
    assert "Prior context is inserted only after user review" in section
    assert "No automatic handoff" in section
    assert "No persistence" in section
    assert "No connectors" in section
    assert "Local Response Agents Workbench" in section
    assert "Request Composer" in section
    assert "Optional Public Web Research" in section
    assert "Read-only public web only" in section
    assert "No logins or accounts" in section
    assert "No forms, posts, purchases, or bookings" in section
    assert "No private networks or localhost" in section
    assert "No downloads or scripts" in section
    assert "Manual click required" in section
    assert "Source context is inserted for review, not executed automatically" in section
    assert "Reviewed source context" in section
    assert "web_context is optional, non-persistent, and supplied only from the manual payload" in section
    assert "Agents consume provided excerpts; they do not browse automatically" in section
    assert "Source labels are for reference, not proof" in section
    assert "Review excerpts before running the selected agent" in section
    assert "How selected agent will use reviewed sources" in section
    assert "Sources support context only; they are not proof" in section
    assert "Agent will not browse automatically" in section
    assert "Verify freshness and authority before acting" in section
    assert "Session Result Board" in section
    assert "Review Packet Composer" in section
    assert "Result Comparison Matrix" in section
    assert "Add latest response to session board" in section
    assert "Insert selected entry as prior_agent_context" in section
    assert "Insert review packet as prior_agent_context" in section
    assert "Session-only" in section
    assert "Not persisted" in section
    assert "Manual review only" in section
    assert "No automatic handoff" in section
    assert "No connector" in section
    assert "No file export" in section
    assert "Board clears when the page reloads" in section
    assert 'id="local-response-agents-discovery-status"' in section
    assert 'id="local-response-agents-category-select"' in section
    assert 'id="local-response-agents-detail-panel"' in section
    assert 'id="local-response-agents-boundary-flags"' in section
    assert 'id="local-response-agents-request-template"' in section
    assert 'id="local-response-agents-sample-payload"' in section
    assert 'id="local-response-agents-use-sample-button"' in section
    assert 'id="local-response-agents-route-preview-input"' in section
    assert 'id="local-response-agents-route-preview-button"' in section
    assert 'id="local-response-agents-route-preview-suggestions"' in section
    assert 'id="local-response-agents-route-preview-result"' in section
    assert 'id="local-response-agents-manual-workflow-builder"' in section
    assert 'id="local-response-agents-manual-workflow-boundaries"' in section
    assert 'id="local-response-agents-manual-workflow-goal"' in section
    assert 'id="local-response-agents-manual-workflow-candidates"' in section
    assert 'id="local-response-agents-manual-workflow-include-web-context"' in section
    assert 'id="local-response-agents-manual-workflow-preview-button"' in section
    assert 'id="local-response-agents-manual-workflow-load-step-button"' in section
    assert 'id="local-response-agents-prior-context-copy-button"' in section
    assert 'id="local-response-agents-manual-workflow-status"' in section
    assert 'id="local-response-agents-manual-workflow-steps"' in section
    assert 'id="local-response-agents-manual-workflow-result"' in section
    assert 'id="local-response-agents-composer"' in section
    assert 'id="local-response-agents-composer-boundaries"' in section
    assert 'id="local-response-agents-output-type-select"' in section
    assert 'id="local-response-agents-payload-preview-status"' in section
    assert 'id="local-response-agents-web-research"' in section
    assert 'id="local-response-agents-web-research-enabled"' in section
    assert 'id="local-response-agents-web-research-urls"' in section
    assert 'id="local-response-agents-web-research-validate-button"' in section
    assert 'id="local-response-agents-web-research-fetch-button"' in section
    assert 'id="local-response-agents-web-research-context-button"' in section
    assert 'id="local-response-agents-web-research-add-button"' in section
    assert 'id="local-response-agents-web-research-status"' in section
    assert 'id="local-response-agents-web-research-result"' in section
    assert 'id="local-response-agents-reviewed-source-context"' in section
    assert 'id="local-response-agents-reviewed-source-manager"' in section
    assert 'id="local-response-agents-reviewed-source-list"' in section
    assert 'id="local-response-agents-reviewed-source-clear-button"' in section
    assert 'id="local-response-agents-source-aware-preview"' in section
    assert 'id="local-response-agents-source-aware-preview-body"' in section
    assert 'id="local-response-agents-reviewed-web-context-preview"' in section
    assert 'id="local-response-agents-workbench-select"' in section
    assert 'id="local-response-agents-workbench-endpoint"' in section
    assert 'id="local-response-agents-workbench-body"' in section
    assert 'id="local-response-agents-workbench-run-button"' in section
    assert "Run selected local response agent" in section
    assert 'id="local-response-agents-workbench-status"' in section
    assert 'id="local-response-agents-response-boundaries"' in section
    assert 'id="local-response-agents-structured-response"' in section
    assert 'id="local-response-agents-workbench-response"' in section
    assert 'id="local-response-agents-session-result-board"' in section
    assert 'id="local-response-agents-session-board-add-button"' in section
    assert 'id="local-response-agents-session-board-compare-button"' in section
    assert 'id="local-response-agents-session-board-packet-button"' in section
    assert 'id="local-response-agents-session-board-insert-entry-button"' in section
    assert 'id="local-response-agents-session-board-insert-packet-button"' in section
    assert 'id="local-response-agents-session-board-clear-button"' in section
    assert 'id="local-response-agents-session-board-entries"' in section
    assert 'id="local-response-agents-result-comparison-matrix"' in section
    assert 'id="local-response-agents-result-comparison-body"' in section
    assert 'id="local-response-agents-review-packet-composer"' in section
    assert 'id="local-response-agents-review-packet-output"' in section


def test_dashboard_workbench_states_local_allowlisted_non_runner_boundaries(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    section = local_response_agents_section().lower()

    assert "local-only workbench" in section
    assert "allowlisted to the 37 local response-agent endpoints" in section
    assert "manual input only" in section
    assert "local only" in section
    assert "response only" in section
    assert "no connector" in section
    assert "non-persistent" in section
    assert "suggested only — not executed" in section
    assert "route preview does not invoke agents" in section
    assert "select manually before running a local response" in section
    assert "manual workflow only" in section
    assert "steps are suggestions, not execution" in section
    assert "run one selected agent at a time" in section
    assert "prior context is inserted only after user review" in section
    assert "no automatic handoff" in section
    assert "no persistence" in section
    assert "no connectors" in section
    assert "not an arbitrary request runner" in section
    assert "not a connector runner" in section
    assert "not persistent" in section
    assert "not certification or validation" in section
    assert "file/data agent requires a registered project" in section
    assert "editable json payload preview" in section
    assert "editable json payload preview - manual input only" in section
    assert "output type from request-template metadata" in section
    assert "public web research is optional, public-only, read-only, and never background browsing" in section
    assert "not executed automatically" in section
    assert "session-only" in section
    assert "not persisted" in section
    assert "manual review only" in section
    assert "no automatic handoff" in section
    assert "no connector" in section
    assert "no file export" in section
    assert "board clears when the page reloads" in section


def test_dashboard_workbench_js_builds_allowlist_from_summary_agents(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "function localResponseAgentAllowlist(agents)" in page_text
    assert "function localResponseAgentId(agent)" in page_text
    assert "function localResponseAgentTemplatePath(agent)" in page_text
    assert "function localResponseAgentTemplateOutputTypes(template, agent)" in page_text
    assert "function selectedOutputTypeField(payload)" in page_text
    assert "function localResponseAgentPayloadWithSelectedOutputType(payload, outputType)" in page_text
    assert "function renderAgentDetail(agent)" in page_text
    assert "async function loadSelectedTemplate(agent)" in page_text
    assert "async function loadDiscoveryCatalogMetadata()" in page_text
    assert "async function loadCategoryMetadata()" in page_text
    assert "function populateOutputTypeSelect(template, agent)" in page_text
    assert "function applySamplePayloadToComposer(template, agent)" in page_text
    assert "function refreshPayloadOutputType()" in page_text
    assert "function localResponseWebResearchUrls()" in page_text
    assert "function localResponseWebContextEntries(sources)" in page_text
    assert "function localResponseSourceLabel(index)" in page_text
    assert "function localResponseReviewedSourcesFromPayload()" in page_text
    assert "function localResponseReviewedSourceWarnings(source, label)" in page_text
    assert "function renderReviewedSourceManager(entries)" in page_text
    assert "function writeReviewedSourcesToPayload(entries, statusText)" in page_text
    assert "function removeReviewedSource(index)" in page_text
    assert "function clearReviewedSources()" in page_text
    assert "function renderSourceAwareUsagePreview(entries)" in page_text
    assert "function renderReviewedWebContextPreview()" in page_text
    assert "function localResponseManualWorkflowCandidateIds()" in page_text
    assert "function localResponseRoutePreviewSuggestionIds()" in page_text
    assert "function renderManualWorkflowSteps(result)" in page_text
    assert "function localResponsePriorContextFromLatestResponse()" in page_text
    assert "function insertLatestResponseAsPriorContext()" in page_text
    assert "function sessionBoardEntryFromLatestResponse()" in page_text
    assert "function renderSessionResultBoard()" in page_text
    assert "function addLatestResponseToSessionBoard()" in page_text
    assert "function buildSessionComparison()" in page_text
    assert "function buildReviewPacket()" in page_text
    assert "function priorContextFromSessionEntry(entry)" in page_text
    assert "function priorContextFromReviewPacket()" in page_text
    assert "function writePriorContextToPayload(context, successText)" in page_text
    assert "function insertSelectedBoardEntryAsPriorContext()" in page_text
    assert "function insertReviewPacketAsPriorContext()" in page_text
    assert "function clearSessionResultBoard()" in page_text
    assert "async function postWebResearchJson(path, body)" in page_text
    assert "outputTypeSelect.onchange = refreshPayloadOutputType" in page_text
    assert "useSampleButton.onclick = () =>" in page_text
    assert "routePreviewSuggestions.onchange = async () =>" in page_text
    assert "manualWorkflowPreviewButton.onclick = async () =>" in page_text
    assert "manualWorkflowLoadStepButton.onclick = async () =>" in page_text
    assert "priorContextCopyButton.onclick = insertLatestResponseAsPriorContext" in page_text
    assert "sessionBoardAddButton.onclick = addLatestResponseToSessionBoard" in page_text
    assert "sessionBoardCompareButton.onclick = buildSessionComparison" in page_text
    assert "sessionBoardPacketButton.onclick = buildReviewPacket" in page_text
    assert "sessionBoardInsertEntryButton.onclick = insertSelectedBoardEntryAsPriorContext" in page_text
    assert "sessionBoardInsertPacketButton.onclick = insertReviewPacketAsPriorContext" in page_text
    assert "sessionBoardClearButton.onclick = clearSessionResultBoard" in page_text
    assert "webResearchValidateButton.onclick = async () =>" in page_text
    assert "webResearchFetchButton.onclick = async () =>" in page_text
    assert "webResearchContextButton.onclick = async () =>" in page_text
    assert "webResearchAddButton.onclick = () =>" in page_text
    assert "renderStructuredLocalResponse(structuredResponse, responseBody)" in page_text
    assert "localResponseAgentEndpointParts(agent.endpoint)" in page_text
    assert "endpoint.method === 'POST'" in page_text
    assert "endpoint.path.startsWith('/agents/')" in page_text
    assert "new Set" in page_text
    assert "agent.category || 'Uncategorized'" in page_text
    assert "agent.displayName || agent.name" in page_text
    assert "agent.web_research_available || agent.webResearchAvailable" in page_text
    assert "Limitations:" in page_text
    assert "agent.safetyNotes || agent.safety_notes" in page_text
    assert "initializeLocalResponseAgentsWorkbench(summary.localResponseAgentsIndex)" in page_text


def test_dashboard_workbench_uses_discovery_template_and_route_preview_endpoints(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "fetch('/agents/local-response-agents/catalog')" in page_text
    assert "fetch('/agents/local-response-agents/categories')" in page_text
    assert "fetch(templatePath)" in page_text
    assert "fetch('/agents/local-response-agents/route-preview'" in page_text
    assert "fetch('/agents/local-response-agents/manual-workflow-preview'" in page_text
    assert "postWebResearchJson('/web-research/validate-url'" in page_text
    assert "postWebResearchJson('/web-research/fetch-public-url'" in page_text
    assert "postWebResearchJson('/web-research/agent-context-preview'" in page_text
    assert "localResponseAgentTemplatePath(agent)" in page_text
    assert "template.sample_payload || template.samplePayload" in page_text
    assert "populateOutputTypeSelect(template, agent)" in page_text
    assert "applySamplePayloadToComposer(template, agent)" in page_text
    assert "preferredOutputType: outputTypeSelect.value || 'summary'" in page_text
    assert "useSampleButton.onclick = () =>" in page_text
    assert "routePreviewButton.onclick = async () =>" in page_text
    assert "Suggested only — not executed" in page_text
    assert "Route preview does not invoke agents" in page_text
    assert "Select manually before running a local response" in page_text
    assert "renderRoutePreviewSuggestions(result)" in page_text
    assert "No handoff, no automation, no persistence, no connector, and no agent invocation." in page_text
    assert "Manual workflow preview does not invoke agents, create handoffs, or persist workflows." in page_text
    assert "Workflow step loaded into the request composer. Manual step only - not executed, not handed off, and not persisted." in page_text
    assert "prior_agent_context inserted into the editable payload for manual review. No automatic handoff, no persistence, and no agent invocation occurred." in page_text
    assert "Latest response is available for manual board capture. Add latest response to session board only after review." in page_text
    assert "No latest response yet. Run one selected local response agent manually, review the result, then add it to the session board." in page_text
    assert "No board entries yet. Add latest response to session board after a structured response returns." in page_text
    assert "No selected entries. Select board entries before building a comparison." in page_text
    assert "Fewer than 2 selected entries for comparison. Select at least two board entries." in page_text
    assert "Invalid editable payload JSON while inserting prior context" in page_text
    assert "prior_agent_context insertion succeeded from selected board entry, but agent was not run. Editable JSON payload updated only." in page_text
    assert "prior_agent_context insertion succeeded from review packet, but agent was not run. Editable JSON payload updated only." in page_text
    assert "Board cleared from current session only. Board clears when the page reloads." in page_text
    assert "manual_session_board_output" in page_text
    assert "manual_session_review_packet" in page_text


def test_dashboard_workbench_web_research_is_manual_public_and_not_agent_execution(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "Optional Public Web Research" in page_text
    assert "Read-only public web only" in page_text
    assert "No logins or accounts" in page_text
    assert "No forms, posts, purchases, or bookings" in page_text
    assert "No private networks or localhost" in page_text
    assert "No downloads or scripts" in page_text
    assert "Manual click required" in page_text
    assert "Source context is inserted for review, not executed automatically" in page_text
    assert "Add source context to payload" in page_text
    assert "Source labels are for reference, not proof" in page_text
    assert "Sources support context only; they are not proof" in page_text
    assert "The selected agent may use these reviewed excerpts for source-aware response sections only" in page_text
    assert "No auto-fetch, no auto-submit, no connector, and no background browsing" in page_text
    assert "Clear reviewed sources" in page_text
    assert "web_context" in page_text
    assert "webResearchEnabled.checked" in page_text
    assert "No agent is invoked." in page_text
    assert "No local response agent is invoked." in page_text
    assert "The selected agent was not invoked." in page_text
    assert "No auto-fetch, no auto-submit, no handoff, no persistence." in page_text
    assert "localResponseWebContextEntries(latestWebResearchSources)" in page_text
    assert "parsedBody.web_context = contextEntries" in page_text
    assert "Reviewed source context inserted into web_context. The selected agent was not invoked." in page_text
    assert "Reviewed source [${label}] removed from web_context. The selected agent was not invoked." in page_text
    assert "Reviewed sources cleared from web_context. The selected agent was not invoked." in page_text
    assert "data-reviewed-source-index" in page_text
    assert "Excerpt is partial, user-reviewed, and not independently verified." in page_text
    assert "renderReviewedWebContextPreview()" in page_text


def test_dashboard_workbench_has_safe_empty_and_unknown_template_states(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "No local response agent selected. Choose a category or agent to inspect local metadata." in page_text
    assert "No boundary flags available for the current selection." in page_text
    assert "No request template available for the current selection." in page_text
    assert "Template metadata was not found for this agent id." in page_text
    assert "Request template unavailable. No local response agent was invoked." in page_text
    assert "Category endpoint unavailable; using dashboard summary metadata." in page_text
    assert "No route preview suggestions available." in page_text
    assert "Unknown template: editable JSON payload preview uses catalog example metadata only." in page_text
    assert "Missing agent" in page_text
    assert "Endpoint rejection" in page_text
    assert "Manual input was not sent to a local response agent" in page_text
    assert "No selected-agent local response was requested" in page_text
    assert "Backend error or validation error" in page_text
    assert "Backend error" in page_text


def test_dashboard_workbench_rejects_unsupported_endpoint_before_fetch(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()
    unsupported_index = page_text.index("Endpoint rejection: missing agent or selected catalog entry is not allowlisted.")
    fetch_index = page_text.index("const response = await fetch(endpointPath")

    assert "!allowlistedEndpointPaths.has(endpointPath)" in page_text
    assert unsupported_index < fetch_index


def test_dashboard_workbench_rejects_invalid_json_before_fetch(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()
    invalid_json_index = page_text.index("Invalid JSON:")
    fetch_index = page_text.index("const response = await fetch(endpointPath")

    assert "JSON.parse(bodyInput.value || '{}')" in page_text
    assert "request body must be a JSON object" in page_text
    assert "renderWorkbenchError(structuredResponse, 'Invalid JSON'" in page_text
    assert "renderWorkbenchError(structuredResponse, 'Validation error'" in page_text
    assert invalid_json_index < fetch_index


def test_dashboard_workbench_posts_only_to_selected_catalog_endpoint_path(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "const response = await fetch(endpointPath" in page_text
    assert "method: 'POST'" in page_text
    assert "headers: { 'Content-Type': 'application/json' }" in page_text
    assert "body: JSON.stringify(parsedBody)" in page_text
    assert "parsedBody = localResponseAgentPayloadWithSelectedOutputType(parsedBody, outputTypeSelect.value || '')" in page_text
    assert "endpointDisplay.textContent = endpointPath" in page_text
    assert "selectedEndpointPath(agent)" in page_text


def test_dashboard_workbench_renders_structured_common_response_fields(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "function renderStructuredLocalResponse(target, responseBody)" in page_text
    assert "function renderLocalResponseValue(value)" in page_text
    assert "function renderWorkbenchError(target, title, message, details)" in page_text
    expected_fields = [
        "title",
        "summary",
        "assumptions",
        "recommended_plan",
        "step_by_step",
        "checklist",
        "next_actions",
        "priority_order",
        "recommended_agents",
        "risk_flags",
        "safety_notes",
        "limitations",
        "local_only_boundaries",
        "follow_up_questions",
        "source_evidence",
        "citation_labels",
        "source_quality_warnings",
        "source_recency_notes",
        "source_context_summary",
        "sources_used",
        "web_context_limitations",
        "source_use_summary",
        "source_supported_points",
        "source_cautions",
        "source_followup_checks",
        "source_informed_assumptions",
        "citation_usage_note",
        "prior_context_used",
        "prior_context_summary",
        "prior_context",
        "prior_context_limitations",
        "output_type",
        "agent_id",
    ]

    assert all(field in page_text for field in expected_fields)
    assert "Raw JSON for unknown fields" in page_text
    assert "Raw JSON remains visible below." in page_text


def test_dashboard_route_preview_suggestions_can_select_agent_without_invocation(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "function renderRoutePreviewSuggestions(result)" in page_text
    assert "async function localResponseAgentSelectSuggestedAgent(agentId)" in page_text
    assert "routePreviewSuggestions.onchange = async () =>" in page_text
    assert (
        "Suggested agent selected for manual review. Route preview does not invoke agents. "
        "Select manually before running a local response."
    ) in page_text
    assert "Select manually before running a local response" in page_text
    route_select_index = page_text.index("async function localResponseAgentSelectSuggestedAgent(agentId)")
    run_index = page_text.index("runButton.onclick = async () =>")

    assert route_select_index < run_index


def test_dashboard_workbench_does_not_support_arbitrary_url_input_or_browser_storage(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text().lower()
    section = local_response_agents_section().lower()

    assert 'type="url"' not in section
    assert "arbitrary url" not in section
    assert "localstorage" not in page_text
    assert "sessionstorage" not in page_text
    assert "indexeddb" not in page_text
    assert "document.cookie" not in page_text
    assert "navigator.clipboard" not in page_text
    assert ".download" not in page_text
    assert "createobjecturl" not in page_text


def test_dashboard_workbench_does_not_add_forbidden_external_or_mutation_controls(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    section = local_response_agents_section().lower()
    forbidden = [
        "oauth",
        "cloud sync",
        "email sending",
        "public posting",
        "save",
        "copy to clipboard",
        "schedule",
        "reminder",
        "shell",
        "git ",
    ]

    assert all(term not in section for term in forbidden)
    assert "no forms, posts, purchases, or bookings" in section
    assert "no downloads or scripts" in section
    assert "no file export" in section
    assert "download file" not in section
    assert section.count("<button") == 17


def test_dashboard_summary_still_exposes_local_response_agents_index(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    index = app_module.dashboard_summary()["localResponseAgentsIndex"]

    assert index["agentCount"] == 37
    assert [agent["endpoint"] for agent in index["agents"]] == EXPECTED_ENDPOINTS
    assert all(agent["exampleRequestBody"] for agent in index["agents"])
    assert all(agent["webResearchAvailable"] is True for agent in index["agents"])
    assert all(agent["webResearchRequiresUserEnabled"] is True for agent in index["agents"])
