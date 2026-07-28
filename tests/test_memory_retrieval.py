from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from jarvis_core.audit import JsonlLogger
from jarvis_core.db import init_db, memory_fts5_available
from jarvis_core.events import EventBus
from jarvis_core.memory import MemoryService, MemoryValidationError
from jarvis_core.memory_retrieval import MemoryRetrievalRequest, MemoryRetrievalService


PILOT_AGENTS = {
    "local_planning_agent",
    "local_drafting_agent",
    "local_decision_agent",
    "local_career_agent",
    "local_personal_knowledge_memory_organizer",
    "local_life_dashboard_cross_agent_coordinator",
}


@pytest.fixture
def retrieval_env(tmp_path):
    conn = init_db(tmp_path / "jarvis.sqlite")
    logger = JsonlLogger(tmp_path / "logs")
    event_bus = EventBus(conn, logger)
    exists = lambda agent_id: agent_id in PILOT_AGENTS
    memory = MemoryService(conn, event_bus, agent_exists=exists)
    retrieval = MemoryRetrievalService(conn, event_bus, agent_exists=exists)
    return memory, retrieval, conn, logger


def approved(memory: MemoryService, content: str, **overrides):
    values = {
        "memory_type": "preference",
        "content": content,
        "scope_type": "global",
        "scope_value": None,
        "source_type": "manual",
        "confidence": "high",
        "sensitivity": "standard",
    }
    values.update(overrides)
    record = memory.create_proposal(**values)
    return memory.approve(record["memoryId"])


def request(query="concise planning", **overrides):
    values = {"query": query, "purpose": "manual_preview"}
    values.update(overrides)
    return MemoryRetrievalRequest(**values)


def test_fts_initialization_backfill_sync_and_hard_delete_are_idempotent(tmp_path):
    path = tmp_path / "jarvis.sqlite"
    conn = init_db(path)
    memory = MemoryService(conn, agent_exists=lambda _agent: True)
    record = approved(memory, "First indexed planning memory.")
    if not memory_fts5_available(conn):
        pytest.skip("SQLite build does not include FTS5")
    memory_id = record["memoryId"]
    assert conn.execute("select count(*) from memory_fts where memory_id = ?", (memory_id,)).fetchone()[0] == 1

    memory.edit(memory_id, {"content": "Edited indexed drafting memory."})
    indexed = conn.execute("select content from memory_fts where memory_id = ?", (memory_id,)).fetchone()
    assert indexed[0] == "Edited indexed drafting memory."
    memory.edit(memory_id, {"scope_type": "project", "scope_value": "Alpha"})
    assert conn.execute("select scope_type, scope_value from memory_fts where memory_id = ?", (memory_id,)).fetchone() == ("project", "Alpha")
    conn.close()

    conn = init_db(path)
    assert conn.execute("select count(*) from memory_fts where memory_id = ?", (memory_id,)).fetchone()[0] == 1
    MemoryService(conn).delete(memory_id)
    assert conn.execute("select count(*) from memory_fts where memory_id = ?", (memory_id,)).fetchone()[0] == 0


def test_fallback_reports_capability_and_contract(retrieval_env):
    memory, _, conn, _ = retrieval_env
    approved(memory, "Concise planning response preference.")
    fallback = MemoryRetrievalService(conn, agent_exists=lambda agent_id: agent_id in PILOT_AGENTS, fts5_available=False)
    result = fallback.retrieve(request())
    assert result["fts5Available"] is False
    assert result["retrievalMode"] == "deterministic_fallback"
    assert result["selectedCount"] == 1
    assert set(result["items"][0]) >= {
        "memoryId", "memoryType", "content", "scopeType", "rank", "textScore",
        "scopePriority", "memoryTypePriority", "confidencePriority", "matchReasons",
    }


