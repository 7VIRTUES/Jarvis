import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.approvals import ApprovalQueue
from jarvis_core.audit import JsonlLogger
from jarvis_core.db import init_db
from jarvis_core.events import EventBus
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.runtime import SafeActionRuntime
from jarvis_core.task_control import TaskControlService
from jarvis_core.tasks import TaskQueue


def stack(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    logger = JsonlLogger(tmp_path / "logs")
    events = EventBus(conn, logger)
    runtime = SafeActionRuntime(logger, conn, events)
    approvals = ApprovalQueue(conn, events)
    tasks = TaskQueue(conn, events, runtime, approvals)
    task_control = TaskControlService(tasks)
    return conn, events, tasks, task_control


def test_stop_task_status_returns_safe_boundary_metadata(tmp_path):
    _, _, _, task_control = stack(tmp_path)

    status = task_control.stop_status()
    status_text = str(status).lower()

    assert status["requirement"] == "v0.1C stop-task control boundary"
    assert status["safeBackendCancellationAvailable"] is True
    assert status["stopControlsEnabled"] is False
    assert status["backendType"] == "jarvis_task_queue_state_only"
    assert status["osProcessControl"] is False
    assert status["arbitraryProcessKill"] is False
    assert status["pidAccepted"] is False
    assert status["processNameAccepted"] is False
    assert status["shellCommandAccepted"] is False
    assert "taskkill" not in status_text


def test_active_tasks_expose_only_safe_jarvis_task_fields(tmp_path):
    _, _, tasks, task_control = stack(tmp_path)
    task = tasks.create_task("sample", "coding_agent", "operate", dry_run=False, write_capable=True)

    active = task_control.active_tasks()

    assert active[0]["taskId"] == task["task_id"]
    assert active[0]["status"] == "queued"
    assert "pid" not in active[0]
    assert "processName" not in active[0]
    assert "command" not in active[0]


def test_stop_task_accepts_only_active_jarvis_owned_task_id_and_records_event(tmp_path):
    conn, events, tasks, task_control = stack(tmp_path)
    task = tasks.create_task("sample", "coding_agent", "operate", dry_run=False, write_capable=True)

    result = task_control.stop_task(task["task_id"])

    assert result["stopAccepted"] is True
    assert result["taskId"] == task["task_id"]
    assert result["status"] == "canceled"
    assert result["osProcessControl"] is False
    assert result["pidAccepted"] is False
    assert tasks.get_task(task["task_id"])["status"] == "canceled"
    assert conn.execute("select count(*) from project_locks where task_id = ?", (task["task_id"],)).fetchone()[0] == 0
    assert any(event["event_type"] == "task.canceled" for event in events.list_events(task["task_id"]))


def test_stop_task_rejects_unknown_task_id(tmp_path):
    _, _, _, task_control = stack(tmp_path)

    with pytest.raises(KeyError):
        task_control.stop_task("not-a-task")


def test_stop_task_rejects_non_active_task(tmp_path):
    _, _, tasks, task_control = stack(tmp_path)
    task = tasks.create_task("sample", "coding_agent", "inspect", dry_run=True)

    with pytest.raises(ValueError):
        task_control.stop_task(task["task_id"])


def test_stop_task_endpoint_maps_unknown_and_non_active_tasks(tmp_path, monkeypatch):
    _, _, tasks, task_control = stack(tmp_path)
    monkeypatch.setattr(app_module, "task_control", task_control)

    with pytest.raises(HTTPException) as unknown:
        app_module.stop_dashboard_task("missing")
    assert unknown.value.status_code == 404

    task = tasks.create_task("sample", "coding_agent", "inspect", dry_run=True)
    with pytest.raises(HTTPException) as non_active:
        app_module.stop_dashboard_task(task["task_id"])
    assert non_active.value.status_code == 409


def test_stop_task_routes_have_lan_guard_dependency():
    protected_paths = {
        "/api/tasks/active",
        "/api/tasks/stop/status",
        "/api/tasks/{task_id}/stop",
        "/tasks/{task_id}/cancel",
    }

    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_no_arbitrary_process_kill_route_is_exposed():
    route_paths = {getattr(route, "path", "") for route in app_module.app.routes}
    route_text = " ".join(sorted(route_paths)).lower()

    assert "/api/tasks/{task_id}/stop" in route_paths
    assert "pid" not in route_text
    assert "process" not in route_text
    assert "taskkill" not in route_text
    assert "kill" not in route_text
