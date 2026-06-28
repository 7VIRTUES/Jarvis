from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_legal_immigration_official_matters"
STATUS = "local_only"
MODE = "response_only_user_provided_legal_immigration_official_planning"
SUPPORTED_OUTPUT_TYPES = (
    "document_checklist",
    "appointment_prep",
    "question_list",
    "deadline_tracker",
    "plain_language_summary",
    "official_task_plan",
    "form_prep_outline",
    "call_script",
    "email_draft_outline",
    "risk_flags",
    "comparison",
    "checklist",
    "summary",
)


@dataclass(frozen=True)
class LocalLegalImmigrationOfficialRequest:
    request: str = ""
    prompt_text: str = ""
    output_type: str = "summary"
    matter_type: str = ""
    jurisdiction_or_country_if_user_provided: str = ""
    current_status: str = ""
    document_list: list[str] = field(default_factory=list)
    deadlines_or_dates: list[str] = field(default_factory=list)
    office_or_agency_name_if_user_provided: str = ""
    user_questions: list[str] = field(default_factory=list)
    desired_outcome: str = ""
    risk_level_or_urgency: str = ""
    constraints_or_notes: str = ""


class LocalLegalImmigrationOfficialAgentService:
    def create_plan(self, request: LocalLegalImmigrationOfficialRequest) -> dict[str, Any]:
        request_text = _clean_text(request.request or request.prompt_text)
        output_type = _normalize_output_type(request.output_type)
        matter_type = _clean_text(request.matter_type) or "official matter"
        jurisdiction = _clean_text(request.jurisdiction_or_country_if_user_provided)
        current_status = _clean_text(request.current_status)
        documents = _clean_list(request.document_list)
        deadlines = _clean_list(request.deadlines_or_dates)
        agency = _clean_text(request.office_or_agency_name_if_user_provided)
        questions = _clean_list(request.user_questions)
        desired_outcome = _clean_text(request.desired_outcome)
        urgency = _clean_text(request.risk_level_or_urgency)
        constraints = _clean_text(request.constraints_or_notes)
        combined_text = " ".join(
            [
                request_text,
                matter_type,
                jurisdiction,
                current_status,
                " ".join(documents),
                " ".join(deadlines),
                agency,
                " ".join(questions),
                desired_outcome,
                urgency,
                constraints,
            ]
        )
        urgent_flags = _risk_flags(combined_text)
        thin_input = not any([request_text, jurisdiction, current_status, documents, deadlines, agency, questions, desired_outcome, urgency, constraints])

        return {
            "agent_id": AGENT_ID,
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": _title(output_type, matter_type),
            "summary": _summary(output_type, matter_type, current_status, thin_input),
            "assumptions": _assumptions(matter_type, jurisdiction, agency, thin_input),
            "non_legal_information": _non_legal_information(matter_type, current_status, desired_outcome),
            "recommended_plan": _recommended_plan(output_type, matter_type, documents, deadlines, questions, urgency),
            "document_checklist": _document_checklist(documents, matter_type),
            "questions_to_ask": _questions_to_ask(questions, matter_type, agency, urgent_flags),
            "deadlines_or_timeline": _deadlines_or_timeline(deadlines, urgency),
            "risk_flags": urgent_flags or ["No urgent legal or official risk flags were identified from the user-provided text; this is not a legal conclusion."],
            "draft_outline": _draft_outline(output_type, matter_type, current_status, desired_outcome),
            "limitations": _limitations(thin_input, bool(urgent_flags)),
            "professional_help_reminder": _professional_help_reminder(bool(urgent_flags)),
            "follow_up_questions": _follow_up_questions(jurisdiction, current_status, documents, deadlines, agency, questions, desired_outcome, urgency),
            "output_type": output_type,
            "safety": local_legal_immigration_official_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_legal_immigration_official_dashboard_summary()


def local_legal_immigration_official_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Legal / Immigration / Official Matters Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/legal-immigration-official/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "governmentPortalAccess": False,
        "immigrationAccountAccess": False,
        "schoolPortalAccess": False,
        "courtSystemAccess": False,
        "legalDatabaseAccess": False,
        "emailAccess": False,
        "calendarAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "paymentAccess": False,
        "mapAccess": False,
        "locationAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "formSubmission": False,
        "applicationFiling": False,
        "documentSigning": False,
        "feePayment": False,
        "appointmentBooking": False,
        "emailSending": False,
        "agencyContact": False,
        "legalAdvice": False,
        "immigrationAdvice": False,
        "attorneyReview": False,
        "eligibilityCertainty": False,
        "deadlineCertainty": False,
        "visaApprovalPrediction": False,
        "officialCompliance": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["organizational/general information only based on user-provided official-matter notes"],
    }


