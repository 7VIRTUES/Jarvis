from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Any
from uuid import uuid4

from .approvals import ApprovalQueue
from .file_data_agent import FileDataAgentService
from .permissions import check_action
from .project_registry import ProjectRegistry
from .project_text_reader import ProjectTextReader
from .report_tool import ReportTool
from .runtime import ActionRequest, SafeActionRuntime
from .tasks import TaskQueue
from .time_utils import utc_now


SUPPORTED_ASSISTANT_ACTION_TYPES: list[str] = [
    "inspect_project",
    "read_project_text_files",
    "write_report",
    "modify_project_files_with_codex",
]

ACTION_DISPLAY_NAMES: dict[str, str] = {
    "inspect_project": "Inspect Registered Project (Read-Only)",
    "read_project_text_files": "Read Project Text Files (Read-Only)",
    "write_report": "Create Markdown Report (Non-Destructive)",
    "modify_project_files_with_codex": "Controlled Coding with Codex",
}

ACTION_TOOL_IDS: dict[str, str] = {
    "inspect_project": "filesystem_tool",
    "read_project_text_files": "filesystem_tool",
    "write_report": "report_tool",
    "modify_project_files_with_codex": "codex_tool",
}

ACTION_TASK_TYPES: dict[str, str] = {
    "inspect_project": "inspect",
    "read_project_text_files": "read_project_text_files",
    "write_report": "report",
    "modify_project_files_with_codex": "plan",
}

CODEX_CODING_SIGNALS: tuple[str, ...] = (
    "modify files with codex",
    "write code with codex",
    "edit code with codex",
    "coding change",
    "execute codex plan",
    "apply code changes",
    "implement code change",
    "change code",
    "refactor code",
    "fix bug in code",
    "modify project files",
    "conservative codex",
    "prepare codex plan",
)

INSPECT_PROJECT_SIGNALS: tuple[str, ...] = (
    "inspect project",
    "review project",
    "analyze project",
    "check project",
    "inspect repository",
    "inspect repo",
    "examine project",
    "inspect codebase",
    "audit project",
    "scan project",
    "check repository",
    "analyze repository",
    "examine codebase",
)

READ_PROJECT_FILES_SIGNALS: tuple[str, ...] = (
    "read project file",
    "read source file",
    "open source file",
    "inspect source file",
    "show file contents",
    "review these files",
    "read code",
    "inspect code file",
    "read file",
    "view source code",
    "show file content",
    "read source code",
    "view project file",
    "read files",
)

WRITE_REPORT_SIGNALS: tuple[str, ...] = (
    "prepare report",
    "create report",
    "write report",
    "produce report",
    "save report",
    "generate report",
    "export report",
    "draft report",
    "compile report",
    "summary report",
)

UNSUPPORTED_INTENT_PATTERNS: list[tuple[str, str]] = [
    (r"\b(send|write|draft)\s+email\b", "Email sending is outside Unified Assistant capabilities."),
    (r"\b(post|tweet|publish)\s+(to|on)\s+(twitter|x|social|linkedin|facebook|reddit)\b", "Social posting is outside Unified Assistant capabilities."),
    (r"\b(buy|purchase|order|checkout|pay)\b", "Purchasing and payment actions are outside Unified Assistant capabilities."),
    (r"\b(book|reserve)\s+(hotel|flight|trip|car|table)\b", "Booking and external reservations are outside Unified Assistant capabilities."),
    (r"\b(delete|remove|erase|rm\s+-rf|del\s+/s|rmdir)\b", "Destructive file deletion is blocked by policy."),
    (r"\b(run|execute)\s+(powershell|pwsh|cmd|bash|sh|script|command|terminal)\b", "Generic shell command execution is not available from Unified Assistant in this pass."),
    (r"\b(connect|call|api|fetch)\s+(connector|webhook|oauth)\b", "External connector execution is not available in local mode."),
]


