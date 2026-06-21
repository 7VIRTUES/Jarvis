import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db
from jarvis_core.vm_validation_prep import VmValidationPrepService


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    monkeypatch.setattr(app_module, "vm_validation_prep", VmValidationPrepService())
    return dashboard


def dashboard_page(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)
    return app_module.local_dashboard().body.decode("utf-8")


def vm_prep_section(page_text):
    start = page_text.index('id="vm-validation-prep-center"')
    end = page_text.index('id="backup-readiness-center"')
    return page_text[start:end]


def test_dashboard_vm_validation_prep_section_exists(tmp_path, monkeypatch):
    section = vm_prep_section(dashboard_page(tmp_path, monkeypatch))

    assert "Clean Windows VM Validation Prep" in section
    assert 'id="vm-validation-prep-status"' in section
    assert 'id="vm-validation-prep-counts"' in section
    assert 'id="vm-validation-prep-list"' in section
    assert "/vm-validation/prep" in section
    assert "/vm-validation/prep/runbook" in section


def test_refresh_vm_validation_prep_exists(tmp_path, monkeypatch):
    section = vm_prep_section(dashboard_page(tmp_path, monkeypatch))

    assert ">Refresh VM validation prep<" in section


def test_forbidden_labels_absent_from_new_section(tmp_path, monkeypatch):
    section = vm_prep_section(dashboard_page(tmp_path, monkeypatch)).lower()
    forbidden = [
        "start vm",
        "install",
        "build installer",
        "package",
        "release",
        "certify",
        "upload",
        "send",
        "share",
        "publish",
        "fix automatically",
        "run commands",
    ]

    assert all(f">{label}<" not in section for label in forbidden)
    assert ">refresh vm validation prep<" in section


def test_vm_validation_prep_client_loader_exists(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "async function loadVmValidationPrep()" in page_text
    assert "renderVmValidationPrep(prep)" in page_text
    assert "bindVmValidationPrepControls()" in page_text
    assert "fetch('/vm-validation/prep')" in page_text


def test_dashboard_section_has_no_mutation_fetch(tmp_path, monkeypatch):
    page_text = dashboard_page(tmp_path, monkeypatch)

    assert "fetch('/vm-validation/prep')" in page_text
    assert "fetch('/vm-validation/prep', { method: 'POST' })" not in page_text
    assert "fetch('/vm-validation/prep/runbook', { method: 'POST' })" not in page_text
