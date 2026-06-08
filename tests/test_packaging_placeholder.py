from pathlib import Path

from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db


REPO_ROOT = Path(__file__).resolve().parents[1]


def dashboard_service(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    return DashboardService(conn, tmp_path, tmp_path / "data" / "jarvis", tmp_path / "connectors")


def test_packaging_summary_reports_documentation_only_status(tmp_path):
    status = dashboard_service(tmp_path).private_alpha_packaging_summary()

    assert status["privateAlphaPackagingStatus"] == "placeholder_only"
    assert status["documentationOnly"] is True
    assert status["installerBuildImplemented"] is False
    assert status["installerArtifactAvailable"] is False
    assert status["tauriProductionBuildImplemented"] is False
    assert status["codeSigningImplemented"] is False
    assert status["autoUpdaterEnabled"] is False
    assert status["telemetryEnabled"] is False
    assert status["publicReleaseReady"] is False
    assert status["cloudDistributionEnabled"] is False
    assert status["githubReleaseAutomationEnabled"] is False
    assert status["releaseWorkflowAdded"] is False
    assert status["packagingScriptsAdded"] is False
    assert status["dependencyChangesAdded"] is False


def test_packaging_summary_includes_vm_readiness_without_release_actions(tmp_path):
    status = dashboard_service(tmp_path).private_alpha_packaging_summary()

    assert status["vmValidationRequired"] is True
    assert status["vmValidationStatus"] == "not_run_in_this_slice"
    assert status["manualLocalRunCurrentPath"] is True
    assert status["freshWindowsVmRequiredBeforePrivateAlpha"] is True
    assert "fresh_windows_vm" in status["readinessChecklist"]
    assert "verify_lan_denied_without_token" in status["readinessChecklist"]
    assert "confirm_no_push_merge_delete_automation" in status["readinessChecklist"]


def test_packaging_docs_exist_and_state_no_installer_is_produced():
    packaging_doc = REPO_ROOT / "docs" / "private-alpha-packaging.md"
    vm_doc = REPO_ROOT / "docs" / "vm-private-alpha-checklist.md"
    desktop_doc = REPO_ROOT / "apps" / "desktop" / "PACKAGING_PLACEHOLDER.md"

    assert packaging_doc.exists()
    assert vm_doc.exists()
    assert desktop_doc.exists()
    text = "\n".join(
        [
            packaging_doc.read_text(encoding="utf-8"),
            vm_doc.read_text(encoding="utf-8"),
            desktop_doc.read_text(encoding="utf-8"),
        ]
    ).lower()

    assert "no installer artifact" in text
    assert "no auto-updater" in text
    assert "no telemetry" in text
    assert "fresh windows vm" in text
    assert "manual local run remains the current path" in text


def test_packaging_placeholder_does_not_add_executable_packaging_files():
    forbidden = [
        REPO_ROOT / "apps" / "desktop" / "package.json",
        REPO_ROOT / "apps" / "desktop" / "src-tauri" / "tauri.conf.json",
        REPO_ROOT / "apps" / "desktop" / "src-tauri" / "Cargo.toml",
        REPO_ROOT / ".github" / "workflows" / "release.yml",
    ]

    for path in forbidden:
        assert not path.exists()
