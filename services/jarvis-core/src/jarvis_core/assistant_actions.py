from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from .approvals import ApprovalQueue
from .permissions import check_action
from .project_registry import ProjectRegistry
from .runtime import SafeActionRuntime
from .tasks import TaskQueue
from .time_utils import utc_now


SUPPORTED_ASSISTANT_ACTION_TYPES: list[str] = [
    "inspect_project",
    "write_report",
]

ACTION_DISPLAY_NAMES: dict[str, str] = {
    "inspect_project": "Inspect Registered Project (Read-Only)",
    "write_report": "Draft Structured Report (Dry-Run Only)",
}

ACTION_TOOL_IDS: dict[str, str] = {
    "inspect_project": "report_tool",
    "write_report": "report_tool",
}

ACTION_TASK_TYPES: dict[str, str] = {
    "inspect_project": "inspect",
    "write_report": "report",
}

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
    """Supervised bridge connecting Unified Assistant responses to Safe Action Runtime dry-run validation."""

    def __init__(
        self,
        projects: ProjectRegistry,
        tasks: TaskQueue,
        runtime: SafeActionRuntime,
        approvals: ApprovalQueue,
    ) -> None:
        self.projects = projects
        self.tasks = tasks
        self.runtime = runtime
        self.approvals = approvals

    def get_capabilities(self) -> dict[str, Any]:
        return {
            "implemented": True,
            "dryRunOnly": True,
            "realExecutionImplemented": False,
            "supportedActionTypes": [
                {
                    "actionType": "inspect_project",
                    "displayLabel": ACTION_DISPLAY_NAMES["inspect_project"],
                    "description": "Read-only inspection and structure check of a registered Jarvis project workspace.",
                    "targetType": "registered_project_name",
                    "riskLevel": "low",
                    "dryRunOnly": True,
                    "executionPermitted": False,
                },
                {
                    "actionType": "write_report",
                    "displayLabel": ACTION_DISPLAY_NAMES["write_report"],
                    "description": "Prepare a structured local report proposal for a registered project (dry-run validation only; no file is written).",
                    "targetType": "registered_project_name",
                    "riskLevel": "low",
                    "dryRunOnly": True,
                    "executionPermitted": False,
                },
            ],
            "unsupportedActionTypes": [
                "command",
                "shell_execution",
                "powershell_execution",
                "file_deletion",
                "file_write_unsupervised",
                "browser_automation",
                "email_sending",
                "public_posting",
                "purchases_or_payments",
                "external_connectors",
            ],
            "boundaries": [
                "Unified Assistant actions are strictly supervised and dry-run only.",
                "Only registered project workspaces within the allowed root can be selected as targets.",
                "No response agent has action execution authority.",
                "Dry-run validation passes through SafeActionRuntime and creates auditable receipts.",
                "Approvals are authorization records only and never trigger automated execution.",
                "No file mutation, command execution, or external network action occurs.",
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

        # Check inspect_project signals
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

        # Non-executing policy preview
        policy_result = check_action(normalized_action, target=resolved_project_name)
        policy_preview_data = {
            "actionType": normalized_action,
            "projectName": resolved_project_name,
            "status": policy_result.status,
            "allowed": policy_result.allowed,
            "reason": policy_result.reason,
            "riskLevel": "low",
            "dryRunOnly": True,
            "executionPermitted": False,
        }

        # Determine readiness state
        is_ready = len(missing_fields) == 0 and policy_result.status != "blocked"
        if not resolved_project_name:
            readiness_status = "needs_project"
            readiness_notes = "A registered project target must be selected before dry-run validation."
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
            "proposedToolId": ACTION_TOOL_IDS.get(normalized_action, "report_tool"),
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
            "executionPermitted": False,
            "dryRunOnly": True,
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
                "dryRunOnly": True,
                "executionPermitted": False,
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
                    "dryRunOnly": True,
                    "executionPermitted": False,
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
            "dryRunOnly": True,
            "executionPermitted": False,
        }

    def validate_dry_run(
        self,
        *,
        action_type: str,
        project_name: str,
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

        tool_id = ACTION_TOOL_IDS.get(normalized_action, "report_tool")
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
            "taskId": task_id,
            "task": task,
            "receipts": receipts,
            "approvals": task_approvals,
            "dryRunOnly": True,
            "executed": False,
            "summary": status_text,
            "validatedAt": utc_now(),
        }

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
            "dryRunOnly": task.get("dry_run", True),
            "executed": False,
        }
