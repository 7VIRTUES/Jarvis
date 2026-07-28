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
    monkeypatch.setattr(audit_module, "JsonlLogger", lambda _path: real_logger_class(tmp_path / "logs"))
    sys.modules.pop("jarvis_core.app", None)
    module = importlib.import_module("jarvis_core.app")
    yield module
    sys.modules.pop("jarvis_core.app", None)
    conn.close()


def approved(api_module, content, **overrides):
    values = {
        "memoryType": "preference", "content": content, "scopeType": "global",
        "scopeValue": None, "sourceType": "manual", "confidence": "high",
        "sensitivity": "standard",
    }
    values.update(overrides)
    pending = api_module.create_memory_proposal(api_module.MemoryProposalInput.model_validate(values))
    return api_module.approve_memory(pending["memoryId"], api_module.MemoryApprovalInput(resolution="approve"))


def preview(api_module, **overrides):
    values = {"query": "planning preference", "maxItems": 5}
    values.update(overrides)
    payload = api_module.MemoryRetrievalPreviewInput.model_validate(values)
    return api_module.preview_memory_retrieval(payload)


def test_ranked_preview_include_sensitive_and_private_blocking(api_module):
    standard = approved(api_module, "Planning preference standard.")
    sensitive = approved(api_module, "Planning preference sensitive.", sensitivity="sensitive")
    default = preview(api_module)
    assert standard["memoryId"] in {item["memoryId"] for item in default["items"]}
    assert sensitive["memoryId"] not in {item["memoryId"] for item in default["items"]}
    included = preview(api_module, includeSensitive=True)
    assert sensitive["memoryId"] in {item["memoryId"] for item in included["items"]}
    before = api_module.conn.execute("select count(*) from memory_retrievals").fetchone()[0]
    blocked = preview(api_module, privateSession=True)
    after = api_module.conn.execute("select count(*) from memory_retrievals").fetchone()[0]
    assert blocked["blocked"] is True and blocked["retrievalId"] is None
    assert after == before


def test_preview_validation_unknown_agent_limits_query_and_extra_fields(api_module):
    with pytest.raises(HTTPException) as unknown:
        preview(api_module, agentId="unknown_agent")
    assert unknown.value.status_code == 422
    with pytest.raises(ValidationError):
        api_module.MemoryRetrievalPreviewInput.model_validate({"query": "valid", "maxItems": 11})
    with pytest.raises(ValidationError):
        api_module.MemoryRetrievalPreviewInput.model_validate({"query": "valid", "unknown": True})
    with pytest.raises(HTTPException) as invalid_query:
        preview(api_module, query="!!!")
    assert invalid_query.value.status_code == 422


def test_retrieval_history_listing_detail_and_unknown(api_module):
    approved(api_module, "Planning preference for history.")
    result = preview(api_module, agentId="local_planning_agent", projectName="Alpha")
    listed = api_module.list_memory_retrievals(
        limit=25, offset=0, agentId="local_planning_agent", projectName="Alpha", purpose="manual_preview"
    )
    assert [row["retrievalId"] for row in listed] == [result["retrievalId"]]
    assert "query" not in listed[0] and "content" not in listed[0]
    detail = api_module.get_memory_retrieval(result["retrievalId"])
    assert detail["items"][0]["memoryId"] == result["items"][0]["memoryId"]
    assert "content" not in detail["items"][0]
    with pytest.raises(HTTPException) as missing:
        api_module.get_memory_retrieval("missing")
    assert missing.value.status_code == 404


def test_existing_unranked_context_preview_contract_is_preserved(api_module):
    approved(api_module, "Existing unranked preview memory.")
    result = api_module.preview_memory_context(api_module.MemoryContextPreviewInput(limit=50))
    assert set(result) == {"context", "policy", "count", "memories", "limitations"}
    assert "retrievalId" not in result
    assert any("No relevance ranking" in limitation for limitation in result["limitations"])


def test_retrieval_routes_keep_existing_lan_access_dependency(api_module):
    expected = {
        ("POST", "/api/memory/retrieval-preview"),
        ("GET", "/api/memory/retrievals"),
        ("GET", "/api/memory/retrievals/{retrieval_id}"),
    }
    found = set()
    for route in api_module.app.routes:
        for method, path in expected:
            if route.path == path and method in route.methods:
                found.add((method, path))
                calls = {dependency.call for dependency in route.dependant.dependencies}
                assert require_dashboard_lan_access in calls
    assert found == expected


def test_memory_summary_reports_truthful_capability_and_pilot_metadata(api_module):
    summary = api_module.memory_summary()
    assert isinstance(summary["fts5Available"], bool)
    assert summary["retrievalMode"] in {"fts5", "deterministic_fallback"}
    assert summary["memoryRetrievalStatus"] == "implemented_pilot"
    assert summary["memoryAgentRetrievalPilotCount"] == 6
