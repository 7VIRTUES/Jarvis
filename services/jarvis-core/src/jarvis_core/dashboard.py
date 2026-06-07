from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from . import APP_NAME, VERSION
from .config import load_json_config
from .lan_security import LAN_TOKEN_ENV_VAR, lan_protection_status, lan_setup_status
from .permissions import is_protected_path
from .registries import validate_connector_manifest
from .task_control import ACTIVE_TASK_STATUSES
from .tasks import TERMINAL_STATUSES


class DashboardService:
    def __init__(self, conn: sqlite3.Connection, workspace_root: Path, data_root: Path, connector_root: Path):
        self.conn = conn
        self.workspace_root = workspace_root
        self.data_root = data_root
        self.connector_root = connector_root
        self.reports_root = data_root / "reports"

    def summary(self) -> dict[str, Any]:
        reports = self.list_reports()
        connectors = self.connector_summary()
        settings = self.settings_summary()
        stop_task = self.stop_task_summary()
        desktop_shell = self.desktop_shell_summary()
        return {
            "app": {"name": APP_NAME, "version": VERSION, "mode": "local"},
            "phase": {"current": "v0.1C Slice 6", "status": "Tauri desktop shell placeholder/readiness foundation"},
            "capabilities": {
                "dashboard": "read_only",
                "reports": "read_only",
                "settings": "read_only_status",
                "projects": "read_only_summary",
                "stopTask": "jarvis_task_queue_state_only",
                "desktopShell": "placeholder_only",
                "connectors": "placeholder_summary_only",
                "unsupportedControlsExposed": False,
            },
            "counts": {
                "projects": self._count("projects"),
                "tasks": self._count("tasks"),
                "approvals": self._count("approvals"),
                "codexPlans": self._count("codex_plans"),
                "codexExecutions": self._count("codex_executions"),
                "reports": len(reports),
                "connectors": len(connectors),
            },
            "projects": self._rows("select name, path, created_at from projects order by name", ["name", "path", "created_at"]),
            "recentTasks": self._rows("select task_id, project_name, task_type, status, created_at from tasks order by created_at desc limit 10", ["taskId", "projectName", "taskType", "status", "createdAt"]),
            "reports": reports,
            "safety": self.safety_summary(),
            "settings": settings,
            "stopTask": stop_task,
            "desktopShell": desktop_shell,
            "activeTasks": self.active_tasks(),
            "lanProtection": lan_protection_status(),
            "lanSetup": lan_setup_status(),
            "connectors": connectors,
            "unsupportedActions": unsupported_actions(),
        }

    def settings_summary(self) -> dict[str, Any]:
        return {
            "appName": APP_NAME,
            "productName": "Jarvis PC Local",
            "version": VERSION,
            "phase": "v0.1C",
            "currentSlice": "Tauri desktop shell placeholder/readiness foundation",
            "localFirst": True,
            "settingsEditable": False,
            "settingsPersistence": "not_implemented_in_this_slice",
            "autonomyMode": "supervised_local_only",
            "safetyMode": "strict_local_read_only_dashboard",
            "paidAiApisEnabled": False,
            "browserAutomationEnabled": False,
            "externalConnectorsEnabled": False,
            "nonCodingConnectorsImplemented": False,
            "mainOnlyPreMvpWorkflow": True,
            "remoteWriteAutomationAllowed": False,
            "destructiveAutomationAllowed": False,
            "lanPairingStatus": "not_implemented_yet",
            "tokenProtectionStatus": "implemented_for_dashboard_api",
            "lanProtection": lan_protection_status(),
            "lanSetup": lan_setup_status(),
            "lanTokenEnvVar": LAN_TOKEN_ENV_VAR,
            "stopTaskStatus": "implemented_for_jarvis_task_queue_state_only",
            "stopTask": self.stop_task_summary(),
            "desktopShellStatus": "placeholder_only",
            "desktopShell": self.desktop_shell_summary(),
            "tauriShellStatus": "placeholder_only",
            "tauriShellImplemented": False,
            "tauriDependenciesInstalled": False,
            "firstRunWizardStatus": "not_implemented_yet",
            "installerStatus": "not_implemented_yet",
            "privateAlphaPackagingStatus": "not_implemented_yet",
            "installerPackagingStatus": "not_implemented_yet",
            "autoUpdaterEnabled": False,
            "telemetryEnabled": False,
            "notes": [
                "Settings are visible as read-only status only.",
                "LAN setup guidance is available from loopback only.",
                "Loopback dashboard access is allowed without a token.",
                "LAN dashboard access requires a configured header or bearer token.",
                "Stop-task controls apply only to Jarvis-owned task records and do not kill OS processes.",
                "Desktop shell is placeholder/readiness only and does not install or launch Tauri.",
                "First-run wizard and installer packaging remain future v0.1C slices.",
            ],
        }

    def safety_summary(self) -> dict[str, Any]:
        return {
            "mode": "local_read_only_dashboard",
            "genericShellExecution": False,
            "paidApis": False,
            "browserAutomation": False,
            "connectorExecution": False,
            "destructiveGitAutomation": False,
            "arbitraryProcessKill": False,
            "desktopShell": self.desktop_shell_summary(),
            "unsupportedControlsExposed": False,
            "lanProtection": lan_protection_status(),
            "reportPathValidation": "contained_md_files_only",
            "stopTask": self.stop_task_summary(),
            "notes": [
                "Dashboard endpoints are read-only.",
                "Non-loopback dashboard requests require a configured token.",
                "Report detail reads only approved Markdown reports under data/jarvis/reports.",
                "Stop-task controls accept only Jarvis task IDs and do not accept PID, process-name, command, or OS service identifiers.",
                "Desktop shell readiness is documentation and status only; no Tauri launch, install, update, telemetry, or packaging controls are exposed.",
                "Future v0.1C controls remain absent or unavailable unless implemented by their own slice.",
            ],
        }

    def desktop_shell_summary(self) -> dict[str, Any]:
        desktop_root = self.workspace_root / "apps" / "desktop"
        return {
            "requirement": "v0.1C Tauri desktop shell placeholder/readiness foundation",
            "desktopShellStatus": "placeholder_only",
            "placeholderDirectory": "apps/desktop",
            "placeholderDirectoryExists": desktop_root.exists(),
            "tauriShellImplemented": False,
            "productionDesktopAppImplemented": False,
            "tauriDependenciesInstalled": False,
            "packageManagerDependenciesAdded": False,
            "desktopLaunchControlAvailable": False,
            "desktopInstallControlAvailable": False,
            "autoUpdaterEnabled": False,
            "telemetryEnabled": False,
            "installerPackagingStatus": "not_implemented_yet",
            "privateAlphaPackagingStatus": "not_implemented_yet",
            "firstRunWizardStatus": "not_implemented_yet",
            "lanTokenProtectionMustBeRespected": True,
            "safeActionRuntimeMustBeRespected": True,
            "osLevelPermissionsAdded": False,
            "hostPcControlAdded": False,
            "notes": [
                "apps/desktop contains documentation-only readiness notes.",
                "A future shell may wrap the local dashboard but must not bypass LAN/token protection.",
                "No auto-updater, telemetry, installer packaging, or Tauri dependency installation is included in this slice.",
            ],
        }

    def stop_task_summary(self) -> dict[str, Any]:
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
        }

    def active_tasks(self) -> list[dict[str, Any]]:
        rows = self._rows(
            """
            select task_id, project_name, agent_id, task_type, status, autonomy_level,
                   dry_run, write_capable, created_at, started_at, finished_at, summary, error
            from tasks
            where status in ('queued', 'running', 'waiting_for_approval')
            order by created_at desc
            """,
            [
                "taskId",
                "projectName",
                "agentId",
                "taskType",
                "status",
                "autonomyLevel",
                "dryRun",
                "writeCapable",
                "createdAt",
                "startedAt",
                "finishedAt",
                "summary",
                "error",
            ],
        )
        for row in rows:
            row["dryRun"] = bool(row["dryRun"])
            row["writeCapable"] = bool(row["writeCapable"])
        return rows

    def connector_summary(self) -> list[dict[str, Any]]:
        connectors: list[dict[str, Any]] = []
        for path in sorted((self.connector_root / "placeholders").glob("*.json")):
            if is_protected_path(path):
                continue
            data = load_json_config(path)
            validate_connector_manifest(data)
            connectors.append(
                {
                    "id": data.get("id"),
                    "provider": data.get("provider"),
                    "implemented": False,
                    "defaultEnabled": False,
                    "readinessLevel": data.get("readinessLevel"),
                    "availableInDashboard": False,
                    "status": "placeholder_only",
                }
            )
        return connectors

    def list_reports(self) -> list[dict[str, Any]]:
        if not self.reports_root.exists():
            return []
        root = self.reports_root.resolve()
        reports: list[dict[str, Any]] = []
        for path in sorted(root.glob("*.md")):
            if not path.is_file() or is_protected_path(path):
                continue
            resolved = path.resolve()
            if not resolved.is_relative_to(root):
                continue
            stat = resolved.stat()
            reports.append({"id": resolved.name, "title": resolved.stem, "sizeBytes": stat.st_size})
        return reports

    def read_report(self, report_id: str) -> dict[str, Any]:
        path = self._validated_report_path(report_id)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("report not found")
        return {
            "id": path.name,
            "title": path.stem,
            "contentType": "text/markdown",
            "content": path.read_text(encoding="utf-8"),
        }

    def _validated_report_path(self, report_id: str) -> Path:
        decoded = unquote(report_id).strip()
        candidate_id = decoded.replace("\\", "/")
        relative = Path(candidate_id)
        if (
            not decoded
            or decoded != report_id
            or relative.is_absolute()
            or len(relative.parts) != 1
            or ".." in relative.parts
            or relative.suffix.lower() != ".md"
        ):
            raise PermissionError("report id must be a single Markdown file name")
        root = self.reports_root.resolve()
        candidate = (root / relative.name).resolve()
        if not candidate.is_relative_to(root) or is_protected_path(candidate):
            raise PermissionError("report path is outside the approved reports directory")
        return candidate

    def _count(self, table: str) -> int:
        return int(self.conn.execute(f"select count(*) from {table}").fetchone()[0])

    def _rows(self, query: str, names: list[str]) -> list[dict[str, Any]]:
        return [dict(zip(names, row)) for row in self.conn.execute(query).fetchall()]


