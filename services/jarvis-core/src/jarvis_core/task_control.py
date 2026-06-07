from __future__ import annotations

from typing import Any

from .tasks import TERMINAL_STATUSES, TaskQueue


ACTIVE_TASK_STATUSES = {"queued", "running", "waiting_for_approval"}


class TaskControlService:
    def __init__(self, tasks: TaskQueue):
        self.tasks = tasks

    def stop_status(self) -> dict[str, Any]:
        active = self.active_tasks()
        return {
            "requirement": "v0.1C stop-task control boundary",
            "safeBackendCancellationAvailable": True,
            "stopControlsEnabled": bool(active),
            "enabledWhen": "known Jarvis-owned task status is queued, running, or waiting_for_approval",
            "backendType": "jarvis_task_queue_state_only",
            "activeTaskCount": len(active),
            "activeStatuses": sorted(ACTIVE_TASK_STATUSES),
            "terminalStatuses": sorted(TERMINAL_STATUSES),
            "scope": "Jarvis-owned task records tracked in the local Jarvis task table",
            "osProcessControl": False,
            "arbitraryProcessKill": False,
            "pidAccepted": False,
            "processNameAccepted": False,
            "shellCommandAccepted": False,
            "windowsServiceControl": False,
            "auditEvent": "task.canceled",
            "notes": [
                "Stop controls apply only to Jarvis task records.",
                "The stop endpoint accepts a Jarvis task_id path parameter only.",
                "Jarvis does not expose PID, process-name, shell-command, or OS service stop controls.",
            ],
        }

    def active_tasks(self) -> list[dict[str, Any]]:
        return [self._safe_task(task) for task in self.tasks.list_tasks() if task["status"] in ACTIVE_TASK_STATUSES]

    def stop_task(self, task_id: str) -> dict[str, Any]:
        task = self.tasks.get_task(task_id)
        if not task:
            raise KeyError("task not found")
        if task["status"] not in ACTIVE_TASK_STATUSES:
            raise ValueError("only active Jarvis-owned tasks can be stopped")
        stopped = self.tasks.cancel_task(task_id)
        return {
            "stopAccepted": True,
            "taskId": task_id,
            "status": stopped["status"],
            "auditEvent": "task.canceled",
            "scope": "Jarvis-owned task record only",
            "osProcessControl": False,
            "arbitraryProcessKill": False,
            "pidAccepted": False,
            "processNameAccepted": False,
            "shellCommandAccepted": False,
            "task": self._safe_task(stopped),
        }

    def _safe_task(self, task: dict[str, Any]) -> dict[str, Any]:
        return {
            "taskId": task["task_id"],
            "projectName": task["project_name"],
            "agentId": task["agent_id"],
            "taskType": task["task_type"],
            "status": task["status"],
            "autonomyLevel": task["autonomy_level"],
            "dryRun": task["dry_run"],
            "writeCapable": task["write_capable"],
            "createdAt": task["created_at"],
            "startedAt": task["started_at"],
            "finishedAt": task["finished_at"],
            "summary": task["summary"],
            "error": task["error"],
        }
