import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_transformation_agent import LocalTransformationAgentService, LocalTransformationRequest


TRANSFORMATION_CONTENT = (
    "Review the private alpha docs. "
    "Confirm local-only safety wording. "
    "Prepare a manual checklist for reviewers. "
    "Avoid claiming certified readiness."
)
TRANSFORMATION_ITEMS = [
    "Review the private alpha docs",
    "Confirm local-only safety wording",
    "Prepare a manual checklist for reviewers",
]


def test_local_transformation_endpoint_returns_structured_local_transformation_response():
    payload = app_module.LocalTransformationInput(
        title="Private alpha transformation",
        content=TRANSFORMATION_CONTENT,
        items=TRANSFORMATION_ITEMS,
        targetFormat="outline",
        audience="Reviewers",
        constraints=["No file export"],
        mustPreserve=["local-only safety wording"],
        mustAvoid=["certified"],
        detailLevel="medium",
    )

    result = app_module.create_local_transformation(payload)

    assert result["agentId"] == "local_transformation_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_transformation"
    assert result["title"] == "Private alpha transformation"
    assert result["targetFormat"] == "outline"
    assert result["detailLevel"] == "medium"
    assert result["audience"] == "Reviewers"
    assert result["transformationFocus"]
    assert result["transformedText"]
    assert result["outline"]
    assert result["checklist"]
    assert result["tableRows"]
    assert result["sopSteps"]
    assert result["flashcards"]
    assert result["jsonStyleText"]
    assert result["csvStyleText"]
    assert result["cleanedNotes"]
    assert result["preservedItems"] == ["local-only safety wording"]
    assert result["avoidedItems"] == ["certified"]
    assert "Based only on user-provided transformation inputs." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("outline", "outline"),
        ("checklist", "checklist"),
        ("table", "table"),
        ("sop_steps", "sop_steps"),
        ("flashcards", "flashcards"),
        ("json_style", "json_style"),
        ("csv_style", "csv_style"),
        ("cleaned_notes", "cleaned_notes"),
        (" CSV_STYLE ", "csv_style"),
    ],
)
def test_local_transformation_supported_target_formats_normalize(requested, expected):
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format=requested))

    assert result["targetFormat"] == expected


def test_local_transformation_unsupported_target_format_falls_back_safely():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format="write_file"))

    assert result["targetFormat"] == "outline"
    assert result["safety"]["fileWrites"] is False
    assert result["safety"]["fileExportCreation"] is False


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("short", "short"),
        ("medium", "medium"),
        ("detailed", "detailed"),
        (" DETAILED ", "detailed"),
    ],
)
def test_local_transformation_supported_detail_levels_normalize(requested, expected):
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, detail_level=requested))

    assert result["detailLevel"] == expected


def test_local_transformation_unsupported_detail_level_falls_back_safely():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, detail_level="full_document"))

    assert result["detailLevel"] == "medium"
    assert result["safety"]["documentRetrieval"] is False


def test_local_transformation_empty_or_thin_input_reports_warnings_and_limitations():
    service = LocalTransformationAgentService()

    empty = service.transform(LocalTransformationRequest())
    thin = service.transform(LocalTransformationRequest(content="Tiny."))

    assert empty["outline"][0]["heading"] == "Limited input"
    assert any("No usable content or items were provided." == item for item in empty["missingContext"])
    assert any("Transformation input is empty or thin" in warning for warning in thin["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in thin["limitations"])


def test_local_transformation_outline_format_returns_outline():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format="outline"))

    assert result["outline"]
    assert "Section" in result["outline"][0]["heading"]


def test_local_transformation_checklist_format_returns_checklist():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format="checklist"))

    assert result["checklist"]
    assert result["transformedText"].startswith("[ ]")


def test_local_transformation_table_format_returns_rows_without_spreadsheet_or_file_creation():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format="table"))
    output_text = str(result).lower()

    assert result["tableRows"]
    assert result["safety"]["spreadsheetCreation"] is False
    assert result["safety"]["fileExportCreation"] is False
    assert "no spreadsheet was created" in output_text
    assert "spreadsheet created" not in output_text


