from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from . import APP_NAME, VERSION
from .permissions import is_protected_path


class DiagnosticExporter:
    def __init__(self, conn: sqlite3.Connection, workspace_root: Path, log_root: Path, connector_root: Path):
        self.conn = conn
        self.workspace_root = workspace_root
        self.log_root = log_root
        self.connector_root = connector_root

    def export(self) -> dict[str, Any]:
        return {
            "app": {"name": APP_NAME, "version": VERSION, "mode": "local"},
            "configSummary": {"workspaceRoot": str(self.workspace_root), "secretValuesExported": False},
            "projects": self._rows("select name, path, created_at from projects order by name", ["name", "path", "created_at"]),
            "tasks": self._rows("select task_id, project_name, status, dry_run, created_at from tasks order by created_at", ["task_id", "project_name", "status", "dry_run", "created_at"]),
            "events": self._rows("select event_id, task_id, event_type, created_at from events order by created_at limit 100", ["event_id", "task_id", "event_type", "created_at"]),
            "actions": self._rows("select receipt_id, task_id, action_type, blocked, approval_required, risk_level from action_receipts order by started_at limit 100", ["receipt_id", "task_id", "action_type", "blocked", "approval_required", "risk_level"]),
            "codexPlans": self._codex_plan_summaries(),
            "connectors": self._connector_status(),
            "recentSecurityEvents": self._recent_security_events(),
            "reports": self._reports_index(),
        }

    def _rows(self, query: str, names: list[str]) -> list[dict[str, Any]]:
        return [dict(zip(names, row)) for row in self.conn.execute(query).fetchall()]

    def _connector_status(self) -> list[dict[str, Any]]:
        connectors: list[dict[str, Any]] = []
        for path in sorted(self.connector_root.glob("placeholders/*.json")):
            if is_protected_path(path):
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            connectors.append(
                {
                    "id": data.get("id"),
                    "provider": data.get("provider"),
                    "implemented": data.get("implemented"),
                    "defaultEnabled": data.get("defaultEnabled"),
                    "readinessLevel": data.get("readinessLevel"),
                    "tokenStorage": data.get("tokenStorage"),
                }
            )
        return connectors

    def _codex_plan_summaries(self) -> list[dict[str, Any]]:
        return self._rows(
            "select plan_id, task_id, project_name, status, risk_level, created_at, approval_required, approval_id from codex_plans order by created_at",
            ["plan_id", "task_id", "project_name", "status", "risk_level", "created_at", "approval_required", "approval_id"],
        )

    def _recent_security_events(self) -> list[dict[str, Any]]:
        path = self.log_root / "security.jsonl"
        if not path.exists() or is_protected_path(path):
            return []
        lines = path.read_text(encoding="utf-8").splitlines()[-50:]
        return [json.loads(line) for line in lines if line.strip()]

    def _reports_index(self) -> list[str]:
        reports_root = self.workspace_root / "data" / "jarvis" / "reports"
        if not reports_root.exists():
            return []
        return [str(path.relative_to(self.workspace_root)) for path in reports_root.glob("*.md") if not is_protected_path(path)]
