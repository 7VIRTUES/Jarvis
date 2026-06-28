from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_personal_admin_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_personal_admin_planning"
SUPPORTED_OUTPUT_TYPES = (
    "admin_brief",
    "document_checklist",
    "deadline_plan",
    "form_prep_plan",
    "appointment_prep",
    "records_organization",
    "submission_readiness",
    "follow_up_plan",
)


@dataclass(frozen=True)
class LocalPersonalAdminRequest:
    admin_goal: str
    profile_name: str = ""
    document_types: list[str] = field(default_factory=list)
    deadlines: list[str] = field(default_factory=list)
    requirements: list[str] = field(default_factory=list)
    current_status: str = ""
    constraints: list[str] = field(default_factory=list)
    people_or_offices_involved: list[str] = field(default_factory=list)
    notes: str = ""
    desired_output_type: str = "admin_brief"


class LocalPersonalAdminAgentService:
    def create_plan(self, request: LocalPersonalAdminRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local personal admin profile"
        admin_goal = _clean_text(request.admin_goal)
        document_types = _clean_list(request.document_types)
        deadlines = _clean_list(request.deadlines)
        requirements = _clean_list(request.requirements, limit=12)
        current_status = _clean_text(request.current_status)
        constraints = _clean_list(request.constraints)
        people_or_offices = _clean_list(request.people_or_offices_involved)
        notes = _clean_text(request.notes)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            admin_goal,
            document_types,
            deadlines,
            requirements,
            current_status,
            constraints,
            people_or_offices,
            notes,
        )
        official_context = _official_context(admin_goal, document_types, requirements, current_status, constraints, people_or_offices, notes)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "adminGoal": admin_goal,
            "desiredOutputType": desired_output_type,
            "adminFocus": _admin_focus(admin_goal, document_types, desired_output_type, thin_input),
            "statusSummary": _status_summary(current_status, notes, people_or_offices, thin_input),
            "documentChecklist": _document_checklist(document_types, requirements, constraints),
            "deadlinePlan": _deadline_plan(deadlines, requirements, current_status),
            "formPrepPlan": _form_prep_plan(admin_goal, document_types, requirements, notes, official_context),
            "appointmentPrep": _appointment_prep(people_or_offices, requirements, deadlines, constraints),
            "recordsOrganization": _records_organization(document_types, requirements, constraints),
            "submissionReadiness": _submission_readiness(admin_goal, document_types, requirements, deadlines, constraints, official_context),
            "followUpPlan": _follow_up_plan(people_or_offices, deadlines, requirements, current_status),
            "nextActions": _next_actions(desired_output_type, thin_input, official_context),
            "openQuestions": _open_questions(
                admin_goal,
                document_types,
                deadlines,
                requirements,
                current_status,
                constraints,
                people_or_offices,
                notes,
            ),
            "warnings": _warnings(thin_input, official_context),
            "limitations": _limitations(thin_input, official_context),
            "safety": local_personal_admin_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_personal_admin_dashboard_summary()


def local_personal_admin_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Personal Admin / Documents Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/personal-admin/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "OAuth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "fileReads": False,
        "fileWrites": False,
        "cloudDriveAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "taskPersistence": False,
        "portalAccess": False,
        "formSubmission": False,
        "uploadActions": False,
        "signatureActions": False,
        "paymentActions": False,
        "dbWrites": False,
        "shellExecution": False,
        "mutation": False,
        "legalValidation": False,
        "taxValidation": False,
        "immigrationValidation": False,
        "governmentValidation": False,
        "schoolValidation": False,
        "loanValidation": False,
        "identityValidation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided personal admin and document-prep notes"],
    }


