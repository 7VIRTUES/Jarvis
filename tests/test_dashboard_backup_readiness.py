import jarvis_core.app as app_module
from jarvis_core.backup_readiness import BackupReadinessService
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    monkeypatch.setattr(app_module, "backup_readiness", BackupReadinessService())
    return dashboard


def dashboard_page(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)
    return app_module.local_dashboard().body.decode("utf-8")


def backup_section(page_text):
    start = page_text.index('id="backup-readiness-center"')
    end = page_text.index('id="activity-timeline-center"')
    return page_text[start:end]


def test_dashboard_backup_readiness_section_exists(tmp_path, monkeypatch):
    section = backup_section(dashboard_page(tmp_path, monkeypatch))

    assert "Backup Readiness Checklist" in section
    assert 'id="backup-readiness-status"' in section
    assert 'id="backup-readiness-counts"' in section
    assert 'id="backup-readiness-list"' in section
    assert "/backup/readiness" in section
    assert "/backup/readiness/runbook" in section


def test_refresh_backup_checklist_exists(tmp_path, monkeypatch):
    section = backup_section(dashboard_page(tmp_path, monkeypatch))

    assert ">Refresh backup checklist<" in section


def test_forbidden_labels_absent_from_new_section(tmp_path, monkeypatch):
    section = backup_section(dashboard_page(tmp_path, monkeypatch)).lower()
    forbidden = [
        "backup now",
        "copy files",
        "delete",
        "format",
        "upload",
        "send",
        "share",
        "publish",
        "certify",
        "fix automatically",
        "detect drives",
    ]

    assert all(f">{label}<" not in section for label in forbidden)
    assert ">refresh backup checklist<" in section


def test_backup_readiness_client_loader_exists(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "async function loadBackupReadiness()" in page_text
    assert "renderBackupReadiness(readiness)" in page_text
    assert "bindBackupReadinessControls()" in page_text
    assert "fetch('/backup/readiness')" in page_text


def test_dashboard_section_has_no_mutation_fetch(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "fetch('/backup/readiness')" in page_text
    assert "fetch('/backup/readiness', { method: 'POST' })" not in page_text
    assert "fetch('/backup/readiness/runbook', { method: 'POST' })" not in page_text
