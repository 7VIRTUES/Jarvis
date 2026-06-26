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


def local_response_agents_section() -> str:
    page_text = app_module.local_dashboard().body.decode("utf-8")
    start = page_text.index('id="local-response-agents-index"')
    end = page_text.index('id="vm-validation-prep-center"')
    return page_text[start:end]


def test_dashboard_html_includes_read_only_example_request_body_area(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    section = local_response_agents_section()

    assert "Read-only example request bodies" in section
    assert "local-response-agent-example" in section
    assert "local-response-agents-example-note" in section
    assert "Example request bodies are read-only JSON display only." in section


def test_dashboard_html_renders_example_request_body_logic_from_summary(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert "agent.exampleRequestBody" in page_text
    assert "JSON.stringify(agent.exampleRequestBody || {}, null, 2)" in page_text
    assert "escapeHtml(JSON.stringify(agent.exampleRequestBody || {}, null, 2))" in page_text
    assert "agent.endpoint" in page_text
    assert "agent.docsLink" in page_text
    assert "agent.safetyNotes" in page_text


def test_dashboard_summary_still_exposes_examples_for_all_index_agents(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    index = app_module.dashboard_summary()["localResponseAgentsIndex"]
    endpoints = [agent["endpoint"] for agent in index["agents"]]

    assert index["agentCount"] == 11
    assert endpoints == EXPECTED_ENDPOINTS
    assert all(agent["exampleRequestBody"] for agent in index["agents"])
    assert all(isinstance(agent["exampleRequestBody"], dict) for agent in index["agents"])


def test_dashboard_examples_section_has_no_execution_or_mutation_controls(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    section = local_response_agents_section().lower()
    forbidden_control_text = [
        "send request",
        "execute",
        "run agent",
        "submit",
        "save",
        "export",
        "copy to clipboard",
    ]

    assert "<button" not in section
    assert "fetch(agent.endpoint" not in section
    assert all(text not in section for text in forbidden_control_text)
    assert ">post<" not in section