def test_status_expiration_sensitivity_and_exact_scope_filters(retrieval_env):
    memory, retrieval, _, _ = retrieval_env
    global_id = approved(memory, "Alpha planning global.")["memoryId"]
    project_id = approved(memory, "Alpha planning project.", scope_type="project", scope_value="Alpha")["memoryId"]
    approved(memory, "Alpha planning wrong project.", scope_type="project", scope_value="Beta")
    agent_id = approved(memory, "Alpha planning agent.", scope_type="agent", scope_value="local_planning_agent")["memoryId"]
    approved(memory, "Alpha planning wrong agent.", scope_type="agent", scope_value="local_drafting_agent")
    sensitive_id = approved(memory, "Alpha planning sensitive.", sensitivity="sensitive")["memoryId"]
    approved(memory, "Alpha planning expired.", expires_at=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat())
    pending = memory.create_proposal(memory_type="preference", content="Alpha planning pending.", scope_type="global", scope_value=None, source_type="manual", confidence="high", sensitivity="standard")
    rejected = memory.create_proposal(memory_type="preference", content="Alpha planning rejected.", scope_type="global", scope_value=None, source_type="manual", confidence="high", sensitivity="standard")
    memory.reject(rejected["memoryId"])
    disabled = approved(memory, "Alpha planning disabled.")
    memory.disable(disabled["memoryId"])

    result = retrieval.retrieve(request("Alpha planning", project_name="Alpha", agent_id="local_planning_agent"))
    ids = {item["memoryId"] for item in result["items"]}
    assert {global_id, project_id, agent_id} <= ids
    assert sensitive_id not in ids
    assert pending["memoryId"] not in ids
    assert rejected["memoryId"] not in ids
    assert disabled["memoryId"] not in ids
    assert all(item["scopeValue"] != "Beta" for item in result["items"])
    assert all(item["scopeValue"] != "local_drafting_agent" for item in result["items"])

    sensitive = retrieval.retrieve(request("sensitive", include_sensitive=True))
    assert sensitive_id in {item["memoryId"] for item in sensitive["items"]}


def test_ranking_uses_text_scope_type_confidence_date_and_stable_id(retrieval_env):
    memory, retrieval, conn, _ = retrieval_env
    global_record = approved(memory, "rankword", memory_type="routine", confidence="low")
    project_record = approved(memory, "rankword", memory_type="constraint", confidence="high", scope_type="project", scope_value="Alpha")
    agent_record = approved(memory, "rankword", memory_type="constraint", confidence="high", scope_type="agent", scope_value="local_planning_agent")
    result = retrieval.retrieve(request("rankword", project_name="Alpha", agent_id="local_planning_agent", max_items=10))
    ids = [item["memoryId"] for item in result["items"]]
    assert ids.index(agent_record["memoryId"]) < ids.index(project_record["memoryId"]) < ids.index(global_record["memoryId"])
    assert result["items"][0]["scopePriority"] == 3
    assert "exact agent scope" in result["items"][0]["matchReasons"]

    for memory_id in ids:
        conn.execute("update memories set updated_at = '2026-01-01T00:00:00+00:00' where memory_id = ?", (memory_id,))
    conn.commit()
    stable_first = retrieval.retrieve(request("rankword", max_items=10))["items"]
    stable_second = retrieval.retrieve(request("rankword", max_items=10))["items"]
    assert [item["memoryId"] for item in stable_first] == [item["memoryId"] for item in stable_second]


@pytest.mark.parametrize("query", ["NEAR(content)", "content:planning OR *", "planning') ; drop table memories; --"])
def test_fts_control_and_injection_text_is_tokenized_safely(retrieval_env, query):
    memory, retrieval, conn, _ = retrieval_env
    approved(memory, "Planning content remains intact.")
    retrieval.retrieve(request(query))
    assert conn.execute("select count(*) from memories").fetchone()[0] == 1


@pytest.mark.parametrize(
    ("query", "message"),
    [
        ("!!!", "word or number"),
        ("x" * 65, "term exceeds 64"),
        (" ".join(f"term{i}" for i in range(25)), "exceeds 24"),
        ("x " * 501, "exceeds 1000"),
    ],
)
def test_query_validation_limits(retrieval_env, query, message):
    _, retrieval, _, _ = retrieval_env
    with pytest.raises(MemoryValidationError, match=message):
        retrieval.retrieve(request(query))


