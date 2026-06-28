import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_culture_taste_high_class_lifestyle_agent import (
    LocalCultureTasteHighClassLifestyleAgentService,
    LocalCultureTasteHighClassLifestyleRequest,
)
from jarvis_core.local_hobbies_adventure_agent import LocalHobbiesAdventureAgentService, LocalHobbiesAdventureRequest
from jarvis_core.local_personal_knowledge_memory_organizer_agent import (
    LocalPersonalKnowledgeMemoryOrganizerAgentService,
    LocalPersonalKnowledgeMemoryOrganizerRequest,
)


def test_local_culture_taste_high_class_lifestyle_endpoint_returns_structured_plan():
    payload = app_module.LocalCultureTasteHighClassLifestyleInput(
        request="Prepare a respectful dinner-event polish plan.",
        outputType="event_prep_plan",
        situationOrEvent="Small professional dinner",
        cultureGoal="Feel prepared without pretending expertise.",
        currentStyleOrBaseline="Usually casual.",
        desiredImpression="Attentive and relaxed.",
        budgetLevel="low",
        wardrobeOrItemsAvailable=["Navy blazer", "Plain shirt"],
        diningOrEventContext="Dinner context supplied by user.",
        conversationContext="Guests may discuss books and food.",
        readingArtMusicFilmInterests=["Film history", "Jazz"],
        etiquetteFocus=["Introductions", "Dining pace"],
        timeline="One week",
    )

    result = app_module.create_local_culture_taste_high_class_lifestyle_plan(payload)

    assert result["agent_id"] == "local_culture_taste_high_class_lifestyle"
    assert result["agentId"] == "local_culture_taste_high_class_lifestyle"
    assert result["status"] == "local_only"
    assert result["output_type"] == "event_prep_plan"
    for field in ["title", "summary", "assumptions", "recommended_plan", "style_or_taste_guidance", "etiquette_notes", "conversation_notes", "learning_plan", "checklist", "budget_notes", "timeline", "limitations", "follow_up_questions"]:
        assert result[field]
    assert result["safety"]["localOnly"] is True
    assert result["safety"]["storeAccess"] is False
    assert result["safety"]["reservationAccess"] is False
    assert result["safety"]["socialAcceptanceGuarantee"] is False


def test_local_hobbies_adventure_endpoint_returns_structured_plan():
    payload = app_module.LocalHobbiesAdventureInput(
        request="Create a conservative beginner weekend plan for a day hike.",
        outputType="weekend_plan",
        hobbyOrActivity="Beginner day hiking",
        experienceLevel="Beginner",
        adventureGoal="Try an easy outdoor activity.",
        availableGear=["Comfortable shoes", "Small backpack"],
        budgetLevel="low",
        locationContextIfUserProvided="User has manually chosen a beginner trail.",
        timeAvailable="Saturday morning",
        groupSize="2 people",
        transportationContext="User arranges transport manually.",
        riskTolerance="Low",
        safetyOrAccessibilityNotes="Avoid steep or remote routes.",
    )

    result = app_module.create_local_hobbies_adventure_plan(payload)

    assert result["agent_id"] == "local_hobbies_adventure"
    assert result["agentId"] == "local_hobbies_adventure"
    assert result["status"] == "local_only"
    assert result["output_type"] == "weekend_plan"
    for field in ["title", "summary", "assumptions", "recommended_plan", "skill_steps", "gear_or_supply_checklist", "safety_notes", "budget_notes", "timeline", "risk_flags", "limitations", "follow_up_questions"]:
        assert result[field]
    assert result["safety"]["localOnly"] is True
    assert result["safety"]["mapAccess"] is False
    assert result["safety"]["weatherServiceAccess"] is False
    assert result["safety"]["booking"] is False


def test_local_personal_knowledge_memory_organizer_endpoint_returns_structured_plan():
    payload = app_module.LocalPersonalKnowledgeMemoryOrganizerInput(
        request="Organize these personal learning notes into a manual memory index.",
        outputType="memory_index",
        knowledgeArea="Home lab networking notes",
        sourceNotesOrSummary="Router reset steps worked after checking cable labels. VLAN notes still need review.",
        organizationGoal="Find useful context quickly before the next setup session.",
        categoriesOrTags=["networking", "troubleshooting"],
        projectsOrLifeAreas=["Home lab"],
        reviewFrequency="Weekly while active",
        priorityLevel="Medium",
        retentionGoal="Remember setup decisions and unresolved questions.",
        decisionOrMemoryContext="Start with cable labels and known-good reset steps.",
    )

    result = app_module.create_local_personal_knowledge_memory_organizer_plan(payload)

    assert result["agent_id"] == "local_personal_knowledge_memory_organizer"
    assert result["agentId"] == "local_personal_knowledge_memory_organizer"
    assert result["status"] == "local_only"
    assert result["output_type"] == "memory_index"
    for field in ["title", "summary", "assumptions", "recommended_structure", "categories", "tags", "key_points", "review_plan", "retrieval_prompts", "checklist", "limitations", "follow_up_questions"]:
        assert result[field]
    assert result["safety"]["localOnly"] is True
    assert result["safety"]["fileReads"] is False
    assert result["safety"]["memoryStoreAccess"] is False
    assert result["safety"]["recordCreation"] is False


