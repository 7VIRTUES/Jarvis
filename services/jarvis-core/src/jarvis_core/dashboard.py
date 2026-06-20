from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from . import APP_NAME, VERSION
from .agent_manifest_health import AgentManifestHealthService
from .config import load_json_config
from .evidence_report_center import EvidenceReportCenterService
from .lan_security import LAN_TOKEN_ENV_VAR, lan_protection_status, lan_setup_status
from .permissions import is_protected_path
from .registries import validate_connector_manifest
from .readiness_snapshot_agent import PrivateAlphaReadinessSnapshotService
from .redacted_diagnostics_agent import RedactedDiagnosticsBundleService
from .task_control import ACTIVE_TASK_STATUSES
from .tasks import TERMINAL_STATUSES
from .validation_agent import ValidationAgentService


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
        first_run = self.first_run_wizard_summary()
        private_alpha = self.private_alpha_packaging_summary()
        validation = self.validation_summary()
        readiness = self.readiness_snapshot_summary()
        diagnostics_bundle = self.diagnostics_bundle_summary()
        evidence_reports = self.evidence_report_center_summary()
        manifest_health = self.agent_manifest_health_summary()
        return {
            "app": {"name": APP_NAME, "version": VERSION, "mode": "local"},
            "phase": {"current": "v0.1C Slice 8", "status": "private-alpha packaging documentation/readiness foundation"},
            "capabilities": {
                "dashboard": "read_only",
                "reports": "read_only",
                "settings": "read_only_status",
                "projects": "read_only_summary",
                "projectProfiles": "read_only_summary",
                "securityReviews": "registered_project_read_only",
                "stopTask": "jarvis_task_queue_state_only",
                "desktopShell": "placeholder_only",
                "firstRunWizard": "placeholder_only",
                "privateAlphaPackaging": "placeholder_only",
                "validationAgent": "local_evidence_tracking",
                "privateAlphaReadinessSnapshot": "local_readiness_snapshot",
                "redactedDiagnosticsBundle": "local_redacted_diagnostics",
                "evidenceReportCenter": "local_report_metadata_only",
                "agentManifestHealth": "local_manifest_metadata_only",
                "connectors": "placeholder_summary_only",
                "unsupportedControlsExposed": False,
            },
            "counts": {
                "projects": self._count("projects"),
                "tasks": self._count("tasks"),
                "approvals": self._count("approvals"),
                "codexPlans": self._count("codex_plans"),
                "codexExecutions": self._count("codex_executions"),
                "validationRuns": self._count("validation_runs"),
                "reports": len(reports),
                "connectors": len(connectors),
            },
            "projects": self._rows("select name, path, created_at from projects order by name", ["name", "path", "created_at"]),
            "recentTasks": self._rows("select task_id, project_name, task_type, status, created_at from tasks order by created_at desc limit 10", ["taskId", "projectName", "taskType", "status", "createdAt"]),
            "reports": reports,
            "profileSecuritySurfaces": {
                "projectProfilesEndpoint": "/api/projects/profiles",
                "securityReviewEndpointPattern": "/api/projects/{name}/security-review",
                "latestSecurityReviewEndpointPattern": "/api/projects/{name}/security-review/latest",
                "registeredProjectsOnly": True,
                "rawPathInputAccepted": False,
                "scriptExecution": False,
                "externalServices": False,
                "gitWrites": False,
                "protectedFileContentsRead": False,
            },
            "safety": self.safety_summary(),
            "settings": settings,
            "stopTask": stop_task,
            "desktopShell": desktop_shell,
            "firstRunWizard": first_run,
            "privateAlphaPackaging": private_alpha,
            "validationAgent": validation,
            "privateAlphaReadinessSnapshot": readiness,
            "redactedDiagnosticsBundle": diagnostics_bundle,
            "evidenceReportCenter": evidence_reports,
            "agentManifestHealth": manifest_health,
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
            "currentSlice": "private-alpha packaging documentation/readiness foundation",
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
            "firstRunWizardStatus": "placeholder_only",
            "firstRunWizard": self.first_run_wizard_summary(),
            "firstRunWizardImplemented": False,
            "setupStatePersistenceImplemented": False,
            "writesConfigFiles": False,
            "tokenGenerationImplemented": False,
            "tokenPersistenceImplemented": False,
            "accountSetupImplemented": False,
            "oauthImplemented": False,
            "cloudSyncEnabled": False,
            "installerStatus": "not_implemented_yet",
            "privateAlphaPackagingStatus": "placeholder_only",
            "privateAlphaPackaging": self.private_alpha_packaging_summary(),
            "installerPackagingStatus": "placeholder_only",
            "installerBuildImplemented": False,
            "installerArtifactAvailable": False,
            "codeSigningImplemented": False,
            "publicReleaseReady": False,
            "vmValidationRequired": True,
            "vmValidationStatus": "not_run_in_this_slice",
            "manualLocalRunCurrentPath": True,
            "githubReleaseAutomationEnabled": False,
            "autoUpdaterEnabled": False,
            "telemetryEnabled": False,
            "notes": [
                "Settings are visible as read-only status only.",
                "LAN setup guidance is available from loopback only.",
                "Loopback dashboard access is allowed without a token.",
                "LAN dashboard access requires a configured header or bearer token.",
                "Stop-task controls apply only to Jarvis-owned task records and do not kill OS processes.",
                "Desktop shell is placeholder/readiness only and does not install or launch Tauri.",
                "First-run wizard is placeholder/readiness only and does not persist setup state or write configuration.",
                "Private-alpha packaging is documentation/readiness only and does not build, sign, publish, or install artifacts.",
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
            "projectProfiles": "registered_project_metadata_only",
            "securityReviewDashboardAction": "registered_project_read_only",
            "desktopShell": self.desktop_shell_summary(),
            "firstRunWizard": self.first_run_wizard_summary(),
            "privateAlphaPackaging": self.private_alpha_packaging_summary(),
            "validationAgent": self.validation_summary(),
            "privateAlphaReadinessSnapshot": self.readiness_snapshot_summary(),
            "evidenceReportCenter": self.evidence_report_center_summary(),
            "agentManifestHealth": self.agent_manifest_health_summary(),
            "unsupportedControlsExposed": False,
            "lanProtection": lan_protection_status(),
            "reportPathValidation": "contained_md_json_reports_only",
            "stopTask": self.stop_task_summary(),
            "notes": [
                "Dashboard endpoints are read-only.",
                "Non-loopback dashboard requests require a configured token.",
                "Report detail reads only approved Markdown reports under data/jarvis/reports.",
                "Project profile and security review dashboard surfaces use registered projects only.",
                "Security review dashboard actions are read-only local reviews and do not execute scripts, install dependencies, or write Git state.",
                "Stop-task controls accept only Jarvis task IDs and do not accept PID, process-name, command, or OS service identifiers.",
                "Desktop shell readiness is documentation and status only; no Tauri launch, install, update, telemetry, or packaging controls are exposed.",
                "First-run readiness is informational only; no setup persistence, token generation, account setup, OAuth, cloud sync, telemetry, or updater is exposed.",
                "Private-alpha packaging readiness is documentation only; no installer build, signing, release automation, auto-updater, telemetry, or public release is exposed.",
                "Validation Agent records manual local evidence only; it does not execute commands, control VirtualBox, create installer artifacts, or write Git state.",
                "Private-Alpha Readiness Snapshot aggregates local metadata/evidence only; it does not create installer artifacts, certify readiness, run VM automation, or push to GitHub.",
                "Redacted Diagnostics Bundle reports aggregate safe local metadata only; they do not upload, run commands, read protected secrets, or certify production/security readiness.",
                "Evidence Report Center indexes bounded local report metadata only; it does not mutate reports, transfer reports off machine, or claim readiness.",
                "Agent Manifest Health Center reads known local manifest directories only; it does not mutate manifests, change connector state, execute tools, or contact external services.",
                "Future v0.1C controls remain absent or unavailable unless implemented by their own slice.",
            ],
        }

    def validation_summary(self) -> dict[str, Any]:
        return ValidationAgentService(self.conn, self.reports_root).dashboard_summary()

    def readiness_snapshot_summary(self) -> dict[str, Any]:
        return PrivateAlphaReadinessSnapshotService(
            self.conn,
            self.reports_root,
            self.workspace_root,
            self.connector_root,
        ).dashboard_summary()

    def diagnostics_bundle_summary(self) -> dict[str, Any]:
        return RedactedDiagnosticsBundleService(
            self.conn,
            self.reports_root,
            self.workspace_root,
            self.connector_root,
        ).dashboard_summary()

    def evidence_report_center_summary(self) -> dict[str, Any]:
        return EvidenceReportCenterService(self.reports_root).dashboard_summary()

    def agent_manifest_health_summary(self) -> dict[str, Any]:
        return AgentManifestHealthService(self.connector_root).dashboard_summary()

    def private_alpha_packaging_summary(self) -> dict[str, Any]:
        return {
            "requirement": "v0.1C private-alpha packaging documentation/readiness foundation",
            "privateAlphaPackagingStatus": "placeholder_only",
            "documentationOnly": True,
            "installerBuildImplemented": False,
            "installerArtifactAvailable": False,
            "installerPackagingStatus": "placeholder_only",
            "tauriProductionBuildImplemented": False,
            "codeSigningImplemented": False,
            "autoUpdaterEnabled": False,
            "telemetryEnabled": False,
            "publicReleaseReady": False,
            "cloudDistributionEnabled": False,
            "githubReleaseAutomationEnabled": False,
            "releaseWorkflowAdded": False,
            "packagingScriptsAdded": False,
            "dependencyChangesAdded": False,
            "vmValidationRequired": True,
            "vmValidationStatus": "not_run_in_this_slice",
            "manualLocalRunCurrentPath": True,
            "freshWindowsVmRequiredBeforePrivateAlpha": True,
            "lanTokenRequiredForLanTesting": True,
            "setupPagesRemainLoopbackOnly": True,
            "stopTaskBoundary": "jarvis_task_record_only",
            "desktopShellStatus": "placeholder_only",
            "firstRunWizardStatus": "placeholder_only",
            "futureConnectorsRemainDisabled": True,
            "paidAiApisEnabled": False,
            "browserAutomationEnabled": False,
            "readinessChecklist": [
                "fresh_windows_vm",
                "clone_repo",
                "create_python_venv",
                "install_documented_python_dependencies",
                "run_tests",
                "start_jarvis_core",
                "verify_loopback_dashboard",
                "configure_lan_dashboard_token_for_lan_test",
                "verify_lan_denied_without_token",
                "verify_lan_allowed_with_token",
                "verify_setup_pages_loopback_only",
                "verify_reports_view",
                "verify_settings_status_view",
                "verify_stop_task_boundary",
                "verify_diagnostic_export",
                "confirm_future_connectors_disabled",
                "confirm_no_paid_ai_apis",
                "confirm_no_browser_automation",
                "confirm_no_push_merge_delete_automation",
            ],
            "notes": [
                "No installer artifact is produced in this slice.",
                "No build signing, auto-updater, telemetry, public release, cloud distribution, or release automation is implemented.",
                "Fresh Windows VM validation is required before any future private-alpha build.",
            ],
        }

    def first_run_wizard_summary(self) -> dict[str, Any]:
        return {
            "requirement": "v0.1C first-run wizard placeholder/readiness foundation",
            "firstRunWizardStatus": "placeholder_only",
            "firstRunWizardImplemented": False,
            "setupPageImplemented": True,
            "setupPageLoopbackOnly": True,
            "setupStatePersistenceImplemented": False,
            "writesConfigFiles": False,
            "editableSettingsImplemented": False,
            "tokenGenerationImplemented": False,
            "tokenPersistenceImplemented": False,
            "tokenInputFormImplemented": False,
            "accountSetupImplemented": False,
            "oauthImplemented": False,
            "cloudSyncEnabled": False,
            "telemetryEnabled": False,
            "autoUpdaterEnabled": False,
            "installerPackagingStatus": "not_implemented_yet",
            "desktopShellStatus": "placeholder_only",
            "lanSetupGuidanceAvailable": True,
            "stopTaskBoundaryAvailable": True,
            "lanTokenProtectionMustBeRespected": True,
            "safeActionRuntimeMustBeRespected": True,
            "futureChecklist": [
                "confirm_local_service",
                "review_lan_token_setup",
                "register_first_project",
                "review_safety_boundaries",
                "open_dashboard",
                "export_diagnostics",
            ],
            "checklistIsInformationalOnly": True,
            "mutationEndpointsImplemented": False,
            "notes": [
                "First-run setup is a placeholder status surface only.",
                "The checklist is informational and does not execute setup actions.",
                "No setup state, token, account, OAuth, cloud, telemetry, updater, or installer behavior is implemented in this slice.",
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
            "privateAlphaPackagingStatus": "placeholder_only",
            "firstRunWizardStatus": "placeholder_only",
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


def first_run_setup_html() -> str:
    checklist = [
        "confirm_local_service",
        "review_lan_token_setup",
        "register_first_project",
        "review_safety_boundaries",
        "open_dashboard",
        "export_diagnostics",
    ]
    checklist_html = "\n".join(f"        <li><code>{item}</code></li>" for item in checklist)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jarvis First-Run Placeholder</title>
  <style>
    body {{ margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f6f7f9; color: #1d2733; }}
    header {{ background: #ffffff; border-bottom: 1px solid #d8dde5; padding: 18px 28px; }}
    main {{ max-width: 920px; margin: 0 auto; padding: 24px; display: grid; gap: 18px; }}
    section {{ background: #ffffff; border: 1px solid #d8dde5; border-radius: 8px; padding: 18px; }}
    h1, h2 {{ margin: 0 0 10px; }}
    code, pre {{ background: #eef1f5; border-radius: 4px; padding: 2px 4px; }}
    .muted {{ color: #5e6b7a; }}
  </style>
</head>
<body>
  <header>
    <h1>First-Run Setup Placeholder</h1>
    <div class="muted">Loopback-only readiness status for a future setup wizard</div>
  </header>
  <main>
    <section>
      <h2>Status</h2>
      <pre id="first-run-status">Loading first-run placeholder status...</pre>
    </section>
    <section>
      <h2>Future Checklist</h2>
      <p>This checklist is informational only. It does not run setup actions or store setup state.</p>
      <ul>
{checklist_html}
      </ul>
    </section>
    <section>
      <h2>Boundaries</h2>
      <p>The future wizard must respect LAN token protection, Safe Action Runtime decisions, approvals, and audit logging.</p>
      <p>This placeholder does not persist setup state, write configuration files, create tokens, store tokens, provide account onboarding, use OAuth, sync cloud data, add telemetry, add an updater, or build installer packaging.</p>
    </section>
  </main>
  <script>
    async function loadFirstRunStatus() {{
      const status = await fetch('/api/setup/first-run/status').then((response) => response.json());
      document.getElementById('first-run-status').textContent = JSON.stringify(status, null, 2);
    }}
    loadFirstRunStatus();
  </script>
</body>
</html>"""


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
    .list { display: grid; gap: 10px; }
    .row { border: 1px solid #e2e6ed; border-radius: 6px; padding: 12px; }
    .stack { display: grid; gap: 10px; }
    .actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    label { display: grid; gap: 4px; font-weight: 600; }
    input, select, textarea { border: 1px solid #bac6d4; border-radius: 6px; padding: 7px 9px; font: inherit; }
    textarea { min-height: 70px; resize: vertical; }
    button { border: 1px solid #9eb3cc; border-radius: 6px; background: #ffffff; color: #1d2733; padding: 7px 10px; cursor: pointer; }
    button:disabled { color: #7a8794; cursor: default; }
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
    <section id="first-run-status">
      <h2>First-Run / Setup</h2>
      <pre id="first-run">Loading first-run placeholder status...</pre>
      <p><a href="/setup/first-run">Open loopback first-run setup placeholder</a></p>
    </section>
    <section id="private-alpha-packaging-status">
      <h2>Private Alpha / Packaging</h2>
      <pre id="private-alpha-packaging">Loading private-alpha packaging placeholder status...</pre>
    </section>
    <section id="validation-agent-status" class="stack">
      <h2>Validation Agent</h2>
      <pre id="validation-agent">Loading validation evidence status...</pre>
      <div id="validation-safety-note" class="row">
        <strong>Manual evidence only.</strong>
        <div class="muted">The Validation Agent records manual evidence only. It does not control VirtualBox, run commands, install dependencies, create installers, push to GitHub, or certify security or production readiness.</div>
      </div>
      <div class="actions">
        <button id="validation-load-runbooks-button" type="button">Load runbooks</button>
        <button id="validation-load-runs-button" type="button">Load recent runs</button>
      </div>
      <div id="validation-runbooks" class="list muted">Runbooks not loaded yet.</div>
      <div id="validation-runbook-steps" class="list muted">Select or load the clean Windows VM runbook to inspect manual steps.</div>
      <div class="row stack">
        <h3>Create Manual Validation Run</h3>
        <label>
          Target environment
          <input id="validation-target-environment" type="text" value="Clean Windows VM manual validation">
        </label>
        <button id="validation-create-run-button" type="button">Create manual validation run</button>
      </div>
      <div id="validation-runs" class="list muted">Recent validation runs not loaded yet.</div>
      <div id="validation-run-detail" class="list muted">Open a run to view manual step result status.</div>
      <div class="row stack">
        <h3>Record Manual Step Result</h3>
        <label>
          Run ID
          <input id="validation-step-run-id" type="text" placeholder="validation-run-...">
        </label>
        <label>
          Step
          <select id="validation-step-id"></select>
        </label>
        <label>
          Status
          <select id="validation-step-status">
            <option value="passed">passed</option>
            <option value="failed">failed</option>
            <option value="blocked">blocked</option>
            <option value="skipped">skipped</option>
            <option value="not_started">not_started</option>
          </select>
        </label>
        <label>
          Notes
          <textarea id="validation-step-notes" placeholder="Manual notes only. Do not paste secrets, .env contents, private keys, or full sensitive logs."></textarea>
        </label>
        <label>
          Evidence
          <textarea id="validation-step-evidence" placeholder="Manual evidence summary only. No files, screenshots, commands, or protected content."></textarea>
        </label>
        <button id="validation-record-step-button" type="button">Record step result</button>
      </div>
      <div class="actions">
        <button id="validation-complete-run-button" type="button">Complete evidence record</button>
        <button id="validation-report-run-button" type="button">Generate local report</button>
      </div>
      <pre id="validation-workflow-result">No validation workflow action from this dashboard session.</pre>
      <p><a href="/validation/runbooks">View validation runbooks API</a></p>
      <p><a href="/validation/runs">View validation runs API</a></p>
    </section>
    <section id="private-alpha-readiness-snapshot" class="stack">
      <h2>Private-Alpha Readiness Snapshot</h2>
      <pre id="readiness-snapshot">Loading private-alpha readiness snapshot...</pre>
      <div id="readiness-safety-note" class="row">
        <strong>Local readiness summary only.</strong>
        <div class="muted">Does not create installer artifacts. Does not certify production readiness. Does not run VM automation. Does not push to GitHub.</div>
      </div>
      <div id="readiness-snapshot-summary" class="grid"></div>
      <div class="actions">
        <button id="readiness-report-button" type="button">Generate local readiness report</button>
      </div>
      <pre id="readiness-report-result">No readiness report generated from this dashboard session.</pre>
      <p><a href="/readiness/snapshot">View readiness snapshot API</a></p>
      <p><a href="/readiness/snapshot/latest">View latest readiness snapshot report metadata</a></p>
    </section>
    <section id="redacted-diagnostics-bundle" class="stack">
      <h2>Redacted Diagnostics Bundle</h2>
      <pre id="diagnostics-bundle">Loading redacted diagnostics bundle status...</pre>
      <div id="diagnostics-bundle-safety-note" class="row">
        <strong>Local redacted diagnostics only.</strong>
        <div class="muted">Does not upload. Does not run commands. Does not read protected secrets. Does not certify production/security readiness.</div>
      </div>
      <div id="diagnostics-bundle-summary" class="grid"></div>
      <div class="actions">
        <button id="diagnostics-bundle-report-button" type="button">Generate local diagnostics report</button>
      </div>
      <pre id="diagnostics-bundle-report-result">No diagnostics report generated from this dashboard session.</pre>
      <p><a href="/diagnostics/bundle">View redacted diagnostics bundle API</a></p>
      <p><a href="/diagnostics/bundle/latest">View latest diagnostics bundle report metadata</a></p>
    </section>
    <section id="evidence-report-center" class="stack">
      <h2>Evidence Report Center</h2>
      <pre id="evidence-report-center-status">Loading evidence report center status...</pre>
      <div id="evidence-report-center-safety-note" class="row">
        <strong>Local report metadata only.</strong>
        <div class="muted">Metadata view only. No report mutation, network transfer, publication, or readiness attestation is available. Reads only allowed report files under Jarvis reports directory. Redacts summaries.</div>
      </div>
      <div id="evidence-report-counts" class="grid"></div>
      <div class="actions">
        <button id="evidence-report-refresh-button" type="button">Refresh report index</button>
      </div>
      <div id="evidence-report-list" class="list muted">Loading safe report metadata...</div>
      <p><a href="/evidence/reports">View evidence report index API</a></p>
      <p><a href="/evidence/reports/{report_id}/metadata">View evidence report metadata endpoint pattern</a></p>
    </section>
    <section id="agent-manifest-health-center" class="stack">
      <h2>Agent Manifest Health Center</h2>
      <pre id="agent-manifest-health-status">Loading agent manifest health...</pre>
      <div id="agent-manifest-health-note" class="row">
        <strong>Known local manifest directories only.</strong>
        <div class="muted">Read-only metadata view. No connector state changes, manifest mutation, tool execution, network transfer, publication, or readiness attestation is available.</div>
      </div>
      <div id="agent-manifest-health-counts" class="grid"></div>
      <div class="actions">
        <button id="agent-manifest-health-refresh-button" type="button">Refresh manifest health</button>
      </div>
      <div id="agent-manifest-health-list" class="list muted">Loading safe manifest metadata...</div>
      <p><a href="/agents/manifest-health">View agent manifest health API</a></p>
    </section>
    <section id="project-profiles">
      <h2>Project Profiles</h2>
      <div id="project-profile-list" class="list muted">Loading project profiles...</div>
    </section>
    <section id="security-safety-review">
      <h2>Security/Safety Review</h2>
      <div id="security-review-list" class="list muted">Loading registered project review actions...</div>
      <pre id="security-review-result">No local review run from this dashboard session.</pre>
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
      const profiles = await fetch('/api/projects/profiles').then((response) => response.json());
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
      document.getElementById('first-run').textContent = JSON.stringify(summary.firstRunWizard, null, 2);
      document.getElementById('private-alpha-packaging').textContent = JSON.stringify(summary.privateAlphaPackaging, null, 2);
      document.getElementById('validation-agent').textContent = JSON.stringify(summary.validationAgent, null, 2);
      document.getElementById('readiness-snapshot').textContent = JSON.stringify(summary.privateAlphaReadinessSnapshot, null, 2);
      document.getElementById('diagnostics-bundle').textContent = JSON.stringify(summary.redactedDiagnosticsBundle, null, 2);
      document.getElementById('evidence-report-center-status').textContent = JSON.stringify(summary.evidenceReportCenter, null, 2);
      document.getElementById('agent-manifest-health-status').textContent = JSON.stringify(summary.agentManifestHealth, null, 2);
      renderReadinessSnapshotSummary(summary.privateAlphaReadinessSnapshot);
      bindReadinessSnapshotControls();
      renderDiagnosticsBundleSummary(summary.redactedDiagnosticsBundle);
      bindDiagnosticsBundleControls();
      renderEvidenceReportCenter(summary.evidenceReportCenter);
      bindEvidenceReportControls();
      renderAgentManifestHealth(summary.agentManifestHealth);
      bindAgentManifestHealthControls();
      await loadValidationWorkflowSummary(false);
      renderProjectProfiles(profiles);
      renderSecurityReviews(profiles);
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
    function renderProjectProfiles(profiles) {
      document.getElementById('project-profile-list').innerHTML = profiles.length
        ? profiles.map((profile) => `<div class="row">
            <strong>${profile.projectName}</strong>
            <div class="muted">${profile.projectType || 'unknown'} · ${(profile.detectedLanguages || []).join(', ') || 'no languages detected'} · ${profile.packageManager || 'none'}</div>
            <div>Mode: <code>${profile.recommendedMode}</code> · Warnings: <code>${profile.warningCount}</code> · Blocked: <code>${profile.blockedReasonCount}</code></div>
            <div>Boundary: root <code>${profile.boundaryStatus.rootValidated ? 'validated' : 'not validated'}</code>, protected patterns <code>${profile.boundaryStatus.protectedPatternsActive ? 'active' : 'inactive'}</code>, runtime skips <code>${profile.boundaryStatus.runtimeSkipDirsActive ? 'active' : 'inactive'}</code></div>
            <div>Checks: ${(profile.preferredCheckOrder || []).map((command) => `<code>${command}</code>`).join(' ') || '<span class="muted">No preferred checks detected.</span>'}</div>
          </div>`).join('')
        : 'No registered projects found.';
    }
    function renderSecurityReviews(profiles) {
      document.getElementById('security-review-list').innerHTML = profiles.length
        ? profiles.map((profile) => `<div class="row">
            <strong>${profile.projectName}</strong>
            <button type="button" data-project="${profile.projectName}">Run local security review</button>
            <span class="muted">Read-only registered project review. No scripts, installs, or Git writes.</span>
          </div>`).join('')
        : 'Register a project before running a local security review.';
      document.querySelectorAll('#security-review-list button').forEach((button) => {
        button.onclick = async () => {
          button.disabled = true;
          const project = button.getAttribute('data-project');
          const result = await fetch(`/api/projects/${encodeURIComponent(project)}/security-review`, { method: 'POST' }).then((response) => response.json());
          document.getElementById('security-review-result').textContent = JSON.stringify(result, null, 2);
          await loadDashboard();
        };
      });
    }
    function renderReadinessSnapshotSummary(snapshot) {
      const values = {
        verdict: snapshot.overallVerdict,
        blockers: snapshot.blockerCount,
        warnings: snapshot.warningCount,
        validation: snapshot.validationEvidenceStatus,
        security: snapshot.securityReviewStatus,
        publicDocs: snapshot.publicRepoDocsStatus,
        connectors: snapshot.connectorCostBoundaryStatus,
      };
      document.getElementById('readiness-snapshot-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function bindReadinessSnapshotControls() {
      const reportButton = document.getElementById('readiness-report-button');
      reportButton.onclick = async () => {
        reportButton.disabled = true;
        const result = await fetch('/readiness/snapshot/report', { method: 'POST' }).then((response) => response.json());
        document.getElementById('readiness-report-result').textContent = JSON.stringify(result, null, 2);
        reportButton.disabled = false;
        await loadDashboard();
      };
    }
    function renderDiagnosticsBundleSummary(bundle) {
      const latest = bundle.latestReport || {};
      const values = {
        warnings: bundle.warningCount,
        sections: bundle.sectionCount,
        latest: latest.available ? latest.reportId : 'none',
        uploads: bundle.uploads ? 'enabled' : 'disabled',
        commands: bundle.commandExecution ? 'enabled' : 'disabled',
        certification: bundle.certification ? 'yes' : 'no',
      };
      document.getElementById('diagnostics-bundle-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function bindDiagnosticsBundleControls() {
      const reportButton = document.getElementById('diagnostics-bundle-report-button');
      reportButton.onclick = async () => {
        reportButton.disabled = true;
        const result = await fetch('/diagnostics/bundle/report', { method: 'POST' }).then((response) => response.json());
        document.getElementById('diagnostics-bundle-report-result').textContent = JSON.stringify(result, null, 2);
        reportButton.disabled = false;
        await loadDashboard();
      };
    }
    function renderEvidenceReportCenter(center) {
      const counts = center.reportCountsByType || {};
      document.getElementById('evidence-report-counts').innerHTML = Object.entries(counts).length
        ? Object.entries(counts)
          .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
          .join('')
        : '<div class="metric"><span>reports</span><strong>0</strong></div>';
      const reports = center.recentReports || [];
      document.getElementById('evidence-report-list').innerHTML = reports.length
        ? reports.map((report) => `<div class="row">
            <strong>${escapeHtml(report.title || report.filename)}</strong>
            <div><code>${escapeHtml(report.reportType)}</code> - ${escapeHtml(report.sizeBytes)} bytes - readable: <code>${report.readable ? 'true' : 'false'}</code></div>
            <div class="muted">${escapeHtml(report.summary || 'No summary available.')}</div>
            <div><a href="/evidence/reports/${encodeURIComponent(report.reportId)}">Safe detail</a> - <a href="/evidence/reports/${encodeURIComponent(report.reportId)}/metadata">Metadata</a></div>
          </div>`).join('')
        : 'No evidence reports found.';
    }
    function bindEvidenceReportControls() {
      const refreshButton = document.getElementById('evidence-report-refresh-button');
      refreshButton.onclick = async () => {
        refreshButton.disabled = true;
        await loadDashboard();
        refreshButton.disabled = false;
      };
    }
    function renderAgentManifestHealth(health) {
      const values = {
        total: health.totalManifests || 0,
        localAgents: health.implementedLocalAgents || 0,
        placeholders: health.disabledPlaceholders || 0,
        warnings: health.warningCount || 0,
      };
      document.getElementById('agent-manifest-health-counts').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
      const manifests = health.recentOrFlaggedManifests || [];
      document.getElementById('agent-manifest-health-list').innerHTML = manifests.length
        ? manifests.map((manifest) => `<div class="row">
            <strong>${escapeHtml(manifest.name || manifest.filename)}</strong>
            <div><code>${escapeHtml(manifest.manifestType)}</code> · implemented: <code>${escapeHtml(manifest.implemented)}</code> · default: <code>${escapeHtml(manifest.defaultEnabled)}</code></div>
            <div>Warnings: <code>${escapeHtml(manifest.warningCount || 0)}</code></div>
            <div class="muted">${escapeHtml((manifest.warnings || []).join('; ') || 'No warnings.')}</div>
            <div><a href="/agents/manifest-health/${encodeURIComponent(manifest.manifestId)}">Safe metadata</a></div>
          </div>`).join('')
        : 'No manifests found.';
    }
    function bindAgentManifestHealthControls() {
      const refreshButton = document.getElementById('agent-manifest-health-refresh-button');
      refreshButton.onclick = async () => {
        refreshButton.disabled = true;
        await loadDashboard();
        refreshButton.disabled = false;
      };
    }
    async function loadValidationWorkflowSummary(refreshLists) {
      bindValidationWorkflowControls();
      if (refreshLists) {
        await Promise.all([loadValidationRunbooks(), loadValidationRuns()]);
      }
    }
    function bindValidationWorkflowControls() {
      const loadRunbooksButton = document.getElementById('validation-load-runbooks-button');
      const loadRunsButton = document.getElementById('validation-load-runs-button');
      const createRunButton = document.getElementById('validation-create-run-button');
      const recordStepButton = document.getElementById('validation-record-step-button');
      const completeRunButton = document.getElementById('validation-complete-run-button');
      const reportRunButton = document.getElementById('validation-report-run-button');
      loadRunbooksButton.onclick = loadValidationRunbooks;
      loadRunsButton.onclick = loadValidationRuns;
      createRunButton.onclick = createManualValidationRun;
      recordStepButton.onclick = recordValidationStepResult;
      completeRunButton.onclick = completeValidationRun;
      reportRunButton.onclick = generateValidationReport;
    }
    async function loadValidationRunbooks() {
      const runbooks = await fetch('/validation/runbooks').then((response) => response.json());
      const cleanRunbook = runbooks.find((runbook) => runbook.runbookId === 'clean_windows_vm_validation') || runbooks[0];
      document.getElementById('validation-runbooks').innerHTML = runbooks.length
        ? runbooks.map((runbook) => `<div class="row">
            <strong>${escapeHtml(runbook.title)}</strong>
            <div><code>${escapeHtml(runbook.runbookId)}</code></div>
            <div class="muted">${escapeHtml(runbook.description)}</div>
            <div>Target: ${escapeHtml(runbook.targetEnvironment)}</div>
          </div>`).join('')
        : 'No validation runbooks found.';
      renderValidationRunbookSteps(cleanRunbook);
    }
    function renderValidationRunbookSteps(runbook) {
      const stepSelect = document.getElementById('validation-step-id');
      if (!runbook || !Array.isArray(runbook.steps)) {
        document.getElementById('validation-runbook-steps').textContent = 'No runbook steps available.';
        stepSelect.innerHTML = '';
        return;
      }
      stepSelect.innerHTML = runbook.steps
        .map((step) => `<option value="${escapeHtml(step.stepId)}">${escapeHtml(step.stepId)}</option>`)
        .join('');
      document.getElementById('validation-runbook-steps').innerHTML = runbook.steps
        .map((step) => `<div class="row">
          <strong>${escapeHtml(step.title)}</strong>
          <div><code>${escapeHtml(step.stepId)}</code> · ${escapeHtml(step.category)} · required: <code>${step.required ? 'true' : 'false'}</code></div>
          <div>Expected: ${escapeHtml(step.expectedResult)}</div>
          <div>Evidence type: <code>${escapeHtml(step.evidenceType)}</code></div>
        </div>`).join('');
    }
    async function createManualValidationRun() {
      const targetEnvironment = document.getElementById('validation-target-environment').value || 'Clean Windows VM manual validation';
      const run = await fetch('/validation/runs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ runbookId: 'clean_windows_vm_validation', targetEnvironment }),
      }).then((response) => response.json());
      showValidationResult(run);
      if (run.runId) {
        document.getElementById('validation-step-run-id').value = run.runId;
        renderValidationRunDetail(run);
      }
      await loadValidationRuns();
      await loadDashboard();
    }
    async function loadValidationRuns() {
      const runs = await fetch('/validation/runs').then((response) => response.json());
      document.getElementById('validation-runs').innerHTML = runs.length
        ? runs.map((run) => `<div class="row">
            <strong>${escapeHtml(run.runId)}</strong>
            <div>Status: <code>${escapeHtml(run.status)}</code> · Runbook: <code>${escapeHtml(run.runbookId)}</code></div>
            <div class="muted">${escapeHtml(run.targetEnvironment)}</div>
            <button type="button" data-validation-run-id="${escapeHtml(run.runId)}">Open run</button>
          </div>`).join('')
        : 'No validation runs found.';
      document.querySelectorAll('[data-validation-run-id]').forEach((button) => {
        button.onclick = async () => {
          await openValidationRun(button.getAttribute('data-validation-run-id'));
        };
      });
    }
    async function openValidationRun(runId) {
      if (!runId) {
        return;
      }
      const run = await fetch(`/validation/runs/${encodeURIComponent(runId)}`).then((response) => response.json());
      showValidationResult(run);
      if (run.runId) {
        document.getElementById('validation-step-run-id').value = run.runId;
        renderValidationRunDetail(run);
      }
    }
    function renderValidationRunDetail(run) {
      const results = Array.isArray(run.stepResults) ? run.stepResults : [];
      document.getElementById('validation-run-detail').innerHTML = `<div class="row">
          <strong>${escapeHtml(run.runId)}</strong>
          <div>Status: <code>${escapeHtml(run.status)}</code></div>
          <div>Target: ${escapeHtml(run.targetEnvironment)}</div>
        </div>` + results.map((result) => `<div class="row">
          <strong>${escapeHtml(result.stepId)}</strong>
          <div>Status: <code>${escapeHtml(result.status)}</code> · Updated: ${escapeHtml(result.updatedAt || '')}</div>
          <div>Notes: ${escapeHtml(result.notes || 'None recorded.')}</div>
          <div>Evidence: ${escapeHtml(result.redactedEvidence || 'None recorded.')}</div>
        </div>`).join('');
    }
    async function recordValidationStepResult() {
      const runId = document.getElementById('validation-step-run-id').value.trim();
      const stepId = document.getElementById('validation-step-id').value;
      if (!runId || !stepId) {
        showValidationResult({ error: 'Open or enter a validation run and choose a step first.' });
        return;
      }
      const payload = {
        status: document.getElementById('validation-step-status').value,
        notes: document.getElementById('validation-step-notes').value,
        evidence: document.getElementById('validation-step-evidence').value,
      };
      const run = await fetch(`/validation/runs/${encodeURIComponent(runId)}/steps/${encodeURIComponent(stepId)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).then((response) => response.json());
      showValidationResult(run);
      if (run.runId) {
        renderValidationRunDetail(run);
      }
      await loadValidationRuns();
      await loadDashboard();
    }
    async function completeValidationRun() {
      const runId = document.getElementById('validation-step-run-id').value.trim();
      if (!runId) {
        showValidationResult({ error: 'Open or enter a validation run first.' });
        return;
      }
      const run = await fetch(`/validation/runs/${encodeURIComponent(runId)}/complete`, { method: 'POST' }).then((response) => response.json());
      showValidationResult({ status: run.status, runId: run.runId, summary: run.summary, note: 'Completed evidence record. This is local validation evidence, not certification.' });
      if (run.runId) {
        renderValidationRunDetail(run);
      }
      await loadValidationRuns();
      await loadDashboard();
    }
    async function generateValidationReport() {
      const runId = document.getElementById('validation-step-run-id').value.trim();
      if (!runId) {
        showValidationResult({ error: 'Open or enter a validation run first.' });
        return;
      }
      const report = await fetch(`/validation/runs/${encodeURIComponent(runId)}/report`, { method: 'POST' }).then((response) => response.json());
      showValidationResult({ ...report, note: 'Generated local validation evidence report. This is not certification.' });
      await loadDashboard();
    }
    function showValidationResult(value) {
      document.getElementById('validation-workflow-result').textContent = JSON.stringify(value, null, 2);
    }
    function escapeHtml(value) {
      return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
    }
    loadDashboard();
  </script>
</body>
</html>"""
