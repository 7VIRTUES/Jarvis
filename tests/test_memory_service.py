from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from jarvis_core.audit import JsonlLogger
from jarvis_core.db import init_db
from jarvis_core.events import EventBus
from jarvis_core.memory import (
    MAX_CONTENT_LENGTH,
    MemoryConflictError,
    MemorySecretError,
    MemoryService,
    MemoryUseContext,
    MemoryValidationError,
)


KNOWN_AGENT = "local_planning_agent"


@pytest.fixture
def memory_env(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    logger = JsonlLogger(tmp_path / "logs")
    events = EventBus(conn, logger)
    service = MemoryService(
        conn,
        events,
        agent_exists=lambda agent_id: agent_id == KNOWN_AGENT,
    )
    return service, conn, logger


def proposal(service: MemoryService, **overrides):
    values = {
        "memory_type": "preference",
        "content": "Use concise local summaries.",
        "scope_type": "global",
        "scope_value": None,
        "source_type": "manual",
        "confidence": "high",
        "sensitivity": "standard",
        "actor": "local_user",
    }
    values.update(overrides)
    return service.create_proposal(**values)


def test_database_initialization_is_idempotent(tmp_path):
    path = tmp_path / "jarvis.sqlite"
    first = init_db(path)
    proposal(MemoryService(first))
    first.close()

    second = init_db(path)
    tables = {
        row[0]
        for row in second.execute(
            "select name from sqlite_master where type = 'table'"
        ).fetchall()
    }
    indexes = {
        row[0]
        for row in second.execute(
            "select name from sqlite_master where type = 'index'"
        ).fetchall()
    }

    assert {"memories", "memory_events"} <= tables
    assert {
        "idx_memories_status",
        "idx_memories_memory_type",
        "idx_memories_scope",
        "idx_memories_expiration",
        "idx_memories_content_hash",
        "idx_memory_events_memory_date",
    } <= indexes
    assert second.execute("select count(*) from memories").fetchone()[0] == 1


def test_proposal_is_normalized_and_always_pending(memory_env):
    service, _, _ = memory_env

    record = proposal(service, content="  First line\r\nSecond line.  ")

    assert record["status"] == "pending"
    assert record["effectiveStatus"] == "pending"
    assert record["active"] is False
    assert record["content"] == "First line\nSecond line."
    assert record["approvedAt"] is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("memory_type", "unknown"),
        ("confidence", "certain"),
        ("sensitivity", "classified"),
        ("scope_type", "workspace"),
        ("source_type", "browser_import"),
    ],
)
def test_controlled_vocabulary_validation(memory_env, field, value):
    service, _, _ = memory_env

    with pytest.raises(MemoryValidationError):
        proposal(service, **{field: value})


def test_scope_and_agent_validation(memory_env):
    service, _, _ = memory_env

    with pytest.raises(MemoryValidationError):
        proposal(service, scope_type="global", scope_value="unexpected")
    with pytest.raises(MemoryValidationError):
        proposal(service, scope_type="project", scope_value="")
    with pytest.raises(MemoryValidationError):
        proposal(service, scope_type="agent", scope_value="missing_agent")

    record = proposal(
        service,
        scope_type="agent",
        scope_value=KNOWN_AGENT,
        source_type="agent_proposal",
        source_agent_id=KNOWN_AGENT,
    )
    assert record["scopeValue"] == KNOWN_AGENT


def test_agent_proposal_requires_existing_source_agent(memory_env):
    service, _, _ = memory_env

    with pytest.raises(MemoryValidationError):
        proposal(service, source_type="agent_proposal")
    with pytest.raises(MemoryValidationError):
        proposal(
            service,
            source_type="agent_proposal",
            source_agent_id="missing_agent",
        )


def test_content_length_limit(memory_env):
    service, _, _ = memory_env

    with pytest.raises(MemoryValidationError):
        proposal(service, content="x" * (MAX_CONTENT_LENGTH + 1))


