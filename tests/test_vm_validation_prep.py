import json

from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.vm_validation_prep import VmValidationPrepService
import jarvis_core.app as app_module


def test_prep_endpoint_returns_checklist(monkeypatch):
    monkeypatch.setattr(app_module, "vm_validation_prep", VmValidationPrepService())

    result = app_module.get_vm_validation_prep()

    assert result["agentId"] == "vm_validation_prep_agent"
    assert result["checklistItemCount"] == 12
    assert {item["itemId"] for item in result["items"]} == {
        "clean-windows-vm-available",
        "git-installed-manually",
        "python-installed-manually",
        "repo-clone-step",
        "venv-setup-step",
        "pytest-validation-step",
        "codex-present-scenario",
        "codex-missing-scenario",
        "dashboard-loopback-access",
        "lan-denied-without-token",
        "future-connectors-disabled",
        "backup-restore-reminder",
    }


def test_runbook_endpoint_returns_manual_guidance(monkeypatch):
    monkeypatch.setattr(app_module, "vm_validation_prep", VmValidationPrepService())

    runbook = app_module.get_vm_validation_prep_runbook()

    assert runbook["title"] == "Clean Windows VM Validation Prep Runbook"
    assert len(runbook["steps"]) >= 6
    assert runbook["manualChecklistOnly"] is True
    assert runbook["commandExecution"] is False
    assert runbook["softwareSetupAutomation"] is False
    assert runbook["vmAutomation"] is False
    assert runbook["installerCreation"] is False


def test_checklist_has_no_automation_or_completion_claims():
    result = VmValidationPrepService().prep()
    text = json.dumps(result, sort_keys=True).lower()

    assert result["completionClaimed"] is False
    assert result["commandExecution"] is False
    assert result["softwareSetupAutomation"] is False
    assert result["vmAutomation"] is False
    assert result["vmStateDetection"] is False
    assert "validation is complete" not in text
    assert "automatically validated" not in text
    assert "start vm" not in text


def test_vm_validation_prep_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/vm-validation/prep",
        "/vm-validation/prep/runbook",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_no_command_install_vm_control_installer_or_release_behavior_in_source():
    source = (app_module.WORKSPACE_ROOT / "services/jarvis-core/src/jarvis_core/vm_validation_prep.py").read_text(
        encoding="utf-8"
    )
    forbidden_source = [
        "subprocess",
        "os.system",
        "powershell",
        "cmd.exe",
        "winget",
        "choco",
        "VBoxManage",
        "VirtualBox",
        "VMware",
        "Hyper-V",
        "pyinstaller",
        "makensis",
        "msbuild",
        "gh release",
    ]
    result = VmValidationPrepService().prep()

    assert all(token not in source for token in forbidden_source)
    assert result["commandExecution"] is False
    assert result["softwareSetupAutomation"] is False
    assert result["vmAutomation"] is False
    assert result["vmStateDetection"] is False
    assert result["installerCreation"] is False
    assert result["releaseArtifactCreation"] is False
    assert result["certification"] is False
