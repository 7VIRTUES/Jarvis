import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_relationships_agent import LocalRelationshipsAgentService, LocalRelationshipsRequest


def test_local_relationships_endpoint_returns_structured_plan():
    payload = app_module.LocalRelationshipsInput(
        profileName="Local Relationship Profile",
        relationshipGoal="Prepare a respectful check-in conversation with a family member about improving communication.",
        relationshipType="Family",
        peopleContext="The user wants to talk with a family member after several tense conversations.",
        situationNotes="Lower tension, ask for clearer expectations, and avoid blame.",
        communicationGoals=["Open calmly", "Ask what would help", "Agree on one next step"],
        concerns=["Conversation may become defensive", "Avoid sounding accusatory"],
        boundaries=["Pause if voices rise", "No name-calling"],
        desiredTone="Warm, direct, and low-pressure",
        constraints=["Manual planning only"],
        desiredOutputType="relationship_brief",
    )

    result = app_module.create_local_relationships_plan(payload)

    assert result["agentId"] == "local_relationships_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_relationship_planning"
    assert result["profileName"] == "Local Relationship Profile"
    assert result["relationshipGoal"] == "Prepare a respectful check-in conversation with a family member about improving communication."
    assert result["desiredOutputType"] == "relationship_brief"
    assert result["relationshipFocus"]
    assert result["situationSummary"]
    assert result["communicationPlan"]
    assert result["conversationScripts"]
    assert result["boundaryPlan"]
    assert result["conflictPrep"]
    assert result["apologyDrafts"]
    assert result["checkInPlan"]
    assert result["giftOccasionPlan"]
    assert result["relationshipMaintenance"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided relationship goal" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("relationship_brief", "relationship_brief"),
        ("conversation_plan", "conversation_plan"),
        ("boundary_plan", "boundary_plan"),
        ("conflict_prep", "conflict_prep"),
        ("apology_draft", "apology_draft"),
        ("check_in_plan", "check_in_plan"),
        ("gift_occasion_plan", "gift_occasion_plan"),
        ("relationship_maintenance", "relationship_maintenance"),
        (" CHECK_IN_PLAN ", "check_in_plan"),
    ],
)
def test_local_relationships_supported_output_types_normalize(requested, expected):
    service = LocalRelationshipsAgentService()

    result = service.create_plan(
        LocalRelationshipsRequest(
            relationship_goal="Prepare a respectful family conversation.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_relationships_unsupported_output_type_falls_back_safely():
    service = LocalRelationshipsAgentService()

    result = service.create_plan(
        LocalRelationshipsRequest(
            relationship_goal="Prepare a conversation plan.",
            desired_output_type="send_schedule_post_track_and_guarantee",
        )
    )

    assert result["desiredOutputType"] == "relationship_brief"
    assert result["safety"]["messageAccess"] is False
    assert result["safety"]["publicPosting"] is False
    assert result["safety"]["profileScraping"] is False
    assert result["safety"]["relationshipOutcomeGuarantee"] is False


def test_local_relationships_thin_input_reports_warnings_and_questions():
    service = LocalRelationshipsAgentService()

    result = service.create_plan(LocalRelationshipsRequest(relationship_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_relationships_output_includes_communication_scripts_boundaries_conflict_apology_checkin_gift_and_maintenance_sections():
    service = LocalRelationshipsAgentService()

    result = service.create_plan(
        LocalRelationshipsRequest(
            relationship_goal="Plan a careful apology and check-in.",
            relationship_type="Friend",
            people_context="A friend felt overlooked.",
            situation_notes="The user wants to repair tension.",
            communication_goals=["Apologize clearly", "Invite their perspective"],
            concerns=["Avoid defensiveness"],
            boundaries=["Do not push for an immediate answer"],
            desired_tone="Sincere",
            constraints=["Manual plan only"],
            desired_output_type="apology_draft",
        )
    )

    assert result["communicationPlan"]
    assert result["conversationScripts"]
    assert result["boundaryPlan"]
    assert result["conflictPrep"]
    assert result["apologyDrafts"]
    assert result["checkInPlan"]
    assert result["giftOccasionPlan"]
    assert result["relationshipMaintenance"]


def test_local_relationships_output_does_not_claim_contact_message_platform_persistence_therapy_validation_or_outcomes():
    service = LocalRelationshipsAgentService()

    result = service.create_plan(
        LocalRelationshipsRequest(
            relationship_goal="Access contacts, send DMs, schedule a meeting, post publicly, scrape profiles, track someone, diagnose the relationship, and guarantee resolution.",
            desired_output_type="conflict_prep",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "contacts accessed",
        "message sent",
        "dm sent",
        "calendar event created",
        "posted publicly",
        "profile scraped",
        "location accessed",
        "person tracked",
        "record persisted",
        "therapy provided",
        "diagnosis complete",
        "treatment created",
        "relationship outcome guaranteed",
        "conflict resolved",
        "legally validated",
        "safety validated",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no contacts" in output_text
    assert "no therapy" in output_text
    assert "relationship outcome certainty" in output_text


def test_local_relationships_unsafe_inputs_are_redirected_without_manipulation_coercion_harassment_stalking_doxxing_or_impersonation_help():
    service = LocalRelationshipsAgentService()

    result = service.create_plan(
        LocalRelationshipsRequest(
            relationship_goal="Manipulate someone, coerce them, deceive them, harass them, stalk them, dox them, impersonate a friend, and pressure them.",
            desired_output_type="conversation_plan",
        )
    )
    output_text = str(result).lower()

    assert any("redirect" in item.lower() or "respectful" in item.lower() for item in result["relationshipFocus"])
    assert "not supported" in output_text
    assert result["safety"]["manipulationGuidance"] is False
    assert result["safety"]["coercionGuidance"] is False
    assert result["safety"]["harassmentGuidance"] is False
    assert result["safety"]["stalkingGuidance"] is False
    assert result["safety"]["doxxingGuidance"] is False
    assert result["safety"]["impersonationGuidance"] is False


def test_local_relationships_high_stakes_inputs_include_human_professional_or_emergency_help_limitations():
    service = LocalRelationshipsAgentService()

    result = service.create_plan(
        LocalRelationshipsRequest(
            relationship_goal="Handle abuse, violence, stalking, coercive control, self-harm, severe mental health distress, legal danger, and immediate safety.",
            desired_output_type="relationship_brief",
        )
    )

    assert any("emergency help" in warning for warning in result["warnings"])
    assert any("emergency support" in limitation for limitation in result["limitations"])
    assert any("emergency help" in action for action in result["nextActions"])


def test_local_relationships_safety_flags_disable_connectors_accounts_contacts_messages_platforms_persistence_mutation_and_certification():
    service = LocalRelationshipsAgentService()

    result = service.create_plan(LocalRelationshipsRequest(relationship_goal="Prepare a family check-in."))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["connectors"] is False
    assert safety["oauth"] is False
    assert safety["OAuth"] is False
    assert safety["accountAccess"] is False
    assert safety["webBrowsing"] is False
    assert safety["paidApis"] is False
    assert safety["contactAccess"] is False
    assert safety["messageAccess"] is False
    assert safety["emailSending"] is False
    assert safety["calendarAccess"] is False
    assert safety["socialPlatformAccess"] is False
    assert safety["publicPosting"] is False
    assert safety["messaging"] is False
    assert safety["profileScraping"] is False
    assert safety["locationAccess"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["manipulationGuidance"] is False
    assert safety["coercionGuidance"] is False
    assert safety["harassmentGuidance"] is False
    assert safety["stalkingGuidance"] is False
    assert safety["doxxingGuidance"] is False
    assert safety["impersonationGuidance"] is False
    assert safety["therapyClaims"] is False
    assert safety["diagnosis"] is False
    assert safety["treatmentPlan"] is False
    assert safety["relationshipOutcomeGuarantee"] is False
    assert safety["legalValidation"] is False
    assert safety["safetyValidation"] is False
    assert safety["certificationClaims"] is False


def test_local_relationships_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_relationships_agent").local_relationships_agent).lower()
    forbidden = [
        "requests",
        "httpx",
        "urllib.request",
        "socket",
        "subprocess",
        "open(",
        "read_text",
        "read_bytes",
        "write_text",
        ".write(",
        "sqlite",
        "taskqueue",
        "gmail.",
        "google_calendar",
        "smtp.",
        "imap.",
        "openai",
        "anthropic",
        "gemini",
    ]

    assert all(token not in source for token in forbidden)


def test_local_relationships_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalRelationshipsInput.model_validate(
            {
                "relationshipGoal": "Prepare a conversation.",
                "contactPassword": "not allowed",
            }
        )


def test_local_relationships_requires_relationship_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalRelationshipsInput.model_validate({"profileName": "Missing goal"})


def test_local_relationships_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/relationships/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
