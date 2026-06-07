from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from . import APP_NAME, VERSION
from .approvals import ApprovalQueue
from .audit import JsonlLogger
from .codex_plans import CodexPlanInput, CodexPlanService
from .codex_execution import CodexExecutionService
from .db import init_db
from .dashboard import DashboardService, dashboard_html
from .diagnostics import DiagnosticExporter
from .events import EventBus
from .inspector import inspect_project, write_markdown_report
from .project_registry import ProjectRegistry
from .reports import missing_implementation_report_sections
from .runtime import ActionRequest, SafeActionRuntime
from .tasks import TaskQueue

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = WORKSPACE_ROOT / "data" / "jarvis"
conn = init_db(DATA_ROOT / "jarvis.sqlite")
logger = JsonlLogger(DATA_ROOT / "logs")
events = EventBus(conn, logger)
projects = ProjectRegistry(conn, WORKSPACE_ROOT)
runtime = SafeActionRuntime(logger, conn, events)
approvals = ApprovalQueue(conn, events)
tasks = TaskQueue(conn, events, runtime, approvals)
codex_plans = CodexPlanService(conn, events, runtime, approvals, projects)
codex_execution = CodexExecutionService(conn, events, runtime, approvals, projects, codex_plans)
diagnostics = DiagnosticExporter(conn, WORKSPACE_ROOT, DATA_ROOT / "logs", WORKSPACE_ROOT / "connectors")
dashboard = DashboardService(conn, WORKSPACE_ROOT, DATA_ROOT, WORKSPACE_ROOT / "connectors")

app = FastAPI(title=APP_NAME, version=VERSION)


class ProjectInput(BaseModel):
    name: str
    path: str


class ActionInput(BaseModel):
    agentId: str
    actionType: str
    target: str | None = None
    taskId: str | None = None
    toolId: str = "policy_engine"
    riskLevel: str = "low"


class ProposedActionInput(BaseModel):
    toolId: str = "policy_engine"
    actionType: str
    target: str | None = None
    riskLevel: str = "low"


class TaskInput(BaseModel):
    projectName: str
    agentId: str = "coding_agent"
    taskType: str
    autonomyLevel: str = "supervised"
    dryRun: bool = True
    writeCapable: bool | None = None
    proposedActions: list[ProposedActionInput] = Field(default_factory=list)
    riskPlan: dict[str, int] = Field(default_factory=dict)


class ApprovalResolutionInput(BaseModel):
    resolvedBy: str = "local_user"
    resolutionNote: str | None = None


class ReportValidationInput(BaseModel):
    text: str


class CodexPlanRequest(BaseModel):
    taskId: str
    projectName: str
    agentId: str = "coding_agent"
    toolId: str = "codex_tool"
    actionType: str = "codex.plan_execution"
    taskGoal: str = ""
    exactScope: str = ""
    nonGoals: str = ""
    allowedFiles: list[str] = Field(default_factory=list)
    testCommands: list[str] = Field(default_factory=list)
    riskPlan: dict[str, int] = Field(default_factory=dict)
    sandboxMode: str = "workspace-write"
    promptPath: str = ".jarvis/prompts/current-task.md"
    outputPath: str = ".jarvis/reports/latest-codex-output.md"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": VERSION, "mode": "local"}


@app.get("/dashboard", response_class=HTMLResponse)
def local_dashboard() -> HTMLResponse:
    return HTMLResponse(dashboard_html())


@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict[str, object]:
    return dashboard.summary()


@app.get("/api/safety/summary")
def safety_summary() -> dict[str, object]:
    return dashboard.safety_summary()


@app.get("/api/reports")
def list_dashboard_reports() -> list[dict[str, object]]:
    return dashboard.list_reports()


