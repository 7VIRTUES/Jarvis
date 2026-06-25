import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_extraction_agent import LocalExtractionAgentService, LocalExtractionRequest


EXTRACTION_CONTENT = (
    "Jarvis Dashboard must show local-only agents for private alpha reviewers. "
    "Next step: update docs and assign an owner before Friday. "
    "Risk: overclaiming validation could confuse reviewers. "
    "Alice should review the Local Extraction Agent notes. "
    "Question: who owns the final review? "
    "Timeline: finish the dashboard card next week."
)


def test_local_extraction_endpoint_returns_structured_local_extraction_response():
    payload = app_module.LocalExtractionInput(
        title="Private alpha extraction notes",
        content=EXTRACTION_CONTENT,
        extractionType="general",
        focusAreas=["requirements", "risks"],
        mustCapture=["local-only agents"],
        mustIgnore=["certified"],
        detailLevel="medium",
    )

    result = app_module.create_local_extraction(payload)

    assert result["agentId"] == "local_extraction_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_extraction"
    assert result["title"] == "Private alpha extraction notes"
    assert result["extractionType"] == "general"
    assert result["detailLevel"] == "medium"
    assert result["extractionFocus"]
    assert result["extractedItems"]
    assert result["actionItems"]
    assert result["requirements"]
    assert result["risks"]
    assert result["entities"]
    assert result["questions"]
    assert result["timelineItems"]
    assert result["capturedItems"] == ["local-only agents"]
    assert result["ignoredItems"] == ["certified"]
    assert result["missingContext"]
    assert "Based only on user-provided extraction content." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("general", "general"),
        ("action_items", "action_items"),
        ("requirements", "requirements"),
        ("risks", "risks"),
        ("entities", "entities"),
        ("questions", "questions"),
        ("timeline", "timeline"),
        (" TIMELINE ", "timeline"),
    ],
)
def test_local_extraction_supported_extraction_types_normalize(requested, expected):
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, extraction_type=requested))

    assert result["extractionType"] == expected


def test_local_extraction_unsupported_extraction_type_falls_back_safely():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, extraction_type="persist_tasks"))

    assert result["extractionType"] == "general"
    assert result["safety"]["taskCreation"] is False
    assert result["safety"]["externalServices"] is False


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("short", "short"),
        ("medium", "medium"),
        ("detailed", "detailed"),
        (" DETAILED ", "detailed"),
    ],
)
def test_local_extraction_supported_detail_levels_normalize(requested, expected):
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, detail_level=requested))

    assert result["detailLevel"] == expected


def test_local_extraction_unsupported_detail_level_falls_back_safely():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, detail_level="full_document"))

    assert result["detailLevel"] == "medium"
    assert result["safety"]["documentRetrieval"] is False


def test_local_extraction_empty_or_thin_content_reports_warnings_and_limitations():
    service = LocalExtractionAgentService()

    empty = service.extract_items(LocalExtractionRequest(content=""))
    thin = service.extract_items(LocalExtractionRequest(content="Tiny note."))

    assert empty["extractedItems"][0]["text"] == "No substantive content was provided to extract from."
    assert any("Content was empty." == item for item in empty["missingContext"])
    assert any("Extraction content is thin" in warning for warning in thin["warnings"])
    assert any("Thin content limits specificity" in limitation for limitation in thin["limitations"])


def test_local_extraction_action_items_returns_action_items_without_task_creation_or_persistence_claims():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, extraction_type="action_items"))
    output_text = str(result).lower()

    assert result["actionItems"]
    assert "next step" in " ".join(result["actionItems"]).lower()
    assert result["safety"]["taskCreation"] is False
    assert result["safety"]["taskPersistence"] is False
    assert "task created" not in output_text
    assert "persisted" not in output_text


def test_local_extraction_requirements_returns_requirements():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, extraction_type="requirements"))

    assert result["requirements"]
    assert "must show" in " ".join(result["requirements"]).lower()


def test_local_extraction_risks_returns_risks():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, extraction_type="risks"))

    assert result["risks"]
    assert "risk" in " ".join(result["risks"]).lower()


def test_local_extraction_entities_returns_entities():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, extraction_type="entities"))

    assert result["entities"]
    assert "Alice" in result["entities"] or "Jarvis Dashboard" in result["entities"]


def test_local_extraction_questions_returns_questions():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, extraction_type="questions"))

    assert result["questions"]
    assert "?" in " ".join(result["questions"])


def test_local_extraction_timeline_returns_timeline_items():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT, extraction_type="timeline"))

    assert result["timelineItems"]
    assert "friday" in " ".join(result["timelineItems"]).lower() or "next week" in " ".join(result["timelineItems"]).lower()


def test_local_extraction_must_capture_points_are_reflected_when_possible():
    service = LocalExtractionAgentService()

    result = service.extract_items(
        LocalExtractionRequest(
            content=EXTRACTION_CONTENT,
            must_capture=["private alpha reviewers"],
        )
    )

    assert result["capturedItems"] == ["private alpha reviewers"]
    assert "private alpha reviewers" in " ".join(item["text"] for item in result["extractedItems"]).lower()


def test_local_extraction_must_ignore_items_are_only_listed_under_ignored_items():
    service = LocalExtractionAgentService()

    result = service.extract_items(
        LocalExtractionRequest(
            content=f"{EXTRACTION_CONTENT} This is not certified.",
            must_ignore=["certified"],
        )
    )
    output_without_ignored = {key: value for key, value in result.items() if key != "ignoredItems"}

    assert result["ignoredItems"] == ["certified"]
    assert "certified" not in str(output_without_ignored).lower()


def test_local_extraction_output_does_not_claim_external_validation_or_access():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT))
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
        "task created",
        "created task",
        "items persisted",
        "persisted items",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no source verification" in output_text
    assert "task creation" in output_text
    assert "persistence" in output_text


def test_local_extraction_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalExtractionAgentService()

    result = service.extract_items(LocalExtractionRequest(content=EXTRACTION_CONTENT))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["extractionPersistence"] is False
    assert safety["taskCreation"] is False
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


def test_local_extraction_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_extraction_agent").local_extraction_agent).lower()
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


def test_local_extraction_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalExtractionInput.model_validate(
            {
                "content": "Extract from this local text.",
                "filePath": "C:/dev/Jarvis/README.md",
            }
        )


def test_local_extraction_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/extraction/local-extract"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
