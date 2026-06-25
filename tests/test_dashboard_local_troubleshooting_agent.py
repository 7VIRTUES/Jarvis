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


def test_dashboard_summary_includes_local_troubleshooting_agent(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    agent = summary["localTroubleshootingAgent"]

    assert summary["capabilities"]["localTroubleshootingAgent"] == "implemented_local_only"
    assert summary["safety"]["localTroubleshootingAgent"]["externalServices"] is False
    assert agent["agentId"] == "local_troubleshooting_agent"
    assert agent["name"] == "Local Troubleshooting Agent"
    assert agent["status"] == "implemented_local_only"
    assert agent["mode"] == "response_only_user_provided_troubleshooting"
    assert agent["endpoint"] == "/agents/troubleshooting/local-triage"
    assert agent["troubleshootingTypes"] == [
        "general",
        "pc_issue",
        "app_issue",
        "build_error",
        "workflow_issue",
        "network_issue",
    ]
    assert agent["urgencyLevels"] == ["low", "normal", "high"]
    assert agent["responseOnly"] is True
    assert agent["ticketPersistence"] is False
    assert agent["fixValidation"] is False
    assert agent["externalVerification"] is False
    assert agent["sourceValidation"] is False
    assert agent["testExecution"] is False
    assert agent["repoInspection"] is False
    assert agent["logReading"] is False
    assert agent["taskPersistence"] is False
    assert agent["dbWrites"] is False
    assert agent["externalServices"] is False
    assert agent["paidApis"] is False
    assert agent["webBrowsing"] is False
    assert agent["connectorExecution"] is False
    assert agent["oauth"] is False
    assert agent["accountAccess"] is False
    assert agent["gmailCalendarSocialAccess"] is False
    assert agent["postingOrSending"] is False
    assert agent["purchases"] is False
    assert agent["fileReads"] is False
    assert agent["fileWrites"] is False
    assert agent["shellExecution"] is False
    assert agent["downloads"] is False
    assert agent["uploads"] is False
    assert agent["mutation"] is False


def test_dashboard_html_includes_read_only_local_troubleshooting_agent_section(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert 'id="local-troubleshooting-agent"' in page_text
    assert "Local Troubleshooting Agent" in page_text
    assert "Response-only triage." in page_text
    assert "POST /agents/troubleshooting/local-triage" in page_text
    assert "/docs/local-troubleshooting-agent.md" in page_text
    assert "renderLocalTroubleshootingAgent(summary.localTroubleshootingAgent)" in page_text


def test_dashboard_local_troubleshooting_agent_section_has_no_unsafe_action_buttons(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    start = page_text.index('id="local-troubleshooting-agent"')
    end = page_text.index('id="vm-validation-prep-center"')
    section = page_text[start:end]
    forbidden_labels = [
        "run command",
        "read logs",
        "inspect repo",
        "run tests",
        "validate fix",
        "save ticket",
        "write file",
        "download",
        "upload",
        "enable connector",
        "delete",
        "wipe",
        "disable security",
        "send",
        "post",
        "purchase",
    ]

    assert "<button" not in section
    assert all(f">{label}<" not in section for label in forbidden_labels)
