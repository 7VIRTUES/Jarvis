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


def test_dashboard_summary_includes_local_drafting_agent(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    agent = summary["localDraftingAgent"]

    assert summary["capabilities"]["localDraftingAgent"] == "implemented_local_only"
    assert summary["safety"]["localDraftingAgent"]["emailSending"] is False
    assert agent["agentId"] == "local_drafting_agent"
    assert agent["name"] == "Local Drafting Agent"
    assert agent["status"] == "implemented_local_only"
    assert agent["mode"] == "response_only_user_provided_drafting"
    assert agent["endpoint"] == "/agents/drafting/local-draft"
    assert agent["formats"] == ["message", "email_draft", "document_section", "checklist", "announcement"]
    assert agent["responseOnly"] is True
    assert agent["draftPersistence"] is False
    assert agent["emailSending"] is False
    assert agent["publicPosting"] is False
    assert agent["gmailCalendarSocialAccess"] is False
    assert agent["taskPersistence"] is False
    assert agent["dbWrites"] is False
    assert agent["externalServices"] is False
    assert agent["paidApis"] is False
    assert agent["webBrowsing"] is False
    assert agent["connectorExecution"] is False
    assert agent["oauth"] is False
    assert agent["accountAccess"] is False
    assert agent["fileReads"] is False
    assert agent["fileWrites"] is False
    assert agent["shellExecution"] is False
    assert agent["uploads"] is False
    assert agent["mutation"] is False


def test_dashboard_html_includes_read_only_local_drafting_agent_section(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert 'id="local-drafting-agent"' in page_text
    assert "Local Drafting Agent" in page_text
    assert "Response-only drafting." in page_text
    assert "POST /agents/drafting/local-draft" in page_text
    assert "/docs/local-drafting-agent.md" in page_text
    assert "renderLocalDraftingAgent(summary.localDraftingAgent)" in page_text


def test_dashboard_local_drafting_agent_section_has_no_unsafe_action_buttons(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    start = page_text.index('id="local-drafting-agent"')
    end = page_text.index('id="vm-validation-prep-center"')
    section = page_text[start:end]
    forbidden_labels = [
        "send email",
        "save draft",
        "post publicly",
        "connect gmail",
        "write file",
        "run command",
        "upload",
        "enable connector",
    ]

    assert "<button" not in section
    assert all(f">{label}<" not in section for label in forbidden_labels)
