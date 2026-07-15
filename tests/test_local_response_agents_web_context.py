import inspect

import jarvis_core.app as app_module


LOCAL_RESPONSE_AGENT_INPUTS = [
    "LocalResearchBriefInput",
    "FileDataSummaryInput",
    "LocalPlanningInput",
    "LocalDraftingInput",
    "LocalReviewInput",
    "LocalDecisionInput",
    "LocalTroubleshootingInput",
    "LocalSummarizationInput",
    "LocalExtractionInput",
    "LocalClassificationInput",
    "LocalTransformationInput",
    "LocalBusinessInput",
    "LocalHealthFitnessInput",
    "LocalFoodCookingGroceryInput",
    "LocalHomeRoomLivingSpaceInput",
    "LocalLegalImmigrationOfficialInput",
    "LocalEmergencyPreparednessInput",
    "LocalCultureTasteHighClassLifestyleInput",
    "LocalHobbiesAdventureInput",
    "LocalPersonalKnowledgeMemoryOrganizerInput",
    "LocalLifeDashboardCoordinatorInput",
    "LocalEverydayLifeInput",
    "LocalOnlinePresenceInput",
    "LocalSecuritySafetyInput",
    "LocalCreatorInput",
    "LocalSchoolRoboticsInput",
    "LocalCareerInput",
    "LocalFinanceBudgetInput",
    "LocalHousingMoveTravelInput",
    "LocalProjectsPortfolioInput",
    "LocalLearningStudyInput",
    "LocalSocialNetworkingInput",
    "LocalPersonalAdminInput",
    "LocalVehicleDevicesGearInput",
    "LocalLifeDirectionInput",
    "LocalRelationshipsInput",
    "LocalEmotionalReflectionInput",
]


LOCAL_RESPONSE_AGENT_HANDLERS = [
    "create_local_research_brief",
    "create_file_data_summary",
    "create_local_plan",
    "create_local_draft",
    "create_local_review",
    "create_local_decision",
    "create_local_troubleshooting_triage",
    "create_local_summarization",
    "create_local_extraction",
    "create_local_classification",
    "create_local_transformation",
    "create_local_business_brief",
    "create_local_health_fitness_plan",
    "create_local_food_cooking_grocery_plan",
    "create_local_home_room_living_space_plan",
    "create_local_legal_immigration_official_plan",
    "create_local_emergency_preparedness_plan",
    "create_local_culture_taste_high_class_lifestyle_plan",
    "create_local_hobbies_adventure_plan",
    "create_local_personal_knowledge_memory_organizer_plan",
    "create_local_life_dashboard_coordinator_plan",
    "create_local_everyday_life_plan",
    "create_local_online_presence_plan",
    "create_local_security_safety_review",
    "create_local_creator_plan",
    "create_local_school_robotics_plan",
    "create_local_career_plan",
    "create_local_finance_budget_plan",
    "create_local_housing_move_travel_plan",
    "create_local_projects_portfolio_plan",
    "create_local_learning_study_plan",
    "create_local_social_networking_plan",
    "create_local_personal_admin_plan",
    "create_local_vehicle_devices_gear_plan",
    "create_local_life_direction_plan",
    "create_local_relationships_plan",
    "create_local_emotional_reflection_plan",
]


def test_all_37_local_response_agent_inputs_accept_optional_web_context():
    assert len(LOCAL_RESPONSE_AGENT_INPUTS) == 37

    for class_name in LOCAL_RESPONSE_AGENT_INPUTS:
        input_model = getattr(app_module, class_name)

        assert "web_context" in input_model.model_fields
        field = input_model.model_fields["web_context"]
        assert field.default_factory is not None
        assert "prior_agent_context" in input_model.model_fields
        assert input_model.model_fields["prior_agent_context"].default is None


def test_web_context_source_schema_is_strict_and_bounded():
    source = app_module.WebContextSourceInput(
        source_id="S1",
        citation_label="[S1]",
        source_url="https://example.com/public-source",
        final_url="https://example.com/public-source",
        title="Example",
        domain="example.com",
        excerpt="Reviewed excerpt",
        content_type="text/plain",
        fetched=True,
        fetched_at="2026-06-29T12:00:00+00:00",
        recency_note="[S1] fetched_at timestamp was supplied; source freshness still requires manual review.",
        quality_warnings=["[S1] Excerpt is partial."],
        limitations=["Manual review only."],
    )

    assert source.source_id == "S1"
    assert source.citation_label == "[S1]"
    assert source.source_url == "https://example.com/public-source"
    assert source.domain == "example.com"
    assert source.source_type == "public_web_excerpt"


def test_all_37_local_response_agent_handlers_add_source_context_response_fields():
    assert len(LOCAL_RESPONSE_AGENT_HANDLERS) == 37
    assert len(app_module.LOCAL_RESPONSE_AGENT_SOURCE_CONTEXT) == 37

    for handler_name in LOCAL_RESPONSE_AGENT_HANDLERS:
        source = inspect.getsource(getattr(app_module, handler_name))

        assert "_local_response_with_web_context(" in source


def test_shared_response_wrapper_adds_evidence_and_citation_fields():
    payload = app_module.LocalPlanningInput(
        goal="Plan a local review",
        web_context=[
            app_module.WebContextSourceInput(
                source_url="https://example.com/source",
                title="Reviewed Source",
                excerpt="Reviewed source excerpt.",
            )
        ],
        prior_agent_context=app_module.PriorAgentContextInput(
            previous_agent_id="local_research_agent",
            previous_agent_name="Local Research Agent",
            previous_output_type="brief",
            previous_summary="Reviewer notes were summarized manually.",
            previous_key_points=["Keep the workflow local."],
            previous_next_actions="Review the next selected agent.",
            previous_limitations=["No automatic handoff."],
        ),
    )

    response = app_module._local_response_with_web_context({"title": "Local response"}, payload)

    assert response["source_evidence"][0]["source_id"] == "S1"
    assert response["citation_labels"] == ["[S1]"]
    assert response["source_quality_warnings"]
    assert response["source_recency_notes"]
    assert response["sources_used"][0]["citation_label"] == "[S1]"
    assert response["source_use_summary"]
    assert response["source_supported_points"]
    assert response["source_cautions"]
    assert response["source_followup_checks"]
    assert response["source_informed_assumptions"]
    assert "not proof" in response["citation_usage_note"]
    assert "not certified" in " ".join(response["web_context_limitations"]) or "not certification" in " ".join(response["web_context_limitations"])
    assert response["prior_context_used"] is True
    assert "Manual prior context" in response["prior_context_summary"]
    assert response["prior_context"]["previous_agent_id"] == "local_research_agent"
    assert response["prior_context"]["previous_next_actions"] == ["Review the next selected agent."]
    assert "Jarvis did not load previous runs automatically." in response["prior_context_limitations"]
    assert "No previous agent was automatically invoked." in response["prior_context_limitations"]
    assert "Prior context is not persisted by this response." in response["prior_context_limitations"]


def test_prior_agent_context_empty_response_fields_are_safe():
    payload = app_module.LocalPlanningInput(goal="Plan a local review")

    response = app_module._local_response_with_web_context({"title": "Local response"}, payload)

    assert response["prior_context_used"] is False
    assert "No manual prior agent context was provided." == response["prior_context_summary"]
    assert "no previous agent result was loaded or inferred" in response["prior_context_limitations"][0]