def test_local_transformation_sop_steps_format_returns_sop_steps():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format="sop_steps"))

    assert result["sopSteps"]
    assert result["sopSteps"][0]["step"] == "1"


def test_local_transformation_flashcards_format_returns_flashcards_without_deck_or_file_creation():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format="flashcards"))
    output_text = str(result).lower()

    assert result["flashcards"]
    assert result["safety"]["deckCreation"] is False
    assert result["safety"]["fileExportCreation"] is False
    assert "no deck or file was created" in output_text
    assert "deck created" not in output_text


def test_local_transformation_json_style_returns_text_only_without_file_write():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(title="Notes", items=TRANSFORMATION_ITEMS, target_format="json_style"))
    output_text = str(result).lower()

    assert result["jsonStyleText"].strip().startswith("{")
    assert result["transformedText"] == result["jsonStyleText"]
    assert result["safety"]["fileWrites"] is False
    assert result["safety"]["fileExportCreation"] is False
    assert "response text only" in output_text
    assert "file was written" not in output_text


def test_local_transformation_csv_style_returns_text_only_without_file_write():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format="csv_style"))
    output_text = str(result).lower()

    assert result["csvStyleText"].startswith("item,status,note")
    assert result["transformedText"] == result["csvStyleText"]
    assert result["safety"]["fileWrites"] is False
    assert result["safety"]["fileExportCreation"] is False
    assert "response text only" in output_text
    assert "file was written" not in output_text


def test_local_transformation_cleaned_notes_format_returns_cleaned_notes():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS, target_format="cleaned_notes"))

    assert result["cleanedNotes"].startswith("Cleaned notes:")
    assert result["transformedText"] == result["cleanedNotes"]


def test_local_transformation_must_preserve_points_are_reflected_when_possible():
    service = LocalTransformationAgentService()

    result = service.transform(
        LocalTransformationRequest(
            items=TRANSFORMATION_ITEMS,
            must_preserve=["local-only safety wording"],
            target_format="checklist",
        )
    )

    assert result["preservedItems"] == ["local-only safety wording"]
    assert "local-only safety wording" in result["transformedText"].lower()


def test_local_transformation_must_avoid_items_are_only_listed_under_avoided_items():
    service = LocalTransformationAgentService()

    result = service.transform(
        LocalTransformationRequest(
            content=TRANSFORMATION_CONTENT,
            must_avoid=["certified"],
            target_format="cleaned_notes",
        )
    )
    output_without_avoided = {key: value for key, value in result.items() if key != "avoidedItems"}

    assert result["avoidedItems"] == ["certified"]
    assert "certified" not in str(output_without_avoided).lower()


def test_local_transformation_output_does_not_claim_external_validation_or_access():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS))
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
        "export created",
        "created export",
        "task created",
        "created task",
        "transformation persisted",
        "persisted transformation",
        "professionally validated",
        "compliance certified",
        "certified compliant",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no source verification" in output_text
    assert "export creation" in output_text
    assert "persistence" in output_text
    assert "professional validation" in output_text
    assert "compliance certification" in output_text


def test_local_transformation_safety_flags_disable_external_persistence_export_and_mutation_behavior():
    service = LocalTransformationAgentService()

    result = service.transform(LocalTransformationRequest(items=TRANSFORMATION_ITEMS))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["transformationPersistence"] is False
    assert safety["fileExportCreation"] is False
    assert safety["documentCreation"] is False
    assert safety["spreadsheetCreation"] is False
    assert safety["deckCreation"] is False
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


def test_local_transformation_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_transformation_agent").local_transformation_agent).lower()
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


def test_local_transformation_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalTransformationInput.model_validate(
            {
                "content": "Transform this local text.",
                "outputPath": "C:/dev/Jarvis/out.csv",
            }
        )


def test_local_transformation_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/transformation/local-transform"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