@app.get("/api/reports/{report_id:path}")
def get_dashboard_report(report_id: str) -> dict[str, object]:
    try:
        return dashboard.read_report(report_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/projects")
def list_projects() -> list[dict[str, str]]:
    return projects.list_projects()


@app.post("/projects")
def add_project(payload: ProjectInput) -> dict[str, str]:
    try:
        return projects.add_project(payload.name, Path(payload.path))
    except (PermissionError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{name}")
def get_project(name: str) -> dict[str, str]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    return project


@app.get("/projects/{name}/inspect")
def inspect_registered_project(name: str) -> dict[str, object]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    inspection = inspect_project(Path(project["path"]))
    report_path = DATA_ROOT / "reports" / f"{name}.md"
    write_markdown_report(inspection, report_path)
    inspection["reportPath"] = str(report_path)
    return inspection


@app.post("/actions/validate")
def validate_action(payload: ActionInput) -> dict[str, str]:
    receipt = runtime.validate(
        ActionRequest(
            agent_id=payload.agentId,
            action_type=payload.actionType,
            target=payload.target,
            task_id=payload.taskId,
            tool_id=payload.toolId,
            risk_level=payload.riskLevel,
        )
    )
    return receipt.__dict__


@app.post("/tasks")
def create_task(payload: TaskInput) -> dict[str, object]:
    return tasks.create_task(
        project_name=payload.projectName,
        agent_id=payload.agentId,
        task_type=payload.taskType,
        autonomy_level=payload.autonomyLevel,
        dry_run=payload.dryRun,
        write_capable=payload.writeCapable,
        proposed_actions=[action.model_dump() for action in payload.proposedActions],
        risk_plan=payload.riskPlan,
    )


@app.get("/tasks")
def list_tasks() -> list[dict[str, object]]:
    return tasks.list_tasks()


@app.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict[str, object]:
    task = tasks.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@app.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str) -> dict[str, object]:
    try:
        return tasks.cancel_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/events")
def list_events() -> list[dict[str, object]]:
    return events.list_events()


@app.get("/tasks/{task_id}/events")
def list_task_events(task_id: str) -> list[dict[str, object]]:
    return events.list_events(task_id)


@app.get("/approvals")
def list_approvals() -> list[dict[str, object]]:
    return approvals.list_approvals()


@app.get("/approvals/{approval_id}")
def get_approval(approval_id: str) -> dict[str, object]:
    approval = approvals.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="approval not found")
    return approval


@app.post("/approvals/{approval_id}/approve")
def approve_approval(approval_id: str, payload: ApprovalResolutionInput) -> dict[str, object]:
    try:
        return approvals.approve(approval_id, payload.resolvedBy, payload.resolutionNote)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/approvals/{approval_id}/reject")
def reject_approval(approval_id: str, payload: ApprovalResolutionInput) -> dict[str, object]:
    try:
        return approvals.reject(approval_id, payload.resolvedBy, payload.resolutionNote)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/diagnostics/export")
def export_diagnostics() -> dict[str, object]:
    return diagnostics.export()


@app.post("/reports/validate")
def validate_report(payload: ReportValidationInput) -> dict[str, object]:
    missing = missing_implementation_report_sections(payload.text)
    return {"valid": not missing, "missingSections": missing}


@app.post("/codex/plans")
def create_codex_plan(payload: CodexPlanRequest) -> dict[str, object]:
    return codex_plans.create_plan(
        CodexPlanInput(
            task_id=payload.taskId,
            project_name=payload.projectName,
            agent_id=payload.agentId,
            tool_id=payload.toolId,
            action_type=payload.actionType,
            task_goal=payload.taskGoal,
            exact_scope=payload.exactScope,
            non_goals=payload.nonGoals,
            allowed_files=payload.allowedFiles,
            test_commands=payload.testCommands,
            risk_plan=payload.riskPlan,
            sandbox_mode=payload.sandboxMode,
            prompt_path=payload.promptPath,
            output_path=payload.outputPath,
        )
    )


@app.get("/codex/plans")
def list_codex_plans() -> list[dict[str, object]]:
    return codex_plans.list_plans()


@app.get("/codex/plans/{plan_id}")
def get_codex_plan(plan_id: str) -> dict[str, object]:
    plan = codex_plans.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="codex plan not found")
    return plan


@app.post("/codex/plans/{plan_id}/cancel")
def cancel_codex_plan(plan_id: str) -> dict[str, object]:
    try:
        return codex_plans.cancel_plan(plan_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/codex/plans/{plan_id}/approve-for-future-execution")
def approve_codex_plan_for_future_execution(plan_id: str, payload: ApprovalResolutionInput) -> dict[str, object]:
    try:
        return codex_plans.approve_for_future_execution(plan_id, payload.resolvedBy, payload.resolutionNote)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/codex/plans/{plan_id}/reject")
def reject_codex_plan(plan_id: str, payload: ApprovalResolutionInput) -> dict[str, object]:
    try:
        return codex_plans.reject_plan(plan_id, payload.resolvedBy, payload.resolutionNote)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/codex/plans/{plan_id}/execute")
def execute_codex_plan(plan_id: str) -> dict[str, object]:
    return codex_execution.execute_plan(plan_id)