@pytest.mark.parametrize(
    ("service", "request", "values"),
    [
        (
            LocalCultureTasteHighClassLifestyleAgentService(),
            LocalCultureTasteHighClassLifestyleRequest(request="Plan culture polish."),
            [
                "etiquette_plan",
                "wardrobe_plan",
                "event_prep_plan",
                "dining_prep",
                "conversation_prep",
                "cultural_literacy_plan",
                "taste_development_plan",
                "social_polish_checklist",
                "high_class_lifestyle_plan",
                "comparison",
                "checklist",
                "summary",
            ],
        ),
        (
            LocalHobbiesAdventureAgentService(),
            LocalHobbiesAdventureRequest(request="Plan an activity."),
            [
                "hobby_plan",
                "adventure_plan",
                "beginner_progression",
                "gear_checklist",
                "safety_checklist",
                "low_cost_activity_plan",
                "weekend_plan",
                "skill_practice_plan",
                "packing_list",
                "comparison",
                "checklist",
                "summary",
            ],
        ),
        (
            LocalPersonalKnowledgeMemoryOrganizerAgentService(),
            LocalPersonalKnowledgeMemoryOrganizerRequest(request="Organize notes."),
            [
                "knowledge_map",
                "note_structure",
                "memory_index",
                "tagging_plan",
                "review_plan",
                "decision_record",
                "project_context_summary",
                "personal_wiki_outline",
                "learning_log_structure",
                "retrieval_checklist",
                "comparison",
                "checklist",
                "summary",
            ],
        ),
    ],
)
def test_new_local_response_agents_supported_output_types_normalize(service, request, values):
    for value in values:
        result = service.create_plan(request.__class__(request="Manual local planning.", output_type=value.upper()))
        assert result["output_type"] == value


def test_new_local_response_agents_include_manual_local_limitations_and_no_prohibited_capabilities():
    culture = LocalCultureTasteHighClassLifestyleAgentService().create_plan(LocalCultureTasteHighClassLifestyleRequest(request="Plan dinner polish."))
    hobbies = LocalHobbiesAdventureAgentService().create_plan(LocalHobbiesAdventureRequest(request="Plan a drone practice outing."))
    knowledge = LocalPersonalKnowledgeMemoryOrganizerAgentService().create_plan(LocalPersonalKnowledgeMemoryOrganizerRequest(request="Organize notes with password text."))

    for result in [culture, hobbies, knowledge]:
        output_text = str(result).lower()
        assert result["safety"]["localOnly"] is True
        assert result["safety"]["responseOnly"] is True
        assert result["safety"]["manualInputOnly"] is True
        assert result["safety"]["externalServices"] is False
        assert result["safety"]["connectors"] is False
        assert result["safety"]["accountAccess"] is False
        assert result["safety"]["fileWrites"] is False
        assert result["safety"]["taskPersistence"] is False
        assert result["safety"]["mutation"] is False
        assert "based only on user-provided" in output_text

    assert culture["safety"]["purchases"] is False
    assert culture["safety"]["privateNetworkAccess"] is False
    assert "no store" in str(culture).lower()
    assert hobbies["safety"]["airspaceVerification"] is False
    assert hobbies["safety"]["liveSafetyVerification"] is False
    assert "faa" in str(hobbies).lower()
    assert knowledge["safety"]["fileReads"] is False
    assert knowledge["safety"]["sync"] is False
    assert "redact sensitive" in str(knowledge).lower()


def test_new_local_response_agent_requests_reject_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalCultureTasteHighClassLifestyleInput.model_validate({"request": "Plan event.", "storeAccount": "not allowed"})
    with pytest.raises(ValidationError):
        app_module.LocalHobbiesAdventureInput.model_validate({"request": "Plan hike.", "mapApiKey": "not allowed"})
    with pytest.raises(ValidationError):
        app_module.LocalPersonalKnowledgeMemoryOrganizerInput.model_validate({"request": "Organize notes.", "filePath": "not allowed"})


def test_new_local_response_agent_routes_are_lan_gated():
    route_paths = {
        "/agents/culture-taste-high-class-lifestyle/local-plan",
        "/agents/hobbies-adventure/local-plan",
        "/agents/personal-knowledge-memory-organizer/local-plan",
    }
    routes = [route for route in app_module.app.routes if getattr(route, "path", None) in route_paths]

    assert len(routes) == 3
    for route in routes:
        dependant_names = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependant_names