def local_legal_immigration_official_safety() -> dict[str, bool]:
    return {key: value for key, value in local_legal_immigration_official_dashboard_summary().items() if isinstance(value, bool)}


def _normalize_output_type(value: str) -> str:
    normalized = (value or "summary").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "summary"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 12) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _risk_flags(text: str) -> list[str]:
    lowered = text.lower()
    checks = {
        "Deportation/removal notice mentioned; seek qualified help promptly.": ("deportation", "removal notice", "removed from"),
        "Court date or hearing mentioned; confirm requirements with qualified help or the relevant official source.": ("court date", "hearing", "court"),
        "Arrest or detention mentioned; use qualified legal help promptly.": ("arrest", "detention", "detained"),
        "Missed or urgent deadline mentioned; do not rely on this response for deadline certainty.": ("missed deadline", "past due", "deadline tomorrow", "urgent deadline"),
        "Benefit termination or official notice mentioned; review with qualified help or the relevant agency.": ("termination", "benefit", "official notice"),
        "Identity, document, or fraud concern mentioned; use qualified help and official channels.": ("fraud", "fake document", "identity theft", "document fraud"),
        "Domestic violence, threats, or safety concern mentioned; seek qualified local help or emergency services where appropriate.": ("domestic violence", "threat", "threats", "unsafe"),
    }
    return [message for message, terms in checks.items() if any(term in lowered for term in terms)]


def _title(output_type: str, matter_type: str) -> str:
    return f"{output_type.replace('_', ' ').title()}: {matter_type[:80]}"


def _summary(output_type: str, matter_type: str, current_status: str, thin_input: bool) -> str:
    if thin_input:
        return "Local manual official-matter planning scaffold; add status, documents, dates, office, questions, and constraints for more specific organization."
    status_note = f" Current status: {current_status}." if current_status else ""
    return f"Manual {output_type.replace('_', ' ')} for {matter_type}.{status_note} No portal, legal database, email, calendar, file, payment, map, or external service was accessed."


def _assumptions(matter_type: str, jurisdiction: str, agency: str, thin_input: bool) -> list[str]:
    assumptions = [f"Uses only user-provided notes about: {matter_type}."]
    if jurisdiction:
        assumptions.append(f"Jurisdiction/country was provided by the user: {jurisdiction}.")
    if agency:
        assumptions.append(f"Office or agency was provided by the user: {agency}.")
    if thin_input:
        assumptions.append("Input is thin; no official records, portals, files, legal databases, or agency sources were checked.")
    return assumptions


def _non_legal_information(matter_type: str, current_status: str, desired_outcome: str) -> list[str]:
    info = [
        "Organize the user-provided facts, documents, dates, and questions before taking action outside Jarvis.",
        "Treat this as general organizational information, not legal advice or immigration advice.",
    ]
    if current_status:
        info.append(f"User-provided status to restate: {current_status}.")
    if desired_outcome:
        info.append(f"Desired outcome to discuss with qualified help or the relevant office: {desired_outcome}.")
    info.append(f"Matter type label supplied or inferred locally: {matter_type}.")
    return info


def _recommended_plan(output_type: str, matter_type: str, documents: list[str], deadlines: list[str], questions: list[str], urgency: str) -> list[str]:
    plan = [f"Create a manual folder or list for {matter_type} using only user-provided information."]
    if documents:
        plan.append(f"Start by checking document availability: {documents[0]}.")
    if deadlines:
        plan.append(f"Flag date for qualified confirmation: {deadlines[0]}.")
    if questions:
        plan.append(f"Bring user question forward: {questions[0]}.")
    if urgency:
        plan.append(f"Urgency note: {urgency}.")
    if output_type in {"call_script", "email_draft_outline"}:
        plan.append("Draft wording only; do not send, call, book, submit, sign, or pay from Jarvis.")
    else:
        plan.append("Review with a qualified attorney, accredited immigration representative, school official, or relevant agency for high-stakes matters.")
    return plan[:6]


