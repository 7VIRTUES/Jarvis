from __future__ import annotations

import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .permissions import is_protected_path
from .validation_models import RUN_STATUSES, STEP_STATUSES, ValidationRun, ValidationRunbook, ValidationStep, ValidationStepResult


MAX_STORED_TEXT_LENGTH = 4000

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

TOKEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{12,}\b", re.IGNORECASE)),
    ("github_ghp_token", re.compile(r"\bghp_[A-Za-z0-9_]{12,}\b")),
    ("github_pat_token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{12,}\b")),
    ("openai_style_token", re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b")),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL)),
]


def clean_windows_vm_runbook() -> ValidationRunbook:
    return ValidationRunbook(
        runbook_id="clean_windows_vm_validation",
        title="Clean Windows VM Validation",
        description=(
            "Manual evidence runbook for validating Jarvis PC Local in a clean Windows VM before private-alpha packaging."
        ),
        target_environment="Clean Windows VM, local-only Jarvis checkout",
        steps=[
            _step(
                "confirm_vm_environment",
                "Confirm VM environment",
                "Record Windows version, CPU, RAM, disk size/free space, and whether VirtualBox Guest Additions are installed.",
                "Windows and VM resource details are captured without collecting secrets.",
                "environment_notes",
                True,
                "environment",
            ),
            _step(
                "confirm_prerequisites",
                "Confirm prerequisites",
                "Manually check Git, Python, pip, and whether Codex CLI is present or explicitly missing.",
                "Prerequisite versions or missing status are recorded.",
                "version_notes",
                True,
                "install",
            ),
            _step(
                "clone_repo",
                "Clone repo",
                "Clone 7VIRTUES/Jarvis, confirm branch main, and confirm clean git status.",
                "Jarvis is on main with a clean working tree.",
                "command_summary",
                True,
                "install",
            ),
            _step(
                "python_setup",
                "Python setup",
                "Create a virtual environment and install documented Python requirements manually.",
                "Virtual environment and requirements installation complete, or blockers recorded.",
                "setup_notes",
                True,
                "install",
            ),
            _step(
                "unit_integration_tests",
                "Unit/integration tests",
                "Run pytest manually and record the current expected result for this validation date.",
                "Pytest result is recorded as date-specific validation evidence, not permanent truth.",
                "test_summary",
                True,
                "tests",
            ),
            _step(
                "service_startup",
                "Service startup",
                "Start uvicorn manually and verify the health endpoint responds.",
                "Local service starts and /health returns safe status.",
                "endpoint_notes",
                True,
                "service",
            ),
            _step(
                "dashboard_loopback",
                "Dashboard loopback",
                "Open the dashboard from loopback and verify summary endpoints return safe status.",
                "Dashboard loads locally without requiring a token from loopback.",
                "dashboard_notes",
                True,
                "dashboard",
            ),
            _step(
                "profile_security_dashboard",
                "Project profile/security review dashboard",
                "Verify project profiles endpoint works and registered-project security review action works.",
                "Profile and security review surfaces operate on registered projects only.",
                "dashboard_notes",
                True,
                "security",
            ),
            _step(
                "lan_token_boundary",
                "LAN token boundary",
                "Verify loopback works without token, LAN access is denied without token, LAN access works with token, and setup pages stay loopback-only.",
                "LAN/token boundary behaves as documented.",
                "lan_test_notes",
                True,
                "LAN",
            ),
            _step(
                "future_connector_boundary",
                "Future connector boundary",
                "Confirm future connectors remain disabled placeholders with implemented=false and defaultEnabled=false.",
                "No future connector is enabled or implemented unexpectedly.",
                "manifest_summary",
                True,
                "connectors",
            ),
            _step(
                "public_repo_safety",
                "Public repo safety",
                "Confirm no paid APIs, browser automation, production installer claims, telemetry, or public posting capabilities are present.",
                "Public safety boundaries remain visible and intact.",
                "safety_notes",
                True,
                "security",
            ),
            _step(
                "backup_readiness",
                "Backup/readiness",
                "Confirm the project can be backed up externally and that a local validation report is produced.",
                "External backup readiness is noted and this validation report is generated locally.",
                "report_notes",
                True,
                "backup",
            ),
        ],
        safety_notes=[
            "This runbook records manual validation evidence only.",
            "Do not paste .env contents, private keys, token values, or full sensitive log dumps.",
            "The Validation Agent does not run commands, use VM-control tooling, install dependencies, produce packaging artifactss, push, merge, or delete files.",
        ],
        non_goals=[
            "VirtualBox automation",
            "Installer creation",
            "Production Tauri work",
            "Pairing wizard or QR/mobile pairing",
            "Paid AI APIs",
            "networked services",
            "GitHub write actions",
        ],
    )



