from __future__ import annotations

import importlib
import sys

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

import jarvis_core.audit as audit_module
import jarvis_core.db as db_module
from jarvis_core.audit import JsonlLogger
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access


@pytest.fixture
def api_module(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    real_logger_class = JsonlLogger
    monkeypatch.setattr(db_module, "init_db", lambda _path: conn)
    monkeypatch.setattr(
        audit_module,
        "JsonlLogger",
        lambda _path: real_logger_class(tmp_path / "logs"),
    )
    sys.modules.pop("jarvis_core.app", None)
    module = importlib.import_module("jarvis_core.app")
    yield module
    sys.modules.pop("jarvis_core.app", None)
    conn.close()


def proposal_payload(module, **overrides):
    values = {
        "memoryType": "preference",
        "content": "Keep local responses concise.",
        "scopeType": "global",
        "scopeValue": None,
        "sourceType": "manual",
        "confidence": "high",
        "sensitivity": "standard",
    }
    values.update(overrides)
    return module.MemoryProposalInput.model_validate(values)


def create_proposal(module, **overrides):
    return module.create_memory_proposal(proposal_payload(module, **overrides))


def test_proposal_listing_filtering_and_fetch(api_module):
    first = create_proposal(api_module)
    create_proposal(
        api_module,
        memoryType="project_fact",
        content="Alpha is a local project.",
        scopeType="project",
        scopeValue="Alpha",
    )

    listed = api_module.list_memories(
        memoryType="project_fact",
        scopeType="project",
        scopeValue="Alpha",
        limit=50,
        offset=0,
    )
    fetched = api_module.get_memory(first["memoryId"])
    summary = api_module.memory_summary()

    assert first["status"] == "pending"
    assert listed[0]["content"] == "Alpha is a local project."
    assert fetched == first
    assert summary["total"] == 2


def test_approval_requires_explicit_resolution_and_maps_conflicts(api_module):
    memory_id = create_proposal(api_module)["memoryId"]

    with pytest.raises(ValidationError):
        api_module.MemoryApprovalInput.model_validate({})

    approved = api_module.approve_memory(
        memory_id,
        api_module.MemoryApprovalInput(resolution="approve"),
    )
    assert approved["status"] == "approved"
    assert approved["approvedBy"] == "local_user"

    with pytest.raises(HTTPException) as exc_info:
        api_module.approve_memory(
            memory_id,
            api_module.MemoryApprovalInput(resolution="approve"),
        )
    assert exc_info.value.status_code == 409


def test_rejection_and_invalid_rejected_to_approved_transition(api_module):
    memory_id = create_proposal(api_module, content="Reject this.")["memoryId"]

    rejected = api_module.reject_memory(
        memory_id,
        api_module.MemoryRejectionInput(
            resolution="reject",
            rejectionReason="Not needed.",
        ),
    )
    assert rejected["status"] == "rejected"
    assert rejected["rejectionReason"] == "Not needed."

    with pytest.raises(HTTPException) as exc_info:
        api_module.approve_memory(
            memory_id,
            api_module.MemoryApprovalInput(resolution="approve"),
        )
    assert exc_info.value.status_code == 409


def test_edit_disable_and_enable(api_module):
    memory_id = create_proposal(api_module)["memoryId"]
    api_module.approve_memory(
        memory_id,
        api_module.MemoryApprovalInput(resolution="approve"),
    )

    edited = api_module.edit_memory(
        memory_id,
        api_module.MemoryEditInput(content="Use detail when the user asks."),
    )
    assert edited["status"] == "pending"
    assert edited["reapprovalRequired"] is True
    api_module.approve_memory(
        memory_id,
        api_module.MemoryApprovalInput(resolution="approve"),
    )

    disabled = api_module.disable_memory(
        memory_id,
        api_module.MemoryActorInput(),
    )
    enabled = api_module.enable_memory(
        memory_id,
        api_module.MemoryActorInput(),
    )
    assert disabled["status"] == "disabled"
    assert enabled["status"] == "approved"
    assert enabled["content"] == edited["content"]


def test_delete_confirms_without_returning_content(api_module):
    content = "Delete this private local fact."
    memory_id = create_proposal(api_module, content=content)["memoryId"]

    result = api_module.delete_memory(memory_id)

    assert result == {"memoryId": memory_id, "deleted": True}
    assert content not in str(result)
    with pytest.raises(HTTPException) as exc_info:
        api_module.get_memory(memory_id)
    assert exc_info.value.status_code == 404


def test_unknown_fields_and_direct_status_assignment_are_rejected(api_module):
    raw = {
        "memoryType": "preference",
        "content": "Never auto-save.",
        "scopeType": "global",
        "sourceType": "manual",
        "confidence": "high",
        "sensitivity": "standard",
        "status": "approved",
    }

    with pytest.raises(ValidationError):
        api_module.MemoryProposalInput.model_validate(raw)
    with pytest.raises(ValidationError):
        api_module.MemoryEditInput.model_validate({"status": "approved"})
    with pytest.raises(ValidationError):
        api_module.MemoryEditInput.model_validate({"unexpected": True})


def test_missing_memory_maps_to_404(api_module):
    with pytest.raises(HTTPException) as exc_info:
        api_module.get_memory("missing-memory")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "memory not found"


def test_secret_rejection_does_not_echo_secret(api_module):
    secret = "api_key=sk_this_value_must_never_be_logged"

    with pytest.raises(HTTPException) as exc_info:
        create_proposal(api_module, content=secret)

    assert exc_info.value.status_code == 422
    assert secret not in str(exc_info.value.detail)
    assert api_module.memory_service.summary()["total"] == 0


def test_all_memory_routes_keep_existing_lan_access_dependency(api_module):
    protected_paths = {
        "/api/memory/summary",
        "/api/memories",
        "/api/memories/{memory_id}",
        "/api/memories/proposals",
        "/api/memories/{memory_id}/approve",
        "/api/memories/{memory_id}/reject",
        "/api/memories/{memory_id}/disable",
        "/api/memories/{memory_id}/enable",
    }
    routes = [
        route
        for route in api_module.app.routes
        if getattr(route, "path", None) in protected_paths
    ]

    assert {route.path for route in routes} == protected_paths
    assert any(
        "PATCH" in route.methods and route.path == "/api/memories/{memory_id}"
        for route in routes
    )
    assert any(
        "DELETE" in route.methods and route.path == "/api/memories/{memory_id}"
        for route in routes
    )
    for route in routes:
        dependency_calls = {
            dependency.call for dependency in route.dependant.dependencies
        }
        assert require_dashboard_lan_access in dependency_calls


def test_query_parameter_and_combined_status_filter(api_module):
    pending = create_proposal(api_module, content="Searchable API memory.")
    approved = create_proposal(api_module, content="Searchable API approved memory.")
    api_module.approve_memory(
        approved["memoryId"],
        api_module.MemoryApprovalInput(resolution="approve"),
    )

    queried = api_module.list_memories(query="searchable api", limit=50, offset=0)
    pending_only = api_module.list_memories(
        query="searchable api",
        status="pending",
        limit=50,
        offset=0,
    )

    assert {record["memoryId"] for record in queried} == {pending["memoryId"], approved["memoryId"]}
    assert [record["memoryId"] for record in pending_only] == [pending["memoryId"]]


def test_query_validation_maps_to_422(api_module):
    with pytest.raises(HTTPException) as exc_info:
        api_module.list_memories(query="x" * 201, limit=50, offset=0)

    assert exc_info.value.status_code == 422


def test_memory_event_endpoint_is_redacted_and_survives_deletion(api_module):
    content = "Event history must never reproduce this full content."
    memory_id = create_proposal(api_module, content=content)["memoryId"]
    api_module.approve_memory(
        memory_id,
        api_module.MemoryApprovalInput(resolution="approve"),
    )

    existing_events = api_module.get_memory_events(memory_id)
    api_module.delete_memory(memory_id)
    deleted_events = api_module.get_memory_events(memory_id)

    assert [event["eventType"] for event in existing_events] == ["memory.proposed", "memory.approved"]
    assert deleted_events[-1]["eventType"] == "memory.deleted"
    assert content not in str(existing_events)
    assert content not in str(deleted_events)


def test_memory_event_endpoint_returns_404_without_memory_or_history(api_module):
    with pytest.raises(HTTPException) as exc_info:
        api_module.get_memory_events("unknown-memory")

    assert exc_info.value.status_code == 404


def test_context_preview_private_session_returns_zero_and_keeps_admin_visibility(api_module):
    memory_id = create_proposal(api_module, content="Private preview global memory.")["memoryId"]
    api_module.approve_memory(
        memory_id,
        api_module.MemoryApprovalInput(resolution="approve"),
    )

    result = api_module.preview_memory_context(
        api_module.MemoryContextPreviewInput(privateSession=True)
    )
    administrative = api_module.list_memories(limit=50, offset=0)

    assert result["count"] == 0
    assert result["memories"] == []
    assert result["policy"]["memoryUseAllowed"] is False
    assert [record["memoryId"] for record in administrative] == [memory_id]
    assert "No response agent was invoked." in result["limitations"]
    assert "No relevance ranking was performed." in result["limitations"]


def test_context_preview_project_and_agent_scope(api_module):
    global_id = create_proposal(api_module, content="Global context API memory.")["memoryId"]
    project_id = create_proposal(
        api_module,
        content="Alpha project context API memory.",
        scopeType="project",
        scopeValue="Alpha",
    )["memoryId"]
    agent_id = create_proposal(
        api_module,
        content="Planning agent context API memory.",
        scopeType="agent",
        scopeValue="local_planning_agent",
    )["memoryId"]
    for memory_id in (global_id, project_id, agent_id):
        api_module.approve_memory(
            memory_id,
            api_module.MemoryApprovalInput(resolution="approve"),
        )

    project_result = api_module.preview_memory_context(
        api_module.MemoryContextPreviewInput(projectName="  Alpha  ")
    )
    agent_result = api_module.preview_memory_context(
        api_module.MemoryContextPreviewInput(agentId="local_planning_agent")
    )

    assert project_result["context"]["projectName"] == "Alpha"
    assert {record["memoryId"] for record in project_result["memories"]} == {global_id, project_id}
    assert {record["memoryId"] for record in agent_result["memories"]} == {global_id, agent_id}


def test_context_preview_rejects_unknown_agent_and_unknown_fields(api_module):
    with pytest.raises(HTTPException) as exc_info:
        api_module.preview_memory_context(
            api_module.MemoryContextPreviewInput(agentId="not_an_existing_agent")
        )
    assert exc_info.value.status_code == 422

    with pytest.raises(ValidationError):
        api_module.MemoryContextPreviewInput.model_validate({"unexpected": True})


def test_context_preview_limit_validation(api_module):
    with pytest.raises(ValidationError):
        api_module.MemoryContextPreviewInput.model_validate({"limit": 0})
    with pytest.raises(ValidationError):
        api_module.MemoryContextPreviewInput.model_validate({"limit": 201})


def test_new_memory_routes_keep_existing_lan_access_dependency(api_module):
    protected_methods = {
        ("POST", "/api/memory/context-preview"),
        ("GET", "/api/memories/{memory_id}/events"),
    }
    matched = set()
    for route in api_module.app.routes:
        route_path = getattr(route, "path", None)
        for method, path in protected_methods:
            if route_path == path and method in getattr(route, "methods", set()):
                dependency_calls = {
                    dependency.call for dependency in route.dependant.dependencies
                }
                assert require_dashboard_lan_access in dependency_calls
                matched.add((method, path))

    assert matched == protected_methods
