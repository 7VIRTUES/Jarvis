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


def test_dashboard_summary_includes_local_transformation_agent(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    agent = summary["localTransformationAgent"]

    assert summary["capabilities"]["localTransformationAgent"] == "implemented_local_only"
    assert summary["safety"]["localTransformationAgent"]["externalServices"] is False
    assert agent["agentId"] == "local_transformation_agent"
    assert agent["name"] == "Local Transformation Agent"
    assert agent["status"] == "implemented_local_only"
    assert agent["mode"] == "response_only_user_provided_transformation"
    assert agent["endpoint"] == "/agents/transformation/local-transform"
    assert agent["targetFormats"] == [
        "outline",
        "checklist",
        "table",
        "sop_steps",
        "flashcards",
        "json_style",
        "csv_style",
        "cleaned_notes",
    ]
    assert agent["detailLevels"] == ["short", "medium", "detailed"]
    assert agent["responseOnly"] is True
    assert agent["transformationPersistence"] is False
    assert agent["fileExportCreation"] is False
    assert agent["documentCreation"] is False
    assert agent["spreadsheetCreation"] is False
    assert agent["deckCreation"] is False
    assert agent["taskCreation"] is False
    assert agent["sourceValidation"] is False
    assert agent["citationValidation"] is False
    assert agent["externalFactChecking"] is False
    assert agent["documentRetrieval"] is False
    assert agent["testExecution"] is False
    assert agent["repoInspection"] is False
    assert agent["professionalValidation"] is False
    assert agent["complianceCertification"] is False
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


def test_dashboard_html_includes_read_only_local_transformation_agent_section(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert 'id="local-transformation-agent"' in page_text
    assert "Local Transformation Agent" in page_text
    assert "Response-only transformation." in page_text
    assert "POST /agents/transformation/local-transform" in page_text
    assert "/docs/local-transformation-agent.md" in page_text
    assert "renderLocalTransformationAgent(summary.localTransformationAgent)" in page_text


def test_dashboard_local_transformation_agent_section_has_no_unsafe_action_buttons(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    start = page_text.index('id="local-transformation-agent"')
    end = page_text.index('id="vm-validation-prep-center"')
    section = page_text[start:end]
    forbidden_labels = [
        "read file",
        "retrieve document",
        "verify source",
        "verify citation",
        "inspect repo",
        "run tests",
        "create task",
        "save transformation",
        "create document",
        "create spreadsheet",
        "create deck",
        "export file",
        "certify compliance",
        "write file",
        "download",
        "upload",
        "enable connector",
        "send",
        "post",
        "purchase",
    ]

    assert "<button" not in section
    assert all(f">{label}<" not in section for label in forbidden_labels)
