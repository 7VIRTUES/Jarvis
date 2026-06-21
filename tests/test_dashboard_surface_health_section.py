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


def dashboard_page(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)
    return app_module.local_dashboard().body.decode("utf-8")


def surface_health_section(page_text):
    start = page_text.index('id="dashboard-surface-health-center"')
    end = page_text.index('id="project-profiles"')
    return page_text[start:end]


def test_dashboard_surface_health_section_exists(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)
    section = surface_health_section(page_text)

    assert "Dashboard Surface Health Center" in section
    assert 'id="dashboard-surface-health-status"' in section
    assert 'id="dashboard-surface-health-list"' in section
    assert "/dashboard/surface-health" in section


def test_refresh_surface_health_exists(tmp_path, monkeypatch):
    section = surface_health_section(dashboard_page(tmp_path, monkeypatch))

    assert ">Refresh surface health<" in section


def test_safety_notes_still_exist(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "Manual evidence only." in page_text
    assert "Local readiness summary only." in page_text
    assert "Local redacted diagnostics only." in page_text
    assert "Local report metadata only." in page_text
    assert "Known local manifest directories only." in page_text
    assert "Approved local Markdown docs only." in page_text
    assert "Local dashboard/API wiring check only." in page_text


def test_forbidden_labels_absent_from_new_health_center_area(tmp_path, monkeypatch):
    section = surface_health_section(dashboard_page(tmp_path, monkeypatch)).lower()
    forbidden = [
        "deploy",
        "install",
        "release",
        "certify",
        "upload",
        "send",
        "share",
        "publish",
        "fix automatically",
        "enable connector",
        "disable connector",
        "connect account",
    ]

    assert all(f">{label}<" not in section for label in forbidden)
    assert ">refresh surface health<" in section


def test_dashboard_surface_health_client_loader_exists(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "async function loadDashboardSurfaceHealth()" in page_text
    assert "renderDashboardSurfaceHealth(health)" in page_text
    assert "bindDashboardSurfaceHealthControls()" in page_text
    assert "fetch('/dashboard/surface-health')" in page_text


def test_no_new_backend_endpoint_required_by_dashboard_section(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "fetch('/dashboard/surface-health')" in page_text
    assert "fetch('/dashboard/surface-health', { method: 'POST' })" not in page_text
    assert "fetch('/dashboard/surface-health/report'" not in page_text
