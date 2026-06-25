import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return dashboard


def test_dashboard_summary_includes_file_data_agent(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    agent = summary["fileDataAgent"]

    assert summary["capabilities"]["fileDataAgent"] == "implemented_local_only"
    assert summary["safety"]["fileDataAgent"]["rawPathInputAccepted"] is False
    assert agent["agentId"] == "file_data_agent"
    assert agent["name"] == "File/Data Agent"
    assert agent["status"] == "implemented_local_only"
    assert agent["mode"] == "registered_project_metadata_only"
    assert agent["endpoint"] == "/agents/files/local-summary"
    assert agent["registeredProjectsOnly"] is True
    assert agent["rawPathInputAccepted"] is False
    assert agent["protectedPatternsActive"] is True
    assert agent["externalServices"] is False
    assert agent["paidApis"] is False
    assert agent["webBrowsing"] is False
    assert agent["connectorExecution"] is False
    assert agent["shellExecution"] is False
    assert agent["fileMutation"] is False
    assert agent["uploads"] is False
    assert agent["accountAccess"] is False


def test_dashboard_html_includes_read_only_file_data_agent_section(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")

    assert 'id="file-data-agent"' in page_text
    assert "File/Data Agent" in page_text
    assert "Registered-project metadata only." in page_text
    assert "POST /agents/files/local-summary" in page_text
    assert "/docs/file-data-agent.md" in page_text
    assert "renderFileDataAgent(summary.fileDataAgent)" in page_text


def test_dashboard_file_data_agent_section_has_no_unsafe_action_buttons(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    start = page_text.index('id="file-data-agent"')
    end = page_text.index('id="vm-validation-prep-center"')
    section = page_text[start:end]
    forbidden_labels = [
        "scan pc",
        "browse files",
        "read secrets",
        "upload",
        "connect account",
        "enable connector",
        "run command",
        "mutate",
        "delete",
    ]

    assert "<button" not in section
    assert all(f">{label}<" not in section for label in forbidden_labels)


def test_file_data_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/files/local-summary")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
