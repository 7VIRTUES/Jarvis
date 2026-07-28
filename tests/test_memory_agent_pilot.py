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


PILOTS = [
    ("LocalPlanningInput", "create_local_plan", "local_planning_agent", {"goal": "Build pilot plan"}),
    ("LocalDraftingInput", "create_local_draft", "local_drafting_agent", {"purpose": "Pilot note", "notes": "Draft locally"}),
    ("LocalDecisionInput", "create_local_decision", "local_decision_agent", {"decision": "Pilot choice", "options": ["A", "B"]}),
    ("LocalCareerInput", "create_local_career_plan", "local_career_agent", {"careerGoal": "Pilot career goal"}),
    ("LocalPersonalKnowledgeMemoryOrganizerInput", "create_local_personal_knowledge_memory_organizer_plan", "local_personal_knowledge_memory_organizer", {"request": "Organize pilot notes"}),
    ("LocalLifeDashboardCoordinatorInput", "create_local_life_dashboard_coordinator_plan", "local_life_dashboard_cross_agent_coordinator", {"request": "Coordinate pilot dashboard"}),
]


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


def invoke(api_module, model_name, function_name, body):
    model = getattr(api_module, model_name)
    function = getattr(api_module, function_name)
    return function(model.model_validate(body))


@pytest.mark.parametrize("model_name,function_name,agent_id,base_body", PILOTS)
def test_each_pilot_is_explicit_server_scoped_and_private_safe(api_module, model_name, function_name, agent_id, base_body):
    own = approved(api_module, f"pilotmarker own memory for {agent_id}", scopeType="agent", scopeValue=agent_id)
    other_agent = "local_drafting_agent" if agent_id != "local_drafting_agent" else "local_planning_agent"
    other = approved(api_module, f"pilotmarker other memory for {other_agent}", scopeType="agent", scopeValue=other_agent)

    before = api_module.conn.execute("select count(*) from memory_retrievals").fetchone()[0]
    omitted = invoke(api_module, model_name, function_name, dict(base_body))
    disabled = invoke(api_module, model_name, function_name, {**base_body, "memory": {"enabled": False}})
    assert omitted["memoryContext"]["requested"] is False
    assert disabled["memoryContext"]["requested"] is False
    assert api_module.conn.execute("select count(*) from memory_retrievals").fetchone()[0] == before

    enabled = invoke(api_module, model_name, function_name, {
        **base_body,
        "memory": {"enabled": True, "query": "pilotmarker own memory", "maxItems": 10},
    })
    context = enabled["memoryContext"]
    ids = {item["memoryId"] for item in context["items"]}
    assert context["requested"] is True and context["blocked"] is False
    assert own["memoryId"] in ids and other["memoryId"] not in ids
    assert any("current request remains authoritative" in item for item in context["limitations"])
    audit = api_module.conn.execute(
        "select purpose, agent_id from memory_retrievals where retrieval_id = ?", (context["retrievalId"],)
    ).fetchone()
    assert audit == ("agent_response", agent_id)

    audit_before_private = api_module.conn.execute("select count(*) from memory_retrievals").fetchone()[0]
    private = invoke(api_module, model_name, function_name, {
        **base_body,
        "memory": {"enabled": True, "privateSession": True, "query": "pilotmarker"},
    })
    assert private["memoryContext"]["blocked"] is True
    assert private["memoryContext"]["blockReason"] == "private_session"
    assert api_module.conn.execute("select count(*) from memory_retrievals").fetchone()[0] == audit_before_private


@pytest.mark.parametrize("model_name,function_name,agent_id,base_body", PILOTS)
def test_each_pilot_rejects_blank_enabled_query(api_module, model_name, function_name, agent_id, base_body):
    with pytest.raises(HTTPException) as exc_info:
        invoke(api_module, model_name, function_name, {**base_body, "memory": {"enabled": True, "query": "  "}})
    assert exc_info.value.status_code == 422
    assert api_module.conn.execute("select count(*) from memory_retrievals").fetchone()[0] == 0


def test_sensitive_memory_requires_explicit_pilot_option(api_module):
    sensitive = approved(api_module, "sensitivepilot career preference", sensitivity="sensitive")
    default = invoke(api_module, "LocalPlanningInput", "create_local_plan", {
        "goal": "Review career", "memory": {"enabled": True, "query": "sensitivepilot career"}
    })
    explicit = invoke(api_module, "LocalPlanningInput", "create_local_plan", {
        "goal": "Review career", "memory": {"enabled": True, "query": "sensitivepilot career", "includeSensitive": True}
    })
    assert sensitive["memoryId"] not in {item["memoryId"] for item in default["memoryContext"]["items"]}
    assert sensitive["memoryId"] in {item["memoryId"] for item in explicit["memoryContext"]["items"]}


def test_web_prior_and_memory_context_coexist_without_memory_mutation(api_module):
    approved(api_module, "coexistmarker planning preference")
    stored_before = api_module.conn.execute("select count(*) from memories").fetchone()[0]
    response = invoke(api_module, "LocalPlanningInput", "create_local_plan", {
        "goal": "Keep current request authoritative",
        "web_context": [{
            "source_id": "manual-source", "citation_label": "[S1]", "source_url": "https://example.com",
            "title": "Reviewed source", "excerpt": "Reviewed local context", "fetched": True,
        }],
        "prior_agent_context": {"previous_agent_id": "local_drafting_agent", "previous_summary": "Manual prior summary"},
        "memory": {"enabled": True, "query": "coexistmarker planning"},
    })
    assert response["memoryContext"]["requested"] is True
    assert response["prior_context_used"] is True
    assert response["sources_used"]
    assert api_module.conn.execute("select count(*) from memories").fetchone()[0] == stored_before
    assert api_module.conn.execute("select count(*) from memory_events where event_type = 'memory.proposed'").fetchone()[0] == stored_before


@pytest.mark.parametrize(
    ("model_name", "normal_body"),
    [
        ("LocalReviewInput", {"subject": "Review", "content": "Normal request"}),
        ("LocalTroubleshootingInput", {"problem": "Normal request"}),
    ],
)
def test_unsupported_agents_reject_memory_field_and_normal_models_still_validate(api_module, model_name, normal_body):
    model = getattr(api_module, model_name)
    validated = model.model_validate(normal_body)
    assert validated is not None
    with pytest.raises(ValidationError):
        model.model_validate({**normal_body, "memory": {"enabled": True, "query": "not allowed"}})


def test_exactly_six_models_are_memory_aware_and_catalog_remains_37(api_module):
    memory_models = {
        name
        for name, value in vars(api_module).items()
        if isinstance(value, type) and name != "MemoryAwareResponseAgentInputBase" and hasattr(value, "model_fields") and "memory" in value.model_fields
    }
    assert memory_models == {row[0] for row in PILOTS}
    catalog = api_module.local_response_agents_discovery_catalog()
    assert catalog["agentCount"] == 37
