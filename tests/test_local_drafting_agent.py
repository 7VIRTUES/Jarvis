import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_drafting_agent import LocalDraftingAgentService, LocalDraftingRequest


def test_local_drafting_endpoint_returns_structured_local_draft():
    payload = app_module.LocalDraftingInput(
        purpose="Invite reviewers to a local alpha check",
        audience="Private alpha reviewers",
        notes="Keep it short. Explain that the review is local-only and feedback should be specific.",
        tone="clear",
        format="message",
        constraints=["No hype"],
        mustInclude=["Local-only review"],
        mustAvoid=["guaranteed"],
    )

    result = app_module.create_local_draft(payload)

    assert result["agentId"] == "local_drafting_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_drafting"
    assert result["purpose"] == "Invite reviewers to a local alpha check"
    assert result["audience"] == "Private alpha reviewers"
    assert result["format"] == "message"
    assert result["tone"] == "clear"
    assert result["draftTitle"]
    assert "Local-only review" in result["includedPoints"]
    assert "Local-only review" in result["draftText"]
    assert "guaranteed" not in result["draftText"].lower()
    assert result["avoidedItems"] == ["guaranteed"]
    assert result["revisionNotes"]
    assert "Based only on user-provided drafting inputs." in result["limitations"]


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("message", "message"),
        ("email_draft", "email_draft"),
        ("document_section", "document_section"),
        ("checklist", "checklist"),
        ("announcement", "announcement"),
        (" EMAIL_DRAFT ", "email_draft"),
    ],
)
def test_local_drafting_supported_formats_normalize(requested, expected):
    service = LocalDraftingAgentService()

    result = service.create_draft(
        LocalDraftingRequest(
            purpose="Draft locally",
            notes="Point one. Point two.",
            draft_format=requested,
        )
    )

    assert result["format"] == expected


def test_local_drafting_unsupported_format_falls_back_safely():
    service = LocalDraftingAgentService()

    result = service.create_draft(
        LocalDraftingRequest(
            purpose="Draft locally",
            notes="Point one. Point two.",
            draft_format="gmail_send",
        )
    )

    assert result["format"] == "message"
    assert result["safety"]["emailSending"] is False
    assert result["safety"]["connectorExecution"] is False


def test_local_drafting_thin_notes_reports_warnings_and_limitations():
    service = LocalDraftingAgentService()

    result = service.create_draft(LocalDraftingRequest(purpose="Say hello", notes="Hi."))

    assert result["warnings"] == ["Drafting notes are thin; output is a provisional local draft."]
    assert any("Thin notes limit specificity" in limitation for limitation in result["limitations"])
    assert "provisional" in result["draftText"]


def test_local_drafting_must_include_points_are_reflected_when_possible():
    service = LocalDraftingAgentService()

    result = service.create_draft(
        LocalDraftingRequest(
            purpose="Share a status note",
            notes="The dashboard is local-only. The review should stay bounded.",
            must_include=["Private alpha readiness"],
        )
    )

    assert "Private alpha readiness" in result["includedPoints"]
    assert "Private alpha readiness" in result["draftText"]


def test_local_drafting_must_avoid_items_are_not_inserted_into_draft_text():
    service = LocalDraftingAgentService()

    result = service.create_draft(
        LocalDraftingRequest(
            purpose="Share a status note",
            notes="The dashboard is local-only. The review should stay bounded.",
            must_avoid=["guaranteed", "instant"],
        )
    )

    assert "guaranteed" not in result["draftText"].lower()
    assert "instant" not in result["draftText"].lower()
    assert result["avoidedItems"] == ["guaranteed", "instant"]


def test_local_drafting_email_format_remains_draft_only():
    service = LocalDraftingAgentService()

    result = service.create_draft(
        LocalDraftingRequest(
            purpose="Review request",
            audience="Casey",
            notes="Please review the local dashboard. Focus on safety boundaries.",
            draft_format="email_draft",
        )
    )

    assert result["format"] == "email_draft"
    assert result["draftText"].startswith("Subject: Review request")
    assert "Email draft is text only; no email was sent or saved." in result["warnings"]
    assert any("draft-only" in note.lower() for note in result["revisionNotes"])
    assert result["safety"]["emailSending"] is False
    assert result["safety"]["gmailAccess"] is False
    assert result["safety"]["draftPersistence"] is False


def test_local_drafting_safety_flags_disable_external_persistence_and_mutation_behavior():
    service = LocalDraftingAgentService()

    result = service.create_draft(
        LocalDraftingRequest(
            purpose="Local drafting safety",
            notes="Use only the request body. Return draft text only.",
        )
    )
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["draftPersistence"] is False
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


def test_local_drafting_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_drafting_agent").local_drafting_agent).lower()
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


def test_local_drafting_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalDraftingInput.model_validate(
            {"purpose": "Draft", "notes": "Local notes.", "gmailThreadId": "abc"}
        )


def test_local_drafting_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/drafting/local-draft")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
