from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import APP_NAME, VERSION
from .config import load_json_config
from .lan_security import lan_protection_status, lan_setup_status
from .permissions import is_protected_path
from .readiness_snapshot_agent import PrivateAlphaReadinessSnapshotService
from .validation_agent import ValidationAgentService


AGENT_ID = "redacted_diagnostics_agent"
AGENT_NAME = "Redacted Diagnostics Bundle Agent"
MODE = "local_redacted_diagnostics"
MAX_STRING_LENGTH = 500
MAX_ROWS = 10

SECRET_KEYWORDS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "api_key",
    "secret_key",
    "access_token",
    "refresh_token",
    "private_key",
    "client_secret",
    "password",
    "passwd",
    "token",
]

ASSIGNMENT_VALUE_RE = re.compile(
    r"(?P<key>\b(?:"
    + "|".join(re.escape(keyword) for keyword in SECRET_KEYWORDS)
    + r")\b\s*(?:=|:)\s*)(?P<quote>['\"]?)(?P<value>[^'\"\s,#;]+)",
    re.IGNORECASE,
)

TOKEN_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("bearerToken", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{12,}\b", re.IGNORECASE), "Bearer <redacted>"),
    ("githubGhpToken", re.compile(r"\bghp_[A-Za-z0-9_]{12,}\b"), "<redacted-token>"),
    ("githubPatToken", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{12,}\b"), "<redacted-token>"),
    ("openAiStyleToken", re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"), "<redacted-token>"),
    (
        "privateKeyBlock",
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
        "<redacted-private-key>",
    ),
    ("longTokenLookingString", re.compile(r"\b(?=[A-Za-z0-9_]{32,}\b)(?=[A-Za-z0-9_]*\d)[A-Za-z0-9_]{32,}\b"), "<redacted-token>"),
]

PRIVATE_PATH_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("windowsUserPath", re.compile(r"C:\\Users\\[^\\\s\"')]+(?:\\[^\\\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    ("windowsUserPath", re.compile("C:" + r"/Users/[^/\s\"')]+(?:/[^/\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    ("oneDriveOrgPath", re.compile(r"OneDrive\s+-\s+[^\\/\"\r\n]+", re.IGNORECASE), "<redacted-org-path>"),
    ("emailAddress", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\b"), "<redacted-email>"),
    ("linuxUserPath", re.compile(r"/home/[^/\s\"')]+(?:/[^\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    ("macUserPath", re.compile(r"/Users/[^/\s\"')]+(?:/[^\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
]


class RedactedDiagnosticsBundleService:
    def __init__(self, conn: sqlite3.Connection, reports_root: Path, workspace_root: Path, connector_root: Path):
        self.conn = conn
        self.reports_root = reports_root
        self.workspace_root = workspace_root.resolve()
        self.connector_root = connector_root
        self.redaction_counts: dict[str, int] = {}

    def generate_bundle(self) -> dict[str, Any]:
        self.redaction_counts = {}
        generated_at = self._now()
        sections = {
            "appMetadata": self._app_metadata(),
            "dashboardSafetySettingsSummary": self._dashboard_safety_settings_summary(),
            "projectProfileSummary": self._project_profile_summary(),
            "validationEvidenceSummary": self._validation_evidence_summary(),
            "readinessSnapshotMetadata": self._readiness_snapshot_metadata(),
            "securityReviewMetadata": self._security_review_metadata(),
            "recentTaskEventApprovalSummary": self._recent_activity_summary(),
            "connectorBoundarySummary": self._connector_boundary_summary(),
            "diagnosticsLimitations": self._diagnostics_limitations(),
        }
        warnings = self._warnings(sections)
        bundle = {
            "bundleId": f"diagnostics-bundle-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "generatedAt": generated_at,
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "mode": MODE,
            "summary": {
                "localOnly": True,
                "uploaded": False,
                "commandExecution": False,
                "externalServices": False,
                "protectedFileContentsRead": False,
                "certification": False,
                "sectionCount": len(sections),
                "warningCount": len(warnings),
            },
            "sections": sections,
            "warnings": warnings,
            "redactionSummary": self._redaction_summary(),
            "reportId": None,
            "jsonReportId": None,
        }
        return self._sanitize(bundle)

    def dashboard_summary(self) -> dict[str, Any]:
        latest = self.get_latest_report_metadata()
        bundle = self.generate_bundle()
        return {
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "status": "implemented_local_only",
            "mode": MODE,
            "warningCount": len(bundle["warnings"]),
            "sectionCount": len(bundle["sections"]),
            "latestReport": latest,
            "endpoints": {
                "bundle": "/diagnostics/bundle",
                "report": "/diagnostics/bundle/report",
                "latest": "/diagnostics/bundle/latest",
            },
            "localOnly": True,
            "commandExecution": False,
            "externalServices": False,
            "uploads": False,
            "protectedSecretReads": False,
            "certification": False,
        }

    def write_reports(self) -> dict[str, Any]:
        bundle = self.generate_bundle()
        self.reports_root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        markdown_id = f"diagnostics-bundle-{timestamp}.md"
        json_id = f"diagnostics-bundle-{timestamp}.json"
        markdown_path = self._report_path(markdown_id, ".md")
        json_path = self._report_path(json_id, ".json")
        markdown_path.write_text(self.markdown_report(bundle), encoding="utf-8")
        json_bundle = {**bundle, "reportId": markdown_id, "jsonReportId": json_id}
        json_path.write_text(json.dumps(json_bundle, indent=2, sort_keys=True), encoding="utf-8")
        return {
            "reportId": markdown_id,
            "reportPath": str(markdown_path),
            "jsonReportId": json_id,
            "jsonReportPath": str(json_path),
            "contentTypes": ["text/markdown", "application/json"],
            "bundle": json_bundle,
        }

    def get_latest_report_metadata(self) -> dict[str, Any]:
        if not self.reports_root.exists():
            return {"available": False}
        root = self.reports_root.resolve()
        candidates = sorted(
            root.glob("diagnostics-bundle-*.md"),
            key=lambda path: path.stat().st_mtime if path.is_file() else 0,
            reverse=True,
        )
        for path in candidates:
            resolved = path.resolve()
            if not resolved.is_file() or not resolved.is_relative_to(root) or is_protected_path(resolved):
                continue
            stat = resolved.stat()
            json_path = resolved.with_suffix(".json")
            return {
                "available": True,
                "reportId": resolved.name,
                "jsonReportId": json_path.name if json_path.exists() else None,
                "sizeBytes": stat.st_size,
                "updatedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            }
        return {"available": False}

    def markdown_report(self, bundle: dict[str, Any]) -> str:
        sections = bundle["sections"]
        lines = [
            "# Redacted Diagnostics Bundle",
            "",
            "## Generated At",
            str(bundle["generatedAt"]),
            "",
            "## Summary",
            self._json_block(bundle["summary"]),
            "",
            "## App Metadata",
            self._json_block(sections["appMetadata"]),
            "",
            "## Dashboard/Safety/Settings Summary",
            self._json_block(sections["dashboardSafetySettingsSummary"]),
            "",
            "## Project/Profile Summary",
            self._json_block(sections["projectProfileSummary"]),
            "",
            "## Validation Evidence Summary",
            self._json_block(sections["validationEvidenceSummary"]),
            "",
            "## Readiness Snapshot Metadata",
            self._json_block(sections["readinessSnapshotMetadata"]),
            "",
            "## Security Review Metadata",
            self._json_block(sections["securityReviewMetadata"]),
            "",
            "## Recent Task/Event/Approval Summary",
            self._json_block(sections["recentTaskEventApprovalSummary"]),
            "",
            "## Connector Boundary Summary",
            self._json_block(sections["connectorBoundarySummary"]),
            "",
            "## Redaction Summary",
            self._json_block(bundle["redactionSummary"]),
            "",
            "## Warnings",
            self._markdown_list(bundle["warnings"], "None recorded."),
            "",
            "## Limitations",
            self._markdown_list(sections["diagnosticsLimitations"]["items"], "None recorded."),
            "",
            "## Safety Note",
            "This is local diagnostic evidence only. It is not uploaded, not production certification, and not security certification. Secrets should still be rotated if they were ever exposed. Protected files are not read.",
            "",
        ]
        return self._redact_text("\n".join(lines))

    def _app_metadata(self) -> dict[str, Any]:
        return {
            "appName": APP_NAME,
            "version": VERSION,
            "mode": "local",
            "currentReadinessPhase": "post-v0.1C local readiness foundation",
        }

    def _dashboard_safety_settings_summary(self) -> dict[str, Any]:
        return {
            "dashboard": {
                "readOnly": True,
                "guardedByDashboardLanAccess": True,
                "reportGeneration": "local_files_only",
            },
            "safety": {
                "genericShellExecution": False,
                "paidApis": False,
                "browserAutomation": False,
                "connectorExecution": False,
                "destructiveGitAutomation": False,
                "arbitraryProcessKill": False,
                "unsupportedControlsExposed": False,
            },
            "settings": {
                "localFirst": True,
                "settingsEditable": False,
                "paidAiApisEnabled": False,
                "browserAutomationEnabled": False,
                "externalConnectorsEnabled": False,
                "telemetryEnabled": False,
                "remoteWriteAutomationAllowed": False,
                "destructiveAutomationAllowed": False,
            },
            "lanProtection": {
                **self._without_token_values(lan_protection_status()),
                "setup": self._without_token_values(lan_setup_status()),
            },
        }

    def _project_profile_summary(self) -> dict[str, Any]:
        rows = self._rows(
            "select name, created_at from projects order by name",
            ["projectName", "createdAt"],
        )
        return {
            "registeredProjectCount": self._count("projects"),
            "projects": rows,
            "profileSummaryFieldsOnly": True,
            "fullLocalPathsIncluded": False,
            "protectedFileContentsRead": False,
        }

    def _validation_evidence_summary(self) -> dict[str, Any]:
        validation = ValidationAgentService(self.conn, self.reports_root).dashboard_summary()
        latest_report = self._latest_report_metadata("validation-*.md")
        return {
            "runbookCount": validation["availableRunbooksCount"],
            "validationRunCount": self._count("validation_runs"),
            "latestRunStatus": validation["lastRunStatus"],
            "recentRuns": self._safe_recent_validation_runs(),
            "latestValidationReport": latest_report,
            "rawValidationNotesIncluded": False,
            "rawValidationEvidenceIncluded": False,
        }

    def _readiness_snapshot_metadata(self) -> dict[str, Any]:
        readiness = PrivateAlphaReadinessSnapshotService(
            self.conn,
            self.reports_root,
            self.workspace_root,
            self.connector_root,
        )
        summary = readiness.dashboard_summary()
        latest = readiness.get_latest_snapshot_metadata()
        return {
            "agentId": summary["agentId"],
            "mode": summary["mode"],
            "overallVerdict": summary["overallVerdict"],
            "blockerCount": summary["blockerCount"],
            "warningCount": summary["warningCount"],
            "validationEvidenceStatus": summary["validationEvidenceStatus"],
            "securityReviewStatus": summary["securityReviewStatus"],
            "latestReadinessReport": latest,
            "certification": False,
        }

    def _security_review_metadata(self) -> dict[str, Any]:
        latest = self._latest_report_metadata("security-safety-*.md")
        return {
            "latestSecurityReviewReport": latest,
            "latestSecurityReviewVerdict": self._read_report_verdict(latest["reportId"]) if latest else None,
            "securityReviewReportCount": len(self._report_ids("security-safety-*.md")),
            "rawFindingSnippetsIncluded": False,
            "rawSecretSnippetsIncluded": False,
        }

    def _recent_activity_summary(self) -> dict[str, Any]:
        return {
            "taskCount": self._count("tasks"),
            "eventCount": self._count("events"),
            "approvalCount": self._count("approvals"),
            "recentTasks": self._rows(
                """
                select task_id, project_name, agent_id, task_type, status, dry_run, write_capable, created_at, finished_at
                from tasks
                order by created_at desc
                limit 10
                """,
                ["taskId", "projectName", "agentId", "taskType", "status", "dryRun", "writeCapable", "createdAt", "finishedAt"],
            ),
            "recentEvents": self._rows(
                "select event_id, task_id, event_type, created_at from events order by created_at desc limit 10",
                ["eventId", "taskId", "eventType", "createdAt"],
            ),
            "recentApprovals": self._rows(
                """
                select approval_id, task_id, action_type, project_name, risk_level, status, requested_at, resolved_at
                from approvals
                order by requested_at desc
                limit 10
                """,
                ["approvalId", "taskId", "actionType", "projectName", "riskLevel", "status", "requestedAt", "resolvedAt"],
            ),
            "rawCommandOutputIncluded": False,
            "stdoutStderrIncluded": False,
        }

    def _connector_boundary_summary(self) -> dict[str, Any]:
        placeholders = self._placeholder_connector_status()
        agent_manifest = self.connector_root / "agents" / "redacted-diagnostics-agent.json"
        return {
            "redactedDiagnosticsAgentManifestPresent": agent_manifest.exists(),
            "futureConnectorsDisabledPlaceholders": all(
                item.get("implemented") is False and item.get("defaultEnabled") is False for item in placeholders
            ),
            "placeholderConnectorCount": len(placeholders),
            "placeholderConnectors": placeholders,
            "paidApiEnabled": False,
            "browserAutomationEnabled": False,
            "oauthEnabled": False,
            "cloudSyncEnabled": False,
            "telemetryEnabled": False,
        }

    def _diagnostics_limitations(self) -> dict[str, Any]:
        return {
            "items": [
                "Local report only; no upload or external service call is performed.",
                "This is not production readiness certification.",
                "This is not security certification or a complete security audit.",
                "Protected file contents, secret files, token stores, browser/session stores, and raw SQLite bytes are not read.",
                "Raw full logs, raw stdout/stderr dumps, and raw validation evidence are not included.",
                "No command execution, Git action, VirtualBox automation, file deletion, installer creation, telemetry, email, or public posting is performed.",
                "History review and credential rotation remain manual human responsibilities.",
            ]
        }

    def _safe_recent_validation_runs(self) -> list[dict[str, Any]]:
        return self._rows(
            """
            select run_id, runbook_id, status, target_environment, created_at, updated_at, completed_at, summary
            from validation_runs
            order by created_at desc
            limit 5
            """,
            ["runId", "runbookId", "status", "targetEnvironment", "createdAt", "updatedAt", "completedAt", "summary"],
        )

    def _placeholder_connector_status(self) -> list[dict[str, Any]]:
        root = self.connector_root / "placeholders"
        if not root.exists() or not root.is_dir():
            return []
        connectors: list[dict[str, Any]] = []
        for path in sorted(root.glob("*.json")):
            resolved = path.resolve()
            if is_protected_path(resolved):
                continue
            data = load_json_config(resolved)
            connectors.append(
                {
                    "id": data.get("id"),
                    "provider": data.get("provider"),
                    "implemented": data.get("implemented"),
                    "defaultEnabled": data.get("defaultEnabled"),
                    "readinessLevel": data.get("readinessLevel"),
                }
            )
        return connectors

    def _latest_report_metadata(self, pattern: str) -> dict[str, Any] | None:
        if not self.reports_root.exists():
            return None
        root = self.reports_root.resolve()
        candidates = sorted(
            root.glob(pattern),
            key=lambda path: path.stat().st_mtime if path.is_file() else 0,
            reverse=True,
        )
        for path in candidates:
            resolved = path.resolve()
            if not resolved.is_file() or not resolved.is_relative_to(root) or is_protected_path(resolved):
                continue
            stat = resolved.stat()
            return {
                "reportId": resolved.name,
                "sizeBytes": stat.st_size,
                "updatedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            }
        return None

    def _report_ids(self, pattern: str) -> list[str]:
        if not self.reports_root.exists():
            return []
        root = self.reports_root.resolve()
        return [
            path.name
            for path in sorted(root.glob(pattern))
            if path.is_file() and path.resolve().is_relative_to(root) and not is_protected_path(path)
        ]

    def _read_report_verdict(self, report_id: str) -> str | None:
        if not report_id.startswith("security-safety-") or not report_id.endswith(".md"):
            return None
        path = self._report_path(report_id, ".md")
        if not path.exists() or path.stat().st_size > 1_000_000:
            return None
        for index, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
            if line.strip().lower() == "## verdict":
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
                return lines[index + 1].strip() if index + 1 < len(lines) else None
        return None

    def _report_path(self, report_id: str, suffix: str) -> Path:
        if (
            not report_id
            or Path(report_id.replace("\\", "/")).name != report_id
            or not report_id.startswith("diagnostics-bundle-") and not report_id.startswith("security-safety-")
            or not report_id.endswith(suffix)
        ):
            raise PermissionError("report id must be a single generated report name")
        root = self.reports_root.resolve()
        candidate = (root / report_id).resolve()
        if not candidate.is_relative_to(root) or is_protected_path(candidate):
            raise PermissionError("diagnostics report path is outside the approved reports directory")
        return candidate

    def _warnings(self, sections: dict[str, Any]) -> list[str]:
        warnings: list[str] = []
        validation = sections["validationEvidenceSummary"]
        if validation["latestRunStatus"] in {"not_started", "blocked", "failed"}:
            warnings.append(f"Latest validation run status is {validation['latestRunStatus']}.")
        readiness = sections["readinessSnapshotMetadata"]
        if readiness["overallVerdict"] in {"blocked", "needs_review", "needs_evidence"}:
            warnings.append(f"Readiness snapshot verdict is {readiness['overallVerdict']}; human review is required.")
        connector = sections["connectorBoundarySummary"]
        if not connector["futureConnectorsDisabledPlaceholders"]:
            warnings.append("One or more future connector placeholders appears implemented or enabled.")
        return warnings

    def _redaction_summary(self) -> dict[str, Any]:
        return {
            "valuesRedacted": bool(self.redaction_counts),
            "categories": dict(sorted(self.redaction_counts.items())),
            "rawSecretValuesIncluded": False,
            "privateLocalPathsIncluded": False,
            "protectedFileContentsIncluded": False,
            "rawLogsIncluded": False,
        }

    def _sanitize(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): self._sanitize(inner) for key, inner in value.items()}
        if isinstance(value, list):
            return [self._sanitize(inner) for inner in value[:MAX_ROWS]]
        if isinstance(value, tuple):
            return [self._sanitize(inner) for inner in value[:MAX_ROWS]]
        if isinstance(value, str):
            return self._redact_text(value)
        return value

    def _redact_text(self, text: str) -> str:
        original = text
        redacted = ASSIGNMENT_VALUE_RE.sub(lambda match: self._counted_replacement("assignment", f"{match.group('key')}{match.group('quote')}<redacted>"), text)
        for category, pattern, replacement in TOKEN_PATTERNS:
            redacted = pattern.sub(lambda _match, cat=category, repl=replacement: self._counted_replacement(cat, repl), redacted)
        for category, pattern, replacement in PRIVATE_PATH_PATTERNS:
            redacted = pattern.sub(lambda _match, cat=category, repl=replacement: self._counted_replacement(cat, repl), redacted)
        if ".env" in redacted.lower() and ("=" in redacted or ":" in redacted):
            self._increment("envLikeLine")
            redacted = re.sub(r"(?im)^.*\.env.*(?:=|:).*$", "<redacted-env-like-line>", redacted)
        compact = " ".join(redacted.replace("\x00", "").split())
        if len(compact) > MAX_STRING_LENGTH:
            compact = compact[:MAX_STRING_LENGTH] + "...<truncated>"
        if compact != original and not self.redaction_counts:
            self._increment("general")
        return compact

    def _counted_replacement(self, category: str, replacement: str) -> str:
        self._increment(category)
        return replacement

    def _increment(self, category: str) -> None:
        self.redaction_counts[category] = self.redaction_counts.get(category, 0) + 1

    def _without_token_values(self, data: dict[str, Any]) -> dict[str, Any]:
        blocked_keys = {"token", "configuredtoken", "providedtoken", "expectedtoken", "authorization", "header"}
        safe: dict[str, Any] = {}
        for key, value in data.items():
            lowered = key.lower()
            if any(blocked in lowered for blocked in blocked_keys) and not isinstance(value, bool):
                safe[key] = "<redacted>"
            else:
                safe[key] = self._sanitize(value)
        return safe

    def _count(self, table: str) -> int:
        return int(self.conn.execute(f"select count(*) from {table}").fetchone()[0])

    def _rows(self, query: str, names: list[str]) -> list[dict[str, Any]]:
        rows = self.conn.execute(query).fetchall()
        return [self._sanitize(dict(zip(names, row))) for row in rows[:MAX_ROWS]]

    def _json_block(self, value: Any) -> str:
        return "```json\n" + json.dumps(self._sanitize(value), indent=2, sort_keys=True) + "\n```"

    def _markdown_list(self, values: list[str], empty: str) -> str:
        return "\n".join(f"- {self._redact_text(value)}" for value in values) if values else f"- {empty}"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
