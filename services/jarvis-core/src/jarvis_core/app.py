from __future__ import annotations

import re
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from . import APP_NAME, VERSION
from .agent_manifest_health import AgentManifestHealthService
from .approvals import ApprovalQueue
from .audit import JsonlLogger
from .codex_plans import CodexPlanInput, CodexPlanService
from .codex_execution import CodexExecutionService
from .db import init_db
from .dashboard import DashboardService, dashboard_html, first_run_setup_html
from .dashboard_surface_health import DashboardSurfaceHealthService
from .diagnostics import DiagnosticExporter
from .docs_center import DocsCenterService
from .evidence_report_center import EvidenceReportCenterService
from .events import EventBus
from .inspector import inspect_project, write_markdown_report
from .lan_security import lan_setup_html, lan_setup_status, require_dashboard_lan_access, require_loopback_request
from .project_profiles import ProjectProfileService
from .project_registry import ProjectRegistry
from .readiness_snapshot_agent import PrivateAlphaReadinessSnapshotService
from .redacted_diagnostics_agent import RedactedDiagnosticsBundleService
from .reports import missing_implementation_report_sections
from .runtime import ActionRequest, SafeActionRuntime
from .security_review_agent import SecurityReviewService
from .task_control import TaskControlService
from .tasks import TaskQueue
from .validation_agent import ValidationAgentService

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = WORKSPACE_ROOT / "data" / "jarvis"
conn = init_db(DATA_ROOT / "jarvis.sqlite")
logger = JsonlLogger(DATA_ROOT / "logs")
events = EventBus(conn, logger)
projects = ProjectRegistry(conn, WORKSPACE_ROOT)
runtime = SafeActionRuntime(logger, conn, events)
approvals = ApprovalQueue(conn, events)
tasks = TaskQueue(conn, events, runtime, approvals)
task_control = TaskControlService(tasks)
codex_plans = CodexPlanService(conn, events, runtime, approvals, projects)
codex_execution = CodexExecutionService(conn, events, runtime, approvals, projects, codex_plans)
diagnostics = DiagnosticExporter(conn, WORKSPACE_ROOT, DATA_ROOT / "logs", WORKSPACE_ROOT / "connectors")
dashboard = DashboardService(conn, WORKSPACE_ROOT, DATA_ROOT, WORKSPACE_ROOT / "connectors")
security_reviews = SecurityReviewService(DATA_ROOT / "reports", WORKSPACE_ROOT, WORKSPACE_ROOT / "connectors")
project_profiles = ProjectProfileService(WORKSPACE_ROOT, WORKSPACE_ROOT / "connectors")
validation_agent = ValidationAgentService(conn, DATA_ROOT / "reports")
readiness_snapshots = PrivateAlphaReadinessSnapshotService(
    conn,
    DATA_ROOT / "reports",
    WORKSPACE_ROOT,
    WORKSPACE_ROOT / "connectors",
)
redacted_diagnostics = RedactedDiagnosticsBundleService(
    conn,
    DATA_ROOT / "reports",
    WORKSPACE_ROOT,
    WORKSPACE_ROOT / "connectors",
)
evidence_reports = EvidenceReportCenterService(DATA_ROOT / "reports")
agent_manifest_health = AgentManifestHealthService(WORKSPACE_ROOT / "connectors")
docs_center = DocsCenterService(WORKSPACE_ROOT)

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


class SecurityReviewInput(BaseModel):
    projectName: str | None = None
    projectPath: str | None = None
    project_name: str | None = None
    project_path: str | None = None
    mode: str = "read_only"


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


class ValidationRunInput(BaseModel):
    runbookId: str | None = None
    runbook_id: str | None = None
    targetEnvironment: str | None = None
    target_environment: str | None = None


class ValidationStepResultInput(BaseModel):
    status: str
    notes: str | None = None
    evidence: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": VERSION, "mode": "local"}


@app.get("/dashboard", response_class=HTMLResponse)
def local_dashboard(_: None = Depends(require_dashboard_lan_access)) -> HTMLResponse:
    return HTMLResponse(dashboard_html())


@app.get("/setup/lan", response_class=HTMLResponse)
def lan_setup_page(_: None = Depends(require_loopback_request)) -> HTMLResponse:
    return HTMLResponse(lan_setup_html())


@app.get("/setup/first-run", response_class=HTMLResponse)
def first_run_setup_page(_: None = Depends(require_loopback_request)) -> HTMLResponse:
    return HTMLResponse(first_run_setup_html())


