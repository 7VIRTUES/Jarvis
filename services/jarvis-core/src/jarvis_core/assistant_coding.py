from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .approvals import ApprovalQueue
from .codex_constants import ALLOWED_SANDBOX_MODE
from .codex_execution import CodexExecutionService
from .codex_execution_control import (
    get_plan_prompt_content,
    is_conservative_plan,
    parse_scope_manifest,
)
from .codex_plans import CodexPlanInput, CodexPlanService
from .events import EventBus
from .project_registry import ProjectRegistry
from .project_text_reader import ProjectTextReader
from .runtime import SafeActionRuntime
from .tasks import TaskQueue


@dataclass(frozen=True)
class AssistantCodingPrepareInput:
    project_name: str
    allowed_files: list[str]
    task_goal: str
    exact_scope: str
    non_goals: str = ""
    source_response_id: str | None = None
    source_turn_index: int | None = None
    actor: str = "local_user"


class AssistantCodingBridge:
    """Infrastructure bridge connecting Unified Assistant to conservative Codex execution."""

    def __init__(
        self,
        projects: ProjectRegistry,
        project_text_reader: ProjectTextReader,
        plans: CodexPlanService,
        execution: CodexExecutionService,
        tasks: TaskQueue,
        runtime: SafeActionRuntime,
        approvals: ApprovalQueue,
        events: EventBus,
    ) -> None:
        self.projects = projects
        self.project_text_reader = project_text_reader
        self.plans = plans
        self.execution = execution
        self.tasks = tasks
        self.runtime = runtime
        self.approvals = approvals
        self.events = events

    def get_coding_capabilities(self) -> dict[str, Any]:
        return {
            "actionType": "modify_project_files_with_codex",
            "name": "Controlled Coding with Codex",
            "implemented": True,
            "description": "Prepare and explicitly execute one approved extreme-budget Codex change against selected existing files.",
            "rules": [
                "Approved registered project only",
                "1 to 10 existing safe files only (no new files, deletions, or renames)",
                "Protected and dependency files strictly blocked",
                "Approval-time SHA-256 hashes recorded into machine scope manifest",
                "Clean Git working tree preflight required before execution",
                "Stale approved file modifications blocked at execution time",
                "Exactly one Codex subprocess execution (zero repair runs, zero automated test/check runs)",
                "Exact post-execution Git diff scope enforcement",
                "No automatic Git commit, push, merge, reset, or rollback",
                "Owned-process cancellation support via exact confirmation",
            ],
            "maxAllowedFiles": 10,
            "maxCodexRuns": 1,
            "maxDiffLines": 700,
            "existingFilesOnly": True,
            "requireCleanWorkingTree": True,
            "automaticTests": False,
            "automaticRepairs": False,
            "approvalConfirmation": "APPROVE CONSERVATIVE CODEX PLAN",
            "executionConfirmation": "EXECUTE APPROVED CODEX CHANGE",
            "stopConfirmation": "STOP CODEX EXECUTION",
        }

    def prepare_coding_plan(self, payload: AssistantCodingPrepareInput) -> dict[str, Any]:
        project = self.projects.get_project(payload.project_name)
        if not project:
            raise ValueError(f"Target project '{payload.project_name}' is not registered.")

        if not payload.allowed_files or len(payload.allowed_files) < 1:
            raise ValueError("At least 1 existing safe project file must be selected.")

        if len(payload.allowed_files) > 10:
            raise ValueError("A maximum of 10 existing files can be selected per conservative plan.")

        if not payload.task_goal or not payload.task_goal.strip():
            raise ValueError("Task goal is required.")

        if not payload.exact_scope or not payload.exact_scope.strip():
            raise ValueError("Exact scope is required.")

        # Create supervised planning task record
        task = self.tasks.create_task(
            agent_id="coding_agent",
            task_type="plan",
            title=f"Plan Codex change for {payload.project_name}",
            project_name=payload.project_name,
            dry_run=True,
            write_capable=False,
            source_agent_id="unified_assistant",
            source_response_id=payload.source_response_id,
            source_turn_index=payload.source_turn_index,
        )

        plan = self.plans.create_conservative_plan(
            CodexPlanInput(
                task_id=task.task_id,
                project_name=payload.project_name,
                agent_id="coding_agent",
                tool_id="codex_tool",
                action_type="codex.plan_execution",
                task_goal=payload.task_goal.strip()[:4000],
                exact_scope=payload.exact_scope.strip()[:6000],
                non_goals=payload.non_goals.strip()[:4000],
                allowed_files=payload.allowed_files,
                test_commands=[],
                sandbox_mode=ALLOWED_SANDBOX_MODE,
                conservative=True,
                execution_mode="extreme_budget",
            )
        )

        prompt_content = get_plan_prompt_content(plan)
        parse_err, manifest = parse_scope_manifest(prompt_content, expected_project_name=payload.project_name)
        if parse_err or manifest is None:
            raise RuntimeError(f"Failed to generate valid conservative scope manifest: {parse_err}")

        return {
            "planId": plan["plan_id"],
            "taskId": task.task_id,
            "projectName": payload.project_name,
            "status": plan["status"],
            "approvalId": plan["approval_id"],
            "taskGoal": payload.task_goal.strip(),
            "exactScope": payload.exact_scope.strip(),
            "nonGoals": payload.non_goals.strip(),
            "allowedFiles": manifest.get("allowedFiles", payload.allowed_files),
            "allowedFileHashes": manifest.get("allowedFileHashes", {}),
            "existingFilesOnly": True,
            "maxCodexRuns": 1,
            "maxChangedFiles": manifest.get("maxChangedFiles", 10),
            "maxDiffLines": manifest.get("maxDiffLines", 700),
            "automaticChecks": False,
            "automaticRepairs": False,
            "requireCleanWorkingTree": True,
            "commandPreview": plan.get("command_preview", {}),
            "createdAt": plan.get("created_at"),
        }

    def approve_coding_plan(self, plan_id: str, confirmation: str, actor: str = "local_user") -> dict[str, Any]:
        if confirmation.strip() != "APPROVE CONSERVATIVE CODEX PLAN":
            raise ValueError("Exact confirmation string 'APPROVE CONSERVATIVE CODEX PLAN' is required.")

        plan = self.plans.get_plan(plan_id)
        if not plan:
            raise KeyError("Codex plan not found.")

        if not is_conservative_plan(plan):
            raise ValueError("Plan is not a valid conservative Codex plan.")

        if plan["status"] != "waiting_for_approval":
            raise ValueError(f"Plan status must be 'waiting_for_approval' (currently: '{plan['status']}').")

        approved_plan = self.plans.approve_for_future_execution(plan_id, resolved_by=actor)
        return self.get_plan_summary(plan_id)

    def reject_coding_plan(self, plan_id: str, actor: str = "local_user") -> dict[str, Any]:
        plan = self.plans.get_plan(plan_id)
        if not plan:
            raise KeyError("Codex plan not found.")

        self.plans.reject_plan(plan_id, resolved_by=actor)
        return self.get_plan_summary(plan_id)

    def execute_coding_plan(
        self,
        plan_id: str,
        project_name: str,
        confirmation: str,
        actor: str = "local_user",
    ) -> dict[str, Any]:
        if confirmation.strip() != "EXECUTE APPROVED CODEX CHANGE":
            raise ValueError("Exact confirmation string 'EXECUTE APPROVED CODEX CHANGE' is required.")

        plan = self.plans.get_plan(plan_id)
        if not plan:
            raise KeyError("Codex plan not found.")

        if not is_conservative_plan(plan):
            raise ValueError("Plan is not a valid conservative Codex plan.")

        if plan["project_name"] != project_name:
            raise ValueError(f"Project name '{project_name}' does not match plan target '{plan['project_name']}'.")

        if plan["status"] != "approved_for_future_execution":
            raise ValueError(f"Plan status must be 'approved_for_future_execution' (currently: '{plan['status']}').")

        approval_id = plan.get("approval_id")
        approval = self.approvals.get_approval(str(approval_id)) if approval_id else None
        if not approval or approval["status"] != "approved":
            raise ValueError("Approved approval record is required.")

        # Directly invoke conservative execution
        result = self.execution.execute_conservative_plan(plan_id)
        return self._format_execution_result(result, plan)

    def get_plan_summary(self, plan_id: str) -> dict[str, Any]:
        plan = self.plans.get_plan(plan_id)
        if not plan:
            raise KeyError("Codex plan not found.")

        prompt_content = get_plan_prompt_content(plan)
        _, manifest = parse_scope_manifest(prompt_content, expected_project_name=plan["project_name"])
        manifest = manifest or {}

        return {
            "planId": plan["plan_id"],
            "taskId": plan["task_id"],
            "projectName": plan["project_name"],
            "status": plan["status"],
            "approvalId": plan["approval_id"],
            "allowedFiles": manifest.get("allowedFiles", []),
            "allowedFileHashes": manifest.get("allowedFileHashes", {}),
            "existingFilesOnly": manifest.get("existingFilesOnly", True),
            "maxCodexRuns": manifest.get("maxCodexRuns", 1),
            "maxChangedFiles": manifest.get("maxChangedFiles", 10),
            "maxDiffLines": manifest.get("maxDiffLines", 700),
            "automaticChecks": False,
            "automaticRepairs": False,
            "requireCleanWorkingTree": True,
            "commandPreview": plan.get("command_preview", {}),
            "createdAt": plan.get("created_at"),
            "updatedAt": plan.get("updated_at"),
        }

    def get_execution_summary(self, execution_id: str) -> dict[str, Any]:
        exec_row = self.execution.get_execution(execution_id)
        if not exec_row:
            raise KeyError("Codex execution record not found.")

        plan = self.plans.get_plan(exec_row["plan_id"])
        return self._format_execution_result(exec_row, plan)

    def _format_execution_result(self, exec_row: dict[str, Any], plan: dict[str, Any] | None) -> dict[str, Any]:
        post_review = exec_row.get("post_review") or {}
        check_results = exec_row.get("check_results") or {}
        repair_results = exec_row.get("repair_results") or {}

        status = exec_row["status"]
        if status == "succeeded":
            message = "Code change completed within approved file scope. Automated checks were skipped by extreme-budget policy."
        elif status == "blocked":
            message = "Codex wrote workspace changes, but Jarvis blocked success because post-execution review found an out-of-policy condition. Changes were NOT automatically reverted."
        elif status == "canceled":
            message = "Codex execution was stopped. Any changes already written remain in the workspace for review."
        else:
            message = f"Codex execution failed (exit code: {exec_row.get('exit_code')}). Workspace changes, if any, were not automatically reverted."

        return {
            "executionId": exec_row["execution_id"],
            "planId": exec_row["plan_id"],
            "taskId": exec_row["task_id"],
            "projectName": exec_row["project_name"],
            "status": status,
            "message": message,
            "exitCode": exec_row.get("exit_code"),
            "startedAt": exec_row.get("started_at"),
            "finishedAt": exec_row.get("finished_at"),
            "blockedReason": exec_row.get("blocked_reason"),
            "error": exec_row.get("error"),
            "changedFiles": post_review.get("changedFiles", []),
            "changedFileCount": post_review.get("changedFileCount", 0),
            "modifiedFiles": post_review.get("modifiedFiles", []),
            "addedFiles": post_review.get("addedFiles", []),
            "untrackedFiles": post_review.get("untrackedFiles", []),
            "deletedFiles": post_review.get("deletedFiles", []),
            "renamedFiles": post_review.get("renamedFiles", []),
            "protectedFilesChanged": post_review.get("protectedFilesChanged", []),
            "dependencyFilesChanged": post_review.get("dependencyFilesChanged", []),
            "diffStat": post_review.get("diffStat", ""),
            "addedLines": post_review.get("addedLines", 0),
            "deletedLines": post_review.get("deletedLines", 0),
            "diffLines": post_review.get("diffLines", 0),
            "baselineHeadSha": post_review.get("baselineHeadSha"),
            "baselineBranch": post_review.get("baselineBranch"),
            "requiresUserReview": post_review.get("requiresUserReview", False),
            "reviewReasons": post_review.get("reasons", []),
            "checksStatus": "SKIPPED — extreme-budget policy",
            "repairsStatus": "SKIPPED — extreme-budget policy",
        }