def clean_windows_vm_runbook_pack() -> list[ValidationRunbook]:
    return [
        _manual_vm_runbook("clean_vm_core_service_smoke", "Clean VM Core Service Smoke", "Manual smoke evidence for the Jarvis core service in a clean Windows VM.", "Clean Windows VM with Jarvis repo cloned manually", [("record_environment", "Record environment", "Capture Windows edition, Python availability, repo branch, and virtual environment status from manual observation.", "Evidence fields: windows_version, python_status, repo_branch, venv_status. Pass: required context is recorded. Fail: required context is missing. Warning: context is partial or ambiguous.", "environment_fields", "environment"), ("record_service_health", "Record service health", "Start the service through the approved manual workflow and record whether the local health response is safe.", "Evidence fields: startup_status, health_status, blocker_summary. Pass: local health status is safe. Fail: service cannot start. Warning: service starts with documented caveats.", "service_smoke_fields", "service"), ("record_no_completion_claim", "Record scope boundary", "Confirm the evidence is a smoke check only and not full validation completion.", "Evidence fields: scope_note, remaining_validation. Pass: boundary is recorded. Fail: evidence claims full completion. Warning: boundary note needs clarification.", "scope_fields", "safety")]),
        _manual_vm_runbook("clean_vm_dashboard_loopback_smoke", "Clean VM Dashboard Loopback Smoke", "Manual evidence for dashboard loopback access in a clean Windows VM.", "Clean Windows VM with Jarvis dashboard started manually", [("record_loopback_page", "Record loopback page access", "Open the dashboard on loopback through a browser and record page availability.", "Evidence fields: loopback_url, page_status, visible_sections. Pass: dashboard loads on loopback. Fail: dashboard is unavailable. Warning: dashboard loads with missing sections.", "loopback_fields", "dashboard"), ("record_safe_summary", "Record safe summary visibility", "Review that dashboard summary content is safe status metadata only.", "Evidence fields: summary_visible, unsafe_content_seen, notes. Pass: only safe metadata is visible. Fail: unsafe content is exposed. Warning: reviewer is unsure about one field.", "summary_fields", "dashboard")]),
        _manual_vm_runbook("clean_vm_lan_guard_smoke", "Clean VM LAN Guard Smoke", "Manual evidence that LAN dashboard access remains guarded in a clean Windows VM.", "Clean Windows VM on a local network test context", [("record_loopback_baseline", "Record loopback baseline", "Confirm loopback dashboard access behavior before checking LAN behavior.", "Evidence fields: loopback_status, local_address, notes. Pass: loopback behavior is understood. Fail: baseline cannot be established. Warning: baseline has caveats.", "loopback_baseline_fields", "LAN"), ("record_lan_without_token", "Record LAN denied without token", "Attempt the documented manual LAN access check without a token and record the denial result.", "Evidence fields: lan_address_used, denied_without_token, response_summary. Pass: LAN access is denied. Fail: LAN access is allowed without token. Warning: network condition prevents a clear result.", "lan_guard_fields", "LAN"), ("record_no_token_values", "Record token handling boundary", "Confirm evidence does not include token values or authorization headers.", "Evidence fields: token_values_included, redaction_note. Pass: no token values included. Fail: token values were pasted. Warning: evidence needs redaction review.", "token_boundary_fields", "security")]),
        _manual_vm_runbook("clean_vm_codex_available_scenario", "Clean VM Codex Available Scenario", "Manual evidence for the scenario where Codex is available in the clean Windows VM.", "Clean Windows VM with Codex availability reviewed manually", [("record_codex_presence", "Record Codex availability", "Record whether Codex is available without exposing account, token, or secret details.", "Evidence fields: codex_available, version_or_channel_summary, account_details_excluded. Pass: availability is recorded safely. Fail: secret/account detail is exposed. Warning: availability is unclear.", "codex_presence_fields", "codex"), ("record_local_boundaries", "Record local workflow boundaries", "Confirm Codex use remains inside approved local Jarvis workflow boundaries.", "Evidence fields: local_only_confirmed, external_account_actions, notes. Pass: boundaries are preserved. Fail: external account automation is used. Warning: boundary needs review.", "codex_boundary_fields", "codex")]),
        _manual_vm_runbook("clean_vm_codex_missing_scenario", "Clean VM Codex Missing Scenario", "Manual evidence for the scenario where Codex is not available in the clean Windows VM.", "Clean Windows VM with Codex absence reviewed manually", [("record_codex_missing", "Record Codex missing state", "Record that Codex is unavailable without attempting automated setup from Jarvis.", "Evidence fields: codex_available, blocker_summary, setup_attempted_by_jarvis. Pass: missing state is recorded safely. Fail: Jarvis attempted setup. Warning: availability is uncertain.", "codex_missing_fields", "codex"), ("record_blocker_handling", "Record blocker handling", "Confirm the blocker is captured for planning rather than treated as validation completion.", "Evidence fields: blocker_recorded, completion_claimed, next_review_needed. Pass: blocker is clear. Fail: completion is claimed. Warning: blocker needs detail.", "blocker_fields", "codex")]),
        _manual_vm_runbook("clean_vm_future_connectors_disabled", "Clean VM Future Connectors Disabled", "Manual evidence that future connector placeholders remain disabled in a clean Windows VM.", "Clean Windows VM with Jarvis connector manifests reviewed manually", [("record_connector_manifest_summary", "Record connector manifest summary", "Review known connector manifest metadata and record implemented/default-enabled states.", "Evidence fields: manifests_reviewed, unexpected_enabled, unexpected_implemented. Pass: placeholders remain disabled. Fail: future placeholder is enabled or implemented. Warning: manifest shape needs review.", "connector_manifest_fields", "connectors"), ("record_no_connector_execution", "Record connector execution boundary", "Confirm no connector account action or networked service action is performed.", "Evidence fields: connector_actions_performed, external_services_used, notes. Pass: no such actions occurred. Fail: connector action occurred. Warning: reviewer is unsure.", "connector_boundary_fields", "connectors")]),
        _manual_vm_runbook("clean_vm_backup_restore_reminder", "Clean VM Backup Restore Reminder", "Manual reminder evidence for backup and restore readiness around clean Windows VM validation.", "Clean Windows VM validation planning context", [("record_backup_readiness_review", "Record backup readiness review", "Review backup readiness checklist status and record whether backup scope is understood.", "Evidence fields: backup_scope_understood, protected_files_excluded, notes. Pass: scope and exclusions are understood. Fail: protected files are included. Warning: scope needs review.", "backup_readiness_fields", "backup"), ("record_restore_test_plan", "Record restore-test plan", "Record the manual restore-test plan or blocker before relying on VM validation evidence.", "Evidence fields: restore_test_planned, restore_blocker, follow_up_owner. Pass: plan or blocker is recorded. Fail: no restore consideration exists. Warning: plan lacks owner/date.", "restore_plan_fields", "backup")]),
    ]


