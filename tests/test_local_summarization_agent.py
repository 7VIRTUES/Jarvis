import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_summarization_agent import LocalSummarizationAgentService, LocalSummarizationRequest


SUMMARY_CONTENT = (
    "Jarvis private alpha notes emphasize local-only scope and reviewer clarity. "
    "The dashboard should show response-only agents without connector actions. "
    "Next steps should identify documentation updates and manual review questions. "
    "Risks include thin context, overclaiming validation, and unclear ownership."
)


def test_local_summarization_endpoint_returns_structured_local_summary():
    payload = app_module.LocalSummarizationInput(
        title="Private alpha notes",
        content=SUMMARY_CONTENT,
        summaryType="general",
        audience="Reviewers",
        detailLevel="medium",
        focusAreas=["scope", "next steps"],
        mustPreserve=["local-only scope"],
        mustAvoid=["certified"],
    )

    result = app_module.create_local_summarization(payload)

    assert result["agentId"] == "local_summarization_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_summarization"
    assert result["title"] == "Private alpha notes"
    assert result["summaryType"] == "general"
    assert result["detailLevel"] == "medium"
    assert result["audience"] == "Reviewers"
    assert result["summary"]
    assert result["keyPoints"]
    assert result["actionItems"]
    assert result["risksOrCaveats"]
    assert result["preservedItems"] == ["local-only scope"]
    assert result["avoidedItems"] == ["certified"]
    assert result["missingContext"]
    assert "Based only on user-provided summarization content." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("general", "general"),
        ("bullets", "bullets"),
        ("executive", "executive"),
        ("action_items", "action_items"),
        ("study_notes", "study_notes"),
        ("risks", "risks"),
        (" RISKS ", "risks"),
    ],
)
def test_local_summarization_supported_summary_types_normalize(requested, expected):
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=SUMMARY_CONTENT, summary_type=requested))

    assert result["summaryType"] == expected


def test_local_summarization_unsupported_summary_type_falls_back_safely():
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=SUMMARY_CONTENT, summary_type="verified_sources"))

    assert result["summaryType"] == "general"
    assert result["safety"]["sourceValidation"] is False
    assert result["safety"]["externalFactChecking"] is False


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("short", "short"),
        ("medium", "medium"),
        ("detailed", "detailed"),
        (" DETAILED ", "detailed"),
    ],
)
def test_local_summarization_supported_detail_levels_normalize(requested, expected):
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=SUMMARY_CONTENT, detail_level=requested))

    assert result["detailLevel"] == expected


def test_local_summarization_unsupported_detail_level_falls_back_safely():
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=SUMMARY_CONTENT, detail_level="full_document"))

    assert result["detailLevel"] == "medium"
    assert result["safety"]["documentRetrieval"] is False


def test_local_summarization_thin_content_reports_warnings_and_limitations():
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content="Too short."))

    assert any("Summarization content is thin" in warning for warning in result["warnings"])
    assert any("Thin content limits specificity" in limitation for limitation in result["limitations"])
    assert "limited local summary" in result["summary"].lower()


def test_local_summarization_empty_content_returns_limited_summary_without_inventing_details():
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=""))

    assert result["keyPoints"] == ["No substantive content was provided to summarize."]
    assert any("Content was empty." == item for item in result["missingContext"])
    assert any("thin" in warning.lower() for warning in result["warnings"])


def test_local_summarization_must_preserve_points_are_reflected_when_possible():
    service = LocalSummarizationAgentService()

    result = service.create_summary(
        LocalSummarizationRequest(
            content=SUMMARY_CONTENT,
            must_preserve=["manual review questions"],
            detail_level="medium",
        )
    )

    assert result["preservedItems"] == ["manual review questions"]
    assert "manual review questions" in " ".join(result["keyPoints"]).lower()
    assert "manual review questions" in result["summary"].lower()


def test_local_summarization_must_avoid_items_are_not_intentionally_inserted_into_summary_text():
    service = LocalSummarizationAgentService()

    result = service.create_summary(
        LocalSummarizationRequest(
            content=f"{SUMMARY_CONTENT} Do not call this certified.",
            must_avoid=["certified"],
        )
    )

    assert "certified" not in result["summary"].lower()
    assert result["avoidedItems"] == ["certified"]


def test_local_summarization_action_items_type_returns_action_items():
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=SUMMARY_CONTENT, summary_type="action_items"))

    assert result["summaryType"] == "action_items"
    assert result["actionItems"]
    assert "next steps" in " ".join(result["actionItems"]).lower()


def test_local_summarization_risks_type_returns_risks_or_caveats():
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=SUMMARY_CONTENT, summary_type="risks"))

    assert result["summaryType"] == "risks"
    assert result["risksOrCaveats"]
    assert "risk" in " ".join(result["risksOrCaveats"]).lower()


def test_local_summarization_output_does_not_claim_external_validation_or_access():
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=SUMMARY_CONTENT))
    output_text = str(result).lower()

    forbidden_claims = [
        "sources verified",
        "citations verified",
        "externally fact checked",
        "external fact checked",
        "files read",
        "repo inspected",
        "repository inspected",
        "documents retrieved",
        "document retrieved",
        "tests passed",
        "test results",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no source verification" in output_text
    assert "citation verification" in output_text
    assert "document retrieval" in output_text


def test_local_summarization_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalSummarizationAgentService()

    result = service.create_summary(LocalSummarizationRequest(content=SUMMARY_CONTENT))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["summaryPersistence"] is False
    assert safety["externalServices"] is False
    assert safety["paidApis"] is False
    assert safety["webBrowsing"] is False
    assert safety["connectorExecution"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["gmailAccess"] is False
    assert safety["calendarAccess"] is False
    assert safety["socialAccess"] is False
    assert safety["postingOrSending"] is False
    assert safety["emailSending"] is False
    assert safety["publicPosting"] is False
    assert safety["purchases"] is False
    assert safety["taskPersistence"] is False
    assert safety["dbWrites"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["shellExecution"] is False
    assert safety["downloads"] is False
    assert safety["uploads"] is False
    assert safety["mutation"] is False
    assert safety["repoInspection"] is False
    assert safety["testExecution"] is False
    assert safety["sourceValidation"] is False
    assert safety["citationValidation"] is False
    assert safety["externalFactChecking"] is False
    assert safety["documentRetrieval"] is False


def test_local_summarization_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_summarization_agent").local_summarization_agent).lower()
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


def test_local_summarization_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalSummarizationInput.model_validate(
            {
                "content": "Summarize this local text.",
                "filePath": "C:/dev/Jarvis/README.md",
            }
        )


def test_local_summarization_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route
        for route in app_module.app.routes
        if getattr(route, "path", None) == "/agents/summarization/local-summary"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
