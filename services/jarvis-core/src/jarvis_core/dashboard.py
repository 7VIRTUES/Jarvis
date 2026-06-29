from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from . import APP_NAME, VERSION
from .agent_manifest_health import AgentManifestHealthService
from .config import load_json_config
from .docs_center import DocsCenterService
from .evidence_report_center import EvidenceReportCenterService
from .file_data_agent import file_data_dashboard_summary
from .lan_security import LAN_TOKEN_ENV_VAR, lan_protection_status, lan_setup_status
from .local_classification_agent import local_classification_dashboard_summary
from .local_decision_agent import local_decision_dashboard_summary
from .local_drafting_agent import local_drafting_dashboard_summary
from .local_extraction_agent import local_extraction_dashboard_summary
from .local_planning_agent import local_planning_dashboard_summary
from .local_research_agent import local_research_dashboard_summary
from .local_response_agents_catalog import local_response_agents_summary
from .local_review_agent import local_review_dashboard_summary
from .local_summarization_agent import local_summarization_dashboard_summary
from .local_transformation_agent import local_transformation_dashboard_summary
from .local_troubleshooting_agent import local_troubleshooting_dashboard_summary
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
        docs_center = self.docs_center_summary()
        local_research = self.local_research_agent_summary()
        file_data = self.file_data_agent_summary()
        local_planning = self.local_planning_agent_summary()
        local_drafting = self.local_drafting_agent_summary()
        local_review = self.local_review_agent_summary()
        local_decision = self.local_decision_agent_summary()
        local_troubleshooting = self.local_troubleshooting_agent_summary()
        local_summarization = self.local_summarization_agent_summary()
        local_extraction = self.local_extraction_agent_summary()
        local_classification = self.local_classification_agent_summary()
        local_transformation = self.local_transformation_agent_summary()
        local_response_agents_index = self.local_response_agents_index_summary()
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
                "docsCenter": "local_docs_metadata_only",
                "localResearchAgent": "implemented_local_only",
                "fileDataAgent": "implemented_local_only",
                "localPlanningAgent": "implemented_local_only",
                "localDraftingAgent": "implemented_local_only",
                "localReviewAgent": "implemented_local_only",
                "localDecisionAgent": "implemented_local_only",
                "localTroubleshootingAgent": "implemented_local_only",
                "localSummarizationAgent": "implemented_local_only",
                "localExtractionAgent": "implemented_local_only",
                "localClassificationAgent": "implemented_local_only",
                "localTransformationAgent": "implemented_local_only",
                "localResponseAgentsIndex": "read_only_index",
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
            "docsCenter": docs_center,
            "localResearchAgent": local_research,
            "fileDataAgent": file_data,
            "localPlanningAgent": local_planning,
            "localDraftingAgent": local_drafting,
            "localReviewAgent": local_review,
            "localDecisionAgent": local_decision,
            "localTroubleshootingAgent": local_troubleshooting,
            "localSummarizationAgent": local_summarization,
            "localExtractionAgent": local_extraction,
            "localClassificationAgent": local_classification,
            "localTransformationAgent": local_transformation,
            "localResponseAgentsIndex": local_response_agents_index,
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
            "docsCenter": self.docs_center_summary(),
            "localResearchAgent": self.local_research_agent_summary(),
            "fileDataAgent": self.file_data_agent_summary(),
            "localPlanningAgent": self.local_planning_agent_summary(),
            "localDraftingAgent": self.local_drafting_agent_summary(),
            "localReviewAgent": self.local_review_agent_summary(),
            "localDecisionAgent": self.local_decision_agent_summary(),
            "localTroubleshootingAgent": self.local_troubleshooting_agent_summary(),
            "localSummarizationAgent": self.local_summarization_agent_summary(),
            "localExtractionAgent": self.local_extraction_agent_summary(),
            "localClassificationAgent": self.local_classification_agent_summary(),
            "localTransformationAgent": self.local_transformation_agent_summary(),
            "localResponseAgentsIndex": self.local_response_agents_index_summary(),
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
                "Docs/Runbook Center reads README.md and direct docs Markdown files only; it does not mutate docs, transfer docs, or claim readiness.",
                "Local Research Agent uses user-provided notes only; it does not browse, verify citations, call connectors, access accounts, or mutate files.",
                "File/Data Agent summarizes registered-project metadata only; it skips protected/runtime paths and does not scan arbitrary paths, upload, execute commands, or mutate files.",
                "Local Planning Agent uses user-provided planning inputs only; it does not create tasks, reminders, calendar/email items, files, database records, or external calls.",
                "Local Drafting Agent uses user-provided drafting inputs only; it does not persist draft text, send email, post publicly, access accounts, read files, write files, or call connectors.",
                "Local Review Agent uses user-provided review content only; it does not verify facts, inspect repos, execute tests, persist reviews, read files, write files, or call connectors.",
                "Local Decision Agent uses user-provided decision inputs only; it does not verify facts, give professional advice, inspect repos, persist decisions, read files, write files, purchase, send, post, or call connectors.",
                "Local Troubleshooting Agent uses user-provided troubleshooting inputs only; it does not execute commands, read files or logs, inspect repos, validate fixes, persist tickets, download, upload, mutate settings, or call connectors.",
                "Local Summarization Agent uses user-provided text only; it does not read files, retrieve documents, verify sources or citations, persist summaries, inspect repos, execute tests, or call connectors.",
                "Local Extraction Agent uses user-provided text only; it does not read files, retrieve documents, verify sources or citations, create tasks, persist extracted items, inspect repos, execute tests, or call connectors.",
                "Local Classification Agent uses user-provided text and items only; it does not read files, retrieve documents, verify sources or citations, create tasks, persist classifications, inspect repos, execute tests, call agents, or call connectors.",
                "Local Transformation Agent uses user-provided text and items only; it does not read files, create documents, export files, persist transformations, inspect repos, execute tests, or call connectors.",
                "Local Response Agents Index is read-only inventory metadata; it does not add agents, execute workflows, call connectors, mutate files, persist tasks, or claim validation/certification.",
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

    def docs_center_summary(self) -> dict[str, Any]:
        return DocsCenterService(self.workspace_root).dashboard_summary()

    def local_research_agent_summary(self) -> dict[str, Any]:
        return local_research_dashboard_summary()

    def file_data_agent_summary(self) -> dict[str, Any]:
        return file_data_dashboard_summary()

    def local_planning_agent_summary(self) -> dict[str, Any]:
        return local_planning_dashboard_summary()

    def local_drafting_agent_summary(self) -> dict[str, Any]:
        return local_drafting_dashboard_summary()

    def local_review_agent_summary(self) -> dict[str, Any]:
        return local_review_dashboard_summary()

    def local_decision_agent_summary(self) -> dict[str, Any]:
        return local_decision_dashboard_summary()

    def local_troubleshooting_agent_summary(self) -> dict[str, Any]:
        return local_troubleshooting_dashboard_summary()

    def local_summarization_agent_summary(self) -> dict[str, Any]:
        return local_summarization_dashboard_summary()

    def local_extraction_agent_summary(self) -> dict[str, Any]:
        return local_extraction_dashboard_summary()

    def local_classification_agent_summary(self) -> dict[str, Any]:
        return local_classification_dashboard_summary()

    def local_transformation_agent_summary(self) -> dict[str, Any]:
        return local_transformation_dashboard_summary()

    def local_response_agents_index_summary(self) -> dict[str, Any]:
        return local_response_agents_summary()

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
    a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible { outline: 3px solid #1b74d1; outline-offset: 2px; }
    .skip-link { position: absolute; left: 12px; top: -48px; background: #ffffff; color: #0b3d75; border: 2px solid #1b74d1; border-radius: 6px; padding: 8px 10px; z-index: 10; }
    .skip-link:focus { top: 12px; }
    .shortcut-help { font-size: 13px; }
    .muted { color: #5e6b7a; }
    .home-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; }
    .home-card { border: 1px solid #d6dee8; border-radius: 6px; padding: 10px; background: #fff; display: grid; gap: 6px; }
    .home-card a { font-weight: 700; text-decoration: none; }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .chip { border: 1px solid #cad5e1; border-radius: 999px; padding: 4px 8px; background: #f8fafc; color: #314154; }
    .home-controls { display: flex; flex-wrap: wrap; gap: 8px; align-items: end; }
    .home-controls label { min-width: min(100%, 280px); }
    .section-toggle { float: right; margin-left: 10px; }
    .dashboard-section.collapsed > :not(h2):not(.section-toggle) { display: none; }
    .section-filter-hidden { display: none; }
    .notice { border-color: #d6b85d; background: #fff8df; }
    .compact-list { display: grid; gap: 8px; max-height: 360px; overflow: auto; }
    .two-column { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
    .checklist { display: grid; gap: 6px; }
    .check-ok { color: #226b38; }
    .check-warn { color: #9a5b00; }
    .button-link { display: inline-flex; align-items: center; justify-content: center; }
  </style>
</head>
<body>
  <a class="skip-link" href="#dashboard-home">Skip to Dashboard Home</a>
  <header>
    <h1>Jarvis PC Local</h1>
    <div class="muted">Read-only dashboard, report, and settings/status visibility</div>
  </header>
  <main>
    <section id="dashboard-home" class="stack">
      <h2>Dashboard Home</h2>
      <div id="dashboard-home-status-chips" class="chips" aria-label="Dashboard status chips">Loading dashboard status...</div>
      <div class="home-controls" aria-label="Dashboard section controls">
        <label>
          Search dashboard sections
          <input id="dashboard-section-search" type="search" placeholder="Search safety, validation, docs..." autocomplete="off">
        </label>
        <button id="dashboard-expand-all-button" type="button">Expand all sections</button>
        <button id="dashboard-collapse-all-button" type="button">Collapse all sections</button>
        <button id="dashboard-clear-filter-button" type="button">Clear filter</button>
      </div>
      <div id="dashboard-section-filter-status" class="muted">Showing all dashboard sections.</div>
      <div id="dashboard-shortcut-help" class="muted shortcut-help">Keyboard shortcuts: / focuses section search, Escape clears the filter, e expands all sections, c collapses all sections.</div>
      <div class="home-grid" aria-label="Dashboard section navigation">
        <div class="home-card"><a href="#safety-summary">View Safety Summary</a><span class="muted">Read-only safety posture.</span></div>
        <div class="home-card"><a href="#project-profiles">View Project Profiles</a><span class="muted">Registered project metadata.</span></div>
        <div class="home-card"><a href="#security-safety-review">View Security/Safety Reviews</a><span class="muted">Registered project review surface.</span></div>
        <div class="home-card"><a href="#validation-agent-status">View Validation Workflow</a><span class="muted">Manual evidence workflow.</span></div>
        <div class="home-card"><a href="#private-alpha-readiness-snapshot">View Private-Alpha Readiness Snapshot</a><span class="muted">Local readiness metadata.</span></div>
        <div class="home-card"><a href="#redacted-diagnostics-bundle">View Redacted Diagnostics Bundle</a><span class="muted">Local redacted diagnostics.</span></div>
        <div class="home-card"><a href="#evidence-report-center">View Evidence Report Center</a><span class="muted">Local report metadata.</span></div>
        <div class="home-card"><a href="#agent-manifest-health-center">View Agent Manifest Health Center</a><span class="muted">Local manifest bounds.</span></div>
        <div class="home-card"><a href="#docs-runbook-center">View Docs/Runbook Center</a><span class="muted">Approved Markdown docs.</span></div>
        <div class="home-card"><a href="#local-research-agent">View Local Research Agent</a><span class="muted">User-provided notes only.</span></div>
        <div class="home-card"><a href="#file-data-agent">View File/Data Agent</a><span class="muted">Registered project metadata.</span></div>
        <div class="home-card"><a href="#local-planning-agent">View Local Planning Agent</a><span class="muted">Response-only planning.</span></div>
        <div class="home-card"><a href="#local-drafting-agent">View Local Drafting Agent</a><span class="muted">Response-only drafting.</span></div>
        <div class="home-card"><a href="#local-review-agent">View Local Review Agent</a><span class="muted">Response-only review.</span></div>
        <div class="home-card"><a href="#local-decision-agent">View Local Decision Agent</a><span class="muted">Response-only decision support.</span></div>
        <div class="home-card"><a href="#local-troubleshooting-agent">View Local Troubleshooting Agent</a><span class="muted">Response-only triage.</span></div>
        <div class="home-card"><a href="#local-summarization-agent">View Local Summarization Agent</a><span class="muted">Response-only summaries.</span></div>
        <div class="home-card"><a href="#local-extraction-agent">View Local Extraction Agent</a><span class="muted">Response-only extraction.</span></div>
        <div class="home-card"><a href="#local-classification-agent">View Local Classification Agent</a><span class="muted">Response-only classification.</span></div>
        <div class="home-card"><a href="#local-transformation-agent">View Local Transformation Agent</a><span class="muted">Response-only transformation.</span></div>
        <div class="home-card"><a href="#local-response-agents-index">View Local Response Agents Index</a><span class="muted">Read-only local agent inventory.</span></div>
        <div class="home-card"><a href="#vm-validation-prep-center">View Clean Windows VM Validation Prep</a><span class="muted">Manual VM validation prep.</span></div>
        <div class="home-card"><a href="#backup-readiness-center">View Backup Readiness Checklist</a><span class="muted">Manual readiness checklist.</span></div>
        <div class="home-card"><a href="#activity-timeline-center">View Recent Activity / Audit Trail</a><span class="muted">Safe local activity metadata.</span></div>
        <div class="home-card"><a href="#dashboard-surface-health-center">View Dashboard Surface Health Center</a><span class="muted">Local surface wiring checks.</span></div>
        <div class="home-card"><a href="#settings-status">View Settings / Status</a><span class="muted">Read-only configuration state.</span></div>
        <div class="home-card"><a href="#lan-protection">View LAN Protection</a><span class="muted">Dashboard access boundary.</span></div>
        <div class="home-card"><a href="#dashboard-status">View Dashboard Status</a><span class="muted">Local summary counts.</span></div>
      </div>
    </section>
    <section id="dashboard-status" class="dashboard-section" data-section-title="Dashboard Status" data-section-keywords="status metrics counts dashboard home">
      <h2>Status</h2>
      <div id="metrics" class="grid"></div>
    </section>
    <section id="settings-status" class="dashboard-section" data-section-title="Settings Status" data-section-keywords="settings status lan local read only">
      <h2>Settings / Status</h2>
      <pre id="settings">Loading settings/status summary...</pre>
    </section>
    <section id="lan-protection" class="dashboard-section" data-section-title="LAN Protection" data-section-keywords="lan protection token access setup">
      <h2>LAN Protection</h2>
      <pre id="lan">Loading LAN protection status...</pre>
      <p><a href="/setup/lan">Open loopback LAN setup guidance</a></p>
    </section>
    <section id="stop-task-control" class="dashboard-section" data-section-title="Active Task Stop Task" data-section-keywords="active task stop queued running">
      <h2>Active Task / Stop Task</h2>
      <div id="active-tasks" class="muted">Loading active task status...</div>
      <button id="stop-task-button" type="button" disabled>Stop Task</button>
      <pre id="stop-task-status">Loading stop-task status...</pre>
    </section>
    <section id="desktop-shell-status" class="dashboard-section" data-section-title="Desktop Shell Tauri" data-section-keywords="desktop shell tauri placeholder">
      <h2>Desktop Shell / Tauri</h2>
      <pre id="desktop-shell">Loading desktop shell placeholder status...</pre>
    </section>
    <section id="first-run-status" class="dashboard-section" data-section-title="First Run Setup" data-section-keywords="first run setup placeholder">
      <h2>First-Run / Setup</h2>
      <pre id="first-run">Loading first-run placeholder status...</pre>
      <p><a href="/setup/first-run">Open loopback first-run setup placeholder</a></p>
    </section>
    <section id="private-alpha-packaging-status" class="dashboard-section" data-section-title="Private Alpha Packaging" data-section-keywords="private alpha packaging readiness">
      <h2>Private Alpha / Packaging</h2>
      <pre id="private-alpha-packaging">Loading private-alpha packaging placeholder status...</pre>
    </section>
    <section id="validation-agent-status" class="stack dashboard-section" data-section-title="Validation Workflow" data-section-keywords="validation workflow manual evidence runbook">
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
    <section id="private-alpha-readiness-snapshot" class="stack dashboard-section" data-section-title="Private Alpha Readiness Snapshot" data-section-keywords="private alpha readiness snapshot local report">
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
    <section id="redacted-diagnostics-bundle" class="stack dashboard-section" data-section-title="Redacted Diagnostics Bundle" data-section-keywords="redacted diagnostics bundle local report">
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
    <section id="evidence-report-center" class="stack dashboard-section" data-section-title="Evidence Report Center" data-section-keywords="evidence report center metadata safe detail">
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
    <section id="agent-manifest-health-center" class="stack dashboard-section" data-section-title="Agent Manifest Health Center" data-section-keywords="agent manifest health connector placeholder local">
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
    <section id="docs-runbook-center" class="stack dashboard-section" data-section-title="Docs Runbook Center" data-section-keywords="docs runbook center markdown readme">
      <h2>Docs/Runbook Center</h2>
      <pre id="docs-center-status">Loading docs index...</pre>
      <div id="docs-center-note" class="row">
        <strong>Approved local Markdown docs only.</strong>
        <div class="muted">Read-only metadata and bounded detail for README.md and direct docs Markdown files. No doc mutation, network transfer, publication, or readiness attestation is available.</div>
      </div>
      <div id="docs-center-counts" class="grid"></div>
      <div class="actions">
        <button id="docs-center-refresh-button" type="button">Refresh docs index</button>
      </div>
      <div id="docs-center-list" class="list muted">Loading safe docs metadata...</div>
      <p><a href="/docs/index">View docs index API</a></p>
    </section>
    <section id="local-research-agent" class="stack dashboard-section" data-section-title="Local Research Agent" data-section-keywords="local research agent notes brief outline comparison reading plan">
      <h2>Local Research Agent</h2>
      <pre id="local-research-agent-status">Loading local research agent status...</pre>
      <div id="local-research-agent-note" class="row">
        <strong>User-provided notes only.</strong>
        <div class="muted">Read-only status for a local brief endpoint. No web browsing, source fetching, citation verification, account access, connector execution, paid API use, posting, sending, or file mutation is available.</div>
      </div>
      <div id="local-research-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/research/local-brief</code></p>
      <p><a href="/docs/local-research-agent.md">Local Research Agent docs</a></p>
    </section>
    <section id="file-data-agent" class="stack dashboard-section" data-section-title="File Data Agent" data-section-keywords="file data agent project metadata registered protected runtime docs">
      <h2>File/Data Agent</h2>
      <pre id="file-data-agent-status">Loading file/data agent status...</pre>
      <div id="file-data-agent-note" class="row">
        <strong>Registered-project metadata only.</strong>
        <div class="muted">Read-only status for a local project metadata endpoint. Raw paths are not accepted. Protected files, runtime directories, dependency caches, external services, uploads, shell execution, and file mutation are unavailable.</div>
      </div>
      <div id="file-data-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/files/local-summary</code></p>
      <p><a href="/docs/file-data-agent.md">File/Data Agent docs</a></p>
    </section>
    <section id="local-planning-agent" class="stack dashboard-section" data-section-title="Local Planning Agent" data-section-keywords="local planning agent response only project plan study checklist weekly">
      <h2>Local Planning Agent</h2>
      <pre id="local-planning-agent-status">Loading local planning agent status...</pre>
      <div id="local-planning-agent-note" class="row">
        <strong>Response-only planning.</strong>
        <div class="muted">Read-only status for a local planning endpoint. It does not create tasks, reminders, calendar or email items, files, database records, connector actions, uploads, shell commands, or external service calls.</div>
      </div>
      <div id="local-planning-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/planning/local-plan</code></p>
      <p><a href="/docs/local-planning-agent.md">Local Planning Agent docs</a></p>
    </section>
    <section id="local-drafting-agent" class="stack dashboard-section" data-section-title="Local Drafting Agent" data-section-keywords="local drafting agent response only message email draft checklist announcement">
      <h2>Local Drafting Agent</h2>
      <pre id="local-drafting-agent-status">Loading local drafting agent status...</pre>
      <div id="local-drafting-agent-note" class="row">
        <strong>Response-only drafting.</strong>
        <div class="muted">Read-only status for a local drafting endpoint. It does not persist draft text, send email, post publicly, read files, write files, access accounts, call connectors, upload content, execute shell commands, or mutate state.</div>
      </div>
      <div id="local-drafting-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/drafting/local-draft</code></p>
      <p><a href="/docs/local-drafting-agent.md">Local Drafting Agent docs</a></p>
    </section>
    <section id="local-review-agent" class="stack dashboard-section" data-section-title="Local Review Agent" data-section-keywords="local review agent response only clarity risk completeness safety actionability">
      <h2>Local Review Agent</h2>
      <pre id="local-review-agent-status">Loading local review agent status...</pre>
      <div id="local-review-agent-note" class="row">
        <strong>Response-only review.</strong>
        <div class="muted">Read-only status for a local review endpoint. It does not verify facts, inspect repos, execute tests, persist reviews, read files, write files, access accounts, call connectors, upload content, execute shell commands, or mutate state.</div>
      </div>
      <div id="local-review-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/review/local-review</code></p>
      <p><a href="/docs/local-review-agent.md">Local Review Agent docs</a></p>
    </section>
    <section id="local-decision-agent" class="stack dashboard-section" data-section-title="Local Decision Agent" data-section-keywords="local decision agent response only balanced safest fastest cheapest highest upside">
      <h2>Local Decision Agent</h2>
      <pre id="local-decision-agent-status">Loading local decision agent status...</pre>
      <div id="local-decision-agent-note" class="row">
        <strong>Response-only decision support.</strong>
        <div class="muted">Read-only status for a local decision endpoint. It does not verify facts, provide professional advice, persist decisions, read files, write files, access accounts, call connectors, upload content, execute shell commands, send, post, purchase, or mutate state.</div>
      </div>
      <div id="local-decision-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/decision/local-decision</code></p>
      <p><a href="/docs/local-decision-agent.md">Local Decision Agent docs</a></p>
    </section>
    <section id="local-troubleshooting-agent" class="stack dashboard-section" data-section-title="Local Troubleshooting Agent" data-section-keywords="local troubleshooting agent response only triage pc app build workflow network">
      <h2>Local Troubleshooting Agent</h2>
      <pre id="local-troubleshooting-agent-status">Loading local troubleshooting agent status...</pre>
      <div id="local-troubleshooting-agent-note" class="row">
        <strong>Response-only triage.</strong>
        <div class="muted">Read-only status for a local troubleshooting endpoint. It does not execute commands, read files or logs, inspect repos, validate fixes, persist tickets, download, upload, mutate settings, access accounts, call connectors, send, post, purchase, or perform destructive repair.</div>
      </div>
      <div id="local-troubleshooting-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/troubleshooting/local-triage</code></p>
      <p><a href="/docs/local-troubleshooting-agent.md">Local Troubleshooting Agent docs</a></p>
    </section>
    <section id="local-summarization-agent" class="stack dashboard-section" data-section-title="Local Summarization Agent" data-section-keywords="local summarization agent response only summary bullets executive action items study notes risks">
      <h2>Local Summarization Agent</h2>
      <pre id="local-summarization-agent-status">Loading local summarization agent status...</pre>
      <div id="local-summarization-agent-note" class="row">
        <strong>Response-only summaries.</strong>
        <div class="muted">Read-only status for a local summarization endpoint. It does not read files, retrieve documents, verify sources or citations, inspect repos, run tests, persist summaries, download, upload, access accounts, call connectors, send, post, purchase, or mutate state.</div>
      </div>
      <div id="local-summarization-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/summarization/local-summary</code></p>
      <p><a href="/docs/local-summarization-agent.md">Local Summarization Agent docs</a></p>
    </section>
    <section id="local-extraction-agent" class="stack dashboard-section" data-section-title="Local Extraction Agent" data-section-keywords="local extraction agent response only action items requirements risks entities questions timeline">
      <h2>Local Extraction Agent</h2>
      <pre id="local-extraction-agent-status">Loading local extraction agent status...</pre>
      <div id="local-extraction-agent-note" class="row">
        <strong>Response-only extraction.</strong>
        <div class="muted">Read-only status for a local extraction endpoint. It does not read files, retrieve documents, verify sources or citations, create tasks, persist extracted items, inspect repos, run tests, download, upload, access accounts, call connectors, send, post, purchase, or mutate state.</div>
      </div>
      <div id="local-extraction-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/extraction/local-extract</code></p>
      <p><a href="/docs/local-extraction-agent.md">Local Extraction Agent docs</a></p>
    </section>
    <section id="local-classification-agent" class="stack dashboard-section" data-section-title="Local Classification Agent" data-section-keywords="local classification agent response only priority risk effort topic routing safety">
      <h2>Local Classification Agent</h2>
      <pre id="local-classification-agent-status">Loading local classification agent status...</pre>
      <div id="local-classification-agent-note" class="row">
        <strong>Response-only classification.</strong>
        <div class="muted">Read-only status for a local classification endpoint. It does not read files, retrieve documents, verify sources or citations, create tasks, persist classifications, inspect repos, run tests, call agents, download, upload, access accounts, call connectors, send, post, purchase, certify compliance, or mutate state.</div>
      </div>
      <div id="local-classification-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/classification/local-classify</code></p>
      <p><a href="/docs/local-classification-agent.md">Local Classification Agent docs</a></p>
    </section>
    <section id="local-transformation-agent" class="stack dashboard-section" data-section-title="Local Transformation Agent" data-section-keywords="local transformation agent response only outline checklist table sop flashcards json csv notes">
      <h2>Local Transformation Agent</h2>
      <pre id="local-transformation-agent-status">Loading local transformation agent status...</pre>
      <div id="local-transformation-agent-note" class="row">
        <strong>Response-only transformation.</strong>
        <div class="muted">Read-only status for a local transformation endpoint. It does not read files, create documents, export files, create spreadsheets, create decks, persist transformations, inspect repos, run tests, download, upload, access accounts, call connectors, send, post, purchase, certify compliance, or mutate state.</div>
      </div>
      <div id="local-transformation-agent-summary" class="grid"></div>
      <p>Endpoint: <code>POST /agents/transformation/local-transform</code></p>
      <p><a href="/docs/local-transformation-agent.md">Local Transformation Agent docs</a></p>
    </section>
    <section id="local-response-agents-index" class="stack dashboard-section" data-section-title="Local Response Agents Index" data-section-keywords="local response agents index inventory safety boundaries docs endpoints">
      <h2>Local Response Agents Index</h2>
      <pre id="local-response-agents-index-status">Loading local response agents index...</pre>
      <div class="row">
        <strong>Read-only inventory.</strong>
        <div class="muted">Lists implemented local response-only and metadata-only agents, endpoints, docs, and safety boundaries. It does not add agents, add endpoints, perform workflows, call connectors, persist tasks, mutate files, or claim clean VM, CI, private-alpha, production, or security certification.</div>
      </div>
      <div id="local-response-agents-index-summary" class="grid"></div>
      <div class="row stack">
        <strong>Discovery and template metadata.</strong>
        <div class="muted">Catalog, categories, single-agent metadata, request templates, and route preview are local-only discovery surfaces. Route preview is suggested route only / not executed.</div>
        <div><code>GET /agents/local-response-agents/catalog</code></div>
        <div><code>GET /agents/local-response-agents/categories</code></div>
        <div><code>GET /agents/local-response-agents/{agent_id}</code></div>
        <div><code>GET /agents/local-response-agents/{agent_id}/request-template</code></div>
        <div><code>POST /agents/local-response-agents/route-preview</code></div>
        <div><code>GET /web-research/policy</code></div>
        <div><code>POST /web-research/validate-url</code></div>
        <div><code>POST /web-research/fetch-public-url</code></div>
        <div><code>POST /web-research/agent-context-preview</code></div>
      </div>
      <div id="local-response-agents-overview" class="row stack">
        <h3>Local Response Agents Overview</h3>
        <div class="muted">Browse the 37 local response agents by category, inspect metadata, view request templates, and preview suggested routes from manual text only.</div>
        <div id="local-response-agents-discovery-status" class="muted">Discovery catalog metadata pending.</div>
        <div id="local-response-agents-boundary-badges">
          <span class="pill">Manual input only</span>
          <span class="pill">Local only</span>
          <span class="pill">Response only</span>
          <span class="pill">No connector</span>
          <span class="pill">Non-persistent</span>
        </div>
      </div>
      <div id="local-response-agents-command-center" class="row stack">
        <h3>Local Response Agent Command Center</h3>
        <div class="muted">Session-only finder for the existing 37 local response agents. Quick actions update this page only; no agent is invoked automatically.</div>
        <div class="two-column">
          <label>
            Search existing agents
            <input id="local-response-agents-command-search" type="search" placeholder="Search id, name, category, tags, endpoint, or capability text">
          </label>
          <label>
            Command Center category
            <select id="local-response-agents-command-category"></select>
          </label>
        </div>
        <div id="local-response-agents-command-count" class="muted">Showing 0 of 37 agents.</div>
        <div id="local-response-agents-high-stakes-banner" class="row stack notice" hidden>
          <strong>High-stakes manual review reminder</strong>
          <div>Response-only guidance. Manual review is required. Verify important details before acting. No professional, legal, medical, or financial decision automation is provided, and no external actions are taken.</div>
        </div>
        <div class="two-column">
          <div class="row stack">
            <strong>Visible agents</strong>
            <div id="local-response-agents-command-list" class="compact-list muted">Agent finder pending.</div>
          </div>
          <div class="row stack">
            <strong>Session pins and recent selections</strong>
            <div class="muted">Pins and recents live in page memory only and clear when the dashboard reloads.</div>
            <div id="local-response-agents-pinned-list" class="compact-list muted">No pinned agents in this session.</div>
            <div id="local-response-agents-recent-list" class="compact-list muted">No recent agents in this session.</div>
          </div>
        </div>
      </div>
      <div id="local-response-agents-playbooks" class="row stack">
        <h3>Manual Workflow Presets / Playbooks</h3>
        <div class="muted">Manual, response-only presets using existing agents only. Selecting a playbook previews a suggested sequence; it does not run, chain, hand off, create tasks, or persist anything.</div>
        <div id="local-response-agents-playbook-list" class="grid"></div>
        <div id="local-response-agents-playbook-status" class="muted">Choose a preset to preview a manual sequence.</div>
        <pre id="local-response-agents-playbook-preview">No playbook selected.</pre>
      </div>
      <div id="local-response-agents-browser" class="grid">
        <div class="row stack">
          <h3>Categories</h3>
          <div id="local-response-agents-category-counts" class="stack muted">Category metadata pending.</div>
          <label>
            Category browser
            <select id="local-response-agents-category-select"></select>
          </label>
        </div>
        <div class="row stack">
          <h3>Agent Details</h3>
          <div id="local-response-agents-detail-panel" class="stack muted">Choose a local response agent to inspect display metadata.</div>
          <div id="local-response-agents-boundary-flags" class="stack muted">Boundary flags pending.</div>
        </div>
      </div>
      <div id="local-response-agents-template-viewer" class="grid">
        <div class="row stack">
          <h3>Request Template</h3>
          <div id="local-response-agents-template-status" class="muted">Template metadata pending.</div>
          <pre id="local-response-agents-request-template">No request template selected.</pre>
        </div>
        <div class="row stack">
          <h3>Sample Payload</h3>
          <div class="muted">Manual example only. Viewing this payload does not invoke an agent.</div>
          <div class="actions">
            <button id="local-response-agents-use-sample-button" type="button">Use sample payload</button>
          </div>
          <pre id="local-response-agents-sample-payload">No sample payload selected.</pre>
        </div>
      </div>
      <div id="local-response-agents-route-preview-panel" class="row stack">
        <h3>Route Preview</h3>
        <div><span class="pill">Suggested only — not executed</span> <span class="pill">Route preview does not invoke agents</span></div>
        <div class="muted">Paste a manual request to receive suggested local response agents from catalog metadata only. Select manually before running a local response. This is not a handoff, not automation, and not execution.</div>
        <label>
          Manual request for route preview
          <textarea id="local-response-agents-route-preview-input" spellcheck="false" placeholder="Describe the local request. Do not paste secrets, account data, or protected content."></textarea>
        </label>
        <div class="actions">
          <button id="local-response-agents-route-preview-button" type="button">Preview suggested agents</button>
        </div>
        <div id="local-response-agents-route-preview-status" class="muted">Route preview does not invoke agents. Suggested only — not executed.</div>
        <label>
          Suggested agent selector
          <select id="local-response-agents-route-preview-suggestions"></select>
        </label>
        <pre id="local-response-agents-route-preview-result">No route preview yet.</pre>
      </div>
      <div id="local-response-agents-manual-workflow-builder" class="row stack">
        <h3>Manual Multi-Agent Workflow Builder</h3>
        <div class="muted">Manual workflow only. Steps are suggestions, not execution. Run one selected agent at a time. Prior context is inserted only after user review.</div>
        <div id="local-response-agents-manual-workflow-boundaries">
          <span class="pill">Manual workflow only</span>
          <span class="pill">Steps are suggestions, not execution</span>
          <span class="pill">Run one selected agent at a time</span>
          <span class="pill">Prior context is inserted only after user review</span>
          <span class="pill">No automatic handoff</span>
          <span class="pill">No persistence</span>
          <span class="pill">No connectors</span>
        </div>
        <label>
          Manual workflow goal
          <textarea id="local-response-agents-manual-workflow-goal" spellcheck="false" placeholder="Describe the local goal. Workflow preview uses catalog metadata only."></textarea>
        </label>
        <label>
          Candidate agent IDs, optional
          <textarea id="local-response-agents-manual-workflow-candidates" spellcheck="false" placeholder="local_planning_agent&#10;local_review_agent"></textarea>
        </label>
        <label>
          <input id="local-response-agents-manual-workflow-include-web-context" type="checkbox">
          Consider optional reviewed web_context in manual payload notes
        </label>
        <div class="actions">
          <button id="local-response-agents-manual-workflow-preview-button" type="button">Preview manual workflow</button>
          <button id="local-response-agents-manual-workflow-load-step-button" type="button">Load selected workflow step</button>
          <button id="local-response-agents-prior-context-copy-button" type="button">Insert latest response as prior context</button>
        </div>
        <div id="local-response-agents-manual-workflow-status" class="muted">Manual workflow preview does not invoke agents, create handoffs, or persist workflows.</div>
        <label>
          Manual workflow step selector
          <select id="local-response-agents-manual-workflow-steps"></select>
        </label>
        <pre id="local-response-agents-manual-workflow-result">No manual workflow preview yet.</pre>
      </div>
      <div id="local-response-agents-index-list" class="stack"></div>
      <div id="local-response-agents-examples-heading"><strong>Read-only example request bodies</strong></div>
      <div class="local-response-agent-example muted">Examples render from the local dashboard summary after load.</div>
      <div id="local-response-agents-example-note" class="muted">Example request bodies are read-only JSON display only. This dashboard does not call agent endpoints or create artifacts from these examples.</div>
      <div id="local-response-agents-workbench" class="row stack">
        <h3>Local Response Agents Workbench</h3>
        <div class="muted">Local-only workbench allowlisted to the 37 local response-agent endpoints. It is not an arbitrary request runner, not a connector runner, not persistent, and not certification or validation.</div>
        <label>
          Select local response agent
          <select id="local-response-agents-workbench-select"></select>
        </label>
        <div>Selected endpoint: <code id="local-response-agents-workbench-endpoint">No agent selected.</code></div>
        <div><a id="local-response-agents-workbench-docs" href="/docs/local-response-agents-index.md">Docs</a></div>
        <div id="local-response-agents-workbench-file-data-note" class="muted">File/Data Agent requires a registered project and remains allowlisted only through its cataloged endpoint.</div>
        <div id="local-response-agents-composer" class="row stack">
          <h3>Request Composer</h3>
          <div id="local-response-agents-composer-boundaries">
            <span class="pill">Manual input only</span>
            <span class="pill">Local only</span>
            <span class="pill">Response only</span>
            <span class="pill">No connector</span>
            <span class="pill">Non-persistent</span>
          </div>
          <label>
            Output type from request-template metadata
            <select id="local-response-agents-output-type-select"></select>
          </label>
        <div id="local-response-agents-payload-preview-status" class="muted">Editable JSON payload preview is filled from the selected template sample.</div>
        </div>
        <div id="local-response-agents-context-kit" class="row stack">
          <h3>Session-only Context Kit Builder</h3>
          <div><span class="pill">Session-only / not saved</span> <span class="pill">Manual insertion only</span> <span class="pill">No clipboard write</span></div>
          <div class="two-column">
            <label>Goal<textarea id="local-response-agents-context-goal" spellcheck="false"></textarea></label>
            <label>Situation/background<textarea id="local-response-agents-context-background" spellcheck="false"></textarea></label>
            <label>Constraints<textarea id="local-response-agents-context-constraints" spellcheck="false"></textarea></label>
            <label>Preferences<textarea id="local-response-agents-context-preferences" spellcheck="false"></textarea></label>
            <label>Evidence/source notes<textarea id="local-response-agents-context-evidence" spellcheck="false"></textarea></label>
            <label>Prior agent output summary<textarea id="local-response-agents-context-prior-summary" spellcheck="false"></textarea></label>
            <label>Decision criteria<textarea id="local-response-agents-context-decision-criteria" spellcheck="false"></textarea></label>
            <label>Risks or high-stakes concerns<textarea id="local-response-agents-context-risks" spellcheck="false"></textarea></label>
          </div>
          <div class="actions">
            <button id="local-response-agents-context-insert-request-button" type="button">Insert context kit into request payload</button>
            <button id="local-response-agents-context-insert-prior-button" type="button">Insert context kit as prior_agent_context</button>
          </div>
          <div id="local-response-agents-context-status" class="muted">Context kit stays in current page memory until manually inserted.</div>
          <pre id="local-response-agents-context-preview">No context kit content yet.</pre>
        </div>
        <div id="local-response-agents-quality-coach" class="row stack">
          <h3>Request Quality Coach</h3>
          <div class="muted">Advisory only. It does not block existing workbench behavior and does not change endpoint contracts.</div>
          <div id="local-response-agents-quality-checklist" class="checklist muted">Quality checklist pending.</div>
          <div id="local-response-agents-quality-warnings" class="stack muted">No readiness warnings yet.</div>
        </div>
        <div id="local-response-agents-web-research" class="row stack">
          <h3>Optional Public Web Research</h3>
          <div class="muted">Read-only public web only. Manual click required. Source context is inserted for review, not executed automatically.</div>
          <div id="local-response-agents-web-research-boundaries">
            <span class="pill">Read-only public web only</span>
            <span class="pill">No logins or accounts</span>
            <span class="pill">No forms, posts, purchases, or bookings</span>
            <span class="pill">No private networks or localhost</span>
            <span class="pill">No downloads or scripts</span>
            <span class="pill">Manual click required</span>
          </div>
          <label>
            <input id="local-response-agents-web-research-enabled" type="checkbox">
            Optional public web source context enabled for this manual payload
          </label>
          <label>
            Public source URLs, one per line
            <textarea id="local-response-agents-web-research-urls" spellcheck="false" placeholder="https://example.com/public-source"></textarea>
          </label>
          <div class="actions">
            <button id="local-response-agents-web-research-validate-button" type="button">Validate public URLs</button>
            <button id="local-response-agents-web-research-fetch-button" type="button">Preview source excerpts</button>
            <button id="local-response-agents-web-research-context-button" type="button">Preview agent context</button>
            <button id="local-response-agents-web-research-add-button" type="button">Add source context to payload</button>
          </div>
          <div id="local-response-agents-web-research-status" class="muted">Public web research is optional, public-only, read-only, and never background browsing.</div>
          <pre id="local-response-agents-web-research-result">No public web source preview yet.</pre>
          <div id="local-response-agents-reviewed-source-context" class="row stack">
            <strong>Reviewed source context</strong>
            <div class="muted">web_context is optional, non-persistent, and supplied only from the manual payload. Agents consume provided excerpts; they do not browse automatically.</div>
            <div class="muted">Source labels are for reference, not proof. Review excerpts before running the selected agent.</div>
            <div id="local-response-agents-reviewed-source-manager" class="stack">
              <div id="local-response-agents-reviewed-source-list" class="stack muted">No reviewed sources in payload.</div>
              <button id="local-response-agents-reviewed-source-clear-button" type="button">Clear reviewed sources</button>
            </div>
            <div id="local-response-agents-source-aware-preview" class="row stack">
              <strong>How selected agent will use reviewed sources</strong>
              <div class="muted">Sources support context only; they are not proof. Agent will not browse automatically. Verify freshness and authority before acting.</div>
              <div id="local-response-agents-source-aware-preview-body" class="muted">No reviewed sources in payload.</div>
            </div>
            <pre id="local-response-agents-reviewed-web-context-preview">No reviewed source context in payload yet.</pre>
          </div>
        </div>
        <label>
          Editable JSON payload preview - manual input only
          <textarea id="local-response-agents-workbench-body" spellcheck="false"></textarea>
        </label>
        <button id="local-response-agents-workbench-run-button" type="button">Run selected local response agent</button>
        <div id="local-response-agents-workbench-status" class="muted">Workbench is ready after the dashboard summary loads.</div>
        <div id="local-response-agents-response-boundaries">
          <span class="pill">Manual input only</span>
          <span class="pill">Local only</span>
          <span class="pill">Response only</span>
          <span class="pill">No connector</span>
          <span class="pill">Non-persistent</span>
        </div>
        <div id="local-response-agents-structured-response" class="row stack muted">No structured local response-agent result yet.</div>
        <pre id="local-response-agents-workbench-response">No local response-agent result yet.</pre>
        <div id="local-response-agents-session-result-board" class="row stack">
          <h3>Session Result Board</h3>
          <div class="muted">Session-only. Not persisted. Manual review only. No automatic handoff. No connector. No file export. Board clears when the page reloads.</div>
          <div id="local-response-agents-session-board-boundaries">
            <span class="pill">Session-only</span>
            <span class="pill">Not persisted</span>
            <span class="pill">Manual review only</span>
            <span class="pill">No automatic handoff</span>
            <span class="pill">No connector</span>
            <span class="pill">No file export</span>
            <span class="pill">Board clears when the page reloads</span>
          </div>
          <div class="actions">
            <button id="local-response-agents-session-board-add-button" type="button">Add latest response to session board</button>
            <button id="local-response-agents-session-board-compare-button" type="button">Build comparison</button>
            <button id="local-response-agents-session-board-packet-button" type="button">Build review packet</button>
            <button id="local-response-agents-session-board-insert-entry-button" type="button">Insert selected entry as prior_agent_context</button>
            <button id="local-response-agents-session-board-insert-packet-button" type="button">Insert review packet as prior_agent_context</button>
            <button id="local-response-agents-session-board-clear-button" type="button">Clear session board</button>
          </div>
          <div id="local-response-agents-session-board-status" class="muted">No latest response yet. The board uses current dashboard page memory only.</div>
          <div id="local-response-agents-session-board-entries" class="stack muted">No board entries yet.</div>
        </div>
        <div id="local-response-agents-result-comparison-matrix" class="row stack">
          <h3>Result Comparison Matrix</h3>
          <div class="muted">Uses selected board entries only. No agent execution, no persistence, and no backend call.</div>
          <div id="local-response-agents-result-comparison-body" class="muted">Select at least two board entries, then build comparison.</div>
        </div>
        <div id="local-response-agents-review-packet-composer" class="row stack">
          <h3>Review Packet Composer</h3>
          <div class="muted">Plain text for manual review. The packet is not persisted, not sent, and not written to clipboard automatically.</div>
          <textarea id="local-response-agents-review-packet-output" spellcheck="false" readonly>No review packet yet.</textarea>
        </div>
      </div>
      <div id="local-response-agents-index-boundaries" class="row"></div>
      <p><a href="/docs/local-response-agents-index.md">Local Response Agents Index docs</a></p>
    </section>
    <section id="vm-validation-prep-center" class="stack dashboard-section" data-section-title="Clean Windows VM Validation Prep" data-section-keywords="clean windows vm validation prep manual checklist loopback lan connectors backup restore">
      <h2>Clean Windows VM Validation Prep</h2>
      <pre id="vm-validation-prep-status">Loading VM validation prep checklist...</pre>
      <div id="vm-validation-prep-note" class="row">
        <strong>Manual preparation only.</strong>
        <div class="muted">Read-only prep metadata for clean Windows VM validation. No command execution, software setup automation, VM control, VM state detection, artifact creation, external calls, or readiness attestation is available.</div>
      </div>
      <div id="vm-validation-prep-counts" class="grid"></div>
      <div class="actions">
        <button id="vm-validation-prep-refresh-button" type="button">Refresh VM validation prep</button>
      </div>
      <div id="vm-validation-prep-list" class="list muted">Loading safe prep checklist metadata...</div>
      <p><a href="/vm-validation/prep">View VM validation prep API</a></p>
      <p><a href="/vm-validation/prep/runbook">View VM validation prep runbook API</a></p>
      <p><a href="/docs/vm-validation-prep-center.md">VM validation prep docs</a> · <a href="/docs/vm-validation-prep-runbook.md">VM validation prep runbook</a></p>
    </section>
    <section id="backup-readiness-center" class="stack dashboard-section" data-section-title="Backup Readiness Checklist" data-section-keywords="backup readiness checklist manual restore protected files reports data">
      <h2>Backup Readiness Checklist</h2>
      <pre id="backup-readiness-status">Loading backup readiness checklist...</pre>
      <div id="backup-readiness-note" class="row">
        <strong>Manual checklist only.</strong>
        <div class="muted">Read-only backup readiness metadata for repo, reports, local data, protected-file exclusions, offline preservation, and restore-test reminders. No file transfer, archive creation, media inspection, deletion, upload, publication, or readiness attestation is available.</div>
      </div>
      <div id="backup-readiness-counts" class="grid"></div>
      <div class="actions">
        <button id="backup-readiness-refresh-button" type="button">Refresh backup checklist</button>
      </div>
      <div id="backup-readiness-list" class="list muted">Loading safe checklist metadata...</div>
      <p><a href="/backup/readiness">View backup readiness API</a></p>
      <p><a href="/backup/readiness/runbook">View backup readiness runbook API</a></p>
      <p><a href="/docs/backup-readiness-center.md">Backup readiness docs</a> · <a href="/docs/backup-readiness-runbook.md">Backup readiness runbook</a></p>
    </section>
    <section id="activity-timeline-center" class="stack dashboard-section" data-section-title="Recent Activity Audit Trail" data-section-keywords="recent activity audit trail tasks events approvals security reports metadata">
      <h2>Recent Activity / Audit Trail</h2>
      <pre id="activity-timeline-status">Loading recent activity timeline...</pre>
      <div id="activity-timeline-note" class="row">
        <strong>Safe local metadata only.</strong>
        <div class="muted">Read-only recent task, event, approval, security note, and action receipt metadata. No raw logs, command output, protected file contents, approval decisions, retries, report transfer, or readiness attestation is available.</div>
      </div>
      <div id="activity-timeline-counts" class="grid"></div>
      <div class="actions">
        <button id="activity-timeline-refresh-button" type="button">Refresh activity timeline</button>
      </div>
      <div id="activity-timeline-list" class="list muted">Loading safe activity metadata...</div>
      <p><a href="/activity/timeline">View activity timeline API</a></p>
      <p><a href="/activity/timeline/{item_id}">View activity timeline detail endpoint pattern</a></p>
    </section>
    <section id="dashboard-surface-health-center" class="stack dashboard-section" data-section-title="Dashboard Surface Health Center" data-section-keywords="dashboard surface health sections endpoints docs safety guards">
      <h2>Dashboard Surface Health Center</h2>
      <pre id="dashboard-surface-health-status">Loading dashboard surface health...</pre>
      <div id="dashboard-surface-health-note" class="row">
        <strong>Local dashboard/API wiring check only.</strong>
        <div class="muted">Read-only visibility for existing dashboard sections, local docs links, guarded endpoints, and safety notes. No route mutation, report mutation, doc mutation, manifest mutation, settings changes, external calls, or readiness attestation is available.</div>
      </div>
      <div id="dashboard-surface-health-counts" class="grid"></div>
      <div class="actions">
        <button id="dashboard-surface-health-refresh-button" type="button">Refresh surface health</button>
      </div>
      <div id="dashboard-surface-health-list" class="list muted">Loading checked surfaces...</div>
      <p><a href="/dashboard/surface-health">View dashboard surface health API</a></p>
      <p><a href="/dashboard/surface-health/{surface_id}">View dashboard surface detail endpoint pattern</a></p>
      <p><a href="/docs/dashboard-surface-health.md">Dashboard surface health docs</a> · <a href="/docs/dashboard-surface-health-runbook.md">Dashboard surface health runbook</a></p>
    </section>
    <section id="project-profiles" class="dashboard-section" data-section-title="Project Profiles" data-section-keywords="project profiles workspace boundaries">
      <h2>Project Profiles</h2>
      <div id="project-profile-list" class="list muted">Loading project profiles...</div>
    </section>
    <section id="security-safety-review" class="dashboard-section" data-section-title="Security Safety Reviews" data-section-keywords="security safety reviews registered project">
      <h2>Security/Safety Review</h2>
      <div id="security-review-list" class="list muted">Loading registered project review actions...</div>
      <pre id="security-review-result">No local review run from this dashboard session.</pre>
    </section>
    <section>
      <h2>Reports</h2>
      <div id="reports" class="muted">Loading reports...</div>
    </section>
    <section id="safety-summary" class="dashboard-section" data-section-title="Safety Summary" data-section-keywords="safety summary boundaries local read only">
      <h2>Safety</h2>
      <pre id="safety">Loading safety summary...</pre>
    </section>
    <section id="connector-placeholders" class="dashboard-section" data-section-title="Connector Placeholders" data-section-keywords="connectors placeholders disabled future">
      <h2>Connectors</h2>
      <div id="connectors" class="muted">Loading connector placeholders...</div>
    </section>
  </main>
  <script>
    async function loadDashboard() {
      const summary = await fetch('/api/dashboard/summary').then((response) => response.json());
      const profiles = await fetch('/api/projects/profiles').then((response) => response.json());
      const counts = summary.counts;
      renderDashboardHome(summary);
      initializeDashboardSectionControls();
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
      document.getElementById('docs-center-status').textContent = JSON.stringify(summary.docsCenter, null, 2);
      document.getElementById('local-research-agent-status').textContent = JSON.stringify(summary.localResearchAgent, null, 2);
      document.getElementById('file-data-agent-status').textContent = JSON.stringify(summary.fileDataAgent, null, 2);
      document.getElementById('local-planning-agent-status').textContent = JSON.stringify(summary.localPlanningAgent, null, 2);
      document.getElementById('local-drafting-agent-status').textContent = JSON.stringify(summary.localDraftingAgent, null, 2);
      document.getElementById('local-review-agent-status').textContent = JSON.stringify(summary.localReviewAgent, null, 2);
      document.getElementById('local-decision-agent-status').textContent = JSON.stringify(summary.localDecisionAgent, null, 2);
      document.getElementById('local-troubleshooting-agent-status').textContent = JSON.stringify(summary.localTroubleshootingAgent, null, 2);
      document.getElementById('local-summarization-agent-status').textContent = JSON.stringify(summary.localSummarizationAgent, null, 2);
      document.getElementById('local-extraction-agent-status').textContent = JSON.stringify(summary.localExtractionAgent, null, 2);
      document.getElementById('local-classification-agent-status').textContent = JSON.stringify(summary.localClassificationAgent, null, 2);
      document.getElementById('local-transformation-agent-status').textContent = JSON.stringify(summary.localTransformationAgent, null, 2);
      document.getElementById('local-response-agents-index-status').textContent = JSON.stringify(summary.localResponseAgentsIndex, null, 2);
      renderReadinessSnapshotSummary(summary.privateAlphaReadinessSnapshot);
      bindReadinessSnapshotControls();
      renderDiagnosticsBundleSummary(summary.redactedDiagnosticsBundle);
      bindDiagnosticsBundleControls();
      renderEvidenceReportCenter(summary.evidenceReportCenter);
      bindEvidenceReportControls();
      renderAgentManifestHealth(summary.agentManifestHealth);
      bindAgentManifestHealthControls();
      renderDocsCenter(summary.docsCenter);
      bindDocsCenterControls();
      renderLocalResearchAgent(summary.localResearchAgent);
      renderFileDataAgent(summary.fileDataAgent);
      renderLocalPlanningAgent(summary.localPlanningAgent);
      renderLocalDraftingAgent(summary.localDraftingAgent);
      renderLocalReviewAgent(summary.localReviewAgent);
      renderLocalDecisionAgent(summary.localDecisionAgent);
      renderLocalTroubleshootingAgent(summary.localTroubleshootingAgent);
      renderLocalSummarizationAgent(summary.localSummarizationAgent);
      renderLocalExtractionAgent(summary.localExtractionAgent);
      renderLocalClassificationAgent(summary.localClassificationAgent);
      renderLocalTransformationAgent(summary.localTransformationAgent);
      renderLocalResponseAgentsIndex(summary.localResponseAgentsIndex);
      initializeLocalResponseAgentsWorkbench(summary.localResponseAgentsIndex);
      await loadVmValidationPrep();
      await loadBackupReadiness();
      await loadActivityTimeline();
      await loadDashboardSurfaceHealth();
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
    function renderDashboardHome(summary) {
      const chips = {
        phase: summary.phase && summary.phase.status,
        projects: summary.counts && summary.counts.projects,
        reports: summary.counts && summary.counts.reports,
        connectors: summary.counts && summary.counts.connectors,
        lan: summary.lanProtection && summary.lanProtection.status,
        docs: summary.docsCenter && summary.docsCenter.totalDocs,
      };
      document.getElementById('dashboard-home-status-chips').innerHTML = Object.entries(chips)
        .filter(([, value]) => value !== undefined && value !== null && value !== '')
        .map(([key, value]) => `<span class="chip"><strong>${escapeHtml(key)}</strong>: ${escapeHtml(value)}</span>`)
        .join('') || '<span class="chip">No status loaded.</span>';
    }
    function dashboardSections() {
      return Array.from(document.querySelectorAll('main section.dashboard-section'));
    }
    function initializeDashboardSectionControls() {
      dashboardSections().forEach((section) => {
        const heading = section.querySelector('h2');
        if (!heading || section.querySelector(':scope > .section-toggle')) {
          return;
        }
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'section-toggle';
        button.textContent = 'View';
        button.setAttribute('aria-label', `View ${heading.textContent}`);
        button.setAttribute('aria-expanded', 'true');
        button.onclick = () => {
          const collapsed = section.classList.toggle('collapsed');
          button.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        };
        heading.insertAdjacentElement('afterend', button);
      });
      const search = document.getElementById('dashboard-section-search');
      const expandAll = document.getElementById('dashboard-expand-all-button');
      const collapseAll = document.getElementById('dashboard-collapse-all-button');
      const clearFilter = document.getElementById('dashboard-clear-filter-button');
      search.oninput = () => filterDashboardSections(search.value);
      expandAll.onclick = () => setDashboardSectionsCollapsed(false);
      collapseAll.onclick = () => setDashboardSectionsCollapsed(true);
      clearFilter.onclick = () => {
        search.value = '';
        filterDashboardSections('');
      };
      filterDashboardSections(search.value || '');
      bindDashboardKeyboardShortcuts();
    }
    function isDashboardTypingTarget(target) {
      const tagName = target && target.tagName ? target.tagName.toLowerCase() : '';
      return tagName === 'input' || tagName === 'textarea' || tagName === 'select';
    }
    function clearDashboardSectionFilter() {
      const search = document.getElementById('dashboard-section-search');
      search.value = '';
      filterDashboardSections('');
    }
    function bindDashboardKeyboardShortcuts() {
      if (window.dashboardKeyboardShortcutsBound) {
        return;
      }
      window.dashboardKeyboardShortcutsBound = true;
      document.addEventListener('keydown', (event) => {
        const search = document.getElementById('dashboard-section-search');
        if (!search) {
          return;
        }
        if (event.key === 'Escape') {
          clearDashboardSectionFilter();
          return;
        }
        if (event.key === '/' && !isDashboardTypingTarget(event.target)) {
          event.preventDefault();
          search.focus();
          return;
        }
        if (isDashboardTypingTarget(event.target)) {
          return;
        }
        if (event.key.toLowerCase() === 'e') {
          setDashboardSectionsCollapsed(false);
        } else if (event.key.toLowerCase() === 'c') {
          setDashboardSectionsCollapsed(true);
        }
      });
    }
    function filterDashboardSections(query) {
      const normalized = String(query || '').trim().toLowerCase();
      let visibleCount = 0;
      dashboardSections().forEach((section) => {
        const haystack = [section.dataset.sectionTitle, section.dataset.sectionKeywords, section.querySelector('h2')?.textContent]
          .join(' ')
          .toLowerCase();
        const visible = !normalized || haystack.includes(normalized);
        section.classList.toggle('section-filter-hidden', !visible);
        if (visible) {
          visibleCount += 1;
        }
      });
      const status = document.getElementById('dashboard-section-filter-status');
      status.textContent = normalized
        ? `${visibleCount} dashboard sections match the current filter.`
        : 'Showing all dashboard sections.';
    }
    function setDashboardSectionsCollapsed(collapsed) {
      dashboardSections().forEach((section) => {
        section.classList.toggle('collapsed', collapsed);
        const button = section.querySelector(':scope > .section-toggle');
        if (button) {
          button.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        }
      });
    }
    async function loadVmValidationPrep() {
      const prep = await fetch('/vm-validation/prep').then((response) => response.json());
      document.getElementById('vm-validation-prep-status').textContent = JSON.stringify(prep, null, 2);
      renderVmValidationPrep(prep);
      bindVmValidationPrepControls();
    }
    function renderVmValidationPrep(prep) {
      const statusCounts = prep.countsByStatus || {};
      const values = {
        items: prep.checklistItemCount || 0,
        manual: statusCounts.manual || 0,
        warning: statusCounts.warning || 0,
      };
      document.getElementById('vm-validation-prep-counts').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
      const items = prep.items || [];
      document.getElementById('vm-validation-prep-list').innerHTML = items.length
        ? items.map((item) => `<div class="row">
            <strong>${escapeHtml(item.title || item.itemId)}</strong>
            <div><code>${escapeHtml(item.status)}</code> · ${escapeHtml(item.category || '')}</div>
            <div class="muted">${escapeHtml(item.summary || 'Manual prep metadata only.')}</div>
          </div>`).join('')
        : 'No VM validation prep checklist items found.';
    }
    function bindVmValidationPrepControls() {
      const refreshButton = document.getElementById('vm-validation-prep-refresh-button');
      refreshButton.onclick = async () => {
        refreshButton.disabled = true;
        await loadVmValidationPrep();
        refreshButton.disabled = false;
      };
    }
    async function loadBackupReadiness() {
      const readiness = await fetch('/backup/readiness').then((response) => response.json());
      document.getElementById('backup-readiness-status').textContent = JSON.stringify(readiness, null, 2);
      renderBackupReadiness(readiness);
      bindBackupReadinessControls();
    }
    function renderBackupReadiness(readiness) {
      const statusCounts = readiness.countsByStatus || {};
      const values = {
        items: readiness.checklistItemCount || 0,
        ready: statusCounts.ready || 0,
        manual: statusCounts.manual || 0,
        warning: statusCounts.warning || 0,
      };
      document.getElementById('backup-readiness-counts').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
      const items = readiness.items || [];
      document.getElementById('backup-readiness-list').innerHTML = items.length
        ? items.map((item) => `<div class="row">
            <strong>${escapeHtml(item.title || item.itemId)}</strong>
            <div><code>${escapeHtml(item.status)}</code> · ${escapeHtml(item.category || '')}</div>
            <div class="muted">${escapeHtml(item.summary || 'Manual checklist metadata only.')}</div>
          </div>`).join('')
        : 'No backup readiness checklist items found.';
    }
    function bindBackupReadinessControls() {
      const refreshButton = document.getElementById('backup-readiness-refresh-button');
      refreshButton.onclick = async () => {
        refreshButton.disabled = true;
        await loadBackupReadiness();
        refreshButton.disabled = false;
      };
    }
    async function loadActivityTimeline() {
      const timeline = await fetch('/activity/timeline').then((response) => response.json());
      document.getElementById('activity-timeline-status').textContent = JSON.stringify(timeline, null, 2);
      renderActivityTimeline(timeline);
      bindActivityTimelineControls();
    }
    function renderActivityTimeline(timeline) {
      const values = {
        recent: timeline.totalRecentItems || 0,
        types: Object.keys(timeline.countsByType || {}).length,
        statuses: Object.keys(timeline.countsByStatus || {}).length,
      };
      document.getElementById('activity-timeline-counts').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
      const items = timeline.items || [];
      document.getElementById('activity-timeline-list').innerHTML = items.length
        ? items.map((item) => `<div class="row">
            <strong>${escapeHtml(item.title || item.itemId)}</strong>
            <div><code>${escapeHtml(item.itemType)}</code> · status: <code>${escapeHtml(item.status)}</code> · ${escapeHtml(item.createdAt || '')}</div>
            <div class="muted">${escapeHtml(item.summary || 'Safe local activity metadata recorded.')}</div>
            <div><a href="/activity/timeline/${encodeURIComponent(item.itemId)}">Safe metadata</a></div>
          </div>`).join('')
        : 'No recent activity metadata found.';
    }
    function bindActivityTimelineControls() {
      const refreshButton = document.getElementById('activity-timeline-refresh-button');
      refreshButton.onclick = async () => {
        refreshButton.disabled = true;
        await loadActivityTimeline();
        refreshButton.disabled = false;
      };
    }
    async function loadDashboardSurfaceHealth() {
      const health = await fetch('/dashboard/surface-health').then((response) => response.json());
      document.getElementById('dashboard-surface-health-status').textContent = JSON.stringify(health, null, 2);
      renderDashboardSurfaceHealth(health);
      bindDashboardSurfaceHealthControls();
    }
    function renderDashboardSurfaceHealth(health) {
      const values = {
        total: health.totalSurfaces || 0,
        healthy: health.healthySurfaces || 0,
        warnings: health.warningCount || 0,
      };
      document.getElementById('dashboard-surface-health-counts').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
      const surfaces = health.surfaces || [];
      document.getElementById('dashboard-surface-health-list').innerHTML = surfaces.length
        ? surfaces.map((surface) => `<div class="row">
            <strong>${escapeHtml(surface.name || surface.surfaceId)}</strong>
            <div>Status: <code>${escapeHtml(surface.status)}</code> · Section: <code>${escapeHtml(surface.sectionId)}</code></div>
            <div class="muted">Warnings: ${escapeHtml((surface.warnings || []).join('; ') || 'No warnings.')}</div>
            <div><a href="/dashboard/surface-health/${encodeURIComponent(surface.surfaceId)}">Safe metadata</a></div>
          </div>`).join('')
        : 'No dashboard surfaces checked.';
    }
    function bindDashboardSurfaceHealthControls() {
      const refreshButton = document.getElementById('dashboard-surface-health-refresh-button');
      refreshButton.onclick = async () => {
        refreshButton.disabled = true;
        await loadDashboardSurfaceHealth();
        refreshButton.disabled = false;
      };
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
    function renderDocsCenter(center) {
      const counts = center.countsByCategory || {};
      const values = { total: center.totalDocs || 0, ...counts };
      document.getElementById('docs-center-counts').innerHTML = Object.entries(values).length
        ? Object.entries(values)
          .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
          .join('')
        : '<div class="metric"><span>docs</span><strong>0</strong></div>';
      const docs = center.recentDocs || [];
      document.getElementById('docs-center-list').innerHTML = docs.length
        ? docs.map((doc) => `<div class="row">
            <strong>${escapeHtml(doc.title || doc.filename)}</strong>
            <div><code>${escapeHtml(doc.category)}</code> · ${escapeHtml(doc.sizeBytes)} bytes · readable: <code>${doc.readable ? 'true' : 'false'}</code></div>
            <div class="muted">${escapeHtml(doc.summary || 'No safe summary available.')}</div>
            <div><a href="/docs/${encodeURIComponent(doc.docId)}">Safe doc</a> · <a href="/docs/${encodeURIComponent(doc.docId)}/metadata">Metadata</a></div>
          </div>`).join('')
        : 'No docs found.';
    }
    function bindDocsCenterControls() {
      const refreshButton = document.getElementById('docs-center-refresh-button');
      refreshButton.onclick = async () => {
        refreshButton.disabled = true;
        await loadDashboard();
        refreshButton.disabled = false;
      };
    }
    function renderLocalResearchAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        webBrowsing: agent.webBrowsing ? 'enabled' : 'disabled',
        connectors: agent.connectorExecution ? 'enabled' : 'disabled',
        fileMutation: agent.fileMutation ? 'enabled' : 'disabled',
      };
      document.getElementById('local-research-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderFileDataAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        rawPaths: agent.rawPathInputAccepted ? 'accepted' : 'rejected',
        protected: agent.protectedPatternsActive ? 'active' : 'inactive',
        mutation: agent.fileMutation ? 'enabled' : 'disabled',
      };
      document.getElementById('file-data-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalPlanningAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        tasks: agent.taskPersistence ? 'enabled' : 'disabled',
        reminders: agent.reminders ? 'enabled' : 'disabled',
      };
      document.getElementById('local-planning-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalDraftingAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        sending: agent.emailSending ? 'enabled' : 'disabled',
        persistence: agent.draftPersistence ? 'enabled' : 'disabled',
      };
      document.getElementById('local-drafting-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalReviewAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        persistence: agent.reviewPersistence ? 'enabled' : 'disabled',
        verification: agent.sourceValidation ? 'enabled' : 'disabled',
      };
      document.getElementById('local-review-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalDecisionAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        persistence: agent.decisionPersistence ? 'enabled' : 'disabled',
        verification: agent.externalVerification ? 'enabled' : 'disabled',
      };
      document.getElementById('local-decision-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalTroubleshootingAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        persistence: agent.ticketPersistence ? 'enabled' : 'disabled',
        commandExecution: agent.shellExecution ? 'enabled' : 'disabled',
      };
      document.getElementById('local-troubleshooting-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalSummarizationAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        persistence: agent.summaryPersistence ? 'enabled' : 'disabled',
        documentRetrieval: agent.documentRetrieval ? 'enabled' : 'disabled',
      };
      document.getElementById('local-summarization-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalExtractionAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        persistence: agent.extractionPersistence ? 'enabled' : 'disabled',
        taskCreation: agent.taskCreation ? 'enabled' : 'disabled',
      };
      document.getElementById('local-extraction-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalClassificationAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        persistence: agent.classificationPersistence ? 'enabled' : 'disabled',
        taskCreation: agent.taskCreation ? 'enabled' : 'disabled',
      };
      document.getElementById('local-classification-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalTransformationAgent(agent) {
      const values = {
        status: agent.status,
        mode: agent.mode,
        endpoint: agent.endpoint,
        responseOnly: agent.responseOnly ? 'true' : 'false',
        persistence: agent.transformationPersistence ? 'enabled' : 'disabled',
        exportCreation: agent.fileExportCreation ? 'enabled' : 'disabled',
      };
      document.getElementById('local-transformation-agent-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
    }
    function renderLocalResponseAgentsIndex(index) {
      const values = {
        status: index.status,
        agentCount: index.agentCount,
        expectedAgentCount: index.expectedAgentCount,
        addsAgents: index.addsAgents ? 'true' : 'false',
        addsEndpoint: index.addsEndpoint ? 'true' : 'false',
        mutation: index.mutation ? 'enabled' : 'disabled',
        certificationClaims: index.certificationClaims ? 'present' : 'absent',
      };
      document.getElementById('local-response-agents-index-summary').innerHTML = Object.entries(values)
        .map(([key, value]) => `<div class="metric"><span>${escapeHtml(key)}</span><strong>${escapeHtml(value)}</strong></div>`)
        .join('');
      const agents = Array.isArray(index.agents) ? index.agents : [];
      const groupedAgents = agents.reduce((groups, agent) => {
        const category = agent.category || 'Uncategorized';
        groups[category] = groups[category] || [];
        groups[category].push(agent);
        return groups;
      }, {});
      document.getElementById('local-response-agents-index-list').innerHTML = agents.length
        ? Object.entries(groupedAgents).map(([category, categoryAgents]) => `<div class="row stack">
            <h3>${escapeHtml(category)}</h3>
            ${categoryAgents.map((agent) => `<div class="row">
              <strong>${escapeHtml(agent.displayName || agent.name)}</strong>
              <div>
                <code>${escapeHtml(agent.agentId || '')}</code> ·
                <code>${escapeHtml(agent.status)}</code> ·
                <code>${escapeHtml(agent.responseMode)}</code>
              </div>
              <div>${(agent.badges || []).map((badge) => `<span class="pill">${escapeHtml(badge)}</span>`).join(' ')}</div>
              <div>Endpoint: <code>${escapeHtml(agent.endpoint)}</code></div>
              <div>Request template: <code>${escapeHtml(`/agents/local-response-agents/${agent.agentId || ''}/request-template`)}</code></div>
              <div>Mode: <code>${escapeHtml(agent.mode)}</code></div>
              <div>Output types: <code>${escapeHtml((agent.outputTypes || []).join(', '))}</code></div>
              <div class="muted">Use when: ${escapeHtml(agent.useWhen || agent.recommendedFor || '')}</div>
              <div><a href="${escapeHtml(agent.docsLink)}">Docs</a></div>
              <div class="muted">${escapeHtml((agent.safetyNotes || []).join(' '))}</div>
              <div><strong>Read-only example request body</strong></div>
              <pre class="local-response-agent-example">${escapeHtml(JSON.stringify(agent.exampleRequestBody || {}, null, 2))}</pre>
            </div>`).join('')}
          </div>`).join('')
        : 'No local response agents indexed.';
      const boundaries = Array.isArray(index.globalBoundaries) ? index.globalBoundaries : [];
      document.getElementById('local-response-agents-index-boundaries').innerHTML = boundaries.length
        ? `<strong>Global boundaries</strong><ul>${boundaries.map((boundary) => `<li>${escapeHtml(boundary)}</li>`).join('')}</ul>`
        : '<strong>Global boundaries</strong><div class="muted">No global boundaries listed.</div>';
    }
    function localResponseAgentEndpointParts(endpoint) {
      const parts = String(endpoint || '').trim().split(/\\s+/);
      return { method: parts[0] || '', path: parts[1] || '' };
    }
    function localResponseAgentAllowlist(agents) {
      return new Set((Array.isArray(agents) ? agents : [])
        .map((agent) => localResponseAgentEndpointParts(agent.endpoint))
        .filter((endpoint) => endpoint.method === 'POST' && endpoint.path.startsWith('/agents/'))
        .map((endpoint) => endpoint.path));
    }
    function localResponseAgentId(agent) {
      return agent && (agent.agentId || agent.agent_id || '');
    }
    function localResponseAgentName(agent) {
      return agent && (agent.displayName || agent.display_name || agent.name || 'Local response agent');
    }
    function localResponseAgentCategory(agent) {
      return agent && (agent.category || 'Uncategorized');
    }
    function localResponseAgentBadges(agent) {
      const badges = agent && (agent.badges || []);
      return Array.isArray(badges) && badges.length
        ? badges
        : ['Manual input only', 'Local only', 'Response only', 'No connector', 'Non-persistent'];
    }
    function localResponseAgentBoundaryFlags(agent) {
      return (agent && (agent.boundaryFlags || agent.boundary_flags)) || {};
    }
    function localResponseAgentExample(agent) {
      if (!agent) {
        return {};
      }
      if (agent.exampleRequestBody) {
        return agent.exampleRequestBody;
      }
      if (Array.isArray(agent.examples) && agent.examples.length) {
        return agent.examples[0] || {};
      }
      return {};
    }
    function localResponseAgentTemplatePath(agent) {
      const agentId = localResponseAgentId(agent);
      return agentId ? `/agents/local-response-agents/${encodeURIComponent(agentId)}/request-template` : '';
    }
    function renderLocalResponseAgentJson(target, value, fallbackText) {
      target.textContent = value ? JSON.stringify(value, null, 2) : fallbackText;
    }
    function localResponseAgentTemplateOutputTypes(template, agent) {
      const templateTypes = template && (template.supported_output_types || template.supportedOutputTypes || template.output_types || template.outputTypes);
      const agentTypes = agent && (agent.outputTypes || agent.output_types);
      const defaultType = template && (template.default_output_type || template.defaultOutputType || template.output_type || template.outputType);
      const types = []
        .concat(Array.isArray(templateTypes) ? templateTypes : [])
        .concat(defaultType ? [defaultType] : [])
        .concat(Array.isArray(agentTypes) ? agentTypes : []);
      return Array.from(new Set(types.map((type) => String(type || '').trim()).filter(Boolean)));
    }
    function selectedOutputTypeField(payload) {
      const knownFields = [
        'output_type',
        'outputType',
        'desired_output_type',
        'desiredOutputType',
        'summary_type',
        'summaryType',
        'review_type',
        'reviewType',
        'classification_type',
        'classificationType',
        'extraction_type',
        'extractionType',
        'target_format',
        'targetFormat',
      ];
      return knownFields.find((field) => payload && Object.prototype.hasOwnProperty.call(payload, field)) || 'output_type';
    }
    function localResponseAgentPayloadWithSelectedOutputType(payload, outputType) {
      const nextPayload = payload && typeof payload === 'object' && !Array.isArray(payload) ? { ...payload } : {};
      if (outputType) {
        nextPayload[selectedOutputTypeField(nextPayload)] = outputType;
      }
      return nextPayload;
    }
    function localResponseAgentFieldLabel(key) {
      return String(key || '')
        .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (letter) => letter.toUpperCase());
    }
    function renderLocalResponseValue(value) {
      if (value === null || value === undefined || value === '') {
        return '<div class="muted">No value returned.</div>';
      }
      if (Array.isArray(value)) {
        return value.length
          ? `<ul>${value.map((item) => `<li>${renderLocalResponseValue(item)}</li>`).join('')}</ul>`
          : '<div class="muted">No items returned.</div>';
      }
      if (typeof value === 'object') {
        return `<pre>${escapeHtml(JSON.stringify(value, null, 2))}</pre>`;
      }
      return `<div>${escapeHtml(String(value))}</div>`;
    }
    function localResponseKnownValue(responseBody, key) {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
      return responseBody && Object.prototype.hasOwnProperty.call(responseBody, key)
        ? responseBody[key]
        : responseBody && Object.prototype.hasOwnProperty.call(responseBody, camelKey)
          ? responseBody[camelKey]
          : undefined;
    }
    function renderStructuredLocalResponse(target, responseBody) {
      const fields = [
        'title',
        'summary',
        'assumptions',
        'recommended_plan',
        'step_by_step',
        'checklist',
        'next_actions',
        'priority_order',
        'recommended_agents',
        'risk_flags',
        'safety_notes',
        'limitations',
        'local_only_boundaries',
        'follow_up_questions',
        'source_evidence',
        'citation_labels',
        'source_quality_warnings',
        'source_recency_notes',
        'source_context_summary',
        'sources_used',
        'web_context_limitations',
        'source_use_summary',
        'source_supported_points',
        'source_cautions',
        'source_followup_checks',
        'source_informed_assumptions',
        'citation_usage_note',
        'prior_context_used',
        'prior_context_summary',
        'prior_context',
        'prior_context_limitations',
        'output_type',
        'agent_id',
      ];
      const usedKeys = new Set(fields.flatMap((field) => [field, field.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())]));
      const rows = fields
        .map((field) => [field, localResponseKnownValue(responseBody, field)])
        .filter(([, value]) => value !== undefined)
        .map(([field, value]) => `<div class="row stack"><strong>${escapeHtml(localResponseAgentFieldLabel(field))}</strong>${renderLocalResponseValue(value)}</div>`);
      const additional = responseBody && typeof responseBody === 'object' && !Array.isArray(responseBody)
        ? Object.fromEntries(Object.entries(responseBody).filter(([key]) => !usedKeys.has(key)))
        : {};
      const additionalRows = Object.keys(additional).length
        ? `<details><summary>Raw JSON for unknown fields</summary><pre>${escapeHtml(JSON.stringify(additional, null, 2))}</pre></details>`
        : '';
      target.className = 'row stack';
      target.innerHTML = rows.length
        ? rows.join('') + additionalRows
        : '<div class="muted">Local response returned no common display fields. Raw JSON remains visible below.</div>' + additionalRows;
    }
    function renderWorkbenchError(target, title, message, details) {
      target.className = 'row stack';
      target.innerHTML = `
        <div><strong>${escapeHtml(title)}</strong></div>
        <div class="muted">${escapeHtml(message)}</div>
        ${details ? `<pre>${escapeHtml(JSON.stringify(details, null, 2))}</pre>` : ''}
      `;
    }
    function initializeLocalResponseAgentsWorkbench(index) {
      const agents = Array.isArray(index && index.agents) ? index.agents : [];
      const allowlistedEndpointPaths = localResponseAgentAllowlist(agents);
      const select = document.getElementById('local-response-agents-workbench-select');
      const categorySelect = document.getElementById('local-response-agents-category-select');
      const categoryCounts = document.getElementById('local-response-agents-category-counts');
      const discoveryStatus = document.getElementById('local-response-agents-discovery-status');
      const detailPanel = document.getElementById('local-response-agents-detail-panel');
      const boundaryFlagsPanel = document.getElementById('local-response-agents-boundary-flags');
      const templateStatus = document.getElementById('local-response-agents-template-status');
      const templateOutput = document.getElementById('local-response-agents-request-template');
      const samplePayloadOutput = document.getElementById('local-response-agents-sample-payload');
      const useSampleButton = document.getElementById('local-response-agents-use-sample-button');
      const routePreviewInput = document.getElementById('local-response-agents-route-preview-input');
      const routePreviewButton = document.getElementById('local-response-agents-route-preview-button');
      const routePreviewStatus = document.getElementById('local-response-agents-route-preview-status');
      const routePreviewSuggestions = document.getElementById('local-response-agents-route-preview-suggestions');
      const routePreviewResult = document.getElementById('local-response-agents-route-preview-result');
      const manualWorkflowGoal = document.getElementById('local-response-agents-manual-workflow-goal');
      const manualWorkflowCandidates = document.getElementById('local-response-agents-manual-workflow-candidates');
      const manualWorkflowIncludeWebContext = document.getElementById('local-response-agents-manual-workflow-include-web-context');
      const manualWorkflowPreviewButton = document.getElementById('local-response-agents-manual-workflow-preview-button');
      const manualWorkflowLoadStepButton = document.getElementById('local-response-agents-manual-workflow-load-step-button');
      const priorContextCopyButton = document.getElementById('local-response-agents-prior-context-copy-button');
      const manualWorkflowStatus = document.getElementById('local-response-agents-manual-workflow-status');
      const manualWorkflowSteps = document.getElementById('local-response-agents-manual-workflow-steps');
      const manualWorkflowResult = document.getElementById('local-response-agents-manual-workflow-result');
      const endpointDisplay = document.getElementById('local-response-agents-workbench-endpoint');
      const docsLink = document.getElementById('local-response-agents-workbench-docs');
      const outputTypeSelect = document.getElementById('local-response-agents-output-type-select');
      const payloadPreviewStatus = document.getElementById('local-response-agents-payload-preview-status');
      const bodyInput = document.getElementById('local-response-agents-workbench-body');
      const runButton = document.getElementById('local-response-agents-workbench-run-button');
      const status = document.getElementById('local-response-agents-workbench-status');
      const structuredResponse = document.getElementById('local-response-agents-structured-response');
      const responseOutput = document.getElementById('local-response-agents-workbench-response');
      const sessionBoardAddButton = document.getElementById('local-response-agents-session-board-add-button');
      const sessionBoardCompareButton = document.getElementById('local-response-agents-session-board-compare-button');
      const sessionBoardPacketButton = document.getElementById('local-response-agents-session-board-packet-button');
      const sessionBoardInsertEntryButton = document.getElementById('local-response-agents-session-board-insert-entry-button');
      const sessionBoardInsertPacketButton = document.getElementById('local-response-agents-session-board-insert-packet-button');
      const sessionBoardClearButton = document.getElementById('local-response-agents-session-board-clear-button');
      const sessionBoardStatus = document.getElementById('local-response-agents-session-board-status');
      const sessionBoardEntries = document.getElementById('local-response-agents-session-board-entries');
      const resultComparisonBody = document.getElementById('local-response-agents-result-comparison-body');
      const reviewPacketOutput = document.getElementById('local-response-agents-review-packet-output');
      const webResearchEnabled = document.getElementById('local-response-agents-web-research-enabled');
      const webResearchUrls = document.getElementById('local-response-agents-web-research-urls');
      const webResearchValidateButton = document.getElementById('local-response-agents-web-research-validate-button');
      const webResearchFetchButton = document.getElementById('local-response-agents-web-research-fetch-button');
      const webResearchContextButton = document.getElementById('local-response-agents-web-research-context-button');
      const webResearchAddButton = document.getElementById('local-response-agents-web-research-add-button');
      const webResearchStatus = document.getElementById('local-response-agents-web-research-status');
      const webResearchResult = document.getElementById('local-response-agents-web-research-result');
      const reviewedWebContextPreview = document.getElementById('local-response-agents-reviewed-web-context-preview');
      const reviewedSourceList = document.getElementById('local-response-agents-reviewed-source-list');
      const reviewedSourceClearButton = document.getElementById('local-response-agents-reviewed-source-clear-button');
      const sourceAwarePreviewBody = document.getElementById('local-response-agents-source-aware-preview-body');
      const commandSearch = document.getElementById('local-response-agents-command-search');
      const commandCategory = document.getElementById('local-response-agents-command-category');
      const commandCount = document.getElementById('local-response-agents-command-count');
      const commandList = document.getElementById('local-response-agents-command-list');
      const pinnedList = document.getElementById('local-response-agents-pinned-list');
      const recentList = document.getElementById('local-response-agents-recent-list');
      const highStakesBanner = document.getElementById('local-response-agents-high-stakes-banner');
      const playbookList = document.getElementById('local-response-agents-playbook-list');
      const playbookStatus = document.getElementById('local-response-agents-playbook-status');
      const playbookPreview = document.getElementById('local-response-agents-playbook-preview');
      const contextFields = {
        goal: document.getElementById('local-response-agents-context-goal'),
        background: document.getElementById('local-response-agents-context-background'),
        constraints: document.getElementById('local-response-agents-context-constraints'),
        preferences: document.getElementById('local-response-agents-context-preferences'),
        evidence: document.getElementById('local-response-agents-context-evidence'),
        priorSummary: document.getElementById('local-response-agents-context-prior-summary'),
        decisionCriteria: document.getElementById('local-response-agents-context-decision-criteria'),
        risks: document.getElementById('local-response-agents-context-risks'),
      };
      const contextInsertRequestButton = document.getElementById('local-response-agents-context-insert-request-button');
      const contextInsertPriorButton = document.getElementById('local-response-agents-context-insert-prior-button');
      const contextStatus = document.getElementById('local-response-agents-context-status');
      const contextPreview = document.getElementById('local-response-agents-context-preview');
      const qualityChecklist = document.getElementById('local-response-agents-quality-checklist');
      const qualityWarnings = document.getElementById('local-response-agents-quality-warnings');
      const groupedAgents = agents.reduce((groups, agent) => {
        const category = localResponseAgentCategory(agent);
        groups[category] = groups[category] || [];
        groups[category].push(agent);
        return groups;
      }, {});
      const categories = Object.keys(groupedAgents);
      let activeAgents = agents.slice();
      let selectedTemplate = null;
      let latestWebResearchSources = [];
      let latestManualWorkflowSteps = [];
      let latestLocalResponseBody = null;
      let latestLocalResponseAgent = null;
      let sessionResultBoard = [];
      let sessionResultBoardSequence = 1;
      let latestReviewPacketText = '';
      let pinnedAgentIds = [];
      let recentAgentIds = [];
      let selectedPlaybook = null;

      categoryCounts.innerHTML = categories.length
        ? categories.map((category) => `<div><strong>${escapeHtml(category)}</strong>: ${escapeHtml(groupedAgents[category].length)} local response agents</div>`).join('')
        : '<div>No category metadata available.</div>';
      categorySelect.innerHTML = ['<option value="__all__">All categories (37)</option>']
        .concat(categories.map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)} (${escapeHtml(groupedAgents[category].length)})</option>`))
        .join('');
      commandCategory.innerHTML = ['<option value="__all__">All categories (37)</option>']
        .concat(categories.map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)} (${escapeHtml(groupedAgents[category].length)})</option>`))
        .join('');

      function renderAgentOptions() {
        activeAgents = categorySelect.value === '__all__'
          ? agents.slice()
          : (groupedAgents[categorySelect.value] || []);
        select.innerHTML = activeAgents.length
          ? activeAgents.map((agent, index) => `<option value="${escapeHtml(index)}">${escapeHtml(localResponseAgentCategory(agent))} - ${escapeHtml(localResponseAgentName(agent))}</option>`).join('')
          : '<option value="0">No local response agents in this category</option>';
      }
      async function loadDiscoveryCatalogMetadata() {
        discoveryStatus.textContent = `Dashboard summary includes ${agents.length} of 37 expected local response agents.`;
        try {
          const catalog = await fetch('/agents/local-response-agents/catalog').then((response) => response.json());
          const count = catalog.agentCount || catalog.agent_count || 0;
          const expected = catalog.expectedAgentCount || catalog.expected_agent_count || 37;
          discoveryStatus.textContent = `Discovery catalog includes ${count} of ${expected} expected local response agents.`;
        } catch {
          discoveryStatus.textContent = `Discovery catalog endpoint unavailable; dashboard summary includes ${agents.length} of 37 expected local response agents.`;
        }
      }
      async function loadCategoryMetadata() {
        try {
          const categoryMetadata = await fetch('/agents/local-response-agents/categories').then((response) => response.json());
          const categoryRows = Array.isArray(categoryMetadata.categories) ? categoryMetadata.categories : [];
          categoryCounts.innerHTML = categoryRows.length
            ? categoryRows.map((category) => `<div><strong>${escapeHtml(category.name)}</strong>: ${escapeHtml(category.count)} local response agents</div>`).join('')
            : categoryCounts.innerHTML;
          if (categoryMetadata.totalCount || categoryMetadata.total_count) {
            const total = categoryMetadata.totalCount || categoryMetadata.total_count;
            categoryCounts.innerHTML += `<div class="muted">Category count total: ${escapeHtml(total)} of 37 expected local response agents.</div>`;
          }
        } catch {
          categoryCounts.innerHTML += '<div class="muted">Category endpoint unavailable; using dashboard summary metadata.</div>';
        }
      }

      function selectedAgent() {
        const index = Number(select.value || 0);
        return activeAgents[index] || null;
      }
      function localResponseAgentSearchText(agent) {
        if (!agent) {
          return '';
        }
        return [
          localResponseAgentId(agent),
          localResponseAgentName(agent),
          localResponseAgentCategory(agent),
          agent.description,
          agent.endpoint,
          agent.docsLink || agent.docs_link,
          agent.useWhen || agent.use_when,
          agent.recommendedFor || agent.recommended_for,
          (agent.badges || []).join(' '),
          (agent.tags || []).join(' '),
          (agent.outputTypes || agent.output_types || []).join(' '),
          (agent.safetyNotes || agent.safety_notes || []).join(' '),
          JSON.stringify(agent.exampleRequestBody || agent.example_request_body || {}),
        ].join(' ').toLowerCase();
      }
      const highStakesTerms = [
        'health',
        'fitness',
        'medical',
        'legal',
        'immigration',
        'finance',
        'loans',
        'budget',
        'emergency',
        'preparedness',
        'security',
        'safety',
        'career',
        'job search',
        'housing',
        'move',
        'travel',
      ];
      function matchingHighStakesTerms(text) {
        const haystack = String(text || '').toLowerCase();
        return highStakesTerms.filter((term) => haystack.includes(term));
      }
      function selectedHighStakesTerms() {
        const agentTerms = matchingHighStakesTerms(localResponseAgentSearchText(selectedAgent()));
        const playbookTerms = selectedPlaybook ? matchingHighStakesTerms(`${selectedPlaybook.title} ${selectedPlaybook.category} ${selectedPlaybook.goal}`) : [];
        return Array.from(new Set(agentTerms.concat(playbookTerms)));
      }
      function selectAgentById(agentId) {
        const agentIndex = agents.findIndex((agent) => localResponseAgentId(agent) === agentId);
        if (agentIndex < 0) {
          return false;
        }
        categorySelect.value = '__all__';
        renderAgentOptions();
        select.value = String(agentIndex);
        return true;
      }
      function trackRecentAgent(agent) {
        const agentId = localResponseAgentId(agent);
        if (!agentId) {
          return;
        }
        recentAgentIds = [agentId].concat(recentAgentIds.filter((id) => id !== agentId)).slice(0, 6);
        renderPinnedAndRecentAgents();
      }
      function agentById(agentId) {
        return agents.find((agent) => localResponseAgentId(agent) === agentId) || null;
      }
      function renderSessionAgentList(agentIds, emptyText) {
        const rows = agentIds.map(agentById).filter(Boolean);
        return rows.length
          ? rows.map((agent) => `
            <div class="row stack">
              <div><strong>${escapeHtml(localResponseAgentName(agent))}</strong></div>
              <div><code>${escapeHtml(localResponseAgentId(agent))}</code> · ${escapeHtml(localResponseAgentCategory(agent))}</div>
              <div class="actions">
                <button type="button" data-command-action="use" data-agent-id="${escapeHtml(localResponseAgentId(agent))}">Use agent</button>
                <button type="button" data-command-action="pin" data-agent-id="${escapeHtml(localResponseAgentId(agent))}">${pinnedAgentIds.includes(localResponseAgentId(agent)) ? 'Unpin' : 'Pin'}</button>
              </div>
            </div>
          `).join('')
          : emptyText;
      }
      function renderPinnedAndRecentAgents() {
        pinnedList.className = pinnedAgentIds.length ? 'compact-list' : 'compact-list muted';
        recentList.className = recentAgentIds.length ? 'compact-list' : 'compact-list muted';
        pinnedList.innerHTML = renderSessionAgentList(pinnedAgentIds, 'No pinned agents in this session.');
        recentList.innerHTML = renderSessionAgentList(recentAgentIds, 'No recent agents in this session.');
        bindCommandButtons(pinnedList);
        bindCommandButtons(recentList);
      }
      function commandCenterVisibleAgents() {
        const query = (commandSearch.value || '').trim().toLowerCase();
        const selectedCategory = commandCategory.value || '__all__';
        return agents.filter((agent) => {
          const inCategory = selectedCategory === '__all__' || localResponseAgentCategory(agent) === selectedCategory;
          const text = localResponseAgentSearchText(agent);
          return inCategory && (!query || text.includes(query));
        });
      }
      function renderCommandCenter() {
        const visibleAgents = commandCenterVisibleAgents();
        commandCount.textContent = `Showing ${visibleAgents.length} of 37 agents.`;
        commandList.className = visibleAgents.length ? 'compact-list' : 'compact-list muted';
        commandList.innerHTML = visibleAgents.length
          ? visibleAgents.slice(0, 37).map((agent) => {
              const agentId = localResponseAgentId(agent);
              const pinned = pinnedAgentIds.includes(agentId);
              return `
                <div class="row stack">
                  <div><strong>${escapeHtml(localResponseAgentName(agent))}</strong></div>
                  <div><code>${escapeHtml(agentId)}</code> · ${escapeHtml(localResponseAgentCategory(agent))}</div>
                  <div class="muted">${escapeHtml(agent.useWhen || agent.use_when || agent.recommendedFor || agent.recommended_for || '')}</div>
                  <div class="actions">
                    <button type="button" data-command-action="use" data-agent-id="${escapeHtml(agentId)}">Use agent</button>
                    <button type="button" data-command-action="sample" data-agent-id="${escapeHtml(agentId)}">Insert template/example</button>
                    <button type="button" data-command-action="prior" data-agent-id="${escapeHtml(agentId)}">Add with prior_agent_context</button>
                    <button type="button" data-command-action="pin" data-agent-id="${escapeHtml(agentId)}">${pinned ? 'Unpin' : 'Pin'}</button>
                    <button type="button" data-command-action="focus" data-agent-id="${escapeHtml(agentId)}">Focus composer</button>
                  </div>
                </div>
              `;
            }).join('')
          : 'No existing agents match the current command-center filter.';
        bindCommandButtons(commandList);
        renderPinnedAndRecentAgents();
        updateReadinessUi();
      }
      async function handleCommandAction(action, agentId) {
        const agent = agentById(agentId);
        if (!agent && action !== 'pin') {
          return;
        }
        if (action === 'pin') {
          pinnedAgentIds = pinnedAgentIds.includes(agentId)
            ? pinnedAgentIds.filter((id) => id !== agentId)
            : [agentId].concat(pinnedAgentIds).slice(0, 8);
          renderCommandCenter();
          return;
        }
        if (!selectAgentById(agentId)) {
          return;
        }
        trackRecentAgent(agent);
        await loadSelectedExample();
        if (action === 'sample') {
          applySamplePayloadToComposer(selectedTemplate, selectedAgent());
          payloadPreviewStatus.textContent = 'Template/example inserted by manual Command Center action. No agent was invoked.';
        }
        if (action === 'prior') {
          const inserted = insertContextKitAsPriorContext('prior_agent_context inserted from the session-only context kit. No agent was invoked.');
          if (!inserted) {
            contextStatus.textContent = 'Agent selected. Add context kit text before inserting prior_agent_context.';
            contextFields.priorSummary.focus();
          }
        }
        if (action === 'focus' || action === 'use' || action === 'sample') {
          bodyInput.focus();
        }
        updateReadinessUi();
      }
      function bindCommandButtons(container) {
        container.querySelectorAll('button[data-command-action]').forEach((button) => {
          button.onclick = async () => {
            await handleCommandAction(button.getAttribute('data-command-action'), button.getAttribute('data-agent-id'));
          };
        });
      }
      const responseAgentPlaybooks = [
        { id: 'school_robotics', title: 'School / robotics planning', category: 'school robotics planning', goal: 'Plan a school or robotics project with review and next-step support.', terms: ['school', 'robotics', 'planning', 'review', 'summarization'] },
        { id: 'career_package', title: 'Career / job search package', category: 'career job search', goal: 'Draft, review, and compare career material manually.', terms: ['career', 'job', 'drafting', 'review', 'decision'] },
        { id: 'housing_move_travel', title: 'Housing / move / travel decision', category: 'housing move travel', goal: 'Compare options, constraints, timelines, and reviewed source notes.', terms: ['housing', 'move', 'travel', 'decision', 'planning'] },
        { id: 'finance_budget', title: 'Finance / loans / budget review', category: 'finance loans budget', goal: 'Organize budget assumptions, risks, and review questions.', terms: ['finance', 'loan', 'budget', 'decision', 'review'] },
        { id: 'project_portfolio', title: 'Project / portfolio review', category: 'project portfolio review', goal: 'Summarize, review, and polish a project or portfolio package.', terms: ['project', 'portfolio', 'summarization', 'review', 'transformation'] },
        { id: 'health_fitness', title: 'Health / fitness planning', category: 'health fitness', goal: 'Draft a reviewed fitness or wellness plan with high-stakes cautions.', terms: ['health', 'fitness', 'planning', 'review', 'safety'] },
        { id: 'emergency_preparedness', title: 'Emergency / preparedness planning', category: 'emergency preparedness safety', goal: 'Build a manual preparedness checklist and risk review.', terms: ['emergency', 'preparedness', 'safety', 'planning', 'extraction'] },
        { id: 'networking_social', title: 'High-class / networking / social polish', category: 'networking social polish', goal: 'Draft and refine social or networking messages manually.', terms: ['networking', 'social', 'drafting', 'review', 'transformation'] },
        { id: 'personal_admin', title: 'Personal admin / documents review', category: 'personal admin documents', goal: 'Extract, review, and summarize admin details from user-provided text.', terms: ['personal', 'admin', 'document', 'extraction', 'summarization'] },
        { id: 'life_dashboard', title: 'Life dashboard / cross-agent synthesis', category: 'life dashboard synthesis', goal: 'Synthesize goals, decisions, risks, and next manual steps across agents.', terms: ['life', 'dashboard', 'synthesis', 'planning', 'decision', 'summarization'] },
      ];
      function scoreAgentForTerms(agent, terms) {
        const text = localResponseAgentSearchText(agent);
        return terms.reduce((score, term) => score + (text.includes(String(term).toLowerCase()) ? 1 : 0), 0);
      }
      function playbookAgents(playbook) {
        const scored = agents
          .map((agent) => ({ agent, score: scoreAgentForTerms(agent, playbook.terms) }))
          .filter((item) => item.score > 0)
          .sort((left, right) => right.score - left.score || localResponseAgentName(left.agent).localeCompare(localResponseAgentName(right.agent)));
        const chosen = scored.map((item) => item.agent).slice(0, 4);
        if (chosen.length) {
          return chosen;
        }
        return agents.slice(0, 4);
      }
      function renderPlaybooks() {
        playbookList.innerHTML = responseAgentPlaybooks.map((playbook) => `
          <div class="row stack">
            <strong>${escapeHtml(playbook.title)}</strong>
            <div class="muted">${escapeHtml(playbook.goal)}</div>
            <div><span class="pill">Manual</span> <span class="pill">Response-only</span> <span class="pill">Session-only preview</span></div>
            <div class="actions">
              <button type="button" data-playbook-id="${escapeHtml(playbook.id)}" data-playbook-action="preview">Preview preset</button>
              <button type="button" data-playbook-id="${escapeHtml(playbook.id)}" data-playbook-action="load">Load into manual builder</button>
            </div>
          </div>
        `).join('');
        playbookList.querySelectorAll('button[data-playbook-id]').forEach((button) => {
          button.onclick = () => handlePlaybookAction(button.getAttribute('data-playbook-id'), button.getAttribute('data-playbook-action'));
        });
      }
      function playbookPreviewText(playbook, chosenAgents) {
        const lines = [
          playbook.title,
          '',
          'Manual response-only preset. No agent is run, no chain is started, no handoff is created, and nothing is persisted.',
          '',
          `Goal: ${playbook.goal}`,
          '',
          'Suggested existing-agent sequence:',
        ];
        chosenAgents.forEach((agent, index) => {
          lines.push(`${index + 1}. ${localResponseAgentName(agent)} (${localResponseAgentId(agent)}) - ${localResponseAgentCategory(agent)}`);
        });
        lines.push('', 'Context steps:');
        lines.push('- Fill the session-only Context Kit Builder.');
        lines.push('- Insert reviewed context into the editable request payload or prior_agent_context.');
        lines.push('- Run one selected agent manually only when ready.');
        lines.push('- Review output before using it in another manual step.');
        return lines.join('\n');
      }
      function handlePlaybookAction(playbookId, action) {
        const playbook = responseAgentPlaybooks.find((item) => item.id === playbookId);
        if (!playbook) {
          return;
        }
        selectedPlaybook = playbook;
        const chosenAgents = playbookAgents(playbook);
        const chosenIds = chosenAgents.map(localResponseAgentId).filter(Boolean);
        playbookPreview.textContent = playbookPreviewText(playbook, chosenAgents);
        playbookStatus.textContent = `${playbook.title} preview uses ${chosenIds.length} existing local response agents. Manual only - not executed, not chained, and not persisted.`;
        manualWorkflowGoal.value = playbook.goal;
        manualWorkflowCandidates.value = chosenIds.join('\n');
        if (action === 'load' && chosenIds[0] && selectAgentById(chosenIds[0])) {
          loadSelectedExample();
        }
        updateReadinessUi();
      }
      function contextKitText() {
        const sections = [
          ['Goal', contextFields.goal.value],
          ['Situation/background', contextFields.background.value],
          ['Constraints', contextFields.constraints.value],
          ['Preferences', contextFields.preferences.value],
          ['Evidence/source notes', contextFields.evidence.value],
          ['Prior agent output summary', contextFields.priorSummary.value],
          ['Decision criteria', contextFields.decisionCriteria.value],
          ['Risks or high-stakes concerns', contextFields.risks.value],
        ].map(([label, value]) => [label, String(value || '').trim()]);
        const lines = ['Session-only context kit', 'Not saved. Review before inserting into a manual request.', ''];
        sections.forEach(([label, value]) => {
          if (value) {
            lines.push(`${label}:`, value, '');
          }
        });
        return lines.join('\n').trim();
      }
      function renderContextKitPreview() {
        const text = contextKitText();
        contextPreview.textContent = text || 'No context kit content yet.';
        updateReadinessUi();
      }
      function readPayloadObject(statusTarget) {
        try {
          const parsedBody = JSON.parse(bodyInput.value || '{}');
          if (!parsedBody || Array.isArray(parsedBody) || typeof parsedBody !== 'object') {
            statusTarget.textContent = 'Editable payload must be a JSON object before inserting context.';
            return null;
          }
          return parsedBody;
        } catch (error) {
          statusTarget.textContent = `Context was not inserted: invalid editable payload JSON (${error.message}).`;
          return null;
        }
      }
      function insertContextKitIntoRequest() {
        const text = contextKitText();
        if (!text) {
          contextStatus.textContent = 'Add context kit text before inserting it into the request payload.';
          return;
        }
        const parsedBody = readPayloadObject(contextStatus);
        if (!parsedBody) {
          return;
        }
        const requestField = ['request', 'prompt', 'user_request', 'userRequest', 'text', 'input', 'content', 'instructions']
          .find((field) => Object.prototype.hasOwnProperty.call(parsedBody, field));
        if (requestField) {
          parsedBody[requestField] = [parsedBody[requestField], '', text].map((value) => String(value || '').trim()).filter(Boolean).join('\n\n');
        } else {
          parsedBody.request = text;
        }
        bodyInput.value = JSON.stringify(parsedBody, null, 2);
        contextStatus.textContent = 'Context kit inserted into the editable request payload. No agent was invoked.';
        renderReviewedWebContextPreview();
        updateReadinessUi();
      }
      function contextKitPriorContext() {
        const text = contextKitText();
        if (!text) {
          return null;
        }
        return {
          previous_agent_id: 'session_context_kit',
          previous_agent_name: 'Session-only Context Kit',
          previous_output_type: 'manual_context',
          previous_summary: text.slice(0, 4000),
          previous_key_points: [
            contextFields.goal.value,
            contextFields.decisionCriteria.value,
            contextFields.evidence.value,
          ].map((value) => String(value || '').trim()).filter(Boolean).slice(0, 10),
          previous_next_actions: [],
          previous_limitations: [
            'Created manually in the current dashboard page.',
            'Not persisted.',
            'Review before using as prior_agent_context.',
          ],
          user_notes: text.slice(0, 4000),
          source_type: 'manual_session_context_kit',
        };
      }
      function insertContextKitAsPriorContext(successText) {
        const context = contextKitPriorContext();
        if (!context) {
          contextStatus.textContent = 'Add context kit text before inserting prior_agent_context.';
          return false;
        }
        const parsedBody = readPayloadObject(contextStatus);
        if (!parsedBody) {
          return false;
        }
        parsedBody.prior_agent_context = context;
        bodyInput.value = JSON.stringify(parsedBody, null, 2);
        contextStatus.textContent = successText || 'Context kit inserted as prior_agent_context. No agent was invoked.';
        renderReviewedWebContextPreview();
        updateReadinessUi();
        return true;
      }
      function payloadReadinessSnapshot() {
        let parsedBody = null;
        try {
          parsedBody = JSON.parse(bodyInput.value || '{}');
        } catch {
          parsedBody = null;
        }
        const payloadText = parsedBody && typeof parsedBody === 'object' && !Array.isArray(parsedBody)
          ? JSON.stringify(parsedBody).toLowerCase()
          : String(bodyInput.value || '').toLowerCase();
        const requestText = [
          parsedBody && (parsedBody.request || parsedBody.prompt || parsedBody.user_request || parsedBody.userRequest || parsedBody.text || parsedBody.input),
          contextKitText(),
        ].map((value) => String(value || '')).join(' ').trim();
        const hasGoal = /\b(goal|objective|trying to|need to|want to)\b/i.test(requestText) || Boolean(contextFields.goal.value.trim());
        const hasConstraints = /\b(constraint|must|cannot|avoid|deadline|budget|limit)\b/i.test(requestText) || Boolean(contextFields.constraints.value.trim());
        const hasPrior = parsedBody && typeof parsedBody === 'object' && !Array.isArray(parsedBody) && Boolean(parsedBody.prior_agent_context || parsedBody.priorAgentContext);
        const hasWebContext = parsedBody && typeof parsedBody === 'object' && !Array.isArray(parsedBody) && Array.isArray(parsedBody.web_context) && parsedBody.web_context.length > 0;
        return { parsedBody, payloadText, requestText, hasGoal, hasConstraints, hasPrior, hasWebContext };
      }
      function updateHighStakesBanner() {
        const terms = selectedHighStakesTerms();
        highStakesBanner.hidden = terms.length === 0;
        if (terms.length) {
          highStakesBanner.innerHTML = `
            <strong>High-stakes manual review reminder</strong>
            <div>Detected category: ${escapeHtml(terms.join(', '))}</div>
            <div>Response-only guidance. Manual review is required. Verify important details before acting. No professional, legal, medical, or financial decision automation is provided, and no external actions are taken.</div>
          `;
        }
      }
      function updateReadinessUi() {
        if (!qualityChecklist || !qualityWarnings) {
          return;
        }
        const snapshot = payloadReadinessSnapshot();
        const terms = selectedHighStakesTerms();
        const checks = [
          ['Agent selected', Boolean(selectedAgent())],
          ['Manual request/prompt present', snapshot.requestText.length > 0],
          ['Request has enough detail', snapshot.requestText.length >= 80],
          ['Goal appears present', snapshot.hasGoal],
          ['Constraints appear present', snapshot.hasConstraints],
          ['prior_agent_context empty/included', true, snapshot.hasPrior ? 'included' : 'empty'],
          ['reviewed web_context/source context none/included', true, snapshot.hasWebContext ? 'included' : 'none'],
          ['High-stakes category warning status', true, terms.length ? `shown for ${terms.join(', ')}` : 'not detected'],
          ['Local-only/manual-only reminder', true, 'visible'],
        ];
        qualityChecklist.innerHTML = checks.map(([label, ok, detail]) => `
          <div class="${ok ? 'check-ok' : 'check-warn'}">${ok ? 'OK' : 'Review'} - ${escapeHtml(label)}${detail ? `: ${escapeHtml(detail)}` : ''}</div>
        `).join('');
        const warnings = [];
        if (!snapshot.requestText) {
          warnings.push('Add a manual request or context kit before using an agent.');
        } else if (snapshot.requestText.length < 80) {
          warnings.push('Request may be too short or vague; add situation, desired output, and decision criteria.');
        }
        if (!snapshot.hasGoal) {
          warnings.push('Goal is not obvious; add the outcome you want.');
        }
        if (!snapshot.hasConstraints) {
          warnings.push('Constraints are not obvious; add limits, preferences, budget, deadline, or must-avoid notes.');
        }
        if (terms.length && !snapshot.hasWebContext) {
          warnings.push('High-stakes topic detected; include reviewed source notes or verify details manually before acting.');
        }
        if (terms.length) {
          warnings.push('High-stakes use remains response-only and requires manual review; no professional, legal, medical, financial, or external action automation is provided.');
        }
        qualityWarnings.className = warnings.length ? 'stack' : 'stack muted';
        qualityWarnings.innerHTML = warnings.length
          ? warnings.map((warning) => `<div class="row notice">${escapeHtml(warning)}</div>`).join('')
          : 'No readiness warnings yet. Review the payload before any manual use.';
        updateHighStakesBanner();
      }
      function selectedEndpointPath(agent) {
        const endpoint = localResponseAgentEndpointParts(agent && agent.endpoint);
        if (endpoint.method !== 'POST' || !endpoint.path.startsWith('/agents/')) {
          return '';
        }
        return endpoint.path;
      }
      function populateOutputTypeSelect(template, agent) {
        const outputTypes = localResponseAgentTemplateOutputTypes(template, agent);
        outputTypeSelect.innerHTML = outputTypes.length
          ? outputTypes.map((type) => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`).join('')
          : '<option value="summary">summary</option>';
      }
      function applySamplePayloadToComposer(template, agent) {
        const samplePayload = (template && (template.sample_payload || template.samplePayload)) || localResponseAgentExample(agent);
        const payload = localResponseAgentPayloadWithSelectedOutputType(samplePayload, outputTypeSelect.value || '');
        if (!Array.isArray(payload.web_context)) {
          payload.web_context = [];
        }
        bodyInput.value = JSON.stringify(payload, null, 2);
        payloadPreviewStatus.textContent = 'Editable JSON payload preview filled from the selected local request template sample.';
        structuredResponse.className = 'row stack muted';
        structuredResponse.textContent = 'No structured local response-agent result yet.';
        responseOutput.textContent = 'No local response-agent result yet.';
        latestLocalResponseBody = null;
        latestLocalResponseAgent = null;
        renderReviewedWebContextPreview();
        updateReadinessUi();
      }
      function refreshPayloadOutputType() {
        try {
          const parsedBody = JSON.parse(bodyInput.value || '{}');
          if (!parsedBody || Array.isArray(parsedBody) || typeof parsedBody !== 'object') {
            payloadPreviewStatus.textContent = 'Output type not applied: payload preview must be a JSON object.';
            updateReadinessUi();
            return;
          }
          const payload = localResponseAgentPayloadWithSelectedOutputType(parsedBody, outputTypeSelect.value || '');
          bodyInput.value = JSON.stringify(payload, null, 2);
          payloadPreviewStatus.textContent = 'Output type applied to the editable JSON payload preview.';
          renderReviewedWebContextPreview();
          updateReadinessUi();
        } catch (error) {
          payloadPreviewStatus.textContent = `Output type not applied: invalid JSON (${error.message}).`;
          renderReviewedWebContextPreview();
          updateReadinessUi();
        }
      }
      async function localResponseAgentSelectSuggestedAgent(agentId) {
        const agentIndex = agents.findIndex((agent) => localResponseAgentId(agent) === agentId);
        if (agentIndex < 0) {
          routePreviewStatus.textContent = 'Suggested agent was not found in the local dashboard summary.';
          return;
        }
        categorySelect.value = '__all__';
        renderAgentOptions();
        select.value = String(agentIndex);
        routePreviewStatus.textContent = 'Suggested agent selected for manual review. Route preview does not invoke agents. Select manually before running a local response.';
        await loadSelectedExample();
      }
      function renderRoutePreviewSuggestions(result) {
        const suggestions = []
          .concat(Array.isArray(result && result.suggested_agents) ? result.suggested_agents : [])
          .concat(Array.isArray(result && result.suggestedAgents) ? result.suggestedAgents : [])
          .concat(Array.isArray(result && result.recommended_agents) ? result.recommended_agents : [])
          .concat(Array.isArray(result && result.recommendedAgents) ? result.recommendedAgents : []);
        const uniqueSuggestions = Array.from(new Set(suggestions
          .map((item) => typeof item === 'string' ? item : (item.agent_id || item.agentId || item.id || ''))
          .filter(Boolean)));
        routePreviewSuggestions.innerHTML = uniqueSuggestions.length
          ? '<option value="">Select manually before running a local response</option>' + uniqueSuggestions.map((agentId) => `<option value="${escapeHtml(agentId)}">${escapeHtml(agentId)}</option>`).join('')
          : '<option value="">No suggested agents available</option>';
      }
      function localResponseManualWorkflowCandidateIds() {
        return Array.from(new Set((manualWorkflowCandidates.value || '')
          .split(/[\r\n,]+/)
          .map((line) => line.trim())
          .filter(Boolean)))
          .slice(0, 8);
      }
      function localResponseRoutePreviewSuggestionIds() {
        return Array.from(routePreviewSuggestions.options || [])
          .map((option) => option.value)
          .filter(Boolean)
          .slice(0, 8);
      }
      function renderManualWorkflowSteps(result) {
        latestManualWorkflowSteps = []
          .concat(Array.isArray(result && result.workflow_steps) ? result.workflow_steps : [])
          .concat(Array.isArray(result && result.workflowSteps) ? result.workflowSteps : []);
        const uniqueSteps = [];
        const seen = new Set();
        latestManualWorkflowSteps.forEach((step) => {
          const agentId = step.agent_id || step.agentId || '';
          const stepNumber = step.step_number || step.stepNumber || uniqueSteps.length + 1;
          const key = `${stepNumber}:${agentId}`;
          if (agentId && !seen.has(key)) {
            seen.add(key);
            uniqueSteps.push(step);
          }
        });
        latestManualWorkflowSteps = uniqueSteps;
        manualWorkflowSteps.innerHTML = uniqueSteps.length
          ? uniqueSteps.map((step, index) => `<option value="${escapeHtml(index)}">Step ${escapeHtml(step.step_number || step.stepNumber || index + 1)} - ${escapeHtml(step.display_name || step.displayName || step.agent_id || step.agentId)}</option>`).join('')
          : '<option value="">No manual workflow steps available</option>';
        renderLocalResponseAgentJson(manualWorkflowResult, result, 'No manual workflow preview available.');
      }
      function localResponsePriorContextFromLatestResponse() {
        if (!latestLocalResponseBody || typeof latestLocalResponseBody !== 'object' || Array.isArray(latestLocalResponseBody)) {
          return null;
        }
        const agent = selectedAgent();
        const asArray = (value) => Array.isArray(value)
          ? value.map((item) => typeof item === 'string' ? item : JSON.stringify(item)).slice(0, 20)
          : value
            ? [typeof value === 'string' ? value : JSON.stringify(value)].slice(0, 20)
            : [];
        return {
          previous_agent_id: localResponseAgentId(agent),
          previous_agent_name: localResponseAgentName(agent),
          previous_output_type: latestLocalResponseBody.output_type || latestLocalResponseBody.outputType || outputTypeSelect.value || '',
          previous_summary: latestLocalResponseBody.summary || latestLocalResponseBody.title || '',
          previous_key_points: asArray(latestLocalResponseBody.key_points || latestLocalResponseBody.keyPoints || latestLocalResponseBody.assumptions || latestLocalResponseBody.recommended_plan || latestLocalResponseBody.recommendedPlan),
          previous_next_actions: asArray(latestLocalResponseBody.next_actions || latestLocalResponseBody.nextActions || latestLocalResponseBody.follow_up_questions || latestLocalResponseBody.followUpQuestions),
          previous_limitations: asArray(latestLocalResponseBody.limitations || latestLocalResponseBody.source_cautions || latestLocalResponseBody.sourceCautions),
          user_notes: 'Inserted manually from the latest visible structured response after user review.',
          source_type: 'manual_prior_agent_output',
        };
      }
      function insertLatestResponseAsPriorContext() {
        const context = localResponsePriorContextFromLatestResponse();
        if (!context) {
          manualWorkflowStatus.textContent = 'No latest structured response is available for prior_agent_context. Run one selected agent manually, review the result, then insert context if useful.';
          return;
        }
        try {
          const parsedBody = JSON.parse(bodyInput.value || '{}');
          if (!parsedBody || Array.isArray(parsedBody) || typeof parsedBody !== 'object') {
            manualWorkflowStatus.textContent = 'Prior context was not inserted because the editable payload is not a JSON object.';
            return;
          }
          parsedBody.prior_agent_context = context;
          bodyInput.value = JSON.stringify(parsedBody, null, 2);
          renderReviewedWebContextPreview();
          manualWorkflowStatus.textContent = 'prior_agent_context inserted into the editable payload for manual review. No automatic handoff, no persistence, and no agent invocation occurred.';
        } catch (error) {
          manualWorkflowStatus.textContent = `Prior context was not inserted: ${error.message}.`;
        }
      }
      function localResponsePlainText(value, maxLength = 4000) {
        const text = Array.isArray(value)
          ? value.map((item) => localResponsePlainText(item, maxLength)).filter(Boolean).join('; ')
          : value && typeof value === 'object'
            ? JSON.stringify(value)
            : String(value || '');
        return text.replace(/\s+/g, ' ').trim().slice(0, maxLength);
      }
      function localResponseList(value, maxItems = 20) {
        if (value === null || value === undefined || value === '') {
          return [];
        }
        const rawItems = Array.isArray(value) ? value : [value];
        return rawItems
          .map((item) => localResponsePlainText(item, 4000))
          .filter(Boolean)
          .slice(0, maxItems);
      }
      function localResponseFirstValue(responseBody, keys) {
        for (const key of keys) {
          const value = localResponseKnownValue(responseBody, key);
          if (value !== undefined && value !== null && value !== '') {
            return value;
          }
        }
        return '';
      }
      function selectedSessionBoardEntries() {
        return sessionResultBoard.filter((entry) => entry.selected);
      }
      function sessionBoardEntryFromLatestResponse() {
        if (!latestLocalResponseBody || typeof latestLocalResponseBody !== 'object' || Array.isArray(latestLocalResponseBody)) {
          return null;
        }
        const agent = latestLocalResponseAgent || selectedAgent();
        const sourceLabels = localResponseList(localResponseFirstValue(latestLocalResponseBody, ['citation_labels', 'citationLabels']));
        const sourcesUsed = localResponseKnownValue(latestLocalResponseBody, 'sources_used') || localResponseKnownValue(latestLocalResponseBody, 'sourcesUsed') || [];
        const derivedSourceLabels = Array.isArray(sourcesUsed)
          ? sourcesUsed.map((source) => source && (source.citation_label || source.citationLabel || source.source_id || source.sourceId)).filter(Boolean)
          : [];
        return {
          id: `session-board-entry-${sessionResultBoardSequence++}`,
          entryNumber: sessionResultBoard.length + 1,
          timestamp: new Date().toLocaleString(),
          selected: true,
          agent_id: localResponsePlainText(localResponseFirstValue(latestLocalResponseBody, ['agent_id', 'agentId']) || localResponseAgentId(agent)),
          display_name: localResponsePlainText(localResponseAgentName(agent)),
          output_type: localResponsePlainText(localResponseFirstValue(latestLocalResponseBody, ['output_type', 'outputType']) || outputTypeSelect.value),
          title: localResponsePlainText(localResponseFirstValue(latestLocalResponseBody, ['title'])),
          summary: localResponsePlainText(localResponseFirstValue(latestLocalResponseBody, ['summary'])),
          recommended_plan: localResponseList(localResponseFirstValue(latestLocalResponseBody, ['recommended_plan', 'recommendedPlan'])),
          next_actions: localResponseList(localResponseFirstValue(latestLocalResponseBody, ['next_actions', 'nextActions', 'checklist'])),
          checklist: localResponseList(localResponseFirstValue(latestLocalResponseBody, ['checklist'])),
          limitations: localResponseList(localResponseFirstValue(latestLocalResponseBody, ['limitations', 'prior_context_limitations', 'priorContextLimitations'])),
          safety_notes: localResponseList(localResponseFirstValue(latestLocalResponseBody, ['safety_notes', 'safetyNotes'])),
          source_context_summary: localResponsePlainText(localResponseFirstValue(latestLocalResponseBody, ['source_context_summary', 'sourceContextSummary'])),
          citation_labels: Array.from(new Set(sourceLabels.concat(localResponseList(derivedSourceLabels)))).slice(0, 20),
          source_cautions: localResponseList(localResponseFirstValue(latestLocalResponseBody, ['source_cautions', 'sourceCautions'])),
          prior_context_used: localResponseKnownValue(latestLocalResponseBody, 'prior_context_used') ?? localResponseKnownValue(latestLocalResponseBody, 'priorContextUsed') ?? '',
          prior_context_summary: localResponsePlainText(localResponseFirstValue(latestLocalResponseBody, ['prior_context_summary', 'priorContextSummary'])),
          prior_context_limitations: localResponseList(localResponseFirstValue(latestLocalResponseBody, ['prior_context_limitations', 'priorContextLimitations'])),
        };
      }
      function renderSessionResultBoard() {
        if (!sessionResultBoard.length) {
          sessionBoardEntries.className = 'stack muted';
          sessionBoardEntries.textContent = 'No board entries yet. Add latest response to session board after a structured response returns.';
          return;
        }
        sessionBoardEntries.className = 'stack';
        sessionBoardEntries.innerHTML = sessionResultBoard.map((entry, index) => {
          const limitationPreview = entry.limitations.length
            ? `${entry.limitations.length} limitation item(s): ${entry.limitations.slice(0, 2).join(' ')}`
            : 'No limitations returned.';
          const priorContextUsed = entry.prior_context_used === '' ? 'not returned' : String(entry.prior_context_used);
          return `
            <div class="row stack">
              <label><input type="checkbox" data-session-board-select="${escapeHtml(entry.id)}" ${entry.selected ? 'checked' : ''}> Select for packet/comparison</label>
              <div><strong>Entry ${escapeHtml(entry.entryNumber)}</strong> · ${escapeHtml(entry.timestamp || 'current session')}</div>
              <div>Agent: <code>${escapeHtml(entry.agent_id || 'unknown_agent')}</code> ${escapeHtml(entry.display_name || '')}</div>
              <div>Output type: <code>${escapeHtml(entry.output_type || 'unspecified')}</code></div>
              <div>Title: ${escapeHtml(entry.title || 'No title returned.')}</div>
              <div>Summary: ${escapeHtml(entry.summary || 'No summary returned.')}</div>
              <div>Limitations: ${escapeHtml(limitationPreview)}</div>
              <div>Source labels: ${escapeHtml(entry.citation_labels.join(', ') || 'None returned.')}</div>
              <div>Prior context used: ${escapeHtml(priorContextUsed)}</div>
              <button type="button" data-session-board-remove="${escapeHtml(index)}">Remove entry</button>
            </div>
          `;
        }).join('');
        sessionBoardEntries.querySelectorAll('input[data-session-board-select]').forEach((checkbox) => {
          checkbox.onchange = () => {
            const entry = sessionResultBoard.find((item) => item.id === checkbox.getAttribute('data-session-board-select'));
            if (entry) {
              entry.selected = checkbox.checked;
            }
          };
        });
        sessionBoardEntries.querySelectorAll('button[data-session-board-remove]').forEach((button) => {
          button.onclick = () => {
            const index = Number(button.getAttribute('data-session-board-remove'));
            sessionResultBoard.splice(index, 1);
            sessionResultBoard.forEach((entry, entryIndex) => {
              entry.entryNumber = entryIndex + 1;
            });
            sessionBoardStatus.textContent = 'Board entry removed from current session only. No persistence, no handoff, and no agent execution occurred.';
            renderSessionResultBoard();
          };
        });
      }
      function addLatestResponseToSessionBoard() {
        const entry = sessionBoardEntryFromLatestResponse();
        if (!entry) {
          sessionBoardStatus.textContent = 'No latest response yet. Run one selected local response agent manually, review the result, then add it to the session board.';
          return;
        }
        sessionResultBoard.push(entry);
        sessionBoardStatus.textContent = 'Latest response added to session board. Board entries are not persisted and clear when the page reloads.';
        renderSessionResultBoard();
      }
      function buildSessionComparison() {
        const entries = selectedSessionBoardEntries();
        if (!entries.length) {
          resultComparisonBody.className = 'muted';
          resultComparisonBody.textContent = 'No selected entries. Select board entries before building a comparison.';
          return;
        }
        if (entries.length < 2) {
          resultComparisonBody.className = 'muted';
          resultComparisonBody.textContent = 'Fewer than 2 selected entries for comparison. Select at least two board entries.';
          return;
        }
        resultComparisonBody.className = '';
        resultComparisonBody.innerHTML = `
          <table>
            <thead><tr><th>Field</th>${entries.map((entry) => `<th>Entry ${escapeHtml(entry.entryNumber)}</th>`).join('')}</tr></thead>
            <tbody>
              ${[
                ['agent', (entry) => `${entry.display_name || ''} ${entry.agent_id || ''}`],
                ['output_type', (entry) => entry.output_type],
                ['title', (entry) => entry.title],
                ['summary', (entry) => entry.summary],
                ['key next actions', (entry) => entry.next_actions.join('; ')],
                ['limitations', (entry) => entry.limitations.concat(entry.safety_notes).join('; ')],
                ['source labels', (entry) => entry.citation_labels.join(', ')],
                ['prior context used', (entry) => String(entry.prior_context_used || '')],
              ].map(([label, reader]) => `<tr><th>${escapeHtml(label)}</th>${entries.map((entry) => `<td>${escapeHtml(reader(entry) || 'No value returned.')}</td>`).join('')}</tr>`).join('')}
            </tbody>
          </table>
        `;
        sessionBoardStatus.textContent = 'Comparison built from selected session board entries only. No agent was run and nothing was persisted.';
      }
      function buildReviewPacketText(entries) {
        const lines = [
          'Packet title',
          'Local Response Review Packet',
          '',
          'Generated in current dashboard session only',
          'This text is held in the current page only until the page reloads.',
          '',
          'Selected local response-agent outputs',
        ];
        entries.forEach((entry) => {
          lines.push(`- Entry ${entry.entryNumber}: ${entry.display_name || entry.agent_id || 'Local response agent'} (${entry.output_type || 'unspecified output_type'})`);
        });
        lines.push('', 'Key summaries');
        entries.forEach((entry) => lines.push(`- Entry ${entry.entryNumber}: ${entry.summary || entry.title || 'No summary returned.'}`));
        lines.push('', 'Next actions');
        entries.flatMap((entry) => entry.next_actions.length ? entry.next_actions : entry.checklist).slice(0, 20).forEach((item) => lines.push(`- ${item}`));
        lines.push('', 'Limitations and safety notes');
        entries.flatMap((entry) => entry.limitations.concat(entry.safety_notes)).slice(0, 20).forEach((item) => lines.push(`- ${item}`));
        lines.push('', 'Reviewed source labels and source cautions');
        entries.flatMap((entry) => entry.citation_labels.concat(entry.source_cautions)).slice(0, 20).forEach((item) => lines.push(`- ${item}`));
        lines.push('', 'Prior context notes');
        entries.forEach((entry) => lines.push(`- Entry ${entry.entryNumber}: prior_context_used=${entry.prior_context_used === '' ? 'not returned' : String(entry.prior_context_used)}. ${entry.prior_context_summary || entry.prior_context_limitations.join(' ') || 'No prior context notes returned.'}`));
        lines.push('', 'Suggested next manual step');
        lines.push('Review the selected outputs, choose one next local response agent manually, and insert reviewed context only if useful.');
        lines.push('', 'Boundary reminder');
        lines.push('This packet was composed from manually selected session outputs.');
        lines.push('It was not persisted.');
        lines.push('It did not run agents automatically.');
        lines.push('It did not browse automatically.');
        lines.push('It did not use connectors.');
        lines.push('Review before using as prior_agent_context.');
        return lines.join('\n').slice(0, 4000);
      }
      function buildReviewPacket() {
        const entries = selectedSessionBoardEntries();
        if (!entries.length) {
          reviewPacketOutput.value = 'No selected entries. Select board entries before building a review packet.';
          sessionBoardStatus.textContent = 'No selected entries for review packet. Nothing was persisted and no agent was run.';
          latestReviewPacketText = '';
          return;
        }
        latestReviewPacketText = buildReviewPacketText(entries);
        reviewPacketOutput.value = latestReviewPacketText;
        sessionBoardStatus.textContent = 'Review packet built from selected session outputs only. It was not persisted, sent, downloaded, or written to clipboard automatically.';
      }
      function priorContextFromSessionEntry(entry) {
        return {
          previous_agent_id: entry.agent_id || '',
          previous_agent_name: entry.display_name || '',
          previous_output_type: entry.output_type || '',
          previous_summary: (entry.summary || entry.title || '').slice(0, 4000),
          previous_key_points: entry.recommended_plan.concat(entry.checklist).slice(0, 20),
          previous_next_actions: entry.next_actions.slice(0, 20),
          previous_limitations: entry.limitations.concat(entry.safety_notes, entry.source_cautions, entry.prior_context_limitations).slice(0, 20),
          user_notes: `Inserted manually from Session Result Board entry ${entry.entryNumber}.`.slice(0, 4000),
          source_type: 'manual_session_board_output',
        };
      }
      function priorContextFromReviewPacket() {
        const entries = selectedSessionBoardEntries();
        const packetText = latestReviewPacketText || reviewPacketOutput.value || '';
        if (!entries.length || !packetText || packetText === 'No review packet yet.') {
          return null;
        }
        return {
          previous_agent_id: 'multi_agent_review_packet',
          previous_agent_name: 'Session Review Packet',
          previous_output_type: 'review_packet',
          previous_summary: entries.map((entry) => `${entry.display_name || entry.agent_id}: ${entry.summary || entry.title || 'No summary returned.'}`).join(' | ').slice(0, 4000),
          previous_key_points: packetText.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).slice(0, 20),
          previous_next_actions: entries.flatMap((entry) => entry.next_actions).slice(0, 20),
          previous_limitations: [
            'This packet was composed from manually selected session outputs.',
            'It was not persisted.',
            'It did not run agents automatically.',
            'It did not browse automatically.',
            'It did not use connectors.',
            'Review before using as prior_agent_context.',
          ],
          user_notes: packetText.slice(0, 4000),
          source_type: 'manual_session_review_packet',
        };
      }
      function writePriorContextToPayload(context, successText) {
        try {
          const parsedBody = JSON.parse(bodyInput.value || '{}');
          if (!parsedBody || Array.isArray(parsedBody) || typeof parsedBody !== 'object') {
            sessionBoardStatus.textContent = 'Invalid editable payload JSON while inserting prior context. The selected agent was not run.';
            return;
          }
          parsedBody.prior_agent_context = context;
          bodyInput.value = JSON.stringify(parsedBody, null, 2);
          renderReviewedWebContextPreview();
          sessionBoardStatus.textContent = successText;
        } catch (error) {
          sessionBoardStatus.textContent = `Invalid editable payload JSON while inserting prior context: ${error.message}. The selected agent was not run.`;
        }
      }
      function insertSelectedBoardEntryAsPriorContext() {
        const entries = selectedSessionBoardEntries();
        if (!entries.length) {
          sessionBoardStatus.textContent = 'No selected entries. Select one board entry before inserting prior_agent_context.';
          return;
        }
        writePriorContextToPayload(
          priorContextFromSessionEntry(entries[0]),
          'prior_agent_context insertion succeeded from selected board entry, but agent was not run. Editable JSON payload updated only.'
        );
      }
      function insertReviewPacketAsPriorContext() {
        const context = priorContextFromReviewPacket();
        if (!context) {
          sessionBoardStatus.textContent = 'No review packet is available. Build review packet from selected entries before inserting prior_agent_context.';
          return;
        }
        writePriorContextToPayload(
          context,
          'prior_agent_context insertion succeeded from review packet, but agent was not run. Editable JSON payload updated only.'
        );
      }
      function clearSessionResultBoard() {
        sessionResultBoard = [];
        latestReviewPacketText = '';
        reviewPacketOutput.value = 'No review packet yet.';
        resultComparisonBody.className = 'muted';
        resultComparisonBody.textContent = 'Select at least two board entries, then build comparison.';
        sessionBoardStatus.textContent = 'Board cleared from current session only. Board clears when the page reloads.';
        renderSessionResultBoard();
      }
      function localResponseWebResearchUrls() {
        return Array.from(new Set((webResearchUrls.value || '')
          .split(/\r?\n/)
          .map((line) => line.trim())
          .filter(Boolean)))
          .slice(0, 5);
      }
      function renderWebResearchResult(value, fallbackText) {
        webResearchResult.textContent = value ? JSON.stringify(value, null, 2) : fallbackText;
      }
      function localResponseWebContextEntries(sources) {
        return sources
          .filter((source) => source && source.fetched && source.excerpt)
          .slice(0, 5)
          .map((source) => ({
            source_url: source.url || source.source_url || '',
            final_url: source.final_url || source.finalUrl || '',
            title: source.title || '',
            excerpt: String(source.excerpt || '').slice(0, 4000),
            content_type: source.content_type || source.contentType || '',
            fetched: true,
            fetched_at: source.fetched_at || source.fetchedAt || '',
            source_type: 'public_web_excerpt',
            limitations: Array.isArray(source.limitations) ? source.limitations.slice(0, 8) : [],
          }));
      }
      function localResponseSourceLabel(index) {
        return `S${index + 1}`;
      }
      function localResponseReviewedSourcesFromPayload() {
        try {
          const parsedBody = JSON.parse(bodyInput.value || '{}');
          return parsedBody && !Array.isArray(parsedBody) && typeof parsedBody === 'object' && Array.isArray(parsedBody.web_context)
            ? parsedBody.web_context.slice(0, 5)
            : [];
        } catch (error) {
          return null;
        }
      }
      function localResponseReviewedSourceWarnings(source, label) {
        const warnings = Array.isArray(source.quality_warnings) ? source.quality_warnings.slice(0, 4) : [];
        if (!source.title) {
          warnings.push(`[${label}] Missing source title.`);
        }
        if (!source.fetched_at && !source.fetchedAt) {
          warnings.push(`[${label}] Missing fetched_at; recency is unknown.`);
        }
        warnings.push(`[${label}] Excerpt is partial, user-reviewed, and not independently verified.`);
        return Array.from(new Set(warnings));
      }
      function renderReviewedSourceManager(entries) {
        if (!Array.isArray(entries)) {
          reviewedSourceList.className = 'stack muted';
          reviewedSourceList.textContent = 'Reviewed-source manager unavailable while payload JSON is invalid.';
          return;
        }
        if (!entries.length) {
          reviewedSourceList.className = 'stack muted';
          reviewedSourceList.textContent = 'No reviewed sources in payload.';
          return;
        }
        reviewedSourceList.className = 'stack';
        reviewedSourceList.innerHTML = entries.map((source, index) => {
          const safeSource = source || {};
          const label = localResponseSourceLabel(index);
          const warnings = localResponseReviewedSourceWarnings(safeSource, label);
          const limitations = Array.isArray(safeSource.limitations) ? safeSource.limitations.slice(0, 4) : [];
          return `
            <div class="row stack">
              <div><strong>[${escapeHtml(label)}]</strong> ${escapeHtml(safeSource.title || 'Untitled reviewed source')}</div>
              <div class="muted">${escapeHtml(safeSource.final_url || safeSource.source_url || 'No public source URL supplied')}</div>
              <div>${escapeHtml(String(safeSource.excerpt || '').slice(0, 360))}</div>
              <div class="muted">Warnings: ${escapeHtml(warnings.join(' '))}</div>
              <div class="muted">Limitations: ${escapeHtml(limitations.join(' ') || 'Source labels are for reference, not proof.')}</div>
              <button type="button" data-reviewed-source-index="${escapeHtml(index)}">Remove [${escapeHtml(label)}]</button>
            </div>
          `;
        }).join('');
        reviewedSourceList.querySelectorAll('button[data-reviewed-source-index]').forEach((button) => {
          button.onclick = () => removeReviewedSource(Number(button.getAttribute('data-reviewed-source-index')));
        });
      }
      function writeReviewedSourcesToPayload(entries, statusText) {
        try {
          const parsedBody = JSON.parse(bodyInput.value || '{}');
          if (!parsedBody || Array.isArray(parsedBody) || typeof parsedBody !== 'object') {
            webResearchStatus.textContent = 'Reviewed sources were not changed because the editable payload is not a JSON object.';
            return;
          }
          parsedBody.web_context = entries.slice(0, 5);
          bodyInput.value = JSON.stringify(parsedBody, null, 2);
          webResearchStatus.textContent = statusText;
          renderReviewedWebContextPreview();
        } catch (error) {
          webResearchStatus.textContent = `Reviewed sources were not changed: ${error.message}.`;
          renderReviewedWebContextPreview();
        }
      }
      function removeReviewedSource(index) {
        const entries = localResponseReviewedSourcesFromPayload();
        if (!Array.isArray(entries)) {
          webResearchStatus.textContent = 'Reviewed source was not removed because the editable payload JSON is invalid.';
          return;
        }
        const label = localResponseSourceLabel(index);
        writeReviewedSourcesToPayload(entries.filter((_, sourceIndex) => sourceIndex !== index), `Reviewed source [${label}] removed from web_context. The selected agent was not invoked.`);
      }
      function clearReviewedSources() {
        writeReviewedSourcesToPayload([], 'Reviewed sources cleared from web_context. The selected agent was not invoked.');
      }
      function renderSourceAwareUsagePreview(entries) {
        if (!Array.isArray(entries) || !entries.length) {
          sourceAwarePreviewBody.className = 'muted';
          sourceAwarePreviewBody.textContent = 'No reviewed sources in payload.';
          return;
        }
        const agent = selectedAgent();
        const labels = entries.map((_, index) => `[${localResponseSourceLabel(index)}]`).join(', ');
        sourceAwarePreviewBody.className = '';
        sourceAwarePreviewBody.innerHTML = `
          <div>Selected agent: <code>${escapeHtml(localResponseAgentName(agent) || 'Local response agent')}</code></div>
          <div>Reviewed source labels available: ${escapeHtml(labels)}</div>
          <div class="muted">The selected agent may use these reviewed excerpts for source-aware response sections only. Citations are labels for reference, not proof or certification.</div>
          <div class="muted">Verify freshness, authority, and exact details manually before acting. No auto-fetch, no auto-submit, no connector, and no background browsing.</div>
        `;
      }
      function renderReviewedWebContextPreview() {
        const entries = localResponseReviewedSourcesFromPayload();
        if (entries === null) {
          reviewedWebContextPreview.textContent = 'Reviewed source context preview unavailable: invalid JSON.';
          renderReviewedSourceManager(null);
          renderSourceAwareUsagePreview(null);
          updateReadinessUi();
          return;
        }
        reviewedWebContextPreview.textContent = entries.length
          ? JSON.stringify(entries, null, 2)
          : 'No reviewed source context in payload yet.';
        renderReviewedSourceManager(entries);
        renderSourceAwareUsagePreview(entries);
        updateReadinessUi();
      }
      async function postWebResearchJson(path, body) {
        const response = await fetch(path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        return response.json();
      }
      function renderAgentDetail(agent) {
        if (!agent) {
          detailPanel.textContent = 'No local response agent selected. Choose a category or agent to inspect local metadata.';
          boundaryFlagsPanel.textContent = 'No boundary flags available for the current selection.';
          return;
        }
        const badges = localResponseAgentBadges(agent).map((badge) => `<span class="pill">${escapeHtml(badge)}</span>`).join(' ');
        const webResearchLine = agent.web_research_available || agent.webResearchAvailable
          ? 'Optional public web research: read-only public URL context, user enabled only.'
          : 'Optional public web research: unavailable for this catalog entry.';
        detailPanel.innerHTML = `
          <div><strong>${escapeHtml(localResponseAgentName(agent))}</strong></div>
          <div>Agent ID: <code>${escapeHtml(localResponseAgentId(agent))}</code></div>
          <div>Endpoint: <code>${escapeHtml(agent.endpoint || '')}</code></div>
          <div>Category: <code>${escapeHtml(localResponseAgentCategory(agent))}</code></div>
          <div>Output types: <code>${escapeHtml(((agent.outputTypes || agent.output_types || [])).join(', ') || 'summary')}</code></div>
          <div>Web research mode: <code>${escapeHtml(agent.web_research_mode || agent.webResearchMode || 'read_only_public_url_context')}</code></div>
          <div>${badges}</div>
          <div class="muted">Use when: ${escapeHtml(agent.useWhen || agent.use_when || agent.recommendedFor || '')}</div>
          <div class="muted">${escapeHtml(webResearchLine)}</div>
          <div class="muted">Limitations: ${escapeHtml(((agent.safetyNotes || agent.safety_notes || [])).join(' ') || 'Manual local review required before using high-stakes guidance.')}</div>
          <div><a href="${escapeHtml(agent.docsLink || agent.docs_link || '/docs/local-response-agents-index.md')}">Docs</a></div>
        `;
        const flags = localResponseAgentBoundaryFlags(agent);
        boundaryFlagsPanel.innerHTML = Object.keys(flags).length
          ? Object.entries(flags).map(([key, value]) => `<div><code>${escapeHtml(key)}</code>: ${escapeHtml(String(value))}</div>`).join('')
          : '<div>No boundary flags available. Treat as manual input only, local only, response only, no connector, and non-persistent.</div>';
        updateReadinessUi();
      }
      async function loadSelectedTemplate(agent) {
        const templatePath = localResponseAgentTemplatePath(agent);
        if (!agent || !templatePath) {
          selectedTemplate = null;
          templateStatus.textContent = 'No request template available for the current selection.';
          templateOutput.textContent = 'No request template selected.';
          samplePayloadOutput.textContent = 'No sample payload selected.';
          populateOutputTypeSelect(null, agent);
          payloadPreviewStatus.textContent = 'No request template available for the current selection.';
          return;
        }
        templateStatus.textContent = 'Loading local request-template metadata...';
        try {
          const template = await fetch(templatePath).then((response) => response.json());
          if (!template || template.found === false) {
            selectedTemplate = null;
            templateStatus.textContent = 'Request template unavailable. No local response agent was invoked.';
            templateOutput.textContent = 'Template metadata was not found for this agent id.';
            samplePayloadOutput.textContent = 'Sample payload unavailable.';
            populateOutputTypeSelect(null, agent);
            payloadPreviewStatus.textContent = 'Unknown template: editable JSON payload preview uses catalog example metadata only.';
            return;
          }
          selectedTemplate = template;
          templateStatus.textContent = 'Request template loaded as local metadata only.';
          renderLocalResponseAgentJson(templateOutput, template, 'Template metadata unavailable.');
          renderLocalResponseAgentJson(samplePayloadOutput, template.sample_payload || template.samplePayload || {}, 'Sample payload unavailable.');
          populateOutputTypeSelect(template, agent);
          applySamplePayloadToComposer(template, agent);
        } catch (error) {
          selectedTemplate = null;
          templateStatus.textContent = `Request template unavailable: ${error.message}. No local response agent was invoked.`;
          templateOutput.textContent = 'Template metadata unavailable.';
          samplePayloadOutput.textContent = 'Sample payload unavailable.';
          populateOutputTypeSelect(null, agent);
          payloadPreviewStatus.textContent = 'Backend error while loading template metadata. No local response agent was invoked.';
        }
      }
      async function loadSelectedExample() {
        const agent = selectedAgent();
        if (!agent) {
          endpointDisplay.textContent = 'No agent selected.';
          bodyInput.value = '{}';
          status.textContent = 'No local response agent is selected.';
          renderReviewedWebContextPreview();
          renderAgentDetail(null);
          renderWorkbenchError(structuredResponse, 'Missing agent', 'No local response agent is selected.', null);
          await loadSelectedTemplate(null);
          return;
        }
        const endpointPath = selectedEndpointPath(agent);
        endpointDisplay.textContent = endpointPath || 'Endpoint rejection.';
        docsLink.href = agent.docsLink || '/docs/local-response-agents-index.md';
        bodyInput.value = JSON.stringify(agent.exampleRequestBody || {}, null, 2);
        responseOutput.textContent = 'No local response-agent result yet.';
        latestLocalResponseBody = null;
        latestLocalResponseAgent = null;
        status.textContent = allowlistedEndpointPaths.has(endpointPath)
          ? 'Ready. This local-only workbench can call only the selected allowlisted endpoint.'
          : 'Endpoint rejection: selected catalog entry is not allowlisted.';
        renderReviewedWebContextPreview();
        renderAgentDetail(agent);
        await loadSelectedTemplate(agent);
        updateReadinessUi();
      }
      categorySelect.onchange = async () => {
        renderAgentOptions();
        await loadSelectedExample();
        trackRecentAgent(selectedAgent());
        renderCommandCenter();
      };
      select.onchange = async () => {
        await loadSelectedExample();
        trackRecentAgent(selectedAgent());
        updateReadinessUi();
      };
      outputTypeSelect.onchange = refreshPayloadOutputType;
      bodyInput.oninput = renderReviewedWebContextPreview;
      commandSearch.oninput = renderCommandCenter;
      commandCategory.onchange = renderCommandCenter;
      Object.values(contextFields).forEach((field) => {
        field.oninput = renderContextKitPreview;
      });
      contextInsertRequestButton.onclick = insertContextKitIntoRequest;
      contextInsertPriorButton.onclick = () => insertContextKitAsPriorContext('Context kit inserted as prior_agent_context. No agent was invoked.');
      reviewedSourceClearButton.onclick = clearReviewedSources;
      useSampleButton.onclick = () => {
        applySamplePayloadToComposer(selectedTemplate, selectedAgent());
      };
      routePreviewSuggestions.onchange = async () => {
        if (routePreviewSuggestions.value) {
          await localResponseAgentSelectSuggestedAgent(routePreviewSuggestions.value);
        }
      };
      manualWorkflowPreviewButton.onclick = async () => {
        manualWorkflowStatus.textContent = 'Manual workflow preview requested. No agent is invoked, no handoff is created, and no workflow is persisted.';
        manualWorkflowResult.textContent = 'Manual workflow preview pending.';
        manualWorkflowSteps.innerHTML = '<option value="">No manual workflow steps available</option>';
        try {
          const response = await fetch('/agents/local-response-agents/manual-workflow-preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              userGoal: manualWorkflowGoal.value.trim(),
              candidateAgentIds: localResponseManualWorkflowCandidateIds(),
              routePreviewSuggestions: localResponseRoutePreviewSuggestionIds(),
              maxSteps: 4,
              includeWebContext: manualWorkflowIncludeWebContext.checked,
              constraintsOrNotes: 'Manual workflow only. Steps are suggestions, not execution. Run one selected agent at a time.',
            }),
          });
          const result = await response.json();
          renderManualWorkflowSteps(result);
          manualWorkflowStatus.textContent = 'Manual workflow preview loaded. Steps are suggestions, not execution. Run one selected agent at a time.';
        } catch (error) {
          latestManualWorkflowSteps = [];
          manualWorkflowStatus.textContent = `Manual workflow preview unavailable: ${error.message}. No agent was invoked.`;
          manualWorkflowResult.textContent = 'No manual workflow preview available.';
        }
      };
      manualWorkflowLoadStepButton.onclick = async () => {
        const step = latestManualWorkflowSteps[Number(manualWorkflowSteps.value || 0)];
        const agentId = step && (step.agent_id || step.agentId);
        if (!agentId) {
          manualWorkflowStatus.textContent = 'No manual workflow step is selected. Nothing was loaded or executed.';
          return;
        }
        await localResponseAgentSelectSuggestedAgent(agentId);
        manualWorkflowStatus.textContent = 'Workflow step loaded into the request composer. Manual step only - not executed, not handed off, and not persisted.';
      };
      priorContextCopyButton.onclick = insertLatestResponseAsPriorContext;
      sessionBoardAddButton.onclick = addLatestResponseToSessionBoard;
      sessionBoardCompareButton.onclick = buildSessionComparison;
      sessionBoardPacketButton.onclick = buildReviewPacket;
      sessionBoardInsertEntryButton.onclick = insertSelectedBoardEntryAsPriorContext;
      sessionBoardInsertPacketButton.onclick = insertReviewPacketAsPriorContext;
      sessionBoardClearButton.onclick = clearSessionResultBoard;
      webResearchValidateButton.onclick = async () => {
        const urls = localResponseWebResearchUrls();
        webResearchStatus.textContent = 'Validating public URLs by manual click. No source content is fetched.';
        latestWebResearchSources = [];
        if (!urls.length) {
          webResearchStatus.textContent = 'No public source URLs provided for validation.';
          renderWebResearchResult(null, 'No public source URLs provided.');
          return;
        }
        try {
          const results = [];
          for (const url of urls) {
            results.push(await postWebResearchJson('/web-research/validate-url', {
              url,
              purpose: 'Optional public web source context for local response-agent payload review.',
              max_excerpt_chars: 1600,
              allow_redirects: true,
              constraintsOrNotes: 'Manual URL validation only. No fetch, no account access, no background browsing.',
            }));
          }
          webResearchStatus.textContent = 'URL validation complete. Source content was not fetched.';
          renderWebResearchResult({ urls: results }, 'No validation results available.');
        } catch (error) {
          webResearchStatus.textContent = `URL validation unavailable: ${error.message}.`;
          renderWebResearchResult(null, 'No validation results available.');
        }
      };
      webResearchFetchButton.onclick = async () => {
        const urls = localResponseWebResearchUrls();
        webResearchStatus.textContent = 'Previewing public source excerpts by manual click. No agent is invoked.';
        latestWebResearchSources = [];
        if (!urls.length) {
          webResearchStatus.textContent = 'No public source URLs provided for source preview.';
          renderWebResearchResult(null, 'No public source URLs provided.');
          return;
        }
        if (!webResearchEnabled.checked) {
          webResearchStatus.textContent = 'Enable optional public web source context before previewing excerpts.';
          renderWebResearchResult(null, 'Optional public web source context is not enabled.');
          return;
        }
        try {
          const results = [];
          for (const url of urls) {
            results.push(await postWebResearchJson('/web-research/fetch-public-url', {
              url,
              purpose: 'Optional public web source context for local response-agent payload review.',
              max_excerpt_chars: 1600,
              allow_redirects: true,
              constraintsOrNotes: 'Manual source preview only. No logins, accounts, forms, posts, purchases, bookings, downloads, scripts, private networks, localhost, or background browsing.',
            }));
          }
          latestWebResearchSources = results.filter((result) => result && result.fetched);
          webResearchStatus.textContent = 'Source preview complete. Source context is inserted for review, not executed automatically.';
          renderWebResearchResult({ sources: results }, 'No source preview results available.');
        } catch (error) {
          webResearchStatus.textContent = `Source preview unavailable: ${error.message}.`;
          renderWebResearchResult(null, 'No source preview results available.');
        }
      };
      webResearchContextButton.onclick = async () => {
        const agent = selectedAgent();
        const urls = localResponseWebResearchUrls();
        webResearchStatus.textContent = 'Previewing selected-agent source context. No local response agent is invoked.';
        try {
          const result = await postWebResearchJson('/web-research/agent-context-preview', {
            agentId: localResponseAgentId(agent),
            userRequest: bodyInput.value || '',
            urls,
            outputType: outputTypeSelect.value || 'summary',
            webResearchEnabled: webResearchEnabled.checked,
            constraintsOrNotes: 'Agent-context preview only. No auto-fetch, no auto-submit, no handoff, no persistence.',
          });
          webResearchStatus.textContent = 'Agent-context preview complete. No agent was invoked and no workbench payload was submitted.';
          renderWebResearchResult(result, 'No agent-context preview available.');
        } catch (error) {
          webResearchStatus.textContent = `Agent-context preview unavailable: ${error.message}.`;
          renderWebResearchResult(null, 'No agent-context preview available.');
        }
      };
      webResearchAddButton.onclick = () => {
        const contextEntries = localResponseWebContextEntries(latestWebResearchSources);
        if (!contextEntries.length) {
          webResearchStatus.textContent = 'No fetched public source excerpts are available to add to web_context.';
          return;
        }
        try {
          const parsedBody = JSON.parse(bodyInput.value || '{}');
          if (!parsedBody || Array.isArray(parsedBody) || typeof parsedBody !== 'object') {
            webResearchStatus.textContent = 'Source context was not inserted because the editable payload is not a JSON object.';
            return;
          }
          parsedBody.web_context = contextEntries;
          bodyInput.value = JSON.stringify(parsedBody, null, 2);
          renderReviewedWebContextPreview();
          webResearchStatus.textContent = 'Reviewed source context inserted into web_context. The selected agent was not invoked.';
        } catch (error) {
          webResearchStatus.textContent = `Source context was not inserted: ${error.message}.`;
          renderReviewedWebContextPreview();
        }
      };
      routePreviewButton.onclick = async () => {
        const requestText = routePreviewInput.value.trim();
        routePreviewStatus.textContent = 'Route preview does not invoke agents. Suggested only — not executed. Select manually before running a local response.';
        routePreviewResult.textContent = 'Suggested only — not executed.';
        routePreviewSuggestions.innerHTML = '<option value="">No suggested agents available</option>';
        try {
          const response = await fetch('/agents/local-response-agents/route-preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              request: requestText,
              preferredOutputType: outputTypeSelect.value || 'summary',
              urgencyLevel: 'manual_review',
              constraintsOrNotes: 'Manual input only. Suggested only — not executed. Route preview does not invoke agents.',
            }),
          });
          const result = await response.json();
          routePreviewStatus.textContent = 'Suggested only — not executed. Route preview does not invoke agents. Select manually before running a local response. No handoff, no automation, no persistence, no connector, and no agent invocation.';
          renderRoutePreviewSuggestions(result);
          renderLocalResponseAgentJson(routePreviewResult, result, 'No route preview suggestions available.');
        } catch (error) {
          routePreviewStatus.textContent = `Route preview unavailable: ${error.message}. Suggested only — not executed. Route preview does not invoke agents.`;
          routePreviewResult.textContent = 'No route preview suggestions available.';
          routePreviewSuggestions.innerHTML = '<option value="">No suggested agents available</option>';
        }
      };
      runButton.onclick = async () => {
        const agent = selectedAgent();
        const endpointPath = selectedEndpointPath(agent);
        if (!agent || !allowlistedEndpointPaths.has(endpointPath)) {
          status.textContent = 'Endpoint rejection: missing agent or selected catalog entry is not allowlisted.';
          responseOutput.textContent = '';
          renderWorkbenchError(structuredResponse, 'Endpoint rejection', 'No selected-agent local response was requested. Choose an allowlisted local response agent first.', null);
          return;
        }
        let parsedBody;
        try {
          parsedBody = JSON.parse(bodyInput.value || '{}');
        } catch (error) {
          status.textContent = `Invalid JSON: ${error.message}. Manual input was not sent to a local response agent.`;
          responseOutput.textContent = '';
          renderWorkbenchError(structuredResponse, 'Invalid JSON', 'Manual input was not sent to a local response agent.', error.message);
          return;
        }
        if (!parsedBody || Array.isArray(parsedBody) || typeof parsedBody !== 'object') {
          status.textContent = 'Invalid JSON: request body must be a JSON object. Manual input was not sent to a local response agent.';
          responseOutput.textContent = '';
          renderWorkbenchError(structuredResponse, 'Validation error', 'Request body must be a JSON object.', parsedBody);
          return;
        }
        parsedBody = localResponseAgentPayloadWithSelectedOutputType(parsedBody, outputTypeSelect.value || '');
        bodyInput.value = JSON.stringify(parsedBody, null, 2);
        status.textContent = 'Calling only the manually selected allowlisted local response-agent endpoint.';
        try {
          const response = await fetch(endpointPath, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(parsedBody),
          });
          const responseText = await response.text();
          let responseBody;
          try {
            responseBody = responseText ? JSON.parse(responseText) : {};
          } catch {
            responseBody = { rawResponse: responseText };
          }
          responseOutput.textContent = JSON.stringify(responseBody, null, 2);
          if (response.ok) {
            latestLocalResponseBody = responseBody;
            latestLocalResponseAgent = agent;
            sessionBoardStatus.textContent = 'Latest response is available for manual board capture. Add latest response to session board only after review.';
            renderStructuredLocalResponse(structuredResponse, responseBody);
          } else {
            latestLocalResponseBody = null;
            latestLocalResponseAgent = null;
            renderWorkbenchError(structuredResponse, 'Backend error or validation error', `Local request returned HTTP ${response.status}.`, responseBody);
          }
          status.textContent = response.ok
            ? 'Local response-agent result received. Request and response are not persisted by this dashboard workbench.'
            : `Backend error or validation error: local request failed with HTTP ${response.status}. Request and response are not persisted by this dashboard workbench.`;
        } catch (error) {
          latestLocalResponseBody = null;
          latestLocalResponseAgent = null;
          status.textContent = `Backend error: ${error.message}`;
          responseOutput.textContent = '';
          renderWorkbenchError(structuredResponse, 'Backend error', error.message, null);
        }
      };
      renderAgentOptions();
      loadDiscoveryCatalogMetadata();
      loadCategoryMetadata();
      renderCommandCenter();
      renderPlaybooks();
      renderContextKitPreview();
      renderSessionResultBoard();
      loadSelectedExample();
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
