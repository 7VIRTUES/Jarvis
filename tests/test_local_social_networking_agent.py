import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_social_networking_agent import LocalSocialNetworkingAgentService, LocalSocialNetworkingRequest


def test_local_social_networking_endpoint_returns_structured_plan():
    payload = app_module.LocalSocialNetworkingInput(
        profileName="Local Social Profile",
        socialGoal="Prepare for a polished robotics networking reception with respectful conversation and follow-up options.",
        setting="University networking reception",
        peopleContext="Students, alumni, professors, and robotics industry guests may attend.",
        eventNotes="Short conversations, light refreshments, and informal introductions after a project showcase.",
        conversationTopics=["Robotics projects", "Career paths", "Research interests"],
        networkingGoals=["Practice concise introductions", "Ask thoughtful questions"],
        presentationNotes="Aim for calm, clear, and sincere rather than flashy.",
        constraints=["Manual planning only"],
        comfortLevel="Somewhat nervous but willing to practice.",
        desiredOutputType="social_brief",
    )

    result = app_module.create_local_social_networking_plan(payload)

    assert result["agentId"] == "local_social_networking_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_social_networking_planning"
    assert result["profileName"] == "Local Social Profile"
    assert result["socialGoal"] == "Prepare for a polished robotics networking reception with respectful conversation and follow-up options."
    assert result["desiredOutputType"] == "social_brief"
    assert result["socialFocus"]
    assert result["settingSummary"]
    assert result["conversationPlan"]
    assert result["networkingPlan"]
    assert result["eventPrep"]
    assert result["etiquetteChecklist"]
    assert result["presencePlan"]
    assert result["followUpDrafts"]
    assert result["socialReview"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided social goal" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("social_brief", "social_brief"),
        ("conversation_plan", "conversation_plan"),
        ("networking_plan", "networking_plan"),
        ("event_prep", "event_prep"),
        ("etiquette_checklist", "etiquette_checklist"),
        ("presence_plan", "presence_plan"),
        ("follow_up_draft", "follow_up_draft"),
        ("social_review", "social_review"),
        (" EVENT_PREP ", "event_prep"),
    ],
)
def test_local_social_networking_supported_output_types_normalize(requested, expected):
    service = LocalSocialNetworkingAgentService()

    result = service.create_plan(
        LocalSocialNetworkingRequest(
            social_goal="Prepare a respectful networking plan.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_social_networking_unsupported_output_type_falls_back_safely():
    service = LocalSocialNetworkingAgentService()

    result = service.create_plan(
        LocalSocialNetworkingRequest(
            social_goal="Prepare a conversation plan.",
            desired_output_type="send_post_scrape_and_track",
        )
    )

    assert result["desiredOutputType"] == "social_brief"
    assert result["safety"]["messaging"] is False
    assert result["safety"]["publicPosting"] is False
    assert result["safety"]["profileScraping"] is False


def test_local_social_networking_thin_input_reports_warnings_and_questions():
    service = LocalSocialNetworkingAgentService()

    result = service.create_plan(LocalSocialNetworkingRequest(social_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_social_networking_output_includes_conversation_networking_event_etiquette_presence_follow_up_and_review_sections():
    service = LocalSocialNetworkingAgentService()

    result = service.create_plan(
        LocalSocialNetworkingRequest(
            social_goal="Prepare for a networking reception.",
            setting="Reception",
            people_context="Students and alumni.",
            event_notes="Short conversations.",
            conversation_topics=["Robotics", "Projects"],
            networking_goals=["Practice intro"],
            presentation_notes="Calm and clear.",
            desired_output_type="networking_plan",
        )
    )

    assert result["conversationPlan"]
    assert result["networkingPlan"]
    assert result["eventPrep"]
    assert result["etiquetteChecklist"]
    assert result["presencePlan"]
    assert result["followUpDrafts"]
    assert result["socialReview"]


def test_local_social_networking_output_does_not_claim_platform_access_sending_tracking_persistence_or_outcomes():
    service = LocalSocialNetworkingAgentService()

    result = service.create_plan(
        LocalSocialNetworkingRequest(
            social_goal="Access contacts, send emails, schedule meetings, post publicly, scrape profiles, track people, and guarantee acceptance.",
            desired_output_type="social_review",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "contacts accessed",
        "email sent",
        "calendar event created",
        "message sent",
        "posted publicly",
        "profile scraped",
        "location accessed",
        "person tracked",
        "record persisted",
        "social success guaranteed",
        "elite acceptance guaranteed",
        "relationship guaranteed",
        "hiring guaranteed",
        "etiquette certified",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no contacts" in output_text
    assert "no social success" in output_text
    assert "no manipulation" in output_text


def test_local_social_networking_unsafe_inputs_are_redirected_without_manipulation_harassment_stalking_or_impersonation_help():
    service = LocalSocialNetworkingAgentService()

    result = service.create_plan(
        LocalSocialNetworkingRequest(
            social_goal="Manipulate someone, track them, find private information, impersonate a friend, and pressure them.",
            desired_output_type="conversation_plan",
        )
    )
    output_text = str(result).lower()

    assert any("redirected" in item.lower() or "respectful" in item.lower() for item in result["socialFocus"])
    assert "not supported" in output_text
    assert result["safety"]["manipulationGuidance"] is False
    assert result["safety"]["harassmentGuidance"] is False
    assert result["safety"]["stalkingGuidance"] is False
    assert result["safety"]["impersonationGuidance"] is False


def test_local_social_networking_high_stakes_inputs_include_human_or_professional_help_limitations():
    service = LocalSocialNetworkingAgentService()

    result = service.create_plan(
        LocalSocialNetworkingRequest(
            social_goal="Handle a workplace harassment, consent, legal, safety, and mental health concern.",
            desired_output_type="social_brief",
        )
    )

    assert any("professional help" in warning for warning in result["warnings"])
    assert any("professional support" in limitation for limitation in result["limitations"])
    assert any("legal" in action and "support" in action for action in result["nextActions"])


def test_local_social_networking_safety_flags_disable_connectors_accounts_messaging_posting_scraping_location_persistence_mutation_and_certification():
    service = LocalSocialNetworkingAgentService()

    result = service.create_plan(LocalSocialNetworkingRequest(social_goal="Prepare a networking plan."))
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
    assert safety["emailSending"] is False
    assert safety["calendarAccess"] is False
    assert safety["socialPlatformAccess"] is False
    assert safety["messaging"] is False
    assert safety["publicPosting"] is False
    assert safety["profileScraping"] is False
    assert safety["locationAccess"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["manipulationGuidance"] is False
    assert safety["harassmentGuidance"] is False
    assert safety["stalkingGuidance"] is False
    assert safety["impersonationGuidance"] is False
    assert safety["outcomeGuarantee"] is False
    assert safety["certificationClaims"] is False


def test_local_social_networking_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_social_networking_agent").local_social_networking_agent).lower()
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


def test_local_social_networking_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalSocialNetworkingInput.model_validate(
            {
                "socialGoal": "Prepare a networking plan.",
                "contactPassword": "not allowed",
            }
        )


def test_local_social_networking_requires_social_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalSocialNetworkingInput.model_validate({"profileName": "Missing goal"})


def test_local_social_networking_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/social-networking/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
