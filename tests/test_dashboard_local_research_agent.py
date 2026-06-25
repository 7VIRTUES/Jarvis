import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return dashboard


def test_dashboard_summary_includes_local_research_agent(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    agent = summary["localResearchAgent"]

    assert summary["capabilities"]["localResearchAgent"] == "implemented_local_only"
    assert agent["agentId"] == "local_research_agent"
    assert agent["name"] == "Local Research Agent"
    assert agent["status"] == "implemented_local_only"
    assert agent["mode"] == "user_provided_notes_only"
    assert agent["endpoint"] == "/agents/research/local-brief"
    assert agent["externalServices"] is False
    assert agent["paidApis"] is False
    assert agent["webBrowsing"] is False
    assert agent["connectorExecution"] is False
    assert agent["fileMutation"] is False
    assert agent["citationVerification"] is False
    assert agent["outputTypes"] == ["brief", "outline", "comparison", "reading_plan"]
    assert agent["limitations"] == ["based only on user-provided input"]


def test_dashboard_html_includes_read_only_local_research_agent_section(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert 'id="local-research-agent"' in page_text
    assert "Local Research Agent" in page_text
    assert "User-provided notes only." in page_text
    assert "/agents/research/local-brief" in page_text
    assert "/docs/local-research-agent.md" in page_text
    assert "renderLocalResearchAgent(summary.localResearchAgent)" in page_text


def test_dashboard_local_research_agent_section_has_no_unsafe_action_buttons(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    start = page_text.index('id="local-research-agent"')
    end = page_text.index('id="vm-validation-prep-center"')
    section = page_text[start:end]
    forbidden_button_labels = [
        "browse",
        "fetch sources",
        "connect account",
        "verify citations",
        "enable connector",
        "send",
        "post",
        "write file",
    ]

    assert "<button" not in section
    assert all(f">{label}<" not in section for label in forbidden_button_labels)
