import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_response_agents_catalog import (
    local_response_agent_categories,
    local_response_agent_manual_workflow_preview,
    local_response_agent_metadata,
    local_response_agent_request_template,
    local_response_agent_route_preview,
    local_response_agents_discovery_catalog,
)
from jarvis_core.local_response_agent_metadata import LOCAL_RESPONSE_AGENT_COUNT


DISCOVERY_ROUTES = [
    ("GET", "/agents/local-response-agents/catalog"),
    ("GET", "/agents/local-response-agents/categories"),
    ("GET", "/agents/local-response-agents/{agent_id}"),
    ("GET", "/agents/local-response-agents/{agent_id}/request-template"),
    ("POST", "/agents/local-response-agents/route-preview"),
    ("POST", "/agents/local-response-agents/manual-workflow-preview"),
]


def test_discovery_catalog_exposes_37_local_response_agents_without_connectors():
    catalog = local_response_agents_discovery_catalog()

    assert catalog["agent_count"] == catalog["agentCount"] == LOCAL_RESPONSE_AGENT_COUNT == 37
    assert catalog["expected_agent_count"] == catalog["expectedAgentCount"] == 37
    assert catalog["local_only"] is True
    assert catalog["manual_input_only"] is True
    assert catalog["response_only"] is True
    assert catalog["non_persistent"] is True
    assert catalog["connector_behavior"] is False
    assert catalog["web_research_available"] is True
    assert catalog["webResearchAvailable"] is True
    assert catalog["web_research_mode"] == "read_only_public_url_context"
    assert catalog["webResearchMode"] == "read_only_public_url_context"
    assert catalog["web_research_requires_user_enabled"] is True
    assert catalog["webResearchRequiresUserEnabled"] is True
    assert catalog["web_research_is_optional"] is True
    assert catalog["webResearchIsOptional"] is True
    assert catalog["web_context_supported"] is True
    assert catalog["webContextSupported"] is True
    assert catalog["web_context_is_optional"] is True
    assert catalog["webContextIsOptional"] is True
    assert catalog["web_context_is_non_persistent"] is True
    assert catalog["webContextIsNonPersistent"] is True
    assert catalog["web_research_requires_manual_fetch"] is True
    assert catalog["webResearchRequiresManualFetch"] is True
    assert catalog["agents_do_not_auto_browse"] is True
    assert catalog["agentsDoNotAutoBrowse"] is True
    assert catalog["source_evidence_supported"] is True
    assert catalog["sourceEvidenceSupported"] is True
    assert catalog["citation_labels_supported"] is True
    assert catalog["citationLabelsSupported"] is True
    assert catalog["source_recency_flags_supported"] is True
    assert catalog["sourceRecencyFlagsSupported"] is True
    assert catalog["source_aware_response_supported"] is True
    assert catalog["sourceAwareResponseSupported"] is True
    assert catalog["consistency"]["valid"] is True
    assert len(catalog["agents"]) == 37

    agent_ids = {agent["agent_id"] for agent in catalog["agents"]}
    endpoints = {agent["endpoint"] for agent in catalog["agents"]}
    assert len(agent_ids) == len(endpoints) == 37

    for agent in catalog["agents"]:
        assert agent["agent_id"] == agent["agentId"]
        assert agent["name"]
        assert agent["display_name"] == agent["displayName"]
        assert agent["status"] == "implemented_local_only"
        assert agent["mode"]
        assert agent["docs_link"] == agent["docsLink"]
        assert agent["docsLink"].startswith("/docs/")
        assert agent["response_mode"] == agent["responseMode"]
        assert agent["boundary_flags"] == agent["boundaryFlags"]
        assert agent["output_types"] == agent["outputTypes"]
        assert agent["use_when"] == agent["useWhen"]
        assert agent["safety_notes"] == agent["safetyNotes"]
        assert agent["safetyNotes"]
        assert agent["has_connector"] is False
        assert agent["hasConnector"] is False
        assert agent["is_local_only"] is True
        assert agent["isLocalOnly"] is True
        assert agent["is_manual_input_only"] is True
        assert agent["isManualInputOnly"] is True
        assert agent["is_response_only"] is True
        assert agent["isResponseOnly"] is True
        assert agent["is_non_persistent"] is True
        assert agent["isNonPersistent"] is True
        assert agent["web_research_available"] is True
        assert agent["webResearchAvailable"] is True
        assert agent["web_research_mode"] == "read_only_public_url_context"
        assert agent["webResearchMode"] == "read_only_public_url_context"
        assert agent["web_research_requires_user_enabled"] is True
        assert agent["webResearchRequiresUserEnabled"] is True
        assert agent["web_research_is_optional"] is True
        assert agent["webResearchIsOptional"] is True
        assert "No logins" in " ".join(agent["web_research_limitations"])
        assert agent["web_context_supported"] is True
        assert agent["webContextSupported"] is True
        assert agent["web_context_is_optional"] is True
        assert agent["webContextIsOptional"] is True
        assert agent["web_context_is_non_persistent"] is True
        assert agent["webContextIsNonPersistent"] is True
        assert agent["web_research_requires_manual_fetch"] is True
        assert agent["webResearchRequiresManualFetch"] is True
        assert agent["agents_do_not_auto_browse"] is True
        assert agent["agentsDoNotAutoBrowse"] is True
        assert agent["source_evidence_supported"] is True
        assert agent["sourceEvidenceSupported"] is True
        assert agent["citation_labels_supported"] is True
        assert agent["citationLabelsSupported"] is True
        assert agent["source_recency_flags_supported"] is True
        assert agent["sourceRecencyFlagsSupported"] is True
        assert agent["source_aware_response_supported"] is True
        assert agent["sourceAwareResponseSupported"] is True
        assert agent["examples"]
        assert agent["boundaryFlags"]["connectorBehavior"] is False
        assert agent["boundaryFlags"]["persistence"] is False
        assert agent["boundaryFlags"]["fileMutation"] is False


