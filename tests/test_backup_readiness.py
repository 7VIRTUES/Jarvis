import json

from jarvis_core.backup_readiness import BackupReadinessService
import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access


def test_readiness_endpoint_returns_checklist(monkeypatch):
    monkeypatch.setattr(app_module, "backup_readiness", BackupReadinessService())

    result = app_module.get_backup_readiness()

    assert result["agentId"] == "backup_readiness_agent"
    assert result["checklistItemCount"] == 7
    assert {item["itemId"] for item in result["items"]} == {
        "repo-pushed-to-github",
        "clean-working-tree",
        "reports-directory-understood",
        "local-data-directory-understood",
        "protected-files-excluded",
        "manual-external-drive-step",
        "restore-test-reminder",
    }


def test_runbook_endpoint_returns_safe_manual_guidance(monkeypatch):
    monkeypatch.setattr(app_module, "backup_readiness", BackupReadinessService())

    runbook = app_module.get_backup_readiness_runbook()

    assert runbook["title"] == "Backup Readiness Checklist Runbook"
    assert len(runbook["steps"]) >= 5
    assert runbook["manualChecklistOnly"] is True
    assert runbook["backupAutomation"] is False
    assert runbook["fileCopy"] is False
    assert runbook["archiveWrites"] is False


def test_checklist_has_no_automation_claims():
    result = BackupReadinessService().readiness()
    text = json.dumps(result, sort_keys=True).lower()

    assert result["completionClaimed"] is False
    assert result["backupAutomation"] is False
    assert "completed automatically" not in text
    assert "created automatically" not in text
    assert "backup now" not in text


def test_protected_files_excluded_and_mentioned_as_excluded():
    result = BackupReadinessService().readiness()
    protected = next(item for item in result["items"] if item["itemId"] == "protected-files-excluded")

    assert protected["status"] == "ready"
    assert "excluded" in protected["summary"].lower()
    assert ".env" in protected["summary"]
    assert "private keys" in protected["summary"]


def test_backup_readiness_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/backup/readiness",
        "/backup/readiness/runbook",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_no_file_copy_delete_archive_drive_detection_or_command_behavior_in_source():
    source = (app_module.WORKSPACE_ROOT / "services/jarvis-core/src/jarvis_core/backup_readiness.py").read_text(
        encoding="utf-8"
    )
    forbidden_source = [
        "subprocess",
        "os.system",
        "shutil",
        "copyfile",
        "copytree",
        "unlink(",
        "remove(",
        "rmtree",
        "zipfile",
        "tarfile",
        "win32",
        "Get-Volume",
        "Get-PSDrive",
    ]
    result = BackupReadinessService().readiness()

    assert all(token not in source for token in forbidden_source)
    assert result["fileCopy"] is False
    assert result["fileDeletion"] is False
    assert result["archiveWrites"] is False
    assert result["externalDriveDetection"] is False
    assert result["secretReads"] is False
