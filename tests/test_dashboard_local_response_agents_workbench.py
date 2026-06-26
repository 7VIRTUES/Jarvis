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

    assert "Local Response Agents Workbench" in section
    assert 'id="local-response-agents-workbench-select"' in section
    assert 'id="local-response-agents-workbench-endpoint"' in section
    assert 'id="local-response-agents-workbench-body"' in section
    assert 'id="local-response-agents-workbench-run-button"' in section
    assert "Run selected local response agent" in section
    assert 'id="local-response-agents-workbench-status"' in section
    assert 'id="local-response-agents-workbench-response"' in section


def test_dashboard_workbench_states_local_allowlisted_non_runner_boundaries(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    section = local_response_agents_section().lower()

    assert "local-only workbench" in section
    assert "allowlisted to the 11 local response-agent endpoints" in section
    assert "not an arbitrary request runner" in section
    assert "not a connector runner" in section
    assert "not persistent" in section
    assert "not certification or validation" in section
    assert "file/data agent requires a registered project" in section


def test_dashboard_workbench_js_builds_allowlist_from_summary_agents(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "function localResponseAgentAllowlist(agents)" in page_text
    assert "localResponseAgentEndpointParts(agent.endpoint)" in page_text
    assert "endpoint.method === 'POST'" in page_text
    assert "endpoint.path.startsWith('/agents/')" in page_text
    assert "new Set" in page_text
    assert "initializeLocalResponseAgentsWorkbench(summary.localResponseAgentsIndex)" in page_text


def test_dashboard_workbench_rejects_unsupported_endpoint_before_fetch(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()
    unsupported_index = page_text.index("Unsupported endpoint: selected catalog entry is not allowlisted.")
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
    assert invalid_json_index < fetch_index


def test_dashboard_workbench_posts_only_to_selected_catalog_endpoint_path(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text()

    assert "const response = await fetch(endpointPath" in page_text
    assert "method: 'POST'" in page_text
    assert "headers: { 'Content-Type': 'application/json' }" in page_text
    assert "body: JSON.stringify(parsedBody)" in page_text
    assert "endpointDisplay.textContent = endpointPath" in page_text
    assert "selectedEndpointPath(agent)" in page_text


def test_dashboard_workbench_does_not_support_arbitrary_url_input_or_browser_storage(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = dashboard_page_text().lower()
    section = local_response_agents_section().lower()

    assert 'type="url"' not in section
    assert "arbitrary url" not in section
    assert "http://" not in section
    assert "https://" not in section
    assert "localstorage" not in page_text
    assert "sessionstorage" not in page_text
    assert "document.cookie" not in page_text


def test_dashboard_workbench_does_not_add_forbidden_external_or_mutation_controls(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    section = local_response_agents_section().lower()
    forbidden = [
        "oauth",
        "cloud sync",
        "email sending",
        "public posting",
        "purchases",
        "save",
        "download",
        "export",
        "copy to clipboard",
        "schedule",
        "reminder",
        "shell",
        "git ",
    ]

    assert all(term not in section for term in forbidden)
    assert section.count("<button") == 1


def test_dashboard_summary_still_exposes_local_response_agents_index(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    index = app_module.dashboard_summary()["localResponseAgentsIndex"]

    assert index["agentCount"] == 11
    assert [agent["endpoint"] for agent in index["agents"]] == EXPECTED_ENDPOINTS
    assert all(agent["exampleRequestBody"] for agent in index["agents"])
