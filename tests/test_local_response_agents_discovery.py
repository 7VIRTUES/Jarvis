import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_response_agents_catalog import (
    local_response_agent_categories,
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
    assert "manual input only" in template["boundary_reminder"].lower()
    assert "no connectors" in template["boundary_reminder"].lower()
    assert template["web_research_available"] is True
    assert template["web_research_mode"] == "read_only_public_url_context"
    assert template["web_research_requires_user_enabled"] is True
    assert template["web_research_is_optional"] is True
    assert "No browser automation" in " ".join(template["web_research_limitations"])
    assert "No source context is submitted automatically." in template["web_research_context_fields"]
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


def test_discovery_endpoints_are_guarded_by_dashboard_lan_guard():
    for method, path in DISCOVERY_ROUTES:
        route = next(
            route
            for route in app_module.app.routes
            if getattr(route, "path", None) == path and method in getattr(route, "methods", set())
        )
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

        assert require_dashboard_lan_access in dependency_calls