def test_maximum_results_match_reasons_and_modes_are_consistent(retrieval_env):
    memory, retrieval, conn, _ = retrieval_env
    for index in range(4):
        approved(memory, f"Concise result {index}.", memory_type="preference")
    fts_result = retrieval.retrieve(request("concise", max_items=2))
    fallback_result = MemoryRetrievalService(conn, fts5_available=False).retrieve(request("concise", max_items=2))
    assert fts_result["selectedCount"] == fallback_result["selectedCount"] == 2
    assert set(fts_result) == set(fallback_result)
    assert all(item["matchReasons"] for item in fts_result["items"])


def test_successful_retrieval_audits_redacted_metadata_and_events(retrieval_env):
    memory, retrieval, conn, logger = retrieval_env
    secret_query = "private-query-marker"
    content = "private-query-marker content must not enter retrieval audit metadata"
    record = approved(memory, content)
    result = retrieval.retrieve(request(secret_query, agent_id="local_planning_agent"))
    retrieval_id = result["retrievalId"]
    row = conn.execute("select * from memory_retrievals where retrieval_id = ?", (retrieval_id,)).fetchone()
    item = conn.execute("select * from memory_retrieval_items where retrieval_id = ?", (retrieval_id,)).fetchone()
    assert row is not None and item is not None
    assert secret_query not in json.dumps(row)
    assert content not in json.dumps(row) + json.dumps(item)
    memory_event = conn.execute("select metadata from memory_events where memory_id = ? and event_type = 'memory.retrieved'", (record["memoryId"],)).fetchone()[0]
    bus_event = conn.execute("select payload from events where event_type = 'memory.retrieved'").fetchone()[0]
    assert secret_query not in memory_event + bus_event
    assert content not in memory_event + bus_event
    assert retrieval_id in memory_event and retrieval_id in bus_event
    log_text = "\n".join(path.read_text(encoding="utf-8") for path in logger.root.glob("*.jsonl"))
    assert secret_query not in log_text and content not in log_text


def test_private_session_suppresses_query_audit_and_events(retrieval_env):
    memory, retrieval, conn, _ = retrieval_env
    approved(memory, "Private planning memory.")
    before = {
        "retrievals": conn.execute("select count(*) from memory_retrievals").fetchone()[0],
        "items": conn.execute("select count(*) from memory_retrieval_items").fetchone()[0],
        "events": conn.execute("select count(*) from events where event_type = 'memory.retrieved'").fetchone()[0],
        "memory_events": conn.execute("select count(*) from memory_events where event_type = 'memory.retrieved'").fetchone()[0],
    }
    result = retrieval.retrieve(request("private planning", private_session=True))
    assert result["blocked"] is True and result["blockReason"] == "private_session"
    assert result["candidateCount"] == result["selectedCount"] == 0
    assert result["items"] == [] and result["retrievalId"] is None
    after = {
        "retrievals": conn.execute("select count(*) from memory_retrievals").fetchone()[0],
        "items": conn.execute("select count(*) from memory_retrieval_items").fetchone()[0],
        "events": conn.execute("select count(*) from events where event_type = 'memory.retrieved'").fetchone()[0],
        "memory_events": conn.execute("select count(*) from memory_events where event_type = 'memory.retrieved'").fetchone()[0],
    }
    assert after == before


def test_deleted_memory_leaves_only_redacted_retrieval_history(retrieval_env):
    memory, retrieval, _, _ = retrieval_env
    record = approved(memory, "Historical deletion marker.")
    result = retrieval.retrieve(request("historical deletion"))
    memory.delete(record["memoryId"])
    detail = retrieval.get_retrieval(result["retrievalId"])
    assert detail["items"][0]["memoryId"] == record["memoryId"]
    assert "content" not in detail["items"][0]
    assert "query" not in detail