@pytest.mark.parametrize(
    "secret_content",
    [
        "password=correct-horse-battery-staple",
        "api_key: sk_this_is_a_long_secret_value",
        "Authorization: Bearer eyJabcdefgh.abcdefghijk.abcdefghijk",
        "-----BEGIN PRIVATE KEY-----\nsecret material",
        "Cookie: sessionid=abcdef0123456789abcdef",
    ],
)
def test_secret_like_content_is_rejected_before_persistence(memory_env, secret_content):
    service, conn, logger = memory_env

    with pytest.raises(MemorySecretError) as exc_info:
        proposal(service, content=secret_content)

    assert secret_content not in str(exc_info.value)
    assert conn.execute("select count(*) from memories").fetchone()[0] == 0
    assert conn.execute("select count(*) from memory_events").fetchone()[0] == 0
    assert not (logger.root / "actions.jsonl").exists()


def test_approval_rejection_disable_enable_and_invalid_transitions(memory_env):
    service, _, _ = memory_env
    approved_id = proposal(service)["memoryId"]

    approved = service.approve(approved_id, approved_by="local_user")
    assert approved["status"] == "approved"
    assert approved["active"] is True
    assert approved["approvedBy"] == "local_user"
    assert approved["lastConfirmedAt"] is not None

    with pytest.raises(MemoryConflictError):
        service.approve(approved_id)
    with pytest.raises(MemoryConflictError):
        service.reject(approved_id)

    disabled = service.disable(approved_id)
    assert disabled["status"] == "disabled"
    assert disabled["active"] is False
    enabled = service.enable(approved_id)
    assert enabled["status"] == "approved"
    assert enabled["content"] == approved["content"]

    rejected_id = proposal(service, content="Reject this proposal.")["memoryId"]
    rejected = service.reject(
        rejected_id,
        rejected_by="local_user",
        rejection_reason="Not useful.",
    )
    assert rejected["status"] == "rejected"
    assert rejected["rejectionReason"] == "Not useful."
    with pytest.raises(MemoryConflictError):
        service.approve(rejected_id)


def test_substantive_edit_requires_reapproval_and_changes_hash(memory_env):
    service, conn, _ = memory_env
    memory_id = proposal(service)["memoryId"]
    service.approve(memory_id)
    old_hash = conn.execute(
        "select content_hash from memories where memory_id = ?", (memory_id,)
    ).fetchone()[0]

    edited = service.edit(
        memory_id,
        {"content": "Use detailed summaries when requested."},
    )
    new_hash = conn.execute(
        "select content_hash from memories where memory_id = ?", (memory_id,)
    ).fetchone()[0]

    assert edited["status"] == "pending"
    assert edited["statusChanged"] is True
    assert edited["reapprovalRequired"] is True
    assert edited["approvedAt"] is None
    assert old_hash != new_hash


def test_rejected_edit_returns_to_pending(memory_env):
    service, _, _ = memory_env
    memory_id = proposal(service)["memoryId"]
    service.reject(memory_id, rejection_reason="Needs correction.")

    edited = service.edit(memory_id, {"confidence": "medium"})

    assert edited["status"] == "pending"
    assert edited["rejectedAt"] is None
    assert edited["rejectionReason"] is None


def test_no_op_edit_does_not_create_false_transition(memory_env):
    service, conn, _ = memory_env
    record = proposal(service)
    before_events = conn.execute(
        "select count(*) from memory_events where memory_id = ?",
        (record["memoryId"],),
    ).fetchone()[0]

    edited = service.edit(record["memoryId"], {"content": record["content"]})
    after_events = conn.execute(
        "select count(*) from memory_events where memory_id = ?",
        (record["memoryId"],),
    ).fetchone()[0]

    assert edited["status"] == "pending"
    assert edited["changedFields"] == []
    assert edited["statusChanged"] is False
    assert edited["reapprovalRequired"] is False
    assert after_events == before_events


def test_expired_pending_rejected_and_disabled_memories_are_inactive(memory_env):
    service, _, _ = memory_env
    past = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    expired_id = proposal(service, content="Expired.", expires_at=past)["memoryId"]
    expired = service.approve(expired_id)
    pending = proposal(service, content="Pending.")
    rejected_id = proposal(service, content="Rejected.")["memoryId"]
    rejected = service.reject(rejected_id)
    disabled_id = proposal(service, content="Disabled.")["memoryId"]
    service.approve(disabled_id)
    disabled = service.disable(disabled_id)

    assert expired["status"] == "approved"
    assert expired["effectiveStatus"] == "expired"
    assert service.is_active(expired) is False
    assert all(
        service.is_active(record) is False
        for record in (pending, rejected, disabled)
    )