def test_discovery_categories_cover_all_37_agents_without_creating_agent_38():
    categories = local_response_agent_categories()

    assert categories["total_count"] == categories["totalCount"] == 37
    assert categories["expected_count"] == categories["expectedCount"] == 37
    assert sum(category["count"] for category in categories["categories"]) == 37
    assert {category["name"] for category in categories["categories"]} == {
        "Coding/Core",
        "Health/Food/Home",
        "Safety/Emergency",
        "Creativity/Hobbies",
        "Knowledge/Coordinator",
        "Life/Admin",
        "Social/Family",
        "School/Career",
        "Finance/Housing/Travel",
    }
    assert any(
        "local_life_dashboard_cross_agent_coordinator" in category["agent_ids"]
        for category in categories["categories"]
    )


def test_single_agent_metadata_and_template_have_safe_fallbacks():
    metadata = local_response_agent_metadata("local_food_cooking_grocery")

    assert metadata["found"] is True
    assert metadata["agent"]["agent_id"] == "local_food_cooking_grocery"
    assert metadata["agent"]["endpoint"] == "POST /agents/food-cooking-grocery/local-plan"

    template = local_response_agent_request_template("local_food_cooking_grocery")
    assert template["found"] is True
    assert template["agent_id"] == "local_food_cooking_grocery"
    assert template["endpoint"] == "/agents/food-cooking-grocery/local-plan"
    assert template["catalog_endpoint"] == "POST /agents/food-cooking-grocery/local-plan"
    assert template["method"] == "POST"
    assert template["recommended_request_fields"]
    assert template["default_output_type"] == "budget_grocery_plan"
    assert template["supported_output_types"] == ["budget_grocery_plan"]
    assert template["sample_payload"]
    assert template["sample_payload"]["web_context"] == []
    assert template["sample_payload"]["prior_agent_context"] is None
    assert "web_context" in template["recommended_request_fields"]
    assert "prior_agent_context" in template["recommended_request_fields"]
    assert "manual input only" in template["boundary_reminder"].lower()
    assert "no connectors" in template["boundary_reminder"].lower()
    assert "agents do not auto-browse" in template["boundary_reminder"].lower()
    assert template["web_research_available"] is True
    assert template["web_research_mode"] == "read_only_public_url_context"
    assert template["web_research_requires_user_enabled"] is True
    assert template["web_research_is_optional"] is True
    assert "No browser automation" in " ".join(template["web_research_limitations"])
    assert template["web_context_supported"] is True
    assert template["webContextSupported"] is True
    assert template["web_context_is_optional"] is True
    assert template["webContextIsOptional"] is True
    assert template["web_context_is_non_persistent"] is True
    assert template["webContextIsNonPersistent"] is True
    assert template["web_research_requires_manual_fetch"] is True
    assert template["webResearchRequiresManualFetch"] is True
    assert template["agents_do_not_auto_browse"] is True
    assert template["agentsDoNotAutoBrowse"] is True
    assert template["source_evidence_supported"] is True
    assert template["sourceEvidenceSupported"] is True
    assert template["citation_labels_supported"] is True
    assert template["citationLabelsSupported"] is True
    assert template["source_recency_flags_supported"] is True
    assert template["sourceRecencyFlagsSupported"] is True
    assert template["source_aware_response_supported"] is True
    assert template["sourceAwareResponseSupported"] is True
    assert template["web_context_template_sample"][0]["source_type"] == "public_web_excerpt"
    assert template["web_context_template_sample"][0]["user_notes"]
    assert template["prior_agent_context_supported"] is True
    assert template["priorAgentContextSupported"] is True
    assert template["prior_agent_context_is_optional"] is True
    assert template["priorAgentContextIsOptional"] is True
    assert template["prior_agent_context_is_non_persistent"] is True
    assert template["priorAgentContextIsNonPersistent"] is True
    assert template["prior_agent_context_template_sample"]["source_type"] == "manual_prior_agent_output"
    assert "previous_summary" in template["prior_agent_context_fields"]
    assert "Optional manual context from a prior local response-agent result." in template["prior_agent_context_guidance"]
    assert "Not loaded automatically." in template["prior_agent_context_guidance"]
    assert "Not persisted." in template["prior_agent_context_guidance"]
    assert "Use only after the user reviews and inserts it manually." in template["prior_agent_context_guidance"]
    assert "Does not trigger multi-agent execution." in template["prior_agent_context_guidance"]
    assert "prior_context_used" in template["prior_agent_context_response_fields"]
    assert "source_evidence" in template["web_context_response_fields"]
    assert "citation_labels" in template["web_context_response_fields"]
    assert "source_quality_warnings" in template["web_context_response_fields"]
    assert "source_recency_notes" in template["web_context_response_fields"]
    assert "source_context_summary" in template["web_context_response_fields"]
    assert "sources_used" in template["web_context_response_fields"]
    assert "web_context_limitations" in template["web_context_response_fields"]
    assert "source_use_summary" in template["web_context_response_fields"]
    assert "source_supported_points" in template["web_context_response_fields"]
    assert "source_cautions" in template["web_context_response_fields"]
    assert "source_followup_checks" in template["web_context_response_fields"]
    assert "source_informed_assumptions" in template["web_context_response_fields"]
    assert "citation_usage_note" in template["web_context_response_fields"]
    assert template["source_aware_response_fields"] == [
        "source_use_summary",
        "source_supported_points",
        "source_cautions",
        "source_followup_checks",
        "source_informed_assumptions",
        "citation_usage_note",
    ]
    assert "citation_label" in template["web_context_evidence_fields"]
    assert template["citation_reminder"] == "Sources are labeled for reference, not certified."
    assert "do not auto-browse" in " ".join(template["web_context_supported_behavior"])
    assert "source-aware response sections" in " ".join(template["web_context_supported_behavior"])
    assert "Source freshness and authority" in " ".join(template["web_context_supported_behavior"])
    assert "not certified" in " ".join(template["web_context_supported_behavior"])
    assert "No login" in " ".join(template["web_context_not_supported"])
    assert "not persisted" in " ".join(template["web_context_limitations"])
    assert "No source context is submitted automatically." in template["web_research_context_fields"]
    assert "source-aware response sections" in " ".join(template["web_research_context_fields"])
    assert "food-safety certification" in " ".join(template["high_stakes_limitations"])

    unknown_metadata = local_response_agent_metadata("missing-agent")
    unknown_template = local_response_agent_request_template("missing-agent")
    assert unknown_metadata["found"] is False
    assert unknown_template["found"] is False
    assert "not_executed_notice" in unknown_metadata
    assert "not_executed_notice" in unknown_template


