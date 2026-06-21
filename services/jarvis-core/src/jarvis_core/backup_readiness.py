from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


AGENT_ID = "backup_readiness_agent"
AGENT_NAME = "Backup Readiness Checklist Center"
MODE = "local_manual_backup_readiness_checklist"


CHECKLIST_ITEMS: tuple[dict[str, str], ...] = (
    {
        "itemId": "repo-pushed-to-github",
        "title": "Repo pushed to GitHub",
        "status": "manual",
        "category": "repo",
        "summary": "Confirm from your normal Git workflow that intended local commits are available remotely before future VM or private-alpha work.",
    },
    {
        "itemId": "clean-working-tree",
        "title": "Clean working tree reviewed",
        "status": "manual",
        "category": "repo",
        "summary": "Confirm the working tree is intentionally clean or that remaining local changes are understood before creating manual backups.",
    },
    {
        "itemId": "reports-directory-understood",
        "title": "Reports directory understood",
        "status": "ready",
        "category": "reports",
        "summary": "Jarvis reports live under the local Jarvis data reports directory and should be reviewed as metadata/report artifacts only.",
    },
    {
        "itemId": "local-data-directory-understood",
        "title": "Local data directory understood",
        "status": "manual",
        "category": "local-data",
        "summary": "Review which local Jarvis data is useful for continuity without opening protected contents or secrets.",
    },
    {
        "itemId": "protected-files-excluded",
        "title": "Protected files excluded",
        "status": "ready",
        "category": "safety",
        "summary": "Protected files such as .env variants, private keys, credential material, logs, databases, and local secret stores are excluded from this checklist surface.",
    },
    {
        "itemId": "manual-external-drive-step",
        "title": "Manual external-drive backup step",
        "status": "manual",
        "category": "manual-offline",
        "summary": "Use your own trusted offline process if you choose to preserve allowed repo/docs/report artifacts. Jarvis does not detect media or create archives.",
    },
    {
        "itemId": "restore-test-reminder",
        "title": "Restore-test reminder",
        "status": "warning",
        "category": "restore",
        "summary": "Plan a manual restore test in a safe location before relying on any backup for future VM or private-alpha work.",
    },
)


RUNBOOK_STEPS: tuple[dict[str, str], ...] = (
    {
        "stepId": "review-scope",
        "title": "Review backup scope manually",
        "summary": "Identify the repo, docs, safe reports, and local metadata you intend to preserve without opening protected secret files.",
    },
    {
        "stepId": "confirm-remote",
        "title": "Confirm remote repo state",
        "summary": "Use your normal GitHub review workflow outside this center to confirm intended code history is remote.",
    },
    {
        "stepId": "exclude-protected",
        "title": "Keep protected files excluded",
        "summary": "Do not include .env files, private keys, service credentials, databases, logs, or local secret stores in portable backup material.",
    },
    {
        "stepId": "manual-offline-preservation",
        "title": "Perform any offline preservation manually",
        "summary": "If needed, use your own trusted local process for allowed artifacts. This center does not transfer files, inspect media, or create archives.",
    },
    {
        "stepId": "restore-test",
        "title": "Plan a restore test",
        "summary": "Verify a future restore in a safe location before depending on backup material for VM/private-alpha work.",
    },
)


class BackupReadinessService:
    def readiness(self) -> dict[str, Any]:
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
            "runbookEndpoint": "/backup/readiness/runbook",
            "localOnly": True,
            "manualChecklistOnly": True,
            "backupAutomation": False,
            "fileCopy": False,
            "fileDeletion": False,
            "wholePcScan": False,
            "secretReads": False,
            "externalDriveDetection": False,
            "archiveWrites": False,
            "completionClaimed": False,
            "uploads": False,
            "externalServices": False,
            "certification": False,
        }

    def runbook(self) -> dict[str, Any]:
        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "agentId": AGENT_ID,
            "title": "Backup Readiness Checklist Runbook",
            "mode": MODE,
            "summary": "Manual guidance for reviewing backup readiness before future VM/private-alpha work.",
            "steps": [dict(step) for step in RUNBOOK_STEPS],
            "safetyNotes": [
                "This is checklist guidance only.",
                "Jarvis does not create backup material, transfer files, inspect removable media, or claim completion.",
                "Protected secret files, local databases, logs, and credential material remain excluded from this surface.",
            ],
            "localOnly": True,
            "manualChecklistOnly": True,
            "backupAutomation": False,
            "fileCopy": False,
            "fileDeletion": False,
            "wholePcScan": False,
            "secretReads": False,
            "externalDriveDetection": False,
            "archiveWrites": False,
            "completionClaimed": False,
            "uploads": False,
            "externalServices": False,
            "certification": False,
        }

    def dashboard_summary(self) -> dict[str, Any]:
        readiness = self.readiness()
        return {
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "mode": MODE,
            "checklistItemCount": readiness["checklistItemCount"],
            "countsByStatus": readiness["countsByStatus"],
            "recentItems": readiness["items"],
            "localOnly": True,
            "manualChecklistOnly": True,
            "backupAutomation": False,
            "fileCopy": False,
            "fileDeletion": False,
            "secretReads": False,
            "externalDriveDetection": False,
            "archiveWrites": False,
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