def test_private_session_and_context_scope_filtering(memory_env):
    service, conn, _ = memory_env
    global_id = proposal(service, content="Global.")["memoryId"]
    project_id = proposal(
        service,
        content="Project Alpha.",
        scope_type="project",
        scope_value="Alpha",
    )["memoryId"]
    other_project_id = proposal(
        service,
        content="Project Beta.",
        scope_type="project",
        scope_value="Beta",
    )["memoryId"]
    agent_id = proposal(
        service,
        content="Agent scoped.",
        scope_type="agent",
        scope_value=KNOWN_AGENT,
    )["memoryId"]
    for memory_id in (global_id, project_id, other_project_id, agent_id):
        service.approve(memory_id)
    before_events = conn.execute("select count(*) from memory_events").fetchone()[0]

    private_results = service.list_active_memories(
        MemoryUseContext(
            private_session=True,
            project_name="Alpha",
            agent_id=KNOWN_AGENT,
        )
    )
    normal_results = service.list_active_memories(
        MemoryUseContext(project_name="Alpha", agent_id=KNOWN_AGENT)
    )
    after_events = conn.execute("select count(*) from memory_events").fetchone()[0]

    assert private_results == []
    assert {record["memoryId"] for record in normal_results} == {
        global_id,
        project_id,
        agent_id,
    }
    assert other_project_id not in {record["memoryId"] for record in normal_results}
    assert before_events == after_events
    assert service.apply_private_session_policy(MemoryUseContext(private_session=True)) == {
        "privateSession": True,
        "memoryUseAllowed": False,
        "automaticProposalAllowed": False,
        "automaticPersistenceAllowed": False,
    }


def test_listing_filters_summary_and_pagination_limits(memory_env):
    service, _, _ = memory_env
    for index in range(3):
        proposal(
            service,
            content=f"Project memory {index}.",
            memory_type="project_fact",
            scope_type="project",
            scope_value="Alpha",
        )
    approved_id = proposal(service, content="Approved global.")["memoryId"]
    service.approve(approved_id)

    page = service.list_memories(
        memory_type="project_fact",
        scope_type="project",
        scope_value="Alpha",
        limit=2,
        offset=1,
    )
    summary = service.summary()

    assert len(page) == 2
    assert all(record["memoryType"] == "project_fact" for record in page)
    assert summary["total"] == 4
    assert summary["counts"]["pending"] == 3
    assert summary["counts"]["approved"] == 1
    assert summary["active"] == 1
    with pytest.raises(MemoryValidationError):
        service.list_memories(limit=201)
    with pytest.raises(MemoryValidationError):
        service.list_memories(offset=-1)


def test_hard_delete_removes_content_and_preserves_redacted_audit(memory_env):
    service, conn, logger = memory_env
    content = "A private preference that must be deleted."
    memory_id = proposal(service, content=content)["memoryId"]

    result = service.delete(memory_id)
    events = service.list_memory_events(memory_id)
    database_dump = "\n".join(
        str(row)
        for row in conn.execute(
            "select event_type, metadata from memory_events where memory_id = ?",
            (memory_id,),
        ).fetchall()
    )
    event_bus_dump = "\n".join(
        row[0]
        for row in conn.execute(
            "select payload from events where event_type like 'memory.%'"
        ).fetchall()
    )
    jsonl_dump = (logger.root / "actions.jsonl").read_text(encoding="utf-8")

    assert result == {"memoryId": memory_id, "deleted": True}
    assert conn.execute(
        "select count(*) from memories where memory_id = ?", (memory_id,)
    ).fetchone()[0] == 0
    assert events[-1]["eventType"] == "memory.deleted"
    assert content not in database_dump
    assert content not in event_bus_dump
    assert content not in jsonl_dump
    assert all("content" not in json.dumps(event["metadata"]).lower() for event in events)
