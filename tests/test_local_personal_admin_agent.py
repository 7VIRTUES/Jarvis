import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_personal_admin_agent import LocalPersonalAdminAgentService, LocalPersonalAdminRequest


def test_local_personal_admin_endpoint_returns_structured_plan():
    payload = app_module.LocalPersonalAdminInput(
        profileName="Local Admin Profile",
        adminGoal="Prepare a manual checklist for school forms and loan paperwork before an office appointment.",
        documentTypes=["School enrollment form", "Loan deferment paperwork", "Photo ID copy checklist"],
        deadlines=["Forms due before the next advising appointment", "Loan paperwork review needed this month"],
        requirements=["Confirm required fields", "List supporting records", "Mark signature fields"],
        currentStatus="Forms are gathered but not fully reviewed.",
        constraints=["Manual planning only"],
        peopleOrOfficesInvolved=["School advising office", "Loan servicer help desk"],
        notes="User wants a calm readiness review before submitting anything outside Jarvis.",
        desiredOutputType="admin_brief",
    )

    result = app_module.create_local_personal_admin_plan(payload)

    assert result["agentId"] == "local_personal_admin_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_personal_admin_planning"
    assert result["profileName"] == "Local Admin Profile"
    assert result["adminGoal"] == "Prepare a manual checklist for school forms and loan paperwork before an office appointment."
    assert result["desiredOutputType"] == "admin_brief"
    assert result["adminFocus"]
    assert result["statusSummary"]
    assert result["documentChecklist"]
    assert result["deadlinePlan"]
    assert result["formPrepPlan"]
    assert result["appointmentPrep"]
    assert result["recordsOrganization"]
    assert result["submissionReadiness"]
    assert result["followUpPlan"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided personal admin goal" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("admin_brief", "admin_brief"),
        ("document_checklist", "document_checklist"),
        ("deadline_plan", "deadline_plan"),
        ("form_prep_plan", "form_prep_plan"),
        ("appointment_prep", "appointment_prep"),
        ("records_organization", "records_organization"),
        ("submission_readiness", "submission_readiness"),
        ("follow_up_plan", "follow_up_plan"),
        (" FORM_PREP_PLAN ", "form_prep_plan"),
    ],
)
def test_local_personal_admin_supported_output_types_normalize(requested, expected):
    service = LocalPersonalAdminAgentService()

    result = service.create_plan(
        LocalPersonalAdminRequest(
            admin_goal="Prepare school form paperwork.",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_personal_admin_unsupported_output_type_falls_back_safely():
    service = LocalPersonalAdminAgentService()

    result = service.create_plan(
        LocalPersonalAdminRequest(
            admin_goal="Prepare paperwork.",
            desired_output_type="read_files_upload_sign_and_pay",
        )
    )

    assert result["desiredOutputType"] == "admin_brief"
    assert result["safety"]["fileReads"] is False
    assert result["safety"]["uploadActions"] is False
    assert result["safety"]["signatureActions"] is False
    assert result["safety"]["paymentActions"] is False


def test_local_personal_admin_thin_input_reports_warnings_and_questions():
    service = LocalPersonalAdminAgentService()

    result = service.create_plan(LocalPersonalAdminRequest(admin_goal=""))

    assert any("input is thin" in warning.lower() for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["nextActions"]


def test_local_personal_admin_output_includes_document_deadline_form_appointment_records_submission_and_follow_up_sections():
    service = LocalPersonalAdminAgentService()

    result = service.create_plan(
        LocalPersonalAdminRequest(
            admin_goal="Prepare a renewal packet.",
            document_types=["Renewal form", "ID checklist"],
            deadlines=["Due next month"],
            requirements=["Signature field", "Proof item"],
            current_status="Gathered forms.",
            people_or_offices_involved=["Local office"],
            desired_output_type="submission_readiness",
        )
    )

    assert result["documentChecklist"]
    assert result["deadlinePlan"]
    assert result["formPrepPlan"]
    assert result["appointmentPrep"]
    assert result["recordsOrganization"]
    assert result["submissionReadiness"]
    assert result["followUpPlan"]


def test_local_personal_admin_output_does_not_claim_file_portal_submission_upload_signing_payment_scheduling_persistence_or_validation():
    service = LocalPersonalAdminAgentService()

    result = service.create_plan(
        LocalPersonalAdminRequest(
            admin_goal="Read my files, access the portal, submit the form, upload IDs, sign documents, pay the fee, schedule the appointment, and validate the government form.",
            desired_output_type="submission_readiness",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "file read complete",
        "portal accessed",
        "account accessed",
        "form submitted",
        "file uploaded",
        "document signed",
        "payment made",
        "appointment scheduled",
        "record persisted",
        "officially validated",
        "identity validated",
        "certified compliant",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no file reading" in output_text
    assert "no documents" in output_text
    assert "no legal, tax, immigration" in output_text
    assert "submission, upload, signature, payment, or scheduling must happen outside jarvis" in output_text


def test_local_personal_admin_official_inputs_include_official_or_professional_confirmation_limitations():
    service = LocalPersonalAdminAgentService()

    result = service.create_plan(
        LocalPersonalAdminRequest(
            admin_goal="Prepare an official immigration, tax, school, loan, government, compliance, and identity form checklist.",
            desired_output_type="form_prep_plan",
        )
    )

    assert any("official or professional confirmation" in warning for warning in result["warnings"])
    assert any("official source, or qualified professional" in limitation for limitation in result["limitations"])
    assert any("qualified professional" in action for action in result["nextActions"])


def test_local_personal_admin_safety_flags_disable_connectors_accounts_files_portals_sending_scheduling_uploads_submissions_payments_persistence_mutation_and_certification():
    service = LocalPersonalAdminAgentService()

    result = service.create_plan(LocalPersonalAdminRequest(admin_goal="Prepare a form checklist."))
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
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["cloudDriveAccess"] is False
    assert safety["emailSending"] is False
    assert safety["calendarAccess"] is False
    assert safety["taskPersistence"] is False
    assert safety["portalAccess"] is False
    assert safety["formSubmission"] is False
    assert safety["uploadActions"] is False
    assert safety["signatureActions"] is False
    assert safety["paymentActions"] is False
    assert safety["dbWrites"] is False
    assert safety["shellExecution"] is False
    assert safety["mutation"] is False
    assert safety["legalValidation"] is False
    assert safety["taxValidation"] is False
    assert safety["immigrationValidation"] is False
    assert safety["governmentValidation"] is False
    assert safety["schoolValidation"] is False
    assert safety["loanValidation"] is False
    assert safety["identityValidation"] is False
    assert safety["certificationClaims"] is False


def test_local_personal_admin_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_personal_admin_agent").local_personal_admin_agent).lower()
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


def test_local_personal_admin_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalPersonalAdminInput.model_validate(
            {
                "adminGoal": "Prepare paperwork.",
                "portalPassword": "not allowed",
            }
        )


def test_local_personal_admin_requires_admin_goal_in_endpoint_input():
    with pytest.raises(ValidationError):
        app_module.LocalPersonalAdminInput.model_validate({"profileName": "Missing goal"})


def test_local_personal_admin_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/personal-admin/local-plan")
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
