import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_classification_agent import LocalClassificationAgentService, LocalClassificationRequest


CLASSIFICATION_CONTENT = (
    "Dashboard docs are high priority before the Friday deadline. "
    "Safety wording has risk because it could overclaim validation. "
    "A small README update should be low effort. "
    "Routing should stay advisory and must not create tasks."
)
CLASSIFICATION_ITEMS = [
    "Urgent dashboard docs before Friday",
    "Security wording risk needs manual review",
    "Small README copy update",
]


def test_local_classification_endpoint_returns_structured_local_classification_response():
    payload = app_module.LocalClassificationInput(
        title="Private alpha classification",
        content=CLASSIFICATION_CONTENT,
        items=CLASSIFICATION_ITEMS,
        classificationType="general",
        labels=["docs", "safety"],
        criteria=["review impact"],
        constraints=["no task creation"],
        detailLevel="medium",
    )

    result = app_module.create_local_classification(payload)

    assert result["agentId"] == "local_classification_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_classification"
    assert result["title"] == "Private alpha classification"
    assert result["classificationType"] == "general"
    assert result["detailLevel"] == "medium"
    assert result["classificationFocus"]
    assert result["classifiedItems"]
    assert result["labelsUsed"]
    assert result["priorityBands"]
    assert result["riskBands"]
    assert result["effortBands"]
    assert result["routingHints"]
    assert result["safetyNotes"]
    assert result["assumptions"]
    assert result["missingContext"]
    assert "Based only on user-provided classification inputs." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("general", "general"),
        ("priority", "priority"),
        ("risk", "risk"),
        ("effort", "effort"),
        ("topic", "topic"),
        ("routing", "routing"),
        ("safety", "safety"),
        (" SAFETY ", "safety"),
    ],
)
def test_local_classification_supported_classification_types_normalize(requested, expected):
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, classification_type=requested))

    assert result["classificationType"] == expected


def test_local_classification_unsupported_classification_type_falls_back_safely():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, classification_type="auto_execute"))

    assert result["classificationType"] == "general"
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
def test_local_classification_supported_detail_levels_normalize(requested, expected):
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, detail_level=requested))

    assert result["detailLevel"] == expected


def test_local_classification_unsupported_detail_level_falls_back_safely():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, detail_level="full_document"))

    assert result["detailLevel"] == "medium"
    assert result["safety"]["documentRetrieval"] is False


def test_local_classification_empty_or_thin_input_reports_warnings_and_limitations():
    service = LocalClassificationAgentService()

    empty = service.classify(LocalClassificationRequest())
    thin = service.classify(LocalClassificationRequest(content="Tiny."))

    assert empty["classifiedItems"][0]["label"] == "unclassified"
    assert any("No usable content or items were provided." == item for item in empty["missingContext"])
    assert any("Classification input is empty or thin" in warning for warning in thin["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in thin["limitations"])


def test_local_classification_labels_are_user_provided_candidate_labels_only():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, labels=["docs", "safety"]))
    labels_text = str(result["labelsUsed"] + result["assumptions"]).lower()

    assert result["labelsUsed"] == [
        {"label": "docs", "source": "user_provided_candidate_label"},
        {"label": "safety", "source": "user_provided_candidate_label"},
    ]
    assert "user-provided candidate labels only" in labels_text
    assert "trained taxonomy" in labels_text
    assert "externally validated" in labels_text


def test_local_classification_priority_returns_priority_bands():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, classification_type="priority"))

    assert result["priorityBands"]["high"]
    assert "urgent" in " ".join(result["priorityBands"]["high"]).lower()


def test_local_classification_risk_returns_risk_bands():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, classification_type="risk"))

    assert result["riskBands"]["high"] or result["riskBands"]["medium"]
    assert "risk" in str(result["riskBands"]).lower() or "security" in str(result["riskBands"]).lower()


def test_local_classification_effort_returns_effort_bands():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, classification_type="effort"))

    assert result["effortBands"]["low"]
    assert "small" in " ".join(result["effortBands"]["low"]).lower()


def test_local_classification_topic_returns_labels_and_classified_items():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, classification_type="topic"))

    assert result["labelsUsed"]
    assert result["classifiedItems"]
    assert any(item["label"] in {"documentation", "safety", "dashboard", "topic_candidate"} for item in result["classifiedItems"])


def test_local_classification_routing_returns_hints_without_task_creation_or_agent_calls():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS, classification_type="routing"))
    output_text = str(result).lower()

    assert result["routingHints"]
    assert result["safety"]["taskCreation"] is False
    assert result["safety"]["agentCalls"] is False
    assert "no task, agent call, or workflow mutation was created" in output_text
    assert "task created" not in output_text
    assert "agent called" not in output_text


def test_local_classification_safety_returns_conservative_notes_without_certification_claims():
    service = LocalClassificationAgentService()

    result = service.classify(
        LocalClassificationRequest(
            items=["Security wording mentions credentials and legal risk"],
            classification_type="safety",
        )
    )
    output_text = str(result).lower()

    assert result["safetyNotes"]
    assert "conservative" in output_text
    assert "does not certify" in output_text
    assert "compliance certification" in output_text
    assert "professional validation" in output_text
    assert "certified compliant" not in output_text
    assert "professionally validated" not in output_text


def test_local_classification_output_does_not_claim_external_validation_or_access():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(content=CLASSIFICATION_CONTENT, items=CLASSIFICATION_ITEMS))
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
        "classification persisted",
        "persisted classification",
        "professionally validated",
        "compliance certified",
        "certified compliant",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no source verification" in output_text
    assert "task creation" in output_text
    assert "professional validation" in output_text
    assert "compliance certification" in output_text


def test_local_classification_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalClassificationAgentService()

    result = service.classify(LocalClassificationRequest(items=CLASSIFICATION_ITEMS))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["classificationPersistence"] is False
    assert safety["taskCreation"] is False
    assert safety["agentCalls"] is False
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
    assert safety["professionalValidation"] is False
    assert safety["complianceCertification"] is False


def test_local_classification_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_classification_agent").local_classification_agent).lower()
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


def test_local_classification_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalClassificationInput.model_validate(
            {
                "content": "Classify this local text.",
                "filePath": "C:/dev/Jarvis/README.md",
            }
        )


def test_local_classification_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/classification/local-classify"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
