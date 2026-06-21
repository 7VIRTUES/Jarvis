import jarvis_core.app as app_module
from jarvis_core.activity_timeline import ActivityTimelineService
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    timeline = ActivityTimelineService(conn)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    monkeypatch.setattr(app_module, "activity_timeline", timeline)
    return dashboard, timeline


def dashboard_page(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)
    return app_module.local_dashboard().body.decode("utf-8")


def activity_section(page_text):
    start = page_text.index('id="activity-timeline-center"')
    end = page_text.index('id="dashboard-surface-health-center"')
    return page_text[start:end]


def test_dashboard_activity_timeline_section_exists(tmp_path, monkeypatch):
    section = activity_section(dashboard_page(tmp_path, monkeypatch))

    assert "Recent Activity / Audit Trail" in section
    assert 'id="activity-timeline-status"' in section
    assert 'id="activity-timeline-counts"' in section
    assert 'id="activity-timeline-list"' in section
    assert "/activity/timeline" in section


def test_refresh_activity_timeline_exists(tmp_path, monkeypatch):
    section = activity_section(dashboard_page(tmp_path, monkeypatch))

    assert ">Refresh activity timeline<" in section


def test_forbidden_labels_absent_from_new_section(tmp_path, monkeypatch):
    section = activity_section(dashboard_page(tmp_path, monkeypatch)).lower()
    forbidden = [
        "approve",
        "deny",
        "retry",
        "run",
        "stop process",
        "delete",
        "upload",
        "send",
        "share",
        "publish",
        "certify",
        "fix automatically",
    ]

    assert all(f">{label}<" not in section for label in forbidden)
    assert ">refresh activity timeline<" in section


def test_activity_timeline_client_loader_exists(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "async function loadActivityTimeline()" in page_text
    assert "renderActivityTimeline(timeline)" in page_text
    assert "bindActivityTimelineControls()" in page_text
    assert "fetch('/activity/timeline')" in page_text


def test_dashboard_section_has_no_mutation_fetch(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "fetch('/activity/timeline')" in page_text
    assert "fetch('/activity/timeline', { method: 'POST' })" not in page_text
    assert "fetch('/activity/timeline/report'" not in page_text
