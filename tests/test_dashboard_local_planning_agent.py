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


def test_dashboard_summary_includes_local_planning_agent(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    agent = summary["localPlanningAgent"]

    assert summary["capabilities"]["localPlanningAgent"] == "implemented_local_only"
    assert summary["safety"]["localPlanningAgent"]["taskPersistence"] is False
    assert agent["agentId"] == "local_planning_agent"
    assert agent["name"] == "Local Planning Agent"
    assert agent["status"] == "implemented_local_only"
    assert agent["mode"] == "response_only_user_provided_planning"
    assert agent["endpoint"] == "/agents/planning/local-plan"
    assert agent["outputTypes"] == ["project_plan", "study_plan", "checklist", "weekly_plan"]
    assert agent["responseOnly"] is True
    assert agent["taskPersistence"] is False
    assert agent["reminders"] is False
    assert agent["calendarEmailIntegration"] is False
    assert agent["externalServices"] is False
    assert agent["paidApis"] is False
    assert agent["webBrowsing"] is False
    assert agent["connectorExecution"] is False
    assert agent["fileReads"] is False
    assert agent["fileWrites"] is False
    assert agent["shellExecution"] is False
    assert agent["uploads"] is False
    assert agent["mutation"] is False


def test_dashboard_html_includes_read_only_local_planning_agent_section(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert 'id="local-planning-agent"' in page_text
    assert "Local Planning Agent" in page_text
    assert "Response-only planning." in page_text
    assert "POST /agents/planning/local-plan" in page_text
    assert "/docs/local-planning-agent.md" in page_text
    assert "renderLocalPlanningAgent(summary.localPlanningAgent)" in page_text


def test_dashboard_local_planning_agent_section_has_no_unsafe_action_buttons(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    start = page_text.index('id="local-planning-agent"')
    end = page_text.index('id="vm-validation-prep-center"')
    section = page_text[start:end]
    forbidden_labels = [
        "create task",
        "schedule",
        "send email",
        "connect calendar",
        "write file",
        "run command",
        "upload",
        "enable connector",
    ]

    assert "<button" not in section
    assert all(f">{label}<" not in section for label in forbidden_labels)
