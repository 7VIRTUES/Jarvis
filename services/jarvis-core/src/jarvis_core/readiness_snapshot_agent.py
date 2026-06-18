from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .permissions import is_protected_path
from .project_profiles import DEFAULT_RUNTIME_SKIP_DIRS, PROTECTED_FILE_PATTERNS
from .readiness_snapshot_models import AGENT_ID, AGENT_NAME, MODE, ReadinessSection, ReadinessSnapshot
from .validation_agent import ValidationAgentService


PUBLIC_READINESS_DOCS = [
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "docs/public-repo-readiness.md",
    "docs/public-safety-boundaries.md",
]

FOUNDATION_DOCS = [
    "docs/security-safety-agent.md",
    "docs/project-profiles.md",
    "docs/dashboard-profile-security-surfaces.md",
    "docs/validation-agent.md",
    "docs/validation-dashboard-workflow.md",
    "docs/vm-validation-runbook.md",
]

RISKY_PUBLIC_CLAIMS = [
    "production-ready",
    "release ready",
    "installer ready",
    "certified secure",
    "certifies security",
]

BOUNDARY_WORDS = [
    "no ",
    "not ",
    "never ",
    "without ",
    "disabled",
    "placeholder",
    "not included",
    "not implemented",
    "not yet",
    "does not",
    "must not",
    "excluded",
]