def local_personal_admin_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "OAuth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "fileReads": False,
        "fileWrites": False,
        "cloudDriveAccess": False,
        "emailSending": False,
        "calendarAccess": False,
        "taskPersistence": False,
        "portalAccess": False,
        "formSubmission": False,
        "uploadActions": False,
        "signatureActions": False,
        "paymentActions": False,
        "dbWrites": False,
        "shellExecution": False,
        "mutation": False,
        "legalValidation": False,
        "taxValidation": False,
        "immigrationValidation": False,
        "governmentValidation": False,
        "schoolValidation": False,
        "loanValidation": False,
        "identityValidation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "admin_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "admin_brief"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 10) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _thin_input(
    admin_goal: str,
    document_types: list[str],
    deadlines: list[str],
    requirements: list[str],
    current_status: str,
    constraints: list[str],
    people_or_offices: list[str],
    notes: str,
) -> bool:
    return not any([admin_goal, document_types, deadlines, requirements, current_status, constraints, people_or_offices, notes])


def _official_context(
    admin_goal: str,
    document_types: list[str],
    requirements: list[str],
    current_status: str,
    constraints: list[str],
    people_or_offices: list[str],
    notes: str,
) -> bool:
    text = " ".join(
        [
            admin_goal,
            " ".join(document_types),
            " ".join(requirements),
            current_status,
            " ".join(constraints),
            " ".join(people_or_offices),
            notes,
        ]
    ).lower()
    terms = (
        "legal",
        "tax",
        "immigration",
        "visa",
        "loan",
        "government",
        "irs",
        "court",
        "compliance",
        "identity",
        "school decision",
        "financial aid",
        "official form",
        "deadline penalty",
    )
    return any(term in text for term in terms)


def _admin_focus(admin_goal: str, document_types: list[str], desired_output_type: str, thin_input: bool) -> list[str]:
    if thin_input:
        return [
            "Capture the admin goal, document types, deadlines, requirements, current status, offices involved, and constraints before relying on the plan.",
            "Keep the result as manual planning and checklist support because no documents, files, accounts, portals, email, calendars, or cloud drives are accessed.",
        ]
    focus = [f"Primary admin goal: {admin_goal}.", f"Requested output shape: {desired_output_type}."]
    if document_types:
        focus.append("Document types from user input: " + "; ".join(document_types) + ".")
    focus.append("Use this as personal admin preparation, not legal, tax, immigration, school, loan, government, identity, or submission validation.")
    return focus


def _status_summary(current_status: str, notes: str, people_or_offices: list[str], thin_input: bool) -> list[str]:
    if thin_input:
        return ["Status summary is limited until the user provides current status, notes, and offices or people involved."]
    summary = []
    if current_status:
        summary.append(f"Current status from user input: {current_status}.")
    if people_or_offices:
        summary.append("People or offices involved: " + "; ".join(people_or_offices) + ".")
    if notes:
        summary.append(f"Notes from user input: {notes}.")
    if not summary:
        summary.append("Add current status and office context before using this as a readiness checklist.")
    return summary


def _document_checklist(document_types: list[str], requirements: list[str], constraints: list[str]) -> list[dict[str, str]]:
    docs = document_types or ["Document type to identify manually"]
    checklist: list[dict[str, str]] = []
    for doc in docs[:8]:
        checklist.append(
            {
                "documentType": doc,
                "manualItems": "; ".join(requirements) if requirements else "List required fields, signatures, IDs, proof, and supporting records from trusted instructions.",
                "reviewStep": "Check spelling, dates, names, addresses, amounts, eligibility notes, and missing attachments manually.",
                "boundary": "No document, file, ID, PDF, portal, email, calendar, or cloud-drive content is read by Jarvis.",
            }
        )
    if constraints:
        checklist.append({"documentType": "Constraints", "manualItems": "; ".join(constraints), "reviewStep": "Confirm constraints against official instructions.", "boundary": "No official validation is claimed."})
    return checklist


def _deadline_plan(deadlines: list[str], requirements: list[str], current_status: str) -> list[str]:
    plan = [
        "Put every deadline on a manually maintained calendar or checklist outside Jarvis.",
        "Work backward from each due date: gather records, fill forms, review, confirm instructions, then submit manually.",
        "Leave extra time for signatures, office hours, mailing, payment processing, or follow-up where relevant.",
    ]
    if deadlines:
        plan.insert(0, "Deadlines from user input: " + "; ".join(deadlines) + ".")
    if requirements:
        plan.append("Requirement timing to check manually: " + "; ".join(requirements[:8]) + ".")
    if current_status:
        plan.append(f"Current status to account for: {current_status}.")
    return plan