def unsupported_actions() -> list[dict[str, Any]]:
    return [
        {"id": "git_push", "label": "Push", "available": False, "reason": "manual user action only"},
        {"id": "git_merge", "label": "Merge", "available": False, "reason": "not exposed in dashboard"},
        {"id": "delete_files", "label": "Delete files", "available": False, "reason": "destructive automation is blocked"},
        {"id": "install_dependencies", "label": "Install dependencies", "available": False, "reason": "not part of v0.1C Slice 2"},
        {"id": "enable_connectors", "label": "Enable connectors", "available": False, "reason": "future connectors remain placeholders"},
        {"id": "send_email", "label": "Send email", "available": False, "reason": "external account actions are excluded"},
        {"id": "public_posting", "label": "Public posting", "available": False, "reason": "external posting is excluded"},
        {"id": "purchases", "label": "Purchases", "available": False, "reason": "payment actions are excluded"},
    ]


def dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jarvis Dashboard</title>
  <style>
    body { margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f6f7f9; color: #1d2733; }
    header { background: #ffffff; border-bottom: 1px solid #d8dde5; padding: 18px 28px; }
    main { max-width: 1120px; margin: 0 auto; padding: 24px; display: grid; gap: 18px; }
    section { background: #ffffff; border: 1px solid #d8dde5; border-radius: 8px; padding: 18px; }
    h1, h2 { margin: 0 0 10px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
    .metric { border: 1px solid #e2e6ed; border-radius: 6px; padding: 12px; }
    .metric strong { display: block; font-size: 24px; }
    code, pre { background: #eef1f5; border-radius: 4px; padding: 2px 4px; }
    a { color: #0b5cad; }
    .muted { color: #5e6b7a; }
  </style>
</head>
<body>
  <header>
    <h1>Jarvis PC Local</h1>
    <div class="muted">Read-only dashboard, report, and settings/status visibility</div>
  </header>
  <main>
    <section>
      <h2>Status</h2>
      <div id="metrics" class="grid"></div>
    </section>
    <section id="settings-status">
      <h2>Settings / Status</h2>
      <pre id="settings">Loading settings/status summary...</pre>
    </section>
    <section id="lan-protection">
      <h2>LAN Protection</h2>
      <pre id="lan">Loading LAN protection status...</pre>
      <p><a href="/setup/lan">Open loopback LAN setup guidance</a></p>
    </section>
    <section id="stop-task-control">
      <h2>Active Task / Stop Task</h2>
      <div id="active-tasks" class="muted">Loading active task status...</div>
      <button id="stop-task-button" type="button" disabled>Stop Task</button>
      <pre id="stop-task-status">Loading stop-task status...</pre>
    </section>
    <section id="desktop-shell-status">
      <h2>Desktop Shell / Tauri</h2>
      <pre id="desktop-shell">Loading desktop shell placeholder status...</pre>
    </section>
    <section>
      <h2>Reports</h2>
      <div id="reports" class="muted">Loading reports...</div>
    </section>
    <section>
      <h2>Safety</h2>
      <pre id="safety">Loading safety summary...</pre>
    </section>
    <section>
      <h2>Connectors</h2>
      <div id="connectors" class="muted">Loading connector placeholders...</div>
    </section>
  </main>
  <script>
    async function loadDashboard() {
      const summary = await fetch('/api/dashboard/summary').then((response) => response.json());
      const counts = summary.counts;
      document.getElementById('metrics').innerHTML = Object.entries(counts)
        .map(([key, value]) => `<div class="metric"><span>${key}</span><strong>${value}</strong></div>`)
        .join('');
      document.getElementById('reports').innerHTML = summary.reports.length
        ? summary.reports.map((report) => `<div><a href="/api/reports/${encodeURIComponent(report.id)}">${report.title}</a> <span class="muted">${report.sizeBytes} bytes</span></div>`).join('')
        : 'No reports found.';
      document.getElementById('settings').textContent = JSON.stringify(summary.settings, null, 2);
      document.getElementById('stop-task-status').textContent = JSON.stringify(summary.stopTask, null, 2);
      document.getElementById('desktop-shell').textContent = JSON.stringify(summary.desktopShell, null, 2);
      const activeTasks = summary.activeTasks || [];
      const stopButton = document.getElementById('stop-task-button');
      if (activeTasks.length) {
        const task = activeTasks[0];
        document.getElementById('active-tasks').innerHTML = `<div>${task.taskId} <span class="muted">${task.status}</span></div>`;
        stopButton.disabled = false;
        stopButton.onclick = async () => {
          stopButton.disabled = true;
          const result = await fetch(`/api/tasks/${encodeURIComponent(task.taskId)}/stop`, { method: 'POST' }).then((response) => response.json());
          document.getElementById('stop-task-status').textContent = JSON.stringify(result, null, 2);
          await loadDashboard();
        };
      } else {
        document.getElementById('active-tasks').textContent = 'No active Jarvis-owned task is available to stop.';
        stopButton.disabled = true;
        stopButton.onclick = null;
      }
      document.getElementById('lan').textContent = JSON.stringify(summary.lanProtection, null, 2);
      document.getElementById('safety').textContent = JSON.stringify(summary.safety, null, 2);
      document.getElementById('connectors').innerHTML = summary.connectors.length
        ? summary.connectors.map((connector) => `<div>${connector.provider}: ${connector.status}</div>`).join('')
        : 'No connector placeholders found.';
    }
    loadDashboard();
  </script>
</body>
</html>"""
