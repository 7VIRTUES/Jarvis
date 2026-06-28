import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_online_presence_agent import (
    LocalOnlinePresenceAgentService,
    LocalOnlinePresenceRequest,
)


def test_local_online_presence_endpoint_returns_structured_plan():
    payload = app_module.LocalOnlinePresenceInput(
        profileName="Local Portfolio Profile",
        platforms=["Portfolio site", "Professional profile"],
        currentBio="Builder of practical local-first tools and documentation.",
        goals=["Clarify positioning", "Draft profile copy"],
        targetAudience="Collaborators and reviewers interested in local-first software",
        tone="Clear and grounded",
        strengths=["Local-first product thinking", "Careful documentation"],
        projects=["Local assistant dashboard", "Manual evidence runbooks"],
        contentIdeas=["Explain a local-only design choice"],
        constraints=["No hype"],
        reputationConcerns=["Avoid unsupported claims"],
        desiredOutputType="presence_brief",
    )

    result = app_module.create_local_online_presence_plan(payload)

    assert result["agentId"] == "local_online_presence_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_online_presence_planning"
    assert result["profileName"] == "Local Portfolio Profile"
    assert result["platforms"] == ["Portfolio site", "Professional profile"]
    assert result["desiredOutputType"] == "presence_brief"
    assert result["presenceFocus"]
    assert result["audienceSummary"]
    assert result["positioningSummary"]
    assert result["bioDrafts"]
    assert result["profileRecommendations"]
    assert result["contentPlan"]
    assert result["portfolioPositioning"]
    assert result["personalBrandPlan"]
    assert result["reputationReview"]
    assert result["postingDrafts"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided online presence planning and drafting inputs." in result["limitations"]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("presence_brief", "presence_brief"),
        ("bio_draft", "bio_draft"),
        ("profile_review", "profile_review"),
        ("content_plan", "content_plan"),
        ("portfolio_positioning", "portfolio_positioning"),
        ("personal_brand_plan", "personal_brand_plan"),
        ("reputation_review", "reputation_review"),
        ("posting_drafts", "posting_drafts"),
        (" BIO_DRAFT ", "bio_draft"),
    ],
)
def test_local_online_presence_supported_output_types_normalize(requested, expected):
    service = LocalOnlinePresenceAgentService()

    result = service.create_plan(
        LocalOnlinePresenceRequest(
            profile_name="Local profile",
            goals=["Clarify copy"],
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_online_presence_unsupported_output_type_falls_back_safely():
    service = LocalOnlinePresenceAgentService()

    result = service.create_plan(
        LocalOnlinePresenceRequest(
            profile_name="Local profile",
            desired_output_type="auto_post_scheduler",
        )
    )

    assert result["desiredOutputType"] == "presence_brief"
    assert result["safety"]["socialPosting"] is False
    assert result["safety"]["scheduling"] is False
    assert result["safety"]["accountAccess"] is False


def test_local_online_presence_thin_input_reports_warnings_and_questions():
    service = LocalOnlinePresenceAgentService()

    result = service.create_plan(LocalOnlinePresenceRequest(profile_name="Local profile"))

    assert any("Online-presence input is thin" in warning for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_online_presence_output_includes_drafts_plans_and_next_actions():
    service = LocalOnlinePresenceAgentService()

    result = service.create_plan(
        LocalOnlinePresenceRequest(
            profile_name="Local Portfolio Profile",
            platforms=["Portfolio site"],
            goals=["Clarify positioning"],
            target_audience="Collaborators",
            tone="Practical",
            strengths=["Careful local-first implementation"],
            projects=["Local dashboard"],
            content_ideas=["Explain a boundary choice"],
            desired_output_type="posting_drafts",
        )
    )

    assert result["bioDrafts"]
    assert result["profileRecommendations"]
    assert result["contentPlan"]
    assert result["portfolioPositioning"]
    assert result["personalBrandPlan"]
    assert result["reputationReview"]
    assert result["postingDrafts"]
    assert result["nextActions"]
    assert result["openQuestions"]


def test_local_online_presence_sensitive_inputs_include_human_review_limitations():
    service = LocalOnlinePresenceAgentService()

    result = service.create_plan(
        LocalOnlinePresenceRequest(
            profile_name="Local profile",
            goals=["Address employment and legal reputation concerns"],
            reputation_concerns=["Sensitive public accusation"],
            desired_output_type="reputation_review",
        )
    )

    assert any("Sensitive, reputation, legal, employment" in warning for warning in result["warnings"])
    assert any("human review" in limitation for limitation in result["limitations"])
    assert any("human review" in action for action in result["nextActions"])


def test_local_online_presence_output_does_not_claim_external_online_actions():
    service = LocalOnlinePresenceAgentService()

    result = service.create_plan(
        LocalOnlinePresenceRequest(
            profile_name="Local Portfolio Profile",
            goals=["Draft profile copy"],
            content_ideas=["Share a project lesson"],
            desired_output_type="posting_drafts",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "posted successfully",
        "scheduled post",
        "message sent",
        "account updated",
        "analytics retrieved",
        "profile verified",
        "scraped results",
        "upload completed",
        "follower growth guaranteed",
        "hiring result guaranteed",
        "platform compliance verified",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no post" in output_text or "no posting" in output_text
    assert "no live reputation search" in output_text
    assert "no linkedin" in output_text
    assert "no brand success" in output_text


def test_local_online_presence_safety_flags_disable_connectors_accounts_and_public_actions():
    service = LocalOnlinePresenceAgentService()

    result = service.create_plan(LocalOnlinePresenceRequest(profile_name="Local profile"))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["connectors"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["webBrowsing"] is False
    assert safety["paidApis"] is False
    assert safety["socialPosting"] is False
    assert safety["scheduling"] is False
    assert safety["messaging"] is False
    assert safety["scraping"] is False
    assert safety["analyticsAccess"] is False
    assert safety["emailSending"] is False
    assert safety["publicPosting"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["certificationClaims"] is False


def test_local_online_presence_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_online_presence_agent").local_online_presence_agent).lower()
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


def test_local_online_presence_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalOnlinePresenceInput.model_validate(
            {
                "profileName": "Local profile",
                "socialAccountToken": "not allowed",
            }
        )


def test_local_online_presence_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/online-presence/local-plan"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