def _form_prep_plan(admin_goal: str, document_types: list[str], requirements: list[str], notes: str, official_context: bool) -> list[str]:
    plan = [
        "Read the official instructions outside Jarvis and copy only the needed requirement notes into the request.",
        "Prepare a blank-field checklist before filling anything in.",
        "Mark any uncertain field for official or professional confirmation.",
        "Review the final form manually before any submission, upload, signature, or payment outside Jarvis.",
    ]
    if admin_goal:
        plan.insert(0, f"Form-prep goal: {admin_goal}.")
    if document_types:
        plan.append("Forms or records to prepare manually: " + "; ".join(document_types[:8]) + ".")
    if requirements:
        plan.append("User-provided requirements to organize: " + "; ".join(requirements[:8]) + ".")
    if notes:
        plan.append(f"Notes to preserve: {notes}.")
    if official_context:
        plan.append("Official, legal, tax, immigration, loan, school, government, compliance, identity, and submission details need official or professional confirmation.")
    return plan


def _appointment_prep(people_or_offices: list[str], requirements: list[str], deadlines: list[str], constraints: list[str]) -> list[str]:
    prep = [
        "Write the appointment purpose in one sentence.",
        "Bring manually gathered documents, IDs, questions, and reference numbers only after confirming official instructions outside Jarvis.",
        "Prepare three questions: what is missing, what happens next, and how to confirm receipt or status.",
        "Record answers manually after the appointment; Jarvis does not schedule, call, message, or persist notes.",
    ]
    if people_or_offices:
        prep.insert(0, "Offices or people to prepare for: " + "; ".join(people_or_offices) + ".")
    if requirements:
        prep.append("Items to ask about: " + "; ".join(requirements[:8]) + ".")
    if deadlines:
        prep.append("Deadlines to mention manually: " + "; ".join(deadlines) + ".")
    if constraints:
        prep.append("Constraints to raise: " + "; ".join(constraints) + ".")
    return prep


def _records_organization(document_types: list[str], requirements: list[str], constraints: list[str]) -> list[str]:
    organization = [
        "Group records by purpose, due date, office, and status using a manual folder or checklist outside Jarvis.",
        "Separate originals from copies and note where each original is kept.",
        "Track which items are pending, reviewed, signed, submitted outside Jarvis, or awaiting reply.",
        "Avoid storing sensitive personal data in Jarvis prompts unless it is necessary and user-chosen.",
    ]
    if document_types:
        organization.append("Suggested groups from user input: " + "; ".join(document_types[:8]) + ".")
    if requirements:
        organization.append("Requirement labels to consider: " + "; ".join(requirements[:8]) + ".")
    if constraints:
        organization.append("Organization constraints: " + "; ".join(constraints) + ".")
    return organization


def _submission_readiness(
    admin_goal: str,
    document_types: list[str],
    requirements: list[str],
    deadlines: list[str],
    constraints: list[str],
    official_context: bool,
) -> list[str]:
    readiness = [
        "All required fields appear accounted for in the user's manual checklist.",
        "Names, dates, contact details, amounts, signatures, attachments, and deadlines are reviewed manually.",
        "Any uncertain official requirement is flagged for the relevant office or professional before submission.",
        "Submission, upload, signature, payment, or scheduling must happen outside Jarvis.",
    ]
    if admin_goal:
        readiness.append(f"Readiness goal: {admin_goal}.")
    if document_types:
        readiness.append("Documents to review manually: " + "; ".join(document_types[:8]) + ".")
    if requirements:
        readiness.append("Requirements to confirm manually: " + "; ".join(requirements[:8]) + ".")
    if deadlines:
        readiness.append("Deadline check: " + "; ".join(deadlines) + ".")
    if constraints:
        readiness.append("Constraints check: " + "; ".join(constraints) + ".")
    if official_context:
        readiness.append("No legal, tax, immigration, school, loan, government, compliance, identity, or submission validation is provided.")
    return readiness