def _manual_vm_runbook(
    runbook_id: str,
    title: str,
    purpose: str,
    target_environment: str,
    step_specs: list[tuple[str, str, str, str, str, str]],
) -> ValidationRunbook:
    return ValidationRunbook(
        runbook_id=runbook_id,
        title=title,
        description=purpose,
        target_environment=target_environment,
        steps=[
            _step(step_id, step_title, instructions, expected_result, evidence_type, True, category)
            for step_id, step_title, instructions, expected_result, evidence_type, category in step_specs
        ],
        safety_notes=[
            "Manual-only validation evidence template.",
            "Do not paste secrets, token values, private keys, protected file contents, or raw sensitive logs.",
            "The Validation Agent does not run commands, install software, control or infer VM environment automatically, create artifacts, transfer evidence, or certify readiness.",
        ],
        non_goals=[
            "Command execution",
            "Software setup automation",
            "VM automation or VM state detection",
            "Artifact creation",
            "Release work",
            "networked services",
            "Upload or sharing behavior",
            "Readiness certification",
        ],
    )
class ValidationAgentService:
    def __init__(self, conn: sqlite3.Connection, reports_root: Path):
        self.conn = conn
        self.reports_root = reports_root
        runbooks = [clean_windows_vm_runbook(), *clean_windows_vm_runbook_pack()]
        self._runbooks = {runbook.runbook_id: runbook for runbook in runbooks}

    def list_runbooks(self) -> list[dict[str, Any]]:
        return [runbook.to_dict() for runbook in self._runbooks.values()]

    def get_runbook(self, runbook_id: str) -> dict[str, Any]:
        return self._runbook(runbook_id).to_dict()

    def create_run(self, runbook_id: str, target_environment: str | None = None) -> dict[str, Any]:
        runbook = self._runbook(runbook_id)
        now = self._now()
        run_id = f"validation-run-{uuid.uuid4().hex[:12]}"
        environment = self._redact(target_environment or runbook.target_environment)
        self.conn.execute(
            """
            insert into validation_runs (
              run_id, runbook_id, status, target_environment, created_at, updated_at, started_at, completed_at, summary
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (run_id, runbook_id, "in_progress", environment, now, now, now, None, ""),
        )
        for step in runbook.steps:
            self.conn.execute(
                """
                insert into validation_step_results (
                  run_id, step_id, status, notes, redacted_evidence, updated_at
                ) values (?, ?, ?, ?, ?, ?)
                """,
                (run_id, step.step_id, "not_started", "", "", now),
            )
        self.conn.commit()
        return self.get_run(run_id)

    def list_runs(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            select run_id, runbook_id, status, target_environment, created_at, updated_at, started_at, completed_at, summary
            from validation_runs
            order by created_at desc
            """
        ).fetchall()
        return [self._run_from_row(row, include_steps=False).to_dict() for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any]:
        return self._run(run_id, include_steps=True).to_dict()

    def update_step_result(
        self,
        run_id: str,
        step_id: str,
        status: str,
        notes: str | None = None,
        evidence: str | None = None,
    ) -> dict[str, Any]:
        run = self._run(run_id, include_steps=False)
        runbook = self._runbook(run.runbook_id)
        if step_id not in {step.step_id for step in runbook.steps}:
            raise KeyError("validation step not found")
        if status not in STEP_STATUSES:
            raise ValueError(f"invalid validation step status: {status}")
        now = self._now()
        redacted_notes = self._redact(notes or "")
        redacted_evidence = self._redact(evidence or "")
        self.conn.execute(
            """
            update validation_step_results
            set status = ?, notes = ?, redacted_evidence = ?, updated_at = ?
            where run_id = ? and step_id = ?
            """,
            (status, redacted_notes, redacted_evidence, now, run_id, step_id),
        )
        self.conn.execute(
            "update validation_runs set status = ?, updated_at = ? where run_id = ?",
            ("in_progress", now, run_id),
        )
        self.conn.commit()
        return self.get_run(run_id)

    def complete_run(self, run_id: str) -> dict[str, Any]:
        run = self._run(run_id, include_steps=True)
        runbook = self._runbook(run.runbook_id)
        status = self._completion_status(runbook, run.step_results)
        now = self._now()
        summary = self._completion_summary(status, run.step_results)
        self.conn.execute(
            """
            update validation_runs
            set status = ?, updated_at = ?, completed_at = ?, summary = ?
            where run_id = ?
            """,
            (status, now, now, summary, run_id),
        )
        self.conn.commit()
        return self.get_run(run_id)

    def write_markdown_report(self, run_id: str) -> dict[str, str]:
        run = self._run(run_id, include_steps=True)
        runbook = self._runbook(run.runbook_id)
        self.reports_root.mkdir(parents=True, exist_ok=True)
        report_id = self._report_id(run)
        report_path = (self.reports_root / report_id).resolve()
        root = self.reports_root.resolve()
        if not report_path.is_relative_to(root) or is_protected_path(report_path):
            raise PermissionError("validation report path is outside the approved reports directory")
        content = self.markdown_report(run, runbook)
        report_path.write_text(content, encoding="utf-8")
        return {"reportId": report_path.name, "reportPath": str(report_path), "contentType": "text/markdown"}

    def read_markdown_report(self, report_id: str) -> dict[str, str]:
        path = self._validated_report_path(report_id)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError("validation report not found")
        return {"reportId": path.name, "contentType": "text/markdown", "content": path.read_text(encoding="utf-8")}

    def dashboard_summary(self) -> dict[str, Any]:
        runs = self.list_runs()[:5]
        last_run = runs[0] if runs else None
        return {
            "agentId": "validation_agent",
            "agentName": "Validation Agent",
            "status": "implemented_local_only",
            "availableRunbooksCount": len(self._runbooks),
            "recentRuns": runs,
            "lastRunStatus": last_run["status"] if last_run else "not_started",
            "endpoints": {
                "runbooks": "/validation/runbooks",
                "runs": "/validation/runs",
                "runDetailPattern": "/validation/runs/{run_id}",
                "stepUpdatePattern": "/validation/runs/{run_id}/steps/{step_id}",
                "completePattern": "/validation/runs/{run_id}/complete",
                "reportPattern": "/validation/runs/{run_id}/report",
            },
            "localOnly": True,
            "commandExecution": False,
            "virtualBoxAutomation": False,
            "installerCreation": False,
            "externalServices": False,
            "gitWrites": False,
            "fileDeletion": False,
            "protectedFileContentsRead": False,
        }

    def markdown_report(self, run: ValidationRun, runbook: ValidationRunbook) -> str:
        failed_or_blocked = [result for result in run.step_results if result.status in {"failed", "blocked"}]
        lines = [
            "# Validation Run Summary",
            "",
            f"- Run ID: {run.run_id}",
            f"- Agent: validation_agent",
            f"- Created: {run.created_at}",
            f"- Updated: {run.updated_at}",
            f"- Completed: {run.completed_at or 'not completed'}",
            "",
            "## Runbook",
            f"- ID: {runbook.runbook_id}",
            f"- Title: {runbook.title}",
            f"- Description: {runbook.description}",
            "",
            "## Target Environment",
            run.target_environment or "Not recorded.",
            "",
            "## Verdict/Status",
            run.status,
            "",
            "## Step Results",
            "",
        ]
        step_titles = {step.step_id: step.title for step in runbook.steps}
        for result in run.step_results:
            lines.extend(
                [
                    f"### {step_titles.get(result.step_id, result.step_id)}",
                    f"- Step ID: {result.step_id}",
                    f"- Status: {result.status}",
                    f"- Updated: {result.updated_at}",
                    f"- Notes: {result.notes or 'None recorded.'}",
                    f"- Evidence: {result.redacted_evidence or 'None recorded.'}",
                    "",
                ]
            )
        lines.extend(
            [
                "## Failed/Blocked Steps",
                "\n".join(f"- {result.step_id}: {result.status}" for result in failed_or_blocked) or "- None recorded.",
                "",
                "## Evidence Notes",
                "Evidence and notes are manually supplied and redacted before storage and report generation.",
                "",
                "## Safety Boundaries",
                "\n".join(f"- {note}" for note in runbook.safety_notes),
                "- No command execution, VirtualBox automation, installer creation, networked service calls, Git writes, or file deletion is performed by this agent.",
                "",
                "## Next Actions",
                self._next_actions(run.status, failed_or_blocked),
                "",
                "## Limitation Note",
                "This report is validation evidence only. It is not certification, warranty, or production-readiness approval.",
                "",
            ]
        )
        return "\n".join(lines)

    def _runbook(self, runbook_id: str) -> ValidationRunbook:
        runbook = self._runbooks.get(runbook_id)
        if not runbook:
            raise KeyError("validation runbook not found")
        return runbook

    def _run(self, run_id: str, include_steps: bool) -> ValidationRun:
        row = self.conn.execute(
            """
            select run_id, runbook_id, status, target_environment, created_at, updated_at, started_at, completed_at, summary
            from validation_runs
            where run_id = ?
            """,
            (run_id,),
        ).fetchone()
        if not row:
            raise KeyError("validation run not found")
        return self._run_from_row(row, include_steps=include_steps)

    def _run_from_row(self, row: sqlite3.Row | tuple[Any, ...], include_steps: bool) -> ValidationRun:
        step_results: list[ValidationStepResult] = []
        if include_steps:
            rows = self.conn.execute(
                """
                select step_id, status, notes, redacted_evidence, updated_at
                from validation_step_results
                where run_id = ?
                order by id
                """,
                (row[0],),
            ).fetchall()
            step_results = [ValidationStepResult(*step_row) for step_row in rows]
        return ValidationRun(
            run_id=row[0],
            runbook_id=row[1],
            status=row[2],
            target_environment=row[3],
            created_at=row[4],
            updated_at=row[5],
            started_at=row[6],
            completed_at=row[7],
            summary=row[8],
            step_results=step_results,
        )

    def _completion_status(self, runbook: ValidationRunbook, results: list[ValidationStepResult]) -> str:
        by_step = {result.step_id: result for result in results}
        required_results = [by_step.get(step.step_id) for step in runbook.steps if step.required]
        if any(result and result.status == "failed" for result in required_results):
            return "failed"
        if any(result and result.status == "blocked" for result in required_results):
            return "blocked"
        if all(result and result.status in {"passed", "skipped"} for result in required_results):
            return "passed"
        return "blocked"

    def _completion_summary(self, status: str, results: list[ValidationStepResult]) -> str:
        counts = {step_status: 0 for step_status in STEP_STATUSES}
        for result in results:
            counts[result.status] = counts.get(result.status, 0) + 1
        return (
            f"Validation run completed as {status}: "
            f"{counts.get('passed', 0)} passed, {counts.get('failed', 0)} failed, "
            f"{counts.get('blocked', 0)} blocked, {counts.get('skipped', 0)} skipped, "
            f"{counts.get('not_started', 0)} not started."
        )

    def _next_actions(self, status: str, failed_or_blocked: list[ValidationStepResult]) -> str:
        if status == "passed":
            return "- Preserve the report with local private-alpha evidence and continue with the approved next plan."
        if failed_or_blocked:
            return "\n".join(f"- Review `{result.step_id}` and rerun the manual validation step after fixes." for result in failed_or_blocked)
        return "- Review incomplete required steps before treating the run as passed."

    def _report_id(self, run: ValidationRun) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_run = re.sub(r"[^A-Za-z0-9_.-]+", "-", run.run_id).strip("-") or "validation-run"
        return f"validation-{safe_run}-{timestamp}.md"

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
            or not relative.name.startswith("validation-")
        ):
            raise PermissionError("validation report id must be a single generated Markdown report name")
        root = self.reports_root.resolve()
        candidate = (root / relative.name).resolve()
        if not candidate.is_relative_to(root) or is_protected_path(candidate):
            raise PermissionError("validation report path is outside the approved reports directory")
        return candidate

    def _redact(self, text: str) -> str:
        compacted = self._compact(text)
        redacted = ASSIGNMENT_VALUE_RE.sub(lambda match: f"{match.group('key')}{match.group('quote')}<redacted>", compacted)
        for category, pattern in TOKEN_PATTERNS:
            replacement = "Bearer <redacted>" if category == "bearer_token" else "<redacted-token>"
            redacted = pattern.sub(replacement, redacted)
        return redacted[:MAX_STORED_TEXT_LENGTH]

    def _compact(self, text: str) -> str:
        lines = []
        for raw_line in text.replace("\x00", "").splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.lower().startswith(("-----begin ", "-----end ")):
                lines.append("<redacted-private-key-boundary>")
            elif ".env" in line.lower() and ("=" in line or ":" in line):
                lines.append("<redacted-env-like-line>")
            else:
                lines.append(" ".join(line.split()))
        return "\n".join(lines)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


def _step(
    step_id: str,
    title: str,
    instructions: str,
    expected_result: str,
    evidence_type: str,
    required: bool,
    category: str,
) -> ValidationStep:
    return ValidationStep(
        step_id=step_id,
        title=title,
        instructions=instructions,
        expected_result=expected_result,
        evidence_type=evidence_type,
        required=required,
        category=category,
    )
