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