def _follow_up_plan(people_or_offices: list[str], deadlines: list[str], requirements: list[str], current_status: str) -> list[str]:
    plan = [
        "Write a short manual follow-up note with the purpose, date, reference number, and question.",
        "Confirm the correct office, channel, hours, and expected response time outside Jarvis.",
        "Track reply status manually; Jarvis does not send email, create tasks, schedule reminders, or persist records.",
    ]
    if people_or_offices:
        plan.insert(0, "Follow-up targets from user input: " + "; ".join(people_or_offices) + ".")
    if deadlines:
        plan.append("Follow-up timing should respect: " + "; ".join(deadlines) + ".")
    if requirements:
        plan.append("Follow-up questions can mention: " + "; ".join(requirements[:8]) + ".")
    if current_status:
        plan.append(f"Current status to reference: {current_status}.")
    return plan


def _next_actions(desired_output_type: str, thin_input: bool, official_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and mark every item that needs official confirmation.",
        "Add missing manual notes for document types, deadlines, requirements, current status, constraints, offices, and appointment context.",
        "Confirm official form instructions, submission rules, fees, signatures, deadlines, and eligibility outside Jarvis.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual admin context before using this for school forms, loan paperwork, renewals, applications, or deadline planning.")
    if official_context:
        actions.append("Ask the relevant office, official source, or qualified professional to confirm legal, tax, immigration, school, loan, government, identity, compliance, and submission decisions.")
    return actions


def _open_questions(
    admin_goal: str,
    document_types: list[str],
    deadlines: list[str],
    requirements: list[str],
    current_status: str,
    constraints: list[str],
    people_or_offices: list[str],
    notes: str,
) -> list[str]:
    questions = []
    if not admin_goal:
        questions.append("What personal admin or document-prep goal should this support?")
    if not document_types:
        questions.append("Which forms, IDs, records, applications, renewals, or paperwork types are involved?")
    if not deadlines:
        questions.append("What deadlines, appointment dates, renewal windows, or response dates matter?")
    if not requirements:
        questions.append("What user-provided requirements, proof items, signatures, fees, or fields need tracking?")
    if not current_status:
        questions.append("What has already been gathered, filled, reviewed, sent outside Jarvis, or left incomplete?")
    if not constraints:
        questions.append("What constraints apply: time, missing records, office hours, eligibility, privacy, cost, or transportation?")
    if not people_or_offices:
        questions.append("Which people, offices, schools, lenders, agencies, clinics, or departments are involved?")
    if not notes:
        questions.append("What extra notes should be preserved from official instructions or prior conversations?")
    return questions[:8]


def _warnings(thin_input: bool, official_context: bool) -> list[str]:
    warnings = [
        "No documents, files, IDs, PDFs, email, calendars, portals, accounts, cloud drives, school systems, loan systems, government sites, or external services are accessed.",
        "The response does not submit forms, send emails, schedule appointments, create reminders, upload files, sign documents, make payments, persist records, mutate files, or write to databases.",
        "No legal, tax, immigration, school, loan, government, compliance, identity, submission, production, security, or certification validation is claimed.",
    ]
    if thin_input:
        warnings.insert(0, "The personal admin input is thin; results are a planning scaffold rather than a specific readiness review.")
    if official_context:
        warnings.append("Official forms, legal, tax, immigration, loan, school, government, compliance, identity, and submission decisions need official or professional confirmation.")
    return warnings


def _limitations(thin_input: bool, official_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided personal admin goal, document type, deadline, requirement, status, constraint, office, and note inputs.",
        "No file reading, document reading, ID reading, PDF reading, email access, calendar access, portal access, account access, cloud-drive access, browsing, scraping, connector use, submission, upload, signing, payment, scheduling, task creation, persistence, shell execution, or mutation behavior.",
        "No legal validation, tax validation, immigration validation, school validation, loan validation, government validation, compliance validation, identity validation, official submission validation, production readiness, security certification, or certification claim.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete document types, deadlines, requirements, status, offices, and constraints.")
    if official_context:
        limitations.append("Official forms and high-stakes personal admin decisions should be confirmed with the relevant office, official source, or qualified professional.")
    return limitations