def _document_checklist(documents: list[str], matter_type: str) -> list[str]:
    checklist = [f"User-provided document: {item}." for item in documents[:8]]
    if not checklist:
        checklist.append(f"List all documents mentioned in the {matter_type} summary before relying on the plan.")
    checklist.extend(["Mark originals vs copies manually.", "Confirm official requirements with the relevant source or qualified professional."])
    return checklist


def _questions_to_ask(questions: list[str], matter_type: str, agency: str, urgent_flags: list[str]) -> list[str]:
    result = questions[:]
    if agency:
        result.append(f"What does {agency} need from me next, according to its official process?")
    result.append(f"What are the risks, deadlines, and required next steps for this {matter_type}?")
    if urgent_flags:
        result.append("What qualified help should I contact promptly because risk flags are present?")
    return result[:8]


def _deadlines_or_timeline(deadlines: list[str], urgency: str) -> list[str]:
    timeline = [f"User-provided date/deadline needing confirmation: {item}." for item in deadlines[:6]]
    if urgency:
        timeline.append(f"Urgency note: {urgency}.")
    timeline.append("No deadline certainty is provided; verify deadlines with official sources or qualified professionals.")
    return timeline


def _draft_outline(output_type: str, matter_type: str, current_status: str, desired_outcome: str) -> list[str]:
    if output_type not in {"call_script", "email_draft_outline", "question_list", "appointment_prep"}:
        return ["No official message, call, filing, appointment, or submission was created."]
    return [
        f"Opening: I am asking about my {matter_type}.",
        f"Status summary: {current_status or 'state current status briefly'}.",
        f"Goal: {desired_outcome or 'ask what next step is required'}.",
        "Questions: ask for required documents, deadlines, fees, and where to verify instructions.",
        "Closing: confirm that the user will review through official or qualified channels before acting.",
    ]


def _limitations(thin_input: bool, urgent: bool) -> list[str]:
    limitations = [
        "This is organizational/general information only, based only on user-provided official-matter notes.",
        "No government portal, immigration account, school portal, court system, legal database, email, calendar, file, payment system, map, location, connector, or external service was accessed or changed.",
        "No form submission, application filing, document signing, fee payment, appointment booking, email sending, agency contact, persistent record, or official action was created.",
        "No legal advice, immigration advice, attorney review, eligibility certainty, deadline certainty, visa approval prediction, government acceptance, official compliance, or certification claim is provided.",
        "Consult a qualified attorney, accredited immigration representative, school official, or relevant agency for high-stakes matters.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add current status, document list, dates, agency name, questions, desired outcome, and urgency.")
    if urgent:
        limitations.append("Urgent legal or official risk flags require qualified help promptly.")
    return limitations


def _professional_help_reminder(urgent: bool) -> str:
    base = "Consult a qualified attorney, accredited immigration representative, school official, or relevant agency before relying on this for high-stakes official matters."
    if urgent:
        return f"{base} Risk flags are present, so qualified help may be time-sensitive."
    return base


def _follow_up_questions(
    jurisdiction: str,
    current_status: str,
    documents: list[str],
    deadlines: list[str],
    agency: str,
    questions: list[str],
    desired_outcome: str,
    urgency: str,
) -> list[str]:
    result = []
    if not jurisdiction:
        result.append("What jurisdiction or country did the user provide, if any?")
    if not current_status:
        result.append("What is the current status?")
    if not documents:
        result.append("What documents are already available?")
    if not deadlines:
        result.append("What deadlines or dates are mentioned?")
    if not agency:
        result.append("What office or agency is involved, if known?")
    if not questions:
        result.append("What questions should be brought to qualified help or the agency?")
    if not desired_outcome:
        result.append("What outcome is the user trying to prepare for?")
    if not urgency:
        result.append("Is there any urgency or official notice?")
    return result[:8]