@app.get("/api/dashboard/summary")
def dashboard_summary(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return dashboard.summary()



@app.get("/dashboard/surface-health")
def get_dashboard_surface_health(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    service = DashboardSurfaceHealthService(app.routes, dashboard.summary(), dashboard_html())
    return service.surface_health()


@app.get("/dashboard/surface-health/{surface_id}")
def get_dashboard_surface_health_detail(surface_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    service = DashboardSurfaceHealthService(app.routes, dashboard.summary(), dashboard_html())
    try:
        return service.surface_detail(surface_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.get("/api/projects/profiles")
def dashboard_project_profiles(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    summaries: list[dict[str, object]] = []
    for project in projects.list_projects():
        profile = project_profiles.generate_profile(Path(project["path"]), str(project["name"]))
        data = profile.to_dict()
        summaries.append(_dashboard_profile_summary(data))
    return summaries


@app.post("/api/projects/{name}/security-review")
def run_dashboard_project_security_review(name: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    try:
        result = security_reviews.review_project(Path(project["path"]), project_name=name, mode="read_only")
        security_reviews.write_markdown_report(result)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _security_review_dashboard_summary(result.to_dict())


@app.get("/api/projects/{name}/security-review/latest")
def latest_dashboard_project_security_review(name: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    safe_project = _safe_report_project_name(name)
    reports_root = DATA_ROOT / "reports"
    if not reports_root.exists():
        return {"projectName": name, "available": False}
    candidates = sorted(
        reports_root.glob(f"security-safety-{safe_project}-*.md"),
        key=lambda path: path.stat().st_mtime if path.is_file() else 0,
        reverse=True,
    )
    for path in candidates:
        resolved = path.resolve()
        if not resolved.is_file() or not resolved.is_relative_to(reports_root.resolve()):
            continue
        stat = resolved.stat()
        return {
            "projectName": name,
            "available": True,
            "reportId": resolved.name,
            "reportPath": str(resolved),
            "sizeBytes": stat.st_size,
        }
    return {"projectName": name, "available": False}


@app.get("/api/setup/lan/status")
def lan_setup_status_endpoint(_: None = Depends(require_loopback_request)) -> dict[str, object]:
    return lan_setup_status()


@app.get("/api/setup/first-run/status")
def first_run_setup_status_endpoint(_: None = Depends(require_loopback_request)) -> dict[str, object]:
    return dashboard.first_run_wizard_summary()


@app.get("/api/safety/summary")
def safety_summary(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return dashboard.safety_summary()


@app.get("/api/settings/summary")
def settings_summary(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return dashboard.settings_summary()


@app.get("/api/tasks/active")
def active_dashboard_tasks(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return task_control.active_tasks()


@app.get("/api/tasks/stop/status")
def task_stop_status(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return task_control.stop_status()


@app.post("/api/tasks/{task_id}/stop")
def stop_dashboard_task(task_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return task_control.stop_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/reports")
def list_dashboard_reports(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return dashboard.list_reports()


@app.get("/api/reports/{report_id:path}")
def get_dashboard_report(report_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return dashboard.read_report(report_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/evidence/reports")
def list_evidence_reports(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return evidence_reports.index_reports()


@app.get("/evidence/reports/{report_id}/metadata")
def get_evidence_report_metadata(report_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return evidence_reports.get_report_metadata(report_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/evidence/reports/{report_id}")
def get_evidence_report_detail(report_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return evidence_reports.get_report_detail(report_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/agents/manifest-health")
def get_agent_manifest_health(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return agent_manifest_health.manifest_health()


@app.get("/agents/manifest-health/{manifest_id}")
def get_agent_manifest_detail(manifest_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return agent_manifest_health.manifest_detail(manifest_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/docs/index")
def get_docs_index(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return docs_center.index_docs()


@app.get("/docs/{doc_id}/metadata")
def get_doc_metadata(doc_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return docs_center.get_doc_metadata(doc_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/docs/{doc_id}")
def get_doc_detail(doc_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return docs_center.get_doc_detail(doc_id)
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


@app.get("/projects/{name}/profile")
def get_project_profile(name: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    project = projects.get_project(name)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    profile = project_profiles.generate_profile(Path(project["path"]), name)
    if profile.blocked_reasons:
        raise HTTPException(status_code=400, detail="; ".join(profile.blocked_reasons))
    return profile.to_dict()


@app.post("/projects/{name}/profile/refresh")
def refresh_project_profile(name: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return get_project_profile(name)


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
def cancel_task(task_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
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


@app.get("/diagnostics/bundle")
def get_redacted_diagnostics_bundle(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return redacted_diagnostics.generate_bundle()


@app.post("/diagnostics/bundle/report")
def write_redacted_diagnostics_bundle_report(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return redacted_diagnostics.write_reports()
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/diagnostics/bundle/latest")
def get_latest_redacted_diagnostics_bundle(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return redacted_diagnostics.get_latest_report_metadata()


@app.post("/reports/validate")
def validate_report(payload: ReportValidationInput) -> dict[str, object]:
    missing = missing_implementation_report_sections(payload.text)
    return {"valid": not missing, "missingSections": missing}


@app.post("/security/reviews")
def create_security_review(payload: SecurityReviewInput, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    project_name = payload.projectName or payload.project_name
    project_path = payload.projectPath or payload.project_path
    if project_name:
        project = projects.get_project(project_name)
        if not project:
            raise HTTPException(status_code=404, detail="project not found")
        project_path = project["path"]
    elif not project_path:
        project_name = "Jarvis"
        project_path = str(WORKSPACE_ROOT)
    try:
        result = security_reviews.review_project(Path(project_path), project_name=project_name, mode=payload.mode)
        security_reviews.write_markdown_report(result)
        return result.to_dict()
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/security/reviews/{review_id:path}")
def get_security_review(review_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, str]:
    try:
        return security_reviews.read_markdown_report(review_id)
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/validation/runbooks")
def list_validation_runbooks(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return validation_agent.list_runbooks()


@app.get("/readiness/snapshot")
def get_readiness_snapshot(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return readiness_snapshots.generate_snapshot()


@app.post("/readiness/snapshot/report")
def write_readiness_snapshot_report(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return readiness_snapshots.write_markdown_report()
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/readiness/snapshot/latest")
def get_latest_readiness_snapshot(_: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    return readiness_snapshots.get_latest_snapshot_metadata()


@app.get("/validation/runbooks/{runbook_id}")
def get_validation_runbook(runbook_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return validation_agent.get_runbook(runbook_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/validation/runs")
def create_validation_run(payload: ValidationRunInput, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    runbook_id = payload.runbookId or payload.runbook_id
    if not runbook_id:
        raise HTTPException(status_code=400, detail="runbookId is required")
    try:
        return validation_agent.create_run(runbook_id, payload.targetEnvironment or payload.target_environment)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/validation/runs")
def list_validation_runs(_: None = Depends(require_dashboard_lan_access)) -> list[dict[str, object]]:
    return validation_agent.list_runs()


@app.get("/validation/runs/{run_id}")
def get_validation_run(run_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return validation_agent.get_run(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/validation/runs/{run_id}/steps/{step_id}")
def update_validation_step_result(
    run_id: str,
    step_id: str,
    payload: ValidationStepResultInput,
    _: None = Depends(require_dashboard_lan_access),
) -> dict[str, object]:
    try:
        return validation_agent.update_step_result(run_id, step_id, payload.status, payload.notes, payload.evidence)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/validation/runs/{run_id}/complete")
def complete_validation_run(run_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, object]:
    try:
        return validation_agent.complete_run(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/validation/runs/{run_id}/report")
def write_validation_report(run_id: str, _: None = Depends(require_dashboard_lan_access)) -> dict[str, str]:
    try:
        return validation_agent.write_markdown_report(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _dashboard_profile_summary(profile: dict[str, object]) -> dict[str, object]:
    public_docs = profile.get("publicReadinessDocsPresent", {})
    security_docs = profile.get("securityDocsPresent", {})
    boundary = profile.get("boundary", {})
    boundary_dict = boundary if isinstance(boundary, dict) else {}
    return {
        "projectName": profile.get("projectName"),
        "projectType": profile.get("projectType"),
        "detectedLanguages": profile.get("detectedLanguages", []),
        "detectedFrameworks": profile.get("detectedFrameworks", []),
        "packageManager": profile.get("packageManager"),
        "preferredCheckOrder": profile.get("preferredCheckOrder", []),
        "gitClean": profile.get("gitClean"),
        "docsPresence": {
            "publicReadiness": public_docs,
            "security": security_docs,
        },
        "futureConnectorsPlaceholderOnly": profile.get("futureConnectorsPlaceholderOnly"),
        "recommendedMode": profile.get("recommendedMode"),
        "warningCount": len(profile.get("warnings", []) if isinstance(profile.get("warnings"), list) else []),
        "blockedReasonCount": len(profile.get("blockedReasons", []) if isinstance(profile.get("blockedReasons"), list) else []),
        "boundaryStatus": {
            "rootValidated": profile.get("rootValidated"),
            "protectedPatternsActive": bool(profile.get("protectedPatterns")),
            "runtimeSkipDirsActive": bool(profile.get("runtimeSkipDirs")),
            "blockedReasonCount": len(profile.get("blockedReasons", []) if isinstance(profile.get("blockedReasons"), list) else []),
            "warningCount": len(profile.get("warnings", []) if isinstance(profile.get("warnings"), list) else []),
            "rootStatus": (boundary_dict.get("root") or {}).get("status") if isinstance(boundary_dict.get("root"), dict) else None,
        },
    }


def _security_review_dashboard_summary(review: dict[str, object]) -> dict[str, object]:
    findings = review.get("findings", [])
    findings_list = findings if isinstance(findings, list) else []
    by_severity = {"high": 0, "medium": 0, "low": 0}
    for finding in findings_list:
        if isinstance(finding, dict):
            severity = str(finding.get("severity", "low"))
            by_severity[severity] = by_severity.get(severity, 0) + 1
    metadata = review.get("metadata", {})
    metadata_dict = metadata if isinstance(metadata, dict) else {}
    return {
        "projectName": metadata_dict.get("projectName"),
        "agentId": metadata_dict.get("agentId"),
        "reviewMode": metadata_dict.get("reviewMode"),
        "verdict": review.get("verdict"),
        "findingCount": len(findings_list),
        "findingsBySeverity": by_severity,
        "reportId": review.get("reportId"),
        "reportPath": review.get("reportPath"),
    }


def _safe_report_project_name(project_name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", project_name.strip()).strip("-") or "project"


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