def test_route_preview_is_suggestions_only_and_does_not_invoke_or_persist():
    preview = local_response_agent_route_preview(
        text="Coordinate school, robotics, budget, workout, and relationship planning.",
        domains_to_consider=["school", "finance", "health"],
        preferred_output_type="priority map",
        urgency_level="normal",
        constraints_or_notes="Manual local response only.",
    )

    assert preview["title"] == "Local Response-Agent Route Preview"
    assert preview["suggested_agents"]
    assert "No agent was invoked" in preview["summary"]
    assert "suggestions only" in preview["not_executed_notice"]
    assert "external services" in preview["not_executed_notice"]
    assert preview["follow_up_questions"]
    for suggestion in preview["suggested_agents"]:
        assert suggestion["suggested_only"] is True
        assert suggestion["invoked"] is False
        assert suggestion["handoff_created"] is False
        assert suggestion["endpoint"].startswith("POST /agents/")


def test_route_preview_uses_coordinator_first_for_ambiguous_requests():
    preview = local_response_agent_route_preview(
        text="Help me think through a broad local request.",
        domains_to_consider=[],
        preferred_output_type="",
        urgency_level="",
        constraints_or_notes="",
    )

    assert preview["suggested_agents"][0]["agent_id"] == "local_life_dashboard_cross_agent_coordinator"
    assert preview["suggested_agents"][0]["invoked"] is False
    assert preview["suggested_agents"][0]["handoff_created"] is False


