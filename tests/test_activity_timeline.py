import json

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.activity_timeline import ActivityTimelineService
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access


def service(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    return ActivityTimelineService(conn)


def app_service(tmp_path, monkeypatch):
    timeline = service(tmp_path)
    monkeypatch.setattr(app_module, "activity_timeline", timeline)
    return timeline


def insert_task(conn, task_id, created_at, status="succeeded", summary="safe summary"):
    conn.execute(
        """
        insert into tasks (
          task_id, project_name, agent_id, task_type, status, autonomy_level, dry_run,
          write_capable, created_at, started_at, finished_at, summary, error
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (task_id, "Jarvis", "coding_agent", "report", status, "supervised", 1, 0, created_at, None, None, summary, None),
    )
    conn.commit()


def insert_event(conn, event_id, created_at, payload=None):
    conn.execute(
        "insert into events (event_id, task_id, event_type, payload, created_at) values (?, ?, ?, ?, ?)",
        (event_id, "task-1", "task.succeeded", json.dumps(payload or {"summary": "safe"}), created_at),
    )
    conn.commit()


def insert_approval(conn, approval_id, created_at, reason="safe approval reason"):
    conn.execute(
        """
        insert into approvals (
          approval_id, task_id, action_id, action_type, project_name, risk_level,
          reason, status, requested_at, resolved_at, resolved_by, resolution_note
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (approval_id, "task-1", "action-1", "risk_budget", "Jarvis", "medium", reason, "pending", created_at, None, None, None),
    )
    conn.commit()


def insert_security(conn, item_id, created_at, detail="safe security note"):
    conn.execute(
        "insert into security_events (id, event_type, detail, created_at) values (?, ?, ?, ?)",
        (item_id, "blocked", detail, created_at),
    )
    conn.commit()


def insert_receipt(conn, receipt_id, created_at, result="raw stdout should not appear"):
    conn.execute(
        """
        insert into action_receipts (
          receipt_id, task_id, agent_id, tool_id, action_type, target, approved, blocked,
          approval_required, risk_level, started_at, finished_at, result, reason
        ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (receipt_id, "task-1", "coding_agent", "report_tool", "write_report", "Jarvis", 1, 0, 0, "low", created_at, created_at, result, "report metadata recorded"),
    )
    conn.commit()


def test_empty_timeline_works(tmp_path):
    timeline = service(tmp_path).timeline()

    assert timeline["totalRecentItems"] == 0
    assert timeline["items"] == []
    assert timeline["limit"] == 25


def test_recent_tasks_events_approvals_are_summarized_safely(tmp_path):
    timeline = service(tmp_path)
    insert_task(timeline.conn, "task-1", "2026-01-01T00:00:00Z", summary="Task finished")
    insert_event(timeline.conn, "event-1", "2026-01-01T00:01:00Z", payload={"secret": "github_pat_" + "a" * 24})
    insert_approval(timeline.conn, "approval-1", "2026-01-01T00:02:00Z", reason="Approval requested")
    insert_security(timeline.conn, 1, "2026-01-01T00:03:00Z", detail="Policy blocked unsafe request")
    insert_receipt(timeline.conn, "receipt-1", "2026-01-01T00:04:00Z")

    result = timeline.timeline()
    item_types = {item["itemType"] for item in result["items"]}

    assert {"task", "event", "approval", "security", "receipt"}.issubset(item_types)
    assert result["countsByType"]["task"] == 1
    assert result["countsByStatus"]["pending"] == 1


def test_result_limit_enforced(tmp_path):
    timeline = service(tmp_path)
    for index in range(30):
        insert_task(timeline.conn, f"task-{index}", f"2026-01-01T00:{index:02d}:00Z")

    result = timeline.timeline(limit=5)

    assert result["limit"] == 5
    assert len(result["items"]) == 5


def test_max_limit_enforced(tmp_path):
    timeline = service(tmp_path)
    for index in range(105):
        insert_task(timeline.conn, f"task-{index}", f"2026-01-01T{index // 60:02d}:{index % 60:02d}:00Z")

    result = timeline.timeline(limit=999)

    assert result["limit"] == 100
    assert len(result["items"]) == 100


def test_item_detail_works_for_safe_metadata(tmp_path):
    timeline = service(tmp_path)
    insert_task(timeline.conn, "task-1", "2026-01-01T00:00:00Z", summary="Task finished")

    detail = timeline.item_detail("task:task-1")

    assert detail["itemId"] == "task:task-1"
    assert detail["detailType"] == "safe_metadata_only"
    assert detail["rawCommandOutputIncluded"] is False


def test_traversal_or_unknown_item_id_blocked_or_404(tmp_path, monkeypatch):
    app_service(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as traversal:
        app_module.get_activity_timeline_detail("..%2Ftask:task-1")
    with pytest.raises(HTTPException) as unknown:
        app_module.get_activity_timeline_detail("task:missing")

    assert traversal.value.status_code == 400
    assert unknown.value.status_code == 404


def test_synthetic_secrets_and_private_paths_redacted(tmp_path):
    timeline = service(tmp_path)
    raw_token = "github_pat_" + "a" * 24
    raw_path = "C:/Users/example/private/.env"
    insert_task(timeline.conn, "task-1", "2026-01-01T00:00:00Z", summary=f"token={raw_token} path {raw_path}")
    insert_approval(timeline.conn, "approval-1", "2026-01-01T00:01:00Z", reason="user@example.test used /home/example/private/.env")

    text = json.dumps(timeline.timeline(), sort_keys=True)

    assert raw_token not in text
    assert raw_path not in text
    assert "user@example.test" not in text
    assert "/home/example" not in text
    assert "<redacted" in text


def test_raw_command_output_not_exposed(tmp_path):
    timeline = service(tmp_path)
    raw_output = "stdout SECRET_OUTPUT github_pat_" + "b" * 24
    insert_event(timeline.conn, "event-1", "2026-01-01T00:00:00Z", payload={"stdout": raw_output})
    insert_receipt(timeline.conn, "receipt-1", "2026-01-01T00:01:00Z", result=raw_output)

    text = json.dumps(timeline.timeline(), sort_keys=True)

    assert raw_output not in text
    assert "stdout SECRET_OUTPUT" not in text
    assert '"payload"' not in text
    assert '"result"' not in text
    assert '"rawCommandOutputIncluded": false' in text


def test_activity_timeline_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/activity/timeline",
        "/activity/timeline/{item_id}",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_no_mutation_external_call_or_command_behavior_in_source(tmp_path):
    source = (app_module.WORKSPACE_ROOT / "services/jarvis-core/src/jarvis_core/activity_timeline.py").read_text(
        encoding="utf-8"
    )
    forbidden_source = ["subprocess", "requests.", "httpx", "urllib.request", "open(", ".write(", "unlink(", "remove("]

    assert all(token not in source for token in forbidden_source)
    summary = service(tmp_path).timeline()
    assert summary["mutation"] is False
    assert summary["externalServices"] is False
    assert summary["uploads"] is False
    assert summary["certification"] is False