class AssistantActionBridge:
    """Supervised bridge connecting Unified Assistant responses to Safe Action Runtime validation and real action execution."""

    def __init__(
        self,
        projects: ProjectRegistry,
        tasks: TaskQueue,
        runtime: SafeActionRuntime,
        approvals: ApprovalQueue,
        file_data_agent: FileDataAgentService | None = None,
        report_tool: ReportTool | None = None,
        project_text_reader: ProjectTextReader | None = None,
        workspace_root: Path | None = None,
    ) -> None:
        self.projects = projects
        self.tasks = tasks
        self.runtime = runtime
        self.approvals = approvals
        self.file_data_agent = file_data_agent
        self.report_tool = report_tool
        self.project_text_reader = project_text_reader
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else None
        self._active_executions: set[str] = set()
        self._execution_lock = threading.Lock()

    def get_capabilities(self) -> dict[str, Any]:
        return {
            "implemented": True,
            "realExecutionImplemented": True,
            "supportedActionTypes": [
                {
                    "actionType": "inspect_project",
                    "displayLabel": ACTION_DISPLAY_NAMES["inspect_project"],
                    "description": "Read-only inspection and structure check of a registered Jarvis project workspace.",
                    "targetType": "registered_project_name",
                    "toolId": "filesystem_tool",
                    "riskLevel": "low",
                    "dryRunSupported": True,
                    "realExecutionSupported": True,
                    "readOnly": True,
                    "nonDestructive": True,
                    "createsNewFileOnly": False,
                    "executionPermitted": True,
                },
                {
                    "actionType": "read_project_text_files",
                    "displayLabel": ACTION_DISPLAY_NAMES["read_project_text_files"],
                    "description": "Read bounded text and source files (max 5 files, 256 KB) from a registered project workspace.",
                    "targetType": "registered_project_name",
                    "toolId": "filesystem_tool",
                    "riskLevel": "low",
                    "dryRunSupported": True,
                    "realExecutionSupported": True,
                    "readOnly": True,
                    "nonDestructive": True,
                    "createsNewFileOnly": False,
                    "executionPermitted": True,
                },
                {
                    "actionType": "write_report",
                    "displayLabel": ACTION_DISPLAY_NAMES["write_report"],
                    "description": "Create a new bounded Markdown report file in the fixed Jarvis reports directory without modifying project files.",
                    "targetType": "registered_project_name",
                    "toolId": "report_tool",
                    "riskLevel": "low",
                    "dryRunSupported": True,
                    "realExecutionSupported": True,
                    "readOnly": False,
                    "nonDestructive": True,
                    "createsNewFileOnly": True,
                    "executionPermitted": True,
                },
                {
                    "actionType": "modify_project_files_with_codex",
                    "displayLabel": ACTION_DISPLAY_NAMES["modify_project_files_with_codex"],
                    "description": "Prepare and explicitly execute one approved extreme-budget Codex change against selected existing files.",
                    "targetType": "registered_project_name",
                    "toolId": "codex_tool",
                    "riskLevel": "high",
                    "dryRunSupported": True,
                    "realExecutionSupported": True,
                    "readOnly": False,
                    "nonDestructive": False,
                    "createsNewFileOnly": False,
                    "executionPermitted": True,
                },
            ],
            "unsupportedActionTypes": [
                "command",
                "shell_execution",
                "powershell_execution",
                "file_deletion",
                "file_write_unsupervised",
                "file_overwrite",
                "file_mutation",
                "browser_automation",
                "email_sending",
                "public_posting",
                "purchases_or_payments",
                "external_connectors",
            ],
            "boundaries": [
                "Unified Assistant actions are strictly supervised, user-reviewed, and user-confirmed.",
                "inspect_project performs read-only workspace metadata inspections.",
                "read_project_text_files reads up to 5 user-selected text/source files (256 KB max) without modifying workspace files.",
                "write_report writes new Markdown files exclusively to the fixed Jarvis reports directory without modifying project source.",
                "modify_project_files_with_codex runs one supervised Codex process against 1-10 approved existing files with post-execution diff verification.",
                "Only registered project workspaces within the allowed root can be selected as targets.",
                "Real execution requires matching successful dry-run verification proof or explicit approval.",
                "SafeActionRuntime creates execution-gate receipts before any action runs.",
                "No arbitrary shell commands or external network requests occur.",
            ],
        }

    def detect_intent(
        self,
        request_text: str,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        cleaned = str(request_text or "").strip().lower()
        if not cleaned:
            return {
                "actionable": False,
                "supported": True,
                "detectedActionType": None,
                "detectedProjectName": None,
                "signals": [],
                "confidence": "none",
                "explanation": "No text provided. Jarvis answered in response-only mode.",
            }

        # Check for explicit unsupported action requests first
        for pattern, explanation in UNSUPPORTED_INTENT_PATTERNS:
            if re.search(pattern, cleaned):
                return {
                    "actionable": False,
                    "supported": False,
                    "detectedActionType": None,
                    "detectedProjectName": None,
                    "signals": [f"unsupported_pattern: '{pattern}'"],
                    "confidence": "strong",
                    "explanation": f"{explanation} Jarvis answered in response-only mode; nothing was executed.",
                }

        matched_signals: list[str] = []
        candidate_action: str | None = None

        # Check codex coding signals
        for sig in CODEX_CODING_SIGNALS:
            if sig in cleaned:
                matched_signals.append(f"coding_signal: '{sig}'")
                candidate_action = "modify_project_files_with_codex"
                break

        # Check read_project_text_files signals
        if not candidate_action:
            for sig in READ_PROJECT_FILES_SIGNALS:
                if sig in cleaned:
                    matched_signals.append(f"read_signal: '{sig}'")
                    candidate_action = "read_project_text_files"

        # Check inspect_project signals if not explicitly reading files
        if not candidate_action:
            for sig in INSPECT_PROJECT_SIGNALS:
                if sig in cleaned:
                    matched_signals.append(f"inspect_signal: '{sig}'")
                    candidate_action = "inspect_project"

        # Check write_report signals
        for sig in WRITE_REPORT_SIGNALS:
            if sig in cleaned:
                matched_signals.append(f"report_signal: '{sig}'")
                if candidate_action and candidate_action != "write_report":
                    candidate_action = None  # Ambiguous
                else:
                    candidate_action = "write_report"

        # Check registered project mentions
        detected_project: str | None = None
        registered_projects = self.projects.list_projects()
        for proj in registered_projects:
            proj_name = proj["name"].lower()
            if re.search(rf"\b{re.escape(proj_name)}\b", cleaned):
                detected_project = proj["name"]
                matched_signals.append(f"registered_project: '{proj['name']}'")
                break

        # Check agent association
        if not candidate_action:
            if agent_id in ("file_data_agent", "local_review_agent"):
                if "project" in cleaned or "repo" in cleaned or "code" in cleaned or detected_project:
                    candidate_action = "inspect_project"
                    matched_signals.append(f"agent_affinity: {agent_id}")
            elif agent_id in ("local_research_agent", "local_business_agent", "local_planning_agent"):
                if "report" in cleaned or "summary" in cleaned or "brief" in cleaned:
                    candidate_action = "write_report"
                    matched_signals.append(f"agent_affinity: {agent_id}")
            elif agent_id in ("coding_agent", "local_coding_agent", "local_refactoring_agent", "local_debugging_agent"):
                candidate_action = "modify_project_files_with_codex"
                matched_signals.append(f"agent_affinity: {agent_id}")

        if not candidate_action and not matched_signals:
            return {
                "actionable": False,
                "supported": True,
                "detectedActionType": None,
                "detectedProjectName": detected_project,
                "signals": [],
                "confidence": "none",
                "explanation": "Request was informational. Jarvis provided a standard response with no action required.",
            }

        confidence = "strong" if len(matched_signals) >= 2 else "moderate" if matched_signals else "weak"

        return {
            "actionable": bool(candidate_action),
            "supported": True,
            "detectedActionType": candidate_action,
            "detectedProjectName": detected_project,
            "signals": matched_signals,
            "confidence": confidence,
            "explanation": (
                f"Identified candidate supervised action: '{candidate_action}' on project '{detected_project or 'unspecified'}'. "
                "You can explicitly prepare a structured proposal and validate it in dry-run mode."
                if candidate_action
                else "Action intent detected but action type is ambiguous. Select a specific action type below."
            ),
        }

    def prepare_proposal(
        self,
        *,
        request_text: str,
        action_type: str,
        project_name: str | None = None,
        selected_relative_paths: list[str] | None = None,
        source_agent_id: str = "unified_assistant",
        source_response_id: str | None = None,
        source_turn_index: int | None = None,
        report_title: str | None = None,
        custom_notes: str | None = None,
    ) -> dict[str, Any]:
        normalized_action = str(action_type or "").strip()
        if normalized_action not in SUPPORTED_ASSISTANT_ACTION_TYPES:
            raise ValueError(f"Action type '{normalized_action}' is not supported by Assistant Action Bridge.")

        proposal_id = str(uuid4())
        created_at = utc_now()
        missing_fields: list[str] = []

        # Resolve registered project
        safe_target: str | None = None
        resolved_project_name: str | None = None
        if project_name and project_name.strip():
            proj = self.projects.get_project(project_name.strip())
            if not proj:
                missing_fields.append("projectName (project not found in registry)")
            else:
                resolved_project_name = proj["name"]
                safe_target = proj["name"]
        else:
            missing_fields.append("projectName")

        clean_paths: list[str] = []
        if normalized_action == "read_project_text_files":
            if selected_relative_paths:
                clean_paths = [p.strip() for p in selected_relative_paths if isinstance(p, str) and p.strip()]
            if not clean_paths:
                missing_fields.append("selectedRelativePaths (at least 1 file must be selected)")

        # Non-executing policy preview
        policy_result = check_action(normalized_action, target=resolved_project_name)
        policy_preview_data = {
            "actionType": normalized_action,
            "projectName": resolved_project_name,
            "status": policy_result.status,
            "allowed": policy_result.allowed,
            "reason": policy_result.reason,
            "riskLevel": "low",
            "dryRunSupported": True,
            "realExecutionSupported": True,
        }

        # Determine readiness state
        is_ready = len(missing_fields) == 0 and policy_result.status != "blocked"
        if not resolved_project_name:
            readiness_status = "needs_project"
            readiness_notes = "A registered project target must be selected before dry-run validation."
        elif normalized_action == "read_project_text_files" and not clean_paths:
            readiness_status = "needs_files"
            readiness_notes = "Select 1 to 5 safe project files to read before dry-run validation."
        elif policy_result.status == "blocked":
            readiness_status = "policy_blocked"
            readiness_notes = f"Action is blocked by Jarvis policy: {policy_result.reason}"
        elif policy_result.status == "approval_required":
            readiness_status = "policy_approval_required"
            readiness_notes = "Action requires explicit policy approval during dry-run validation."
        else:
            readiness_status = "ready_for_policy_preview"
            readiness_notes = "Ready for supervised dry-run validation."

        reason_text = (
            f"Supervised action proposal prepared from Assistant turn: {normalized_action} "
            f"on project '{resolved_project_name or 'unselected'}'."
        )
        if clean_paths:
            reason_text += f" Target files ({len(clean_paths)}): {', '.join(clean_paths[:3])}"
        if custom_notes:
            reason_text += f" Notes: {custom_notes.strip()}"

        return {
            "proposalId": proposal_id,
            "sourceResponseId": source_response_id,
            "sourceAgentId": source_agent_id,
            "sourceTurnIndex": source_turn_index,
            "actionType": normalized_action,
            "displayLabel": ACTION_DISPLAY_NAMES.get(normalized_action, normalized_action),
            "projectName": resolved_project_name,
            "safeTarget": safe_target,
            "selectedRelativePaths": clean_paths,
            "selectedFileCount": len(clean_paths),
            "proposedToolId": ACTION_TOOL_IDS.get(normalized_action, "filesystem_tool"),
            "riskLevel": "low",
            "reason": reason_text,
            "reportTitle": report_title.strip() if report_title else None,
            "policyPreview": policy_preview_data,
            "readiness": {
                "isReady": is_ready,
                "missingFields": missing_fields,
                "readinessNotes": readiness_notes,
                "readinessStatus": readiness_status,
            },
            "status": readiness_status,
            "dryRunSupported": True,
            "realExecutionSupported": True,
            "userReviewRequired": True,
            "createdAt": created_at,
        }

    def policy_preview(
        self,
        action_type: str,
        project_name: str | None = None,
    ) -> dict[str, Any]:
        normalized_action = str(action_type or "").strip()
        if normalized_action not in SUPPORTED_ASSISTANT_ACTION_TYPES:
            return {
                "actionType": normalized_action,
                "projectName": project_name,
                "status": "blocked",
                "allowed": False,
                "reason": f"Action type '{normalized_action}' is not supported by Assistant Action Bridge.",
                "riskLevel": "high",
                "dryRunSupported": False,
                "realExecutionSupported": False,
            }

        resolved_name: str | None = None
        if project_name and project_name.strip():
            proj = self.projects.get_project(project_name.strip())
            if not proj:
                return {
                    "actionType": normalized_action,
                    "projectName": project_name,
                    "status": "blocked",
                    "allowed": False,
                    "reason": f"Project '{project_name}' is not registered in Jarvis project registry.",
                    "riskLevel": "medium",
                    "dryRunSupported": False,
                    "realExecutionSupported": False,
                }
            resolved_name = proj["name"]

        result = check_action(normalized_action, target=resolved_name)
        return {
            "actionType": normalized_action,
            "projectName": resolved_name,
            "status": result.status,
            "allowed": result.allowed,
            "reason": result.reason,
            "riskLevel": "low",
            "dryRunSupported": True,
            "realExecutionSupported": True,
        }

    def validate_dry_run(
        self,
        *,
        action_type: str,
        project_name: str,
        selected_relative_paths: list[str] | None = None,
        proposal_id: str | None = None,
        source_agent_id: str = "unified_assistant",
        source_response_id: str | None = None,
        report_title: str | None = None,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        normalized_action = str(action_type or "").strip()
        if normalized_action not in SUPPORTED_ASSISTANT_ACTION_TYPES:
            raise ValueError(f"Action type '{normalized_action}' is not supported by Assistant Action Bridge.")

        normalized_project = str(project_name or "").strip()
        proj = self.projects.get_project(normalized_project)
        if not proj:
            raise ValueError(f"Project '{normalized_project}' is not registered in Jarvis project registry.")

        tool_id = ACTION_TOOL_IDS.get(normalized_action, "filesystem_tool")
        task_type = ACTION_TASK_TYPES.get(normalized_action, "inspect")

        proposed_actions = [
            {
                "tool_id": tool_id,
                "action_type": normalized_action,
                "target": proj["name"],
                "risk_level": "low",
            }
        ]

        risk_plan = {
            "risk_level": "low",
            "reason": f"Supervised Assistant dry-run validation for {normalized_action} on {proj['name']}",
        }

        # CREATE SUPERVISED DRY-RUN TASK (DRY RUN IS HARD-CODED TRUE)
        task = self.tasks.create_task(
            project_name=proj["name"],
            agent_id=source_agent_id,
            task_type=task_type,
            autonomy_level="supervised",
            dry_run=True,  # Server-enforced invariant
            write_capable=False,
            proposed_actions=proposed_actions,
            risk_plan=risk_plan,
        )

        task_id = task["task_id"]
        receipts = self.runtime.list_receipts(task_id=task_id)
        task_approvals = [a for a in self.approvals.list_approvals() if a.get("task_id") == task_id]

        status_text: str
        if task["status"] == "succeeded":
            if normalized_action == "read_project_text_files":
                status_text = "Dry run validated. No project files have been read."
            else:
                status_text = "Dry run validated. No local action was executed."
        elif task["status"] == "blocked":
            status_text = "Proposal blocked by Jarvis policy. Nothing was executed."
        elif task["status"] == "waiting_for_approval":
            status_text = "Approval is required before any future execution path. Nothing was executed."
        else:
            status_text = f"Task finished with status: {task['status']}. Nothing was executed."

        return {
            "proposalId": proposal_id or str(uuid4()),
            "sourceResponseId": source_response_id,
            "sourceAgentId": source_agent_id,
            "actionType": normalized_action,
            "displayLabel": ACTION_DISPLAY_NAMES.get(normalized_action, normalized_action),
            "projectName": proj["name"],
            "selectedRelativePaths": selected_relative_paths or [],
            "taskId": task_id,
            "task": task,
            "receipts": receipts,
            "approvals": task_approvals,
            "dryRunOnly": True,
            "executed": False,
            "realExecutionAvailable": task["status"] == "succeeded",
            "summary": status_text,
            "validatedAt": utc_now(),
        }

    def verify_dry_run_proof(
        self,
        dry_run_task_id: str,
        project_name: str,
        expected_receipt_id: str | None = None,
        expected_action_type: str = "inspect_project",
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        task = self.tasks.get_task(dry_run_task_id)
        if not task:
            raise ValueError(f"Dry-run task '{dry_run_task_id}' not found.")
        if not task.get("dry_run"):
            raise ValueError("Specified task is not a dry-run task.")
        if task.get("status") != "succeeded":
            raise ValueError(f"Dry-run task status is '{task.get('status')}', but must be 'succeeded'.")
        if task.get("project_name") != project_name:
            raise ValueError(
                f"Dry-run task project '{task.get('project_name')}' does not match requested project '{project_name}'."
            )

        if expected_action_type == "inspect_project":
            if task.get("task_type") not in ("inspect", "inspect_project"):
                raise ValueError(f"Dry-run task type '{task.get('task_type')}' is not an inspection task.")
        elif expected_action_type == "read_project_text_files":
            if task.get("task_type") not in ("read_project_text_files", "read", "inspect"):
                raise ValueError(f"Dry-run task type '{task.get('task_type')}' is not a project text read task.")
        elif expected_action_type == "write_report":
            if task.get("task_type") not in ("report", "write_report"):
                raise ValueError(f"Dry-run task type '{task.get('task_type')}' is not a report task.")
        else:
            raise ValueError(f"Unknown expected action type: {expected_action_type}")

        receipts = self.runtime.list_receipts(task_id=dry_run_task_id)
        matching_receipt: dict[str, Any] | None = None
        for r in receipts:
            if r.get("action_type") == expected_action_type and r.get("target") == project_name:
                if expected_receipt_id:
                    if r.get("receipt_id") == expected_receipt_id:
                        matching_receipt = r
                        break
                else:
                    matching_receipt = r
                    break

        if not matching_receipt:
            raise ValueError(f"No matching valid dry-run receipt found for {expected_action_type} on '{project_name}'.")
        if matching_receipt.get("blocked"):
            raise PermissionError(f"Dry-run receipt was blocked by policy: {matching_receipt.get('reason')}")
        if matching_receipt.get("approval_required") and not matching_receipt.get("approved"):
            raise PermissionError(f"Dry-run receipt requires unresolved approval: {matching_receipt.get('reason')}")
        if not matching_receipt.get("approved"):
            raise PermissionError("Dry-run receipt was not approved by policy.")

        return task, matching_receipt

    def execute_read_only(
        self,
        *,
        dry_run_task_id: str,
        project_name: str,
        expected_receipt_id: str | None = None,
        confirmation: str = "",
        source_agent_id: str = "unified_assistant",
        source_response_id: str | None = None,
        source_turn_index: int | None = None,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        # 1. Exact confirmation requirement
        if confirmation.strip() != "EXECUTE READ-ONLY INSPECTION":
            raise ValueError("Explicit confirmation string 'EXECUTE READ-ONLY INSPECTION' is required.")

        # 2. Concurrency / duplicate execution protection
        with self._execution_lock:
            if dry_run_task_id in self._active_executions:
                raise ValueError(f"Execution for dry-run task '{dry_run_task_id}' is already in progress.")
            self._active_executions.add(dry_run_task_id)

        real_task_id: str | None = None
        gate_receipt_id: str | None = None

        try:
            # 3. Dry-run proof verification
            _, dry_run_receipt = self.verify_dry_run_proof(
                dry_run_task_id=dry_run_task_id,
                project_name=project_name,
                expected_receipt_id=expected_receipt_id,
                expected_action_type="inspect_project",
            )

            # 4. Re-resolve registered project at execution time
            proj = self.projects.get_project(project_name.strip())
            if not proj:
                raise KeyError(f"Registered project '{project_name}' no longer found in registry.")

            project_root = Path(proj["path"]).expanduser().resolve()
            if not project_root.exists() or not project_root.is_dir():
                raise FileNotFoundError(f"Project directory '{project_root}' does not exist or is not a directory.")

            # 5. Re-validate workspace boundary
            if self.workspace_root is not None and not project_root.is_relative_to(self.workspace_root):
                raise PermissionError("Project root escapes the allowed workspace root.")

            # 6. Create real execution task record (dry_run=False)
            real_task = self.tasks.create_task(
                project_name=proj["name"],
                agent_id=source_agent_id,
                task_type="inspect",
                autonomy_level="supervised",
                dry_run=False,
                write_capable=False,
                proposed_actions=[{
                    "tool_id": "filesystem_tool",
                    "action_type": "inspect_project",
                    "target": proj["name"],
                    "risk_level": "low",
                }],
                risk_plan={
                    "risk_level": "low",
                    "reason": f"Supervised read-only inspection execution for {proj['name']}",
                },
            )
            real_task_id = real_task["task_id"]

            # 7. SafeActionRuntime execution gate receipt
            gate_receipt = self.runtime.validate(
                ActionRequest(
                    task_id=real_task_id,
                    agent_id=source_agent_id,
                    tool_id="filesystem_tool",
                    action_type="inspect_project",
                    target=proj["name"],
                    risk_level="low",
                )
            )
            gate_receipt_id = gate_receipt.receipt_id

            if gate_receipt.blocked:
                self.tasks.block_task(real_task_id, reason=gate_receipt.reason)
                self.runtime.finalize_execution_receipt(
                    gate_receipt.receipt_id,
                    result_status="execution_failed",
                    execution_note=f"Blocked: {gate_receipt.reason}",
                    task_id=real_task_id,
                )
                return {
                    "executed": False,
                    "status": "blocked",
                    "taskId": real_task_id,
                    "receiptId": gate_receipt.receipt_id,
                    "summary": f"Execution blocked by policy: {gate_receipt.reason}",
                    "inspectionResult": None,
                }

            if gate_receipt.approval_required and not gate_receipt.approved:
                self.tasks.block_task(real_task_id, reason="Approval required before execution")
                return {
                    "executed": False,
                    "status": "waiting_for_approval",
                    "taskId": real_task_id,
                    "receiptId": gate_receipt.receipt_id,
                    "summary": "Approval required before execution. Nothing was executed.",
                    "inspectionResult": None,
                }

            # 8. Start task lifecycle
            self.tasks.start_task(real_task_id, mode="read_only")

            # 9. Perform trusted read-only inspection
            if self.file_data_agent:
                raw_summary = self.file_data_agent.local_summary(proj["name"])
            else:
                service = FileDataAgentService(self.projects, self.workspace_root or project_root.parent)
                raw_summary = service.local_summary(proj["name"])

            # Bounded summary data
            bounded_result = {
                "projectName": raw_summary.get("projectName", proj["name"]),
                "projectRoot": raw_summary.get("projectRoot", str(project_root)),
                "scannedFiles": raw_summary.get("scannedFiles", 0),
                "skippedFiles": raw_summary.get("skippedFiles", 0),
                "skippedDirs": raw_summary.get("skippedDirs", 0),
                "skippedDirList": raw_summary.get("skippedDirList", []),
                "protectedSkippedFiles": raw_summary.get("protectedSkippedFiles", 0),
                "runtimeSkippedDirs": raw_summary.get("runtimeSkippedDirs", 0),
                "fileTypeCounts": raw_summary.get("fileTypeCounts", {}),
                "docsDetected": raw_summary.get("docsDetected", []),
                "warnings": raw_summary.get("warnings", []),
                "limitations": raw_summary.get("limitations", []),
            }

            # 10. Finalize execution receipt
            finalized_receipt = self.runtime.finalize_execution_receipt(
                gate_receipt.receipt_id,
                result_status="executed_read_only",
                execution_note=f"Scanned {bounded_result['scannedFiles']} files safely",
                task_id=real_task_id,
            )

            # 11. Complete task lifecycle
            self.tasks.succeed_task(
                real_task_id,
                summary=f"Read-only project inspection executed successfully. Scanned {bounded_result['scannedFiles']} files.",
            )

            return {
                "executed": True,
                "status": "succeeded",
                "actionType": "inspect_project",
                "toolId": "filesystem_tool",
                "projectName": proj["name"],
                "taskId": real_task_id,
                "receiptId": finalized_receipt.get("receipt_id", gate_receipt.receipt_id),
                "dryRunTaskId": dry_run_task_id,
                "sourceResponseId": source_response_id,
                "sourceTurnIndex": source_turn_index,
                "summary": f"Read-only inspection executed successfully on '{proj['name']}'.",
                "inspectionResult": bounded_result,
                "executedAt": utc_now(),
            }
        except Exception as exc:
            if real_task_id:
                try:
                    self.tasks.fail_task(real_task_id, error=str(exc))
                except Exception:
                    pass
                if gate_receipt_id:
                    try:
                        self.runtime.finalize_execution_receipt(
                            gate_receipt_id,
                            result_status="execution_failed",
                            execution_note=str(exc),
                            task_id=real_task_id,
                        )
                    except Exception:
                        pass
            raise
        finally:
            with self._execution_lock:
                self._active_executions.discard(dry_run_task_id)

    def execute_project_text_read(
        self,
        *,
        dry_run_task_id: str,
        project_name: str,
        relative_paths: list[str],
        expected_receipt_id: str | None = None,
        confirmation: str = "",
        source_agent_id: str = "unified_assistant",
        source_response_id: str | None = None,
        source_turn_index: int | None = None,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        # 1. Exact confirmation requirement
        if confirmation.strip() != "READ LOCAL PROJECT FILES":
            raise ValueError("Explicit confirmation string 'READ LOCAL PROJECT FILES' is required.")

        if not relative_paths:
            raise ValueError("At least 1 relative file path must be specified.")

        # 2. Concurrency / duplicate execution protection
        with self._execution_lock:
            if dry_run_task_id in self._active_executions:
                raise ValueError(f"Execution for dry-run task '{dry_run_task_id}' is already in progress.")
            self._active_executions.add(dry_run_task_id)

        real_task_id: str | None = None
        gate_receipt_id: str | None = None

        try:
            # 3. Dry-run proof verification
            _, dry_run_receipt = self.verify_dry_run_proof(
                dry_run_task_id=dry_run_task_id,
                project_name=project_name,
                expected_receipt_id=expected_receipt_id,
                expected_action_type="read_project_text_files",
            )

            # 4. Re-resolve registered project at execution time
            proj = self.projects.get_project(project_name.strip())
            if not proj:
                raise KeyError(f"Registered project '{project_name}' no longer found in registry.")

            project_root = Path(proj["path"]).expanduser().resolve()
            if not project_root.exists() or not project_root.is_dir():
                raise FileNotFoundError(f"Project directory '{project_root}' does not exist or is not a directory.")

            # 5. Re-validate workspace boundary
            if self.workspace_root is not None and not project_root.is_relative_to(self.workspace_root):
                raise PermissionError("Project root escapes the allowed workspace root.")

            # 6. Create real execution task record (dry_run=False, write_capable=False)
            real_task = self.tasks.create_task(
                project_name=proj["name"],
                agent_id=source_agent_id,
                task_type="read_project_text_files",
                autonomy_level="supervised",
                dry_run=False,
                write_capable=False,
                proposed_actions=[{
                    "tool_id": "filesystem_tool",
                    "action_type": "read_project_text_files",
                    "target": proj["name"],
                    "risk_level": "low",
                }],
                risk_plan={
                    "risk_level": "low",
                    "reason": f"Supervised project source reading for {proj['name']} ({len(relative_paths)} files)",
                },
            )
            real_task_id = real_task["task_id"]

            # 7. SafeActionRuntime execution gate receipt
            gate_receipt = self.runtime.validate(
                ActionRequest(
                    task_id=real_task_id,
                    agent_id=source_agent_id,
                    tool_id="filesystem_tool",
                    action_type="read_project_text_files",
                    target=proj["name"],
                    risk_level="low",
                )
            )
            gate_receipt_id = gate_receipt.receipt_id

            if gate_receipt.blocked:
                self.tasks.block_task(real_task_id, reason=gate_receipt.reason)
                self.runtime.finalize_execution_receipt(
                    gate_receipt.receipt_id,
                    result_status="execution_failed",
                    execution_note=f"Blocked: {gate_receipt.reason}",
                    task_id=real_task_id,
                )
                return {
                    "executed": False,
                    "status": "blocked",
                    "taskId": real_task_id,
                    "receiptId": gate_receipt.receipt_id,
                    "summary": f"Execution blocked by policy: {gate_receipt.reason}",
                    "readResult": None,
                }

            if gate_receipt.approval_required and not gate_receipt.approved:
                self.tasks.block_task(real_task_id, reason="Approval required before execution")
                return {
                    "executed": False,
                    "status": "waiting_for_approval",
                    "taskId": real_task_id,
                    "receiptId": gate_receipt.receipt_id,
                    "summary": "Approval required before execution. Nothing was executed.",
                    "readResult": None,
                }

            # 8. Start task lifecycle
            self.tasks.start_task(real_task_id, mode="read_only")

            # 9. Perform safe bounded source read
            if not self.project_text_reader:
                raise RuntimeError("ProjectTextReader is not initialized.")

            read_res = self.project_text_reader.read_text_files(
                project_name=proj["name"],
                relative_paths=relative_paths,
            )

            # 10. Finalize execution receipt (metadata only, no content stored)
            finalized_receipt = self.runtime.finalize_execution_receipt(
                gate_receipt.receipt_id,
                result_status="executed_read_only",
                execution_note=f"Read {read_res['totalFiles']} text files ({read_res['totalBytes']} bytes)",
                task_id=real_task_id,
            )

            # 11. Complete task lifecycle
            self.tasks.succeed_task(
                real_task_id,
                summary=f"Read {read_res['totalFiles']} project text files safely ({read_res['totalBytes']} bytes).",
            )

            return {
                "executed": True,
                "status": "succeeded",
                "actionType": "read_project_text_files",
                "toolId": "filesystem_tool",
                "projectName": proj["name"],
                "taskId": real_task_id,
                "receiptId": finalized_receipt.get("receipt_id", gate_receipt.receipt_id),
                "dryRunTaskId": dry_run_task_id,
                "sourceResponseId": source_response_id,
                "sourceTurnIndex": source_turn_index,
                "summary": f"Read {read_res['totalFiles']} text files successfully from '{proj['name']}'.",
                "readResult": read_res,
                "executedAt": utc_now(),
            }
        except Exception as exc:
            if real_task_id:
                try:
                    self.tasks.fail_task(real_task_id, error=str(exc))
                except Exception:
                    pass
                if gate_receipt_id:
                    try:
                        self.runtime.finalize_execution_receipt(
                            gate_receipt_id,
                            result_status="execution_failed",
                            execution_note=str(exc),
                            task_id=real_task_id,
                        )
                    except Exception:
                        pass
            raise
        finally:
            with self._execution_lock:
                self._active_executions.discard(dry_run_task_id)

    def execute_report(
        self,
        *,
        dry_run_task_id: str,
        project_name: str,
        title: str,
        content: str,
        expected_receipt_id: str | None = None,
        confirmation: str = "",
        source_agent_id: str = "unified_assistant",
        source_response_id: str | None = None,
        source_turn_index: int | None = None,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        # 1. Exact confirmation requirement
        if confirmation.strip() != "WRITE NEW LOCAL REPORT":
            raise ValueError("Explicit confirmation string 'WRITE NEW LOCAL REPORT' is required.")

        # 2. Concurrency / duplicate execution protection
        with self._execution_lock:
            if dry_run_task_id in self._active_executions:
                raise ValueError(f"Execution for dry-run task '{dry_run_task_id}' is already in progress.")
            self._active_executions.add(dry_run_task_id)

        real_task_id: str | None = None
        gate_receipt_id: str | None = None

        try:
            # 3. Dry-run proof verification
            _, dry_run_receipt = self.verify_dry_run_proof(
                dry_run_task_id=dry_run_task_id,
                project_name=project_name,
                expected_receipt_id=expected_receipt_id,
                expected_action_type="write_report",
            )

            # 4. Re-resolve registered project at execution time
            proj = self.projects.get_project(project_name.strip())
            if not proj:
                raise KeyError(f"Registered project '{project_name}' no longer found in registry.")

            project_root = Path(proj["path"]).expanduser().resolve()
            if not project_root.exists() or not project_root.is_dir():
                raise FileNotFoundError(f"Project directory '{project_root}' does not exist or is not a directory.")

            # 5. Re-validate workspace boundary
            if self.workspace_root is not None and not project_root.is_relative_to(self.workspace_root):
                raise PermissionError("Project root escapes the allowed workspace root.")

            # 6. Create real execution task record (dry_run=False, write_capable=True)
            real_task = self.tasks.create_task(
                project_name=proj["name"],
                agent_id=source_agent_id,
                task_type="write_report",
                autonomy_level="supervised",
                dry_run=False,
                write_capable=True,
                proposed_actions=[{
                    "tool_id": "report_tool",
                    "action_type": "write_report",
                    "target": proj["name"],
                    "risk_level": "low",
                }],
                risk_plan={
                    "risk_level": "low",
                    "reason": f"Supervised Markdown report creation for {proj['name']}",
                },
            )
            real_task_id = real_task["task_id"]
            if real_task.get("status") == "blocked":
                raise PermissionError(f"Project '{proj['name']}' is locked by another write operation.")

            # 7. SafeActionRuntime execution gate receipt
            gate_receipt = self.runtime.validate(
                ActionRequest(
                    task_id=real_task_id,
                    agent_id=source_agent_id,
                    tool_id="report_tool",
                    action_type="write_report",
                    target=proj["name"],
                    risk_level="low",
                )
            )
            gate_receipt_id = gate_receipt.receipt_id

            if gate_receipt.blocked:
                self.tasks.block_task(real_task_id, reason=gate_receipt.reason)
                self.runtime.finalize_execution_receipt(
                    gate_receipt.receipt_id,
                    result_status="execution_failed",
                    execution_note=f"Blocked: {gate_receipt.reason}",
                    task_id=real_task_id,
                )
                return {
                    "executed": False,
                    "status": "blocked",
                    "taskId": real_task_id,
                    "receiptId": gate_receipt.receipt_id,
                    "summary": f"Execution blocked by policy: {gate_receipt.reason}",
                    "reportResult": None,
                }

            if gate_receipt.approval_required and not gate_receipt.approved:
                self.tasks.block_task(real_task_id, reason="Approval required before execution")
                return {
                    "executed": False,
                    "status": "waiting_for_approval",
                    "taskId": real_task_id,
                    "receiptId": gate_receipt.receipt_id,
                    "summary": "Approval required before execution. Nothing was executed.",
                    "reportResult": None,
                }

            # 8. Start task lifecycle
            self.tasks.start_task(real_task_id, mode="write_report")

            # 9. Perform safe exclusive report writing
            if not self.report_tool:
                raise RuntimeError("ReportTool is not initialized.")

            report_meta = self.report_tool.create_markdown_report(
                project_name=proj["name"],
                title=title,
                content=content,
            )

            # 10. Finalize execution receipt
            finalized_receipt = self.runtime.finalize_execution_receipt(
                gate_receipt.receipt_id,
                result_status="executed_write_report",
                execution_note=f"Created {report_meta['filename']} ({report_meta['charCount']} chars)",
                task_id=real_task_id,
            )

            # 11. Complete task lifecycle
            self.tasks.succeed_task(
                real_task_id,
                summary=f"Local Markdown report '{report_meta['filename']}' created successfully ({report_meta['charCount']} chars).",
            )

            return {
                "executed": True,
                "status": "succeeded",
                "actionType": "write_report",
                "toolId": "report_tool",
                "projectName": proj["name"],
                "taskId": real_task_id,
                "receiptId": finalized_receipt.get("receipt_id", gate_receipt.receipt_id),
                "dryRunTaskId": dry_run_task_id,
                "sourceResponseId": source_response_id,
                "sourceTurnIndex": source_turn_index,
                "summary": f"Local Markdown report created successfully for '{proj['name']}'.",
                "reportResult": report_meta,
                "executedAt": utc_now(),
            }
        except Exception as exc:
            if real_task_id:
                try:
                    self.tasks.fail_task(real_task_id, error=str(exc))
                except Exception:
                    pass
                if gate_receipt_id:
                    try:
                        self.runtime.finalize_execution_receipt(
                            gate_receipt_id,
                            result_status="execution_failed",
                            execution_note=str(exc),
                            task_id=real_task_id,
                        )
                    except Exception:
                        pass
            raise
        finally:
            with self._execution_lock:
                self._active_executions.discard(dry_run_task_id)

    def get_task_action_view(self, task_id: str) -> dict[str, Any] | None:
        task = self.tasks.get_task(task_id)
        if not task:
            return None
        receipts = self.runtime.list_receipts(task_id=task_id)
        task_approvals = [a for a in self.approvals.list_approvals() if a.get("task_id") == task_id]
        return {
            "taskId": task_id,
            "task": task,
            "receipts": receipts,
            "approvals": task_approvals,
            "dryRun": task.get("dry_run", True),
            "executed": not task.get("dry_run", True) and task.get("status") == "succeeded",
        }