class PrivateAlphaReadinessSnapshotService:
    def __init__(self, conn: sqlite3.Connection, reports_root: Path, workspace_root: Path, connector_root: Path):
        self.conn = conn
        self.reports_root = reports_root
        self.workspace_root = workspace_root.resolve()
        self.connector_root = connector_root
        self.validation_agent = ValidationAgentService(conn, reports_root)

    def generate_snapshot(self) -> dict[str, Any]:
        snapshot = self._snapshot()
        return snapshot.to_dict()

    def dashboard_summary(self) -> dict[str, Any]:
        snapshot = self._snapshot()
        sections = snapshot.sections
        validation = sections["validation_evidence"].items
        security = sections["security_safety_review_status"].items
        public_docs = sections["public_repository_readiness"].items
        connector = sections["connector_and_cost_boundary"].items
        return {
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "status": "implemented_local_only",
            "mode": MODE,
            "overallVerdict": snapshot.overall_verdict,
            "blockerCount": len(snapshot.blockers),
            "warningCount": len(snapshot.warnings),
            "validationEvidenceStatus": validation.get("cleanWindowsVmValidationEvidenceStatus"),
            "securityReviewStatus": security.get("latestSecurityReviewStatus"),
            "publicRepoDocsStatus": public_docs.get("docsStatus"),
            "connectorCostBoundaryStatus": connector.get("status"),
            "endpoints": {
                "snapshot": "/readiness/snapshot",
                "report": "/readiness/snapshot/report",
                "latest": "/readiness/snapshot/latest",
            },
            "localOnly": True,
            "commandExecution": False,
            "virtualBoxAutomation": False,
            "installerCreation": False,
            "githubWrites": False,
            "externalServices": False,
            "secretFileContentsRead": False,
            "certification": False,
        }

    def write_markdown_report(self, snapshot_data: dict[str, Any] | None = None) -> dict[str, Any]:
        snapshot = self._snapshot_from_dict(snapshot_data) if snapshot_data else self._snapshot()
        self.reports_root.mkdir(parents=True, exist_ok=True)
        report_id = self._report_id(snapshot)
        report_path = (self.reports_root / report_id).resolve()
        root = self.reports_root.resolve()
        if not report_path.is_relative_to(root) or is_protected_path(report_path):
            raise PermissionError("readiness snapshot report path is outside the approved reports directory")
        snapshot = replace(snapshot, report_id=report_id)
        report_path.write_text(self.markdown_report(snapshot), encoding="utf-8")
        return {
            "reportId": report_id,
            "reportPath": str(report_path),
            "contentType": "text/markdown",
            "snapshot": snapshot.to_dict(),
        }

    def get_latest_snapshot_metadata(self) -> dict[str, Any]:
        metadata = self._latest_report_metadata("private-alpha-readiness-snapshot-*.md")
        if not metadata:
            return {"available": False}
        return {"available": True, **metadata}

    def read_markdown_report(self, report_id: str) -> dict[str, str]:
        path = self._validated_report_path(report_id)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("readiness snapshot report not found")
        return {"reportId": path.name, "contentType": "text/markdown", "content": path.read_text(encoding="utf-8")}

    def markdown_report(self, snapshot: ReadinessSnapshot) -> str:
        lines = [
            "# Private-Alpha Readiness Snapshot",
            "",
            f"- Generated At: {snapshot.generated_at}",
            f"- Agent: {AGENT_NAME} ({AGENT_ID})",
            f"- Mode: {MODE}",
            f"- Overall Verdict: {snapshot.overall_verdict}",
            "",
            "## Summary",
            snapshot.summary,
            "",
        ]
        headings = [
            ("current_milestone_status", "Milestone Status"),
            ("validation_evidence", "Validation Evidence"),
            ("security_safety_review_status", "Security/Safety Review Status"),
            ("project_profile_workspace_boundary_status", "Project Profile / Workspace Boundary Status"),
            ("dashboard_readiness_surfaces", "Dashboard Readiness Surfaces"),
            ("public_repository_readiness", "Public Repository Readiness"),
            ("connector_and_cost_boundary", "Connector and Cost Boundary"),
            ("explicit_non_release_boundary", "Explicit Non-Release Boundary"),
        ]
        for section_id, heading in headings:
            section = snapshot.sections[section_id]
            lines.extend(
                [
                    f"## {heading}",
                    f"- Status: {section.status}",
                    f"- Summary: {section.summary}",
                    "```json",
                    json.dumps(section.items, indent=2),
                    "```",
                    "",
                ]
            )
        lines.extend(
            [
                "## Blockers",
                self._markdown_list(snapshot.blockers, "None recorded."),
                "",
                "## Warnings",
                self._markdown_list(snapshot.warnings, "None recorded."),
                "",
                "## Recommended Next Actions",
                self._markdown_list(snapshot.recommended_next_actions, "No action required."),
                "",
                "## Safety Note",
                "This is not production certification. This is not security certification. This is not an installer or release artifact. Manual review is required before any private-alpha packaging. Clean Windows VM validation still needs real evidence unless already recorded.",
                "",
            ]
        )
        return "\n".join(lines)

    def _snapshot(self) -> ReadinessSnapshot:
        generated_at = self._now()
        sections = {
            "current_milestone_status": self._milestone_section(),
            "validation_evidence": self._validation_section(),
            "security_safety_review_status": self._security_section(),
            "project_profile_workspace_boundary_status": self._project_profile_section(),
            "dashboard_readiness_surfaces": self._dashboard_section(),
            "public_repository_readiness": self._public_repo_section(),
            "connector_and_cost_boundary": self._connector_section(),
            "explicit_non_release_boundary": self._non_release_section(),
        }
        blockers = self._blockers(sections)
        warnings = self._warnings(sections)
        verdict = self._overall_verdict(sections, blockers, warnings)
        return ReadinessSnapshot(
            snapshot_id=f"readiness-snapshot-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            generated_at=generated_at,
            overall_verdict=verdict,
            summary=self._summary(verdict),
            sections=sections,
            blockers=blockers,
            warnings=warnings,
            recommended_next_actions=self._next_actions(verdict, sections, blockers, warnings),
        )

    def _milestone_section(self) -> ReadinessSection:
        foundation_presence = {relative: (self.workspace_root / relative).exists() for relative in FOUNDATION_DOCS}
        present = all(foundation_presence.values())
        return ReadinessSection(
            "current_milestone_status",
            "Current milestone status",
            "present" if present else "needs_review",
            "v0.1A, v0.1B, and v0.1C are closed; post-v0.1C readiness foundations are tracked locally.",
            {
                "v0.1A": "closed",
                "v0.1B": "closed",
                "v0.1C": "closed",
                "postV0.1CFoundationsPresent": present,
                "foundationDocsPresent": foundation_presence,
                "v0.2BroadlyStarted": False,
            },
        )

    def _validation_section(self) -> ReadinessSection:
        runbooks = self.validation_agent.list_runbooks()
        runbook_exists = any(runbook.get("runbookId") == "clean_windows_vm_validation" for runbook in runbooks)
        runs = self.validation_agent.list_runs()
        latest_run = runs[0] if runs else None
        latest_report = self._latest_report_metadata("validation-*.md")
        evidence_status = self._validation_evidence_status(latest_run)
        status = "ready" if evidence_status == "passed" and latest_report else "needs_evidence"
        if evidence_status in {"failed", "blocked"}:
            status = "blocked"
        return ReadinessSection(
            "validation_evidence",
            "Validation evidence",
            status,
            "Manual clean Windows VM validation evidence is summarized without raw notes or evidence values.",
            {
                "validationRunbookExists": runbook_exists,
                "validationRunbooksCount": len(runbooks),
                "validationRunsCount": len(runs),
                "latestValidationRunStatus": latest_run.get("status") if latest_run else "not_started",
                "latestValidationRunId": latest_run.get("runId") if latest_run else None,
                "latestValidationReport": latest_report,
                "cleanWindowsVmValidationEvidenceStatus": evidence_status,
                "rawValidationNotesIncluded": False,
                "rawValidationEvidenceIncluded": False,
            },
        )

    def _security_section(self) -> ReadinessSection:
        manifest = self.workspace_root / "connectors" / "agents" / "security-safety-agent.json"
        latest = self._latest_report_metadata("security-safety-*.md")
        verdict = self._read_report_verdict(latest["reportId"]) if latest else None
        status = "present"
        if verdict in {"needs_review", "blocked"}:
            status = "needs_review"
        elif not latest:
            status = "needs_review"
        return ReadinessSection(
            "security_safety_review_status",
            "Security/Safety Review status",
            status,
            "Security/Safety Review Agent metadata is included without raw finding snippets.",
            {
                "securitySafetyReviewAgentPresent": manifest.exists(),
                "latestSecurityReviewReport": latest,
                "latestSecurityReviewVerdict": verdict,
                "latestSecurityReviewStatus": verdict or "not_run",
                "rawFindingSnippetsIncluded": False,
            },
        )

    def _project_profile_section(self) -> ReadinessSection:
        profile_module = self.workspace_root / "services" / "jarvis-core" / "src" / "jarvis_core" / "project_profiles.py"
        boundary_module = self.workspace_root / "services" / "jarvis-core" / "src" / "jarvis_core" / "workspace_boundary.py"
        return ReadinessSection(
            "project_profile_workspace_boundary_status",
            "Project Profile / Workspace Boundary status",
            "present" if profile_module.exists() and boundary_module.exists() else "needs_review",
            "Workspace boundary metadata is reported without invoking project checks or shell commands.",
            {
                "projectProfileCapabilityPresent": profile_module.exists(),
                "workspaceBoundaryValidatorPresent": boundary_module.exists(),
                "projectProfileDashboardSurfacePresent": self._file_contains(
                    "services/jarvis-core/src/jarvis_core/dashboard.py", "project-profiles"
                ),
                "protectedPatternsActive": bool(PROTECTED_FILE_PATTERNS),
                "protectedPatternCount": len(PROTECTED_FILE_PATTERNS),
                "runtimeSkipDirsActive": bool(DEFAULT_RUNTIME_SKIP_DIRS),
                "runtimeSkipDirs": list(DEFAULT_RUNTIME_SKIP_DIRS),
                "trackedProtectedFilenameCheck": {
                    "implemented": False,
                    "reason": "The readiness snapshot agent does not run git commands.",
                    "contentsRead": False,
                },
            },
        )

    def _dashboard_section(self) -> ReadinessSection:
        dashboard_path = self.workspace_root / "services" / "jarvis-core" / "src" / "jarvis_core" / "dashboard.py"
        text = self._read_small_text(dashboard_path)
        items = {
            "dashboardReportVisibility": "api_reports" in text or "/api/reports" in text,
            "settingsStatusVisibility": "settings-status" in text,
            "projectProfileSurfaces": "project-profiles" in text,
            "securityReviewSurfaces": "security-safety-review" in text,
            "validationWorkflowSurfaces": "validation-agent-status" in text and "Generate local report" in text,
            "readinessSnapshotSurface": "private-alpha-readiness-snapshot" in text,
            "lanDashboardGuardStatus": "require_dashboard_lan_access",
            "snapshotEndpoint": "/readiness/snapshot",
            "reportEndpoint": "/readiness/snapshot/report",
        }
        return ReadinessSection(
            "dashboard_readiness_surfaces",
            "Dashboard readiness surfaces",
            "present" if all(value is True for key, value in items.items() if key.endswith("Visibility") or key.endswith("Surfaces") or key == "readinessSnapshotSurface") else "needs_review",
            "Dashboard readiness visibility is summarized as local status and report controls only.",
            items,
        )

    def _public_repo_section(self) -> ReadinessSection:
        docs = {relative: (self.workspace_root / relative).exists() for relative in PUBLIC_READINESS_DOCS}
        missing = [relative for relative, exists in docs.items() if not exists]
        risky_claims = self._safe_doc_claim_scan(PUBLIC_READINESS_DOCS)
        status = "present" if not missing and not risky_claims else "needs_review"
        return ReadinessSection(
            "public_repository_readiness",
            "Public repository readiness",
            status,
            "Known public-readiness documentation is present and checked for obvious unsafe readiness claims.",
            {
                "docs": docs,
                "missingDocs": missing,
                "docsStatus": "present" if not missing else "missing",
                "productionClaimAmbiguityFound": bool(risky_claims),
                "riskyClaimMatches": risky_claims,
                "contentsRead": "known_safe_docs_only",
            },
        )

    def _connector_section(self) -> ReadinessSection:
        manifests = self._placeholder_connector_status()
        unexpected = [
            item for item in manifests if item.get("implemented") is not False or item.get("defaultEnabled") is not False
        ]
        status = "blocked" if unexpected else "present"
        return ReadinessSection(
            "connector_and_cost_boundary",
            "Connector and cost boundary",
            status,
            "Future connectors and paid/external service boundaries remain disabled or placeholder-only.",
            {
                "status": "placeholder_only" if not unexpected else "unexpected_enabled_or_implemented",
                "futureConnectorsPlaceholderOnly": not unexpected,
                "placeholderManifestsChecked": len(manifests),
                "unexpectedEnabledOrImplemented": unexpected,
                "paidAiApisImplemented": False,
                "browserAutomationImplemented": False,
                "externalAccountConnectorsImplemented": False,
                "oauthImplemented": False,
                "cloudSyncEnabled": False,
                "telemetryEnabled": False,
            },
        )

    def _non_release_section(self) -> ReadinessSection:
        return ReadinessSection(
            "explicit_non_release_boundary",
            "Explicit non-release boundary",
            "present",
            "The snapshot is readiness evidence only and does not create release or installer artifacts.",
            {
                "installerArtifact": False,
                "productionTauri": False,
                "fullPairing": False,
                "qrMobilePairing": False,
                "productionFirstRunSetup": False,
                "publicReleaseBuild": False,
                "autoUpdater": False,
                "telemetry": False,
                "codeSigning": False,
                "githubReleaseAutomation": False,
                "certifiesProductionReadiness": False,
                "certifiesSecurity": False,
            },
        )

    def _validation_evidence_status(self, latest_run: dict[str, Any] | None) -> str:
        if not latest_run:
            return "missing"
        status = str(latest_run.get("status") or "not_started")
        if status == "passed":
            return "passed"
        if status in {"failed", "blocked"}:
            return status
        return "partial"

    def _blockers(self, sections: dict[str, ReadinessSection]) -> list[str]:
        blockers: list[str] = []
        validation_status = sections["validation_evidence"].items["cleanWindowsVmValidationEvidenceStatus"]
        if validation_status in {"failed", "blocked"}:
            blockers.append(f"Clean Windows VM validation evidence is {validation_status}.")
        connector = sections["connector_and_cost_boundary"].items
        if connector["unexpectedEnabledOrImplemented"]:
            blockers.append("One or more future connector placeholders are implemented or enabled unexpectedly.")
        public_docs = sections["public_repository_readiness"].items
        if not public_docs["docs"].get("docs/public-safety-boundaries.md", False):
            blockers.append("Public safety boundary documentation is missing.")
        return blockers

    def _warnings(self, sections: dict[str, ReadinessSection]) -> list[str]:
        warnings: list[str] = []
        validation = sections["validation_evidence"].items
        if validation["cleanWindowsVmValidationEvidenceStatus"] in {"missing", "partial"}:
            warnings.append("Clean Windows VM validation evidence is missing or incomplete.")
        if not validation["latestValidationReport"]:
            warnings.append("No local validation report has been generated yet.")
        security = sections["security_safety_review_status"].items
        if security["latestSecurityReviewStatus"] in {"not_run", "needs_review", "blocked"}:
            warnings.append("Security/Safety Review metadata needs human review before private-alpha packaging planning.")
        public_docs = sections["public_repository_readiness"].items
        if public_docs["missingDocs"]:
            warnings.append("Public-readiness documentation is missing: " + ", ".join(public_docs["missingDocs"]))
        if public_docs["productionClaimAmbiguityFound"]:
            warnings.append("Potential production/release wording ambiguity found in known public docs.")
        return warnings

    def _overall_verdict(
        self,
        sections: dict[str, ReadinessSection],
        blockers: list[str],
        warnings: list[str],
    ) -> str:
        if blockers:
            return "blocked"
        security_status = sections["security_safety_review_status"].items["latestSecurityReviewStatus"]
        public_docs = sections["public_repository_readiness"].items
        if security_status in {"needs_review", "blocked"} or public_docs["missingDocs"] or public_docs["productionClaimAmbiguityFound"]:
            return "needs_review"
        validation = sections["validation_evidence"].items
        if validation["cleanWindowsVmValidationEvidenceStatus"] in {"missing", "partial"} or not validation["latestValidationReport"]:
            return "needs_evidence"
        return "ready_for_manual_vm_validation"

    def _summary(self, verdict: str) -> str:
        if verdict == "blocked":
            return "A readiness blocker must be resolved before private-alpha packaging planning continues."
        if verdict == "needs_review":
            return "Local readiness foundations are present, but human review is needed before relying on the snapshot."
        if verdict == "needs_evidence":
            return "Local readiness foundations are present, but clean Windows VM validation evidence or reports are still missing."
        return "Local readiness foundations are present for manual VM validation planning; this is not production readiness."

    def _next_actions(
        self,
        verdict: str,
        sections: dict[str, ReadinessSection],
        blockers: list[str],
        warnings: list[str],
    ) -> list[str]:
        if blockers:
            return ["Resolve blockers without weakening safety boundaries.", "Regenerate the local readiness snapshot report."]
        actions: list[str] = []
        validation = sections["validation_evidence"].items
        if validation["cleanWindowsVmValidationEvidenceStatus"] in {"missing", "partial"}:
            actions.append("Record real clean Windows VM validation evidence through the manual Validation Agent workflow.")
        if not validation["latestValidationReport"]:
            actions.append("Generate a local validation report after evidence is recorded.")
        if warnings:
            actions.append("Review warnings before any future private-alpha packaging plan.")
        if verdict == "ready_for_manual_vm_validation":
            actions.append("Use this snapshot as planning evidence only; manual review is still required.")
        return actions or ["No snapshot action is required beyond preserving manual review boundaries."]

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

    def _read_report_verdict(self, report_id: str) -> str | None:
        try:
            text = self.read_security_report_text(report_id)
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            return None
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if line.strip().lower() == "## verdict" and index + 1 < len(lines):
                return lines[index + 1].strip() or None
        return None

    def read_security_report_text(self, report_id: str) -> str:
        decoded = unquote(report_id).strip()
        relative = Path(decoded.replace("\\", "/"))
        if (
            not decoded
            or decoded != report_id
            or relative.is_absolute()
            or len(relative.parts) != 1
            or ".." in relative.parts
            or relative.suffix.lower() != ".md"
            or not relative.name.startswith("security-safety-")
        ):
            raise PermissionError("security report id must be a single generated Markdown report name")
        root = self.reports_root.resolve()
        candidate = (root / relative.name).resolve()
        if not candidate.is_relative_to(root) or is_protected_path(candidate):
            raise PermissionError("security report path is outside the approved reports directory")
        return candidate.read_text(encoding="utf-8")

    def _placeholder_connector_status(self) -> list[dict[str, Any]]:
        placeholder_root = self.connector_root / "placeholders"
        if not placeholder_root.exists() or not placeholder_root.is_dir():
            return []
        statuses: list[dict[str, Any]] = []
        for path in sorted(placeholder_root.glob("*.json")):
            resolved = path.resolve()
            if is_protected_path(resolved):
                continue
            try:
                data = json.loads(resolved.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                statuses.append({"path": self._safe_relative(resolved), "implemented": None, "defaultEnabled": None})
                continue
            statuses.append(
                {
                    "path": self._safe_relative(resolved),
                    "id": data.get("id"),
                    "provider": data.get("provider"),
                    "implemented": data.get("implemented"),
                    "defaultEnabled": data.get("defaultEnabled"),
                }
            )
        return statuses

    def _safe_doc_claim_scan(self, relatives: list[str]) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for relative in relatives:
            path = self.workspace_root / relative
            text = self._read_small_text(path)
            if not text:
                continue
            for line_number, line in enumerate(text.splitlines(), start=1):
                lowered = line.lower()
                if any(term in lowered for term in RISKY_PUBLIC_CLAIMS) and not any(word in lowered for word in BOUNDARY_WORDS):
                    matches.append({"path": relative, "line": line_number, "match": self._compact(line)})
        return matches

    def _file_contains(self, relative: str, needle: str) -> bool:
        return needle in self._read_small_text(self.workspace_root / relative)

    def _read_small_text(self, path: Path) -> str:
        if not path.exists() or not path.is_file() or is_protected_path(path):
            return ""
        try:
            if path.stat().st_size > 1_000_000:
                return ""
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def _snapshot_from_dict(self, data: dict[str, Any]) -> ReadinessSnapshot:
        sections_data = data.get("sections", {}) if isinstance(data, dict) else {}
        sections = {
            key: ReadinessSection(
                section_id=str(value.get("section_id") or value.get("sectionId") or key),
                title=str(value.get("title") or key),
                status=str(value.get("status") or "unknown"),
                summary=str(value.get("summary") or ""),
                items=dict(value.get("items") or {}),
            )
            for key, value in sections_data.items()
            if isinstance(value, dict)
        }
        if set(sections) != {
            "current_milestone_status",
            "validation_evidence",
            "security_safety_review_status",
            "project_profile_workspace_boundary_status",
            "dashboard_readiness_surfaces",
            "public_repository_readiness",
            "connector_and_cost_boundary",
            "explicit_non_release_boundary",
        }:
            return self._snapshot()
        return ReadinessSnapshot(
            snapshot_id=str(data.get("snapshot_id") or data.get("snapshotId") or "readiness-snapshot"),
            generated_at=str(data.get("generated_at") or data.get("generatedAt") or self._now()),
            overall_verdict=str(data.get("overall_verdict") or data.get("overallVerdict") or "needs_review"),
            summary=str(data.get("summary") or ""),
            sections=sections,
            blockers=list(data.get("blockers") or []),
            warnings=list(data.get("warnings") or []),
            recommended_next_actions=list(data.get("recommended_next_actions") or data.get("recommendedNextActions") or []),
            report_id=data.get("report_id") or data.get("reportId"),
        )

    def _validated_report_path(self, report_id: str) -> Path:
        decoded = unquote(report_id).strip()
        relative = Path(decoded.replace("\\", "/"))
        if (
            not decoded
            or decoded != report_id
            or relative.is_absolute()
            or len(relative.parts) != 1
            or ".." in relative.parts
            or relative.suffix.lower() != ".md"
            or not relative.name.startswith("private-alpha-readiness-snapshot-")
        ):
            raise PermissionError("readiness snapshot report id must be a single generated Markdown report name")
        root = self.reports_root.resolve()
        candidate = (root / relative.name).resolve()
        if not candidate.is_relative_to(root) or is_protected_path(candidate):
            raise PermissionError("readiness snapshot report path is outside the approved reports directory")
        return candidate

    def _report_id(self, snapshot: ReadinessSnapshot) -> str:
        safe_snapshot = re.sub(r"[^A-Za-z0-9_.-]+", "-", snapshot.snapshot_id).strip("-") or "readiness-snapshot"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"private-alpha-{safe_snapshot}-{timestamp}.md"

    def _safe_relative(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.workspace_root)).replace("\\", "/")
        except ValueError:
            return path.name

    def _markdown_list(self, values: list[str], empty: str) -> str:
        return "\n".join(f"- {value}" for value in values) if values else f"- {empty}"

    def _compact(self, line: str) -> str:
        return " ".join(line.strip().split())[:240]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()