def test_manual_workflow_preview_is_catalog_only_and_manual():
    preview = local_response_agent_manual_workflow_preview(
        user_goal="Create a local review workflow for planning then drafting.",
        candidate_agent_ids=["local_planning_agent", "local_drafting_agent"],
        route_preview_suggestions=[],
        max_steps=4,
        include_web_context=True,
        constraints_or_notes="Manual only.",
    )

    assert preview["title"] == "Manual Multi-Agent Workflow Preview"
    assert preview["workflow_steps"]
    assert preview["workflow_steps"][0]["agent_id"] == "local_planning_agent"
    assert "No agent was invoked" in preview["summary"]
    assert "suggestions only" in preview["not_executed_notice"]
    assert "Manual workflow only." in preview["manual_only_boundaries"]
    assert "Steps are suggestions, not execution." in preview["manual_only_boundaries"]
    assert "Run one selected agent at a time." in preview["manual_only_boundaries"]
    assert "Prior context is inserted only after user review." in preview["manual_only_boundaries"]
    assert "No automatic handoff." in preview["manual_only_boundaries"]
    assert "No persistence." in preview["manual_only_boundaries"]
    assert "No connectors." in preview["manual_only_boundaries"]
    for step in preview["workflow_steps"]:
        assert step["suggested_only"] is True
        assert step["invoked"] is False
        assert step["handoff_created"] is False
        assert step["endpoint"].startswith("POST /agents/")
        assert "prior_agent_context" in " ".join(step["suggested_manual_payload_notes"])


def test_manual_workflow_preview_uses_coordinator_first_for_ambiguous_requests():
    preview = local_response_agent_manual_workflow_preview(
        user_goal="Help with a broad local request.",
        candidate_agent_ids=[],
        route_preview_suggestions=[],
        max_steps=4,
        include_web_context=False,
        constraints_or_notes="",
    )

    assert preview["workflow_steps"][0]["agent_id"] == "local_life_dashboard_cross_agent_coordinator"
    assert preview["workflow_steps"][0]["invoked"] is False
    assert preview["workflow_steps"][0]["handoff_created"] is False


def test_app_route_preview_payload_accepts_aliases_and_rejects_extra_fields():
    payload = app_module.LocalResponseAgentRoutePreviewInput(
        promptText="Plan a local weekly dashboard for school and workouts.",
        domainsToConsider=["school", "health"],
        preferredOutputType="summary",
        urgencyLevel="normal",
        constraintsOrNotes="No accounts or connectors.",
    )

    preview = app_module.preview_local_response_agent_route(payload)
    assert preview["suggested_agents"]

    with pytest.raises(ValidationError):
        app_module.LocalResponseAgentRoutePreviewInput.model_validate(
            {
                "request": "Preview a route.",
                "oauthToken": "not allowed",
            }
        )


def test_app_manual_workflow_preview_payload_accepts_aliases_and_rejects_extra_fields():
    payload = app_module.LocalResponseAgentManualWorkflowPreviewInput(
        userGoal="Manual local workflow",
        candidateAgentIds=["local_planning_agent"],
        routePreviewSuggestions=[{"agentId": "local_review_agent"}],
        maxSteps=3,
        includeWebContext=True,
        constraintsOrNotes="No handoff.",
    )

    preview = app_module.preview_local_response_agent_manual_workflow(payload)
    assert preview["workflow_steps"][0]["agent_id"] == "local_planning_agent"

    with pytest.raises(ValidationError):
        app_module.LocalResponseAgentManualWorkflowPreviewInput.model_validate(
            {
                "userGoal": "Preview a workflow.",
                "oauthToken": "not allowed",
            }
        )


def test_discovery_endpoints_are_guarded_by_dashboard_lan_guard():
    for method, path in DISCOVERY_ROUTES:
        route = next(
            route
            for route in app_module.app.routes
            if getattr(route, "path", None) == path and method in getattr(route, "methods", set())
        )
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

        assert require_dashboard_lan_access in dependency_calls
