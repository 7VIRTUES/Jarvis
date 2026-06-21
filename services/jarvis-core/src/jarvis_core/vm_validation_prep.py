from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


AGENT_ID = "vm_validation_prep_agent"
AGENT_NAME = "Clean Windows VM Validation Prep Center"
MODE = "local_manual_vm_validation_prep"


CHECKLIST_ITEMS: tuple[dict[str, str], ...] = (
    {
        "itemId": "clean-windows-vm-available",
        "title": "Clean Windows VM available",
        "status": "manual",
        "category": "environment",
        "summary": "Confirm a clean Windows VM is available through your normal local VM workflow. Jarvis does not detect or control VM state.",
    },
    {
        "itemId": "git-installed-manually",
        "title": "Manual Git prerequisite",
        "status": "manual",
        "category": "tools",
        "summary": "Confirm Git is available in the VM using your own manual setup process.",
    },
    {
        "itemId": "python-installed-manually",
        "title": "Manual Python prerequisite",
        "status": "manual",
        "category": "tools",
        "summary": "Confirm Python is available in the VM using your own manual setup process.",
    },
    {
        "itemId": "repo-clone-step",
        "title": "Repo clone step",
        "status": "manual",
        "category": "repo",
        "summary": "Clone the Jarvis repo manually in the clean VM and review the branch before validation.",
    },
    {
        "itemId": "venv-setup-step",
        "title": "Virtual environment setup step",
        "status": "manual",
        "category": "python",
        "summary": "Prepare the Python virtual environment manually according to the project docs.",
    },
    {
        "itemId": "pytest-validation-step",
        "title": "Pytest validation step",
        "status": "manual",
        "category": "validation",
        "summary": "Execute validation manually and record results through the existing validation evidence workflow.",
    },
    {
        "itemId": "codex-present-scenario",
        "title": "Codex available scenario",
        "status": "manual",
        "category": "codex",
        "summary": "If Codex is available in the VM, use the approved local workflow boundaries and do not enable external account automation.",
    },
    {
        "itemId": "codex-missing-scenario",
        "title": "Codex missing scenario",
        "status": "warning",
        "category": "codex",
        "summary": "If Codex is not available, record the blocker manually rather than attempting automated setup from Jarvis.",
    },
    {
        "itemId": "dashboard-loopback-access",
        "title": "Dashboard loopback access",
        "status": "manual",
        "category": "dashboard",
        "summary": "Confirm the dashboard is reachable from loopback only as expected in the VM.",
    },
    {
        "itemId": "lan-denied-without-token",
        "title": "LAN denied without token",
        "status": "manual",
        "category": "lan",
        "summary": "Confirm LAN dashboard access is denied without the configured token.",
    },
    {
        "itemId": "future-connectors-disabled",
        "title": "Future connectors still disabled",
        "status": "manual",
        "category": "connectors",
        "summary": "Confirm future connector placeholders remain disabled and not implemented.",
    },
    {
        "itemId": "backup-restore-reminder",
        "title": "Backup/restore reminder",
        "status": "warning",
        "category": "backup",
        "summary": "Review backup readiness and plan a restore check before relying on VM validation evidence.",
    },
)


RUNBOOK_STEPS: tuple[dict[str, str], ...] = (
    {
        "stepId": "prepare-clean-vm",
        "title": "Prepare clean Windows VM manually",
        "summary": "Use your normal local VM tooling. Jarvis does not start, stop, detect, or control VM software.",
    },
    {
        "stepId": "prepare-tools",
        "title": "Prepare required tools manually",
        "summary": "Confirm Git and Python availability without Jarvis performing tool setup.",
    },
    {
        "stepId": "clone-and-setup",
        "title": "Clone repo and prepare environment",
        "summary": "Clone the repo and prepare the virtual environment manually according to project docs.",
    },
    {
        "stepId": "manual-validation",
        "title": "Perform validation manually",
        "summary": "Run project validation yourself and record results in the existing local validation evidence workflow.",
    },
    {
        "stepId": "dashboard-boundaries",
        "title": "Check dashboard access boundaries",
        "summary": "Confirm loopback access works, LAN access without token is denied, and future connectors remain disabled.",
    },
    {
        "stepId": "backup-restore",
        "title": "Review backup and restore readiness",
        "summary": "Use the backup readiness checklist and keep restore testing manual.",
    },
)


class VmValidationPrepService:
    def prep(self) -> dict[str, Any]:
        items = [dict(item) for item in CHECKLIST_ITEMS]
        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "mode": MODE,
            "checklistItemCount": len(items),
            "countsByStatus": self._counts(items, "status"),
            "countsByCategory": self._counts(items, "category"),
            "items": items,
            "runbookEndpoint": "/vm-validation/prep/runbook",
            "localOnly": True,
            "manualChecklistOnly": True,
            "commandExecution": False,
            "softwareSetupAutomation": False,
            "vmAutomation": False,
            "vmStateDetection": False,
            "installerCreation": False,
            "releaseArtifactCreation": False,
            "completionClaimed": False,
            "uploads": False,
            "externalServices": False,
            "certification": False,
        }

    def runbook(self) -> dict[str, Any]:
        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "agentId": AGENT_ID,
            "title": "Clean Windows VM Validation Prep Runbook",
            "mode": MODE,
            "summary": "Manual guidance for preparing clean Windows VM validation without automation.",
            "steps": [dict(step) for step in RUNBOOK_STEPS],
            "safetyNotes": [
                "This is preparation guidance only.",
                "Jarvis does not run commands, prepare software, control VM software, create artifacts, or claim validation completion.",
                "Record validation evidence manually through the existing validation workflow.",
            ],
            "localOnly": True,
            "manualChecklistOnly": True,
            "commandExecution": False,
            "softwareSetupAutomation": False,
            "vmAutomation": False,
            "vmStateDetection": False,
            "installerCreation": False,
            "releaseArtifactCreation": False,
            "completionClaimed": False,
            "uploads": False,
            "externalServices": False,
            "certification": False,
        }

    def _counts(self, items: list[dict[str, str]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in items:
            value = item[key]
            counts[value] = counts.get(value, 0) + 1
        return dict(sorted(counts.items()))
