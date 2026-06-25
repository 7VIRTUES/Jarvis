import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_review_agent import LocalReviewAgentService, LocalReviewRequest


def test_local_review_endpoint_returns_structured_local_review():
    payload = app_module.LocalReviewInput(
        subject="Private alpha checklist",
        content="The checklist should stay local-only. It should name scope, safety boundaries, and unresolved risks.",
        reviewType="risk",
        audience="Private alpha reviewers",
        criteria=["Clear scope"],
        constraints=["No external verification claims"],
        severity="balanced",
    )

    result = app_module.create_local_review(payload)

    assert result["agentId"] == "local_review_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_review"
    assert result["subject"] == "Private alpha checklist"
    assert result["reviewType"] == "risk"
    assert result["severity"] == "balanced"
    assert result["audience"] == "Private alpha reviewers"
    assert result["reviewFocus"]
    assert result["strengths"]
    assert result["issues"]
    assert result["missingInformation"]
    assert result["riskFlags"]
    assert result["improvementSuggestions"]
    assert result["actionItems"]
    assert result["reviewQuestions"]
    assert "Based only on user-provided review content." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("general", "general"),
        ("clarity", "clarity"),
        ("risk", "risk"),
        ("completeness", "completeness"),
        ("safety", "safety"),
        ("actionability", "actionability"),
        (" SAFETY ", "safety"),
    ],
)
def test_local_review_supported_review_types_normalize(requested, expected):
    service = LocalReviewAgentService()

    result = service.create_review(
        LocalReviewRequest(
            subject="Review locally",
            content="Point one is clear. Point two needs a follow-up action.",
            review_type=requested,
        )
    )

    assert result["reviewType"] == expected


def test_local_review_unsupported_review_type_falls_back_safely():
    service = LocalReviewAgentService()

    result = service.create_review(
        LocalReviewRequest(
            subject="Review locally",
            content="Point one is clear. Point two needs a follow-up action.",
            review_type="repo_audit",
        )
    )

    assert result["reviewType"] == "general"
    assert result["safety"]["repoInspection"] is False
    assert result["safety"]["externalServices"] is False


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("gentle", "gentle"),
        ("balanced", "balanced"),
        ("strict", "strict"),
        (" STRICT ", "strict"),
    ],
)
def test_local_review_supported_severity_values_normalize(requested, expected):
    service = LocalReviewAgentService()

    result = service.create_review(
        LocalReviewRequest(
            subject="Review locally",
            content="Point one is clear. Point two needs a follow-up action.",
            severity=requested,
        )
    )

    assert result["severity"] == expected


def test_local_review_unsupported_severity_falls_back_safely():
    service = LocalReviewAgentService()

    result = service.create_review(
        LocalReviewRequest(
            subject="Review locally",
            content="Point one is clear. Point two needs a follow-up action.",
            severity="certified",
        )
    )

    assert result["severity"] == "balanced"
    assert result["safety"]["sourceValidation"] is False
    assert result["safety"]["testExecution"] is False


def test_local_review_thin_content_reports_warnings_and_limitations():
    service = LocalReviewAgentService()

    result = service.create_review(LocalReviewRequest(subject="Tiny note", content="Looks okay."))

    assert result["warnings"] == ["Review content is thin; output is a provisional local review."]
    assert any("Thin content limits specificity" in limitation for limitation in result["limitations"])
    assert any("too thin" in result["reviewFocus"].lower() for _ in [result])


def test_local_review_output_does_not_claim_external_validation_or_execution():
    service = LocalReviewAgentService()

    result = service.create_review(
        LocalReviewRequest(
            subject="Review boundaries",
            content="This note asks for a local review. The output should stay bounded and not claim validation.",
        )
    )
    output_text = str(result).lower()

    forbidden_claims = [
        "externally verified",
        "web verified",
        "tests passed",
        "test results",
        "repo inspected",
        "repository inspected",
        "citations validated",
        "sources validated",
        "files read",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no external verification" in output_text
    assert "no files" in output_text


def test_local_review_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalReviewAgentService()

    result = service.create_review(
        LocalReviewRequest(
            subject="Local review safety",
            content="Use only the request body. Return review text only.",
        )
    )
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["reviewPersistence"] is False
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
    assert safety["taskPersistence"] is False
    assert safety["dbWrites"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["shellExecution"] is False
    assert safety["uploads"] is False
    assert safety["mutation"] is False
    assert safety["repoInspection"] is False
    assert safety["testExecution"] is False
    assert safety["sourceValidation"] is False
    assert safety["citationValidation"] is False


def test_local_review_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_review_agent").local_review_agent).lower()
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


def test_local_review_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalReviewInput.model_validate(
            {"subject": "Review", "content": "Local notes.", "repoPath": "C:/dev/Jarvis"}
        )


def test_local_review_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/review/local-review")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
