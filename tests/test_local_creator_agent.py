import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_creator_agent import LocalCreatorAgentService, LocalCreatorRequest


def test_local_creator_endpoint_returns_structured_plan():
    payload = app_module.LocalCreatorInput(
        creatorName="Local Workshop Channel",
        platforms=["Video channel", "Short-form clips"],
        niche="Local-first software workflows",
        audience="Builders who want practical local tools",
        contentIdea="Explain how a local-only planning assistant stays review-friendly.",
        goals=["Clarify the idea", "Draft an outline"],
        tone="Practical and clear",
        formatNotes="Short explainer with a simple three-part structure.",
        productionResources=["Screen notes", "Demo outline"],
        constraints=["No platform claims"],
        existingContentNotes="Previous notes focus on local-only boundaries.",
        desiredOutputType="creator_brief",
    )

    result = app_module.create_local_creator_plan(payload)

    assert result["agentId"] == "local_creator_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_creator_planning"
    assert result["creatorName"] == "Local Workshop Channel"
    assert result["platforms"] == ["Video channel", "Short-form clips"]
    assert result["desiredOutputType"] == "creator_brief"
    assert result["creatorFocus"]
    assert result["audienceSummary"]
    assert result["positioningSummary"]
    assert result["channelPlan"]
    assert result["contentCalendar"]
    assert result["videoOutline"]
    assert result["scriptDraft"]
    assert result["titleThumbnailIdeas"]
    assert result["productionChecklist"]
    assert result["repurposingPlan"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided creator planning and drafting inputs." in result["limitations"]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("creator_brief", "creator_brief"),
        ("channel_plan", "channel_plan"),
        ("content_calendar", "content_calendar"),
        ("video_outline", "video_outline"),
        ("script_draft", "script_draft"),
        ("title_thumbnail_ideas", "title_thumbnail_ideas"),
        ("production_checklist", "production_checklist"),
        ("repurposing_plan", "repurposing_plan"),
        (" SCRIPT_DRAFT ", "script_draft"),
    ],
)
def test_local_creator_supported_output_types_normalize(requested, expected):
    service = LocalCreatorAgentService()

    result = service.create_plan(
        LocalCreatorRequest(
            creator_name="Local creator",
            content_idea="Explain a local planning workflow.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_creator_unsupported_output_type_falls_back_safely():
    service = LocalCreatorAgentService()

    result = service.create_plan(
        LocalCreatorRequest(
            creator_name="Local creator",
            content_idea="Explain a local planning workflow.",
            desired_output_type="auto_upload_scheduler",
        )
    )

    assert result["desiredOutputType"] == "creator_brief"
    assert result["safety"]["upload"] is False
    assert result["safety"]["scheduling"] is False
    assert result["safety"]["publicPosting"] is False


def test_local_creator_thin_input_reports_warnings_and_questions():
    service = LocalCreatorAgentService()

    result = service.create_plan(LocalCreatorRequest(content_idea=""))

    assert any("Creator input is thin" in warning for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_creator_output_includes_plans_scripts_checklists_and_next_actions():
    service = LocalCreatorAgentService()

    result = service.create_plan(
        LocalCreatorRequest(
            creator_name="Local Workshop Channel",
            platforms=["Video channel"],
            niche="Local-first workflows",
            audience="Builders",
            content_idea="Explain a local-only design choice.",
            goals=["Draft an outline"],
            tone="Practical",
            format_notes="Short explainer",
            production_resources=["Outline"],
            desired_output_type="video_outline",
        )
    )

    assert result["channelPlan"]
    assert result["contentCalendar"]
    assert result["videoOutline"]
    assert result["scriptDraft"]
    assert result["titleThumbnailIdeas"]
    assert result["productionChecklist"]
    assert result["repurposingPlan"]
    assert result["nextActions"]
    assert result["openQuestions"]


def test_local_creator_sensitive_inputs_include_human_review_limitations():
    service = LocalCreatorAgentService()

    result = service.create_plan(
        LocalCreatorRequest(
            creator_name="Local creator",
            content_idea="Discuss copyright, sponsorship, brand deal, reputation, and legal concerns.",
            desired_output_type="script_draft",
        )
    )

    assert any("Copyright, reputation, legal, sponsorship" in warning for warning in result["warnings"])
    assert any("human review" in limitation for limitation in result["limitations"])
    assert any("human review" in action for action in result["nextActions"])


def test_local_creator_output_does_not_claim_platform_actions_or_validation():
    service = LocalCreatorAgentService()

    result = service.create_plan(
        LocalCreatorRequest(
            creator_name="Local creator",
            content_idea="Plan a short explainer.",
            desired_output_type="title_thumbnail_ideas",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "upload completed",
        "posted successfully",
        "scheduled post",
        "analytics retrieved",
        "scraped trends",
        "account accessed",
        "trend validated",
        "monetization guaranteed",
        "copyright cleared",
        "platform compliance verified",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no upload" in output_text
    assert "no follower growth" in output_text
    assert "no youtube" in output_text
    assert "no monetization success" in output_text


def test_local_creator_safety_flags_disable_platforms_persistence_mutation_and_claims():
    service = LocalCreatorAgentService()

    result = service.create_plan(LocalCreatorRequest(content_idea="Plan a creator brief."))
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
    assert safety["youtubeAccess"] is False
    assert safety["socialPlatformAccess"] is False
    assert safety["analyticsAccess"] is False
    assert safety["scraping"] is False
    assert safety["upload"] is False
    assert safety["publicPosting"] is False
    assert safety["scheduling"] is False
    assert safety["messaging"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["copyrightClearance"] is False
    assert safety["platformComplianceValidation"] is False
    assert safety["monetizationGuarantee"] is False
    assert safety["certificationClaims"] is False


def test_local_creator_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_creator_agent").local_creator_agent).lower()
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


def test_local_creator_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalCreatorInput.model_validate(
            {
                "contentIdea": "Plan a short explainer.",
                "youtubeAccountToken": "not allowed",
            }
        )


def test_local_creator_requires_content_idea_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalCreatorInput.model_validate({"creatorName": "Missing idea"})


def test_local_creator_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/creator/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
