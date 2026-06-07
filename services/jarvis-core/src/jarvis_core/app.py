from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import APP_NAME, VERSION
from .audit import JsonlLogger
from .db import init_db
from .inspector import inspect_project, write_markdown_report
from .project_registry import ProjectRegistry
from .runtime import ActionRequest, SafeActionRuntime

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DATA_ROOT = WORKSPACE_ROOT / "data" / "jarvis"
conn = init_db(DATA_ROOT / "jarvis.sqlite")
logger = JsonlLogger(DATA_ROOT / "logs")
projects = ProjectRegistry(conn, WORKSPACE_ROOT)
runtime = SafeActionRuntime(logger)

app = FastAPI(title=APP_NAME, version=VERSION)


class ProjectInput(BaseModel):
    name: str
    path: str


class ActionInput(BaseModel):
    agentId: str
    actionType: str
    target: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": APP_NAME, "version": VERSION, "mode": "local"}


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
    receipt = runtime.validate(ActionRequest(payload.agentId, payload.actionType, payload.target))
    return receipt.__dict__
