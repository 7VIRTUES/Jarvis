from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_business_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_business_planning"
SUPPORTED_OUTPUT_TYPES = (
    "business_brief",
    "lean_canvas",
    "swot",
    "offer_plan",
    "marketing_plan",
    "operations_plan",
    "risk_review",
    "launch_checklist",
)


@dataclass(frozen=True)
class LocalBusinessRequest:
    business_idea: str
    business_name: str = ""
    target_customer: str = ""
    problem: str = ""
    offer: str = ""
    pricing_notes: str = ""
    operations_notes: str = ""
    marketing_notes: str = ""
    constraints: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)
    desired_output_type: str = "business_brief"


class LocalBusinessAgentService:
    def create_brief(self, request: LocalBusinessRequest) -> dict[str, Any]:
        business_name = _clean_text(request.business_name) or "Untitled local business concept"
        business_idea = _clean_text(request.business_idea) or "Untitled local business idea"
        target_customer = _clean_text(request.target_customer)
        problem = _clean_text(request.problem)
        offer = _clean_text(request.offer)
        pricing_notes = _clean_text(request.pricing_notes)
        operations_notes = _clean_text(request.operations_notes)
        marketing_notes = _clean_text(request.marketing_notes)
        constraints = _clean_list(request.constraints)
        resources = _clean_list(request.resources)
        risks = _clean_list(request.risks)
        goals = _clean_list(request.goals)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            target_customer,
            problem,
            offer,
            pricing_notes,
            operations_notes,
            marketing_notes,
            constraints,
            resources,
            risks,
            goals,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "businessName": business_name,
            "businessIdea": business_idea,
            "desiredOutputType": desired_output_type,
            "businessFocus": _business_focus(business_name, business_idea, desired_output_type, goals, thin_input),
            "customerAssumptions": _customer_assumptions(target_customer, goals, thin_input),
            "problemSummary": _problem_summary(problem, target_customer, thin_input),
            "offerSummary": _offer_summary(offer, business_idea, target_customer),
            "valueProposition": _value_proposition(offer, problem, target_customer, business_idea),
            "revenueNotes": _revenue_notes(pricing_notes, constraints),
            "operationsNotes": _operations_summary(operations_notes, resources, constraints),
            "marketingAngles": _marketing_angles(marketing_notes, target_customer, problem, offer),
            "swot": _swot(business_idea, offer, resources, constraints, risks, goals, thin_input),
            "leanCanvas": _lean_canvas(
                business_idea,
                target_customer,
                problem,
                offer,
                pricing_notes,
                operations_notes,
                marketing_notes,
                resources,
                goals,
                thin_input,
            ),
            "launchChecklist": _launch_checklist(desired_output_type, goals, constraints, resources, risks, thin_input),
            "risks": _risks(risks, constraints, thin_input),
            "nextActions": _next_actions(desired_output_type, thin_input),
            "openQuestions": _open_questions(target_customer, problem, offer, pricing_notes, operations_notes, marketing_notes),
            "warnings": _warnings(thin_input),
            "limitations": _limitations(thin_input),
            "safety": local_business_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_business_dashboard_summary()


def local_business_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Business Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/business/local-brief",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "financeConnectorAccess": False,
        "paymentActions": False,
        "purchases": False,
        "emailSending": False,
        "publicPosting": False,
        "crmAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "professionalAdviceValidation": False,
        "complianceCertification": False,
        "limitations": ["based only on user-provided business planning inputs"],
    }


def local_business_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "financeConnectorAccess": False,
        "paymentActions": False,
        "purchases": False,
        "emailSending": False,
        "publicPosting": False,
        "crmAccess": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "professionalAdviceValidation": False,
        "complianceCertification": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "business_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "business_brief"


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
    target_customer: str,
    problem: str,
    offer: str,
    pricing_notes: str,
    operations_notes: str,
    marketing_notes: str,
    constraints: list[str],
    resources: list[str],
    risks: list[str],
    goals: list[str],
) -> bool:
    return not any(
        [
            target_customer,
            problem,
            offer,
            pricing_notes,
            operations_notes,
            marketing_notes,
            constraints,
            resources,
            risks,
            goals,
        ]
    )


def _business_focus(business_name: str, business_idea: str, desired_output_type: str, goals: list[str], thin_input: bool) -> str:
    if thin_input:
        return f"Clarify {business_name} from the initial idea before treating this as a validated business plan."
    if desired_output_type == "lean_canvas":
        return f"Organize {business_name} into a lean-canvas view using only the supplied business idea."
    if desired_output_type == "swot":
        return f"Pressure-test {business_name} with a local SWOT view from user-provided inputs."
    if desired_output_type == "offer_plan":
        return f"Turn the supplied idea for {business_name} into a clearer offer and value proposition."
    if desired_output_type == "marketing_plan":
        return f"Identify manual marketing angles for {business_name} without creating posts or contacting accounts."
    if desired_output_type == "operations_plan":
        return f"Outline manual operations considerations for {business_name} without creating files, tasks, or records."
    if desired_output_type == "risk_review":
        return f"Review visible business risks for {business_name} from the user-provided notes."
    if desired_output_type == "launch_checklist":
        return f"Create a manual launch-readiness checklist for {business_name} without scheduling or persistence."
    if goals:
        return f"Shape {business_name} around the first stated goal: {goals[0]}."
    return f"Summarize {business_name} as a local response-only business brief for: {business_idea}."


def _customer_assumptions(target_customer: str, goals: list[str], thin_input: bool) -> list[str]:
    assumptions = ["Customer assumptions are based only on the request body."]
    if target_customer:
        assumptions.append(f"Primary customer described by the user: {target_customer}.")
    else:
        assumptions.append("Target customer is not yet specific enough for confident positioning.")
    if goals:
        assumptions.append(f"Goals are treated as desired outcomes, starting with: {goals[0]}.")
    if thin_input:
        assumptions.append("The concept needs more customer, problem, offer, pricing, operations, and risk detail.")
    return assumptions


def _problem_summary(problem: str, target_customer: str, thin_input: bool) -> str:
    if problem and target_customer:
        return f"{target_customer} appear to need relief from: {problem}."
    if problem:
        return f"The stated problem is: {problem}."
    if target_customer:
        return f"The target customer is named, but the problem still needs to be made explicit for {target_customer}."
    if thin_input:
        return "The business problem is not yet defined beyond the initial idea."
    return "No explicit problem was provided."


def _offer_summary(offer: str, business_idea: str, target_customer: str) -> str:
    if offer and target_customer:
        return f"Offer described for {target_customer}: {offer}."
    if offer:
        return f"Offer described by the user: {offer}."
    return f"Initial offer direction inferred from the business idea only: {business_idea}."


def _value_proposition(offer: str, problem: str, target_customer: str, business_idea: str) -> str:
    customer = target_customer or "the intended customer"
    if offer and problem:
        return f"Help {customer} address {problem} through {offer}."
    if offer:
        return f"Help {customer} with a clearer, easier-to-understand version of {offer}."
    return f"Help {customer} by turning the idea into a concrete promise: {business_idea}."


def _revenue_notes(pricing_notes: str, constraints: list[str]) -> list[str]:
    notes = []
    if pricing_notes:
        notes.append(f"User-provided pricing note: {pricing_notes}.")
    else:
        notes.append("Pricing is not specified; treat revenue assumptions as unknown.")
    if constraints:
        notes.append(f"Check pricing manually against constraint: {constraints[0]}.")
    notes.append("No profitability, demand, market-size, tax, accounting, or revenue outcome is validated.")
    return notes


def _operations_summary(operations_notes: str, resources: list[str], constraints: list[str]) -> list[str]:
    notes = []
    if operations_notes:
        notes.append(f"User-provided operations note: {operations_notes}.")
    if resources:
        notes.append(f"Available resource to consider manually: {resources[0]}.")
    if constraints:
        notes.append(f"Operational boundary to respect: {constraints[0]}.")
    if not notes:
        notes.append("Operations are not specified; define delivery steps, capacity, review points, and manual ownership.")
    notes.append("No tasks, calendar events, order records, invoices, files, or database entries were created.")
    return notes


def _marketing_angles(marketing_notes: str, target_customer: str, problem: str, offer: str) -> list[str]:
    angles = []
    if marketing_notes:
        angles.append(f"Use the supplied marketing note as a positioning seed: {marketing_notes}.")
    if target_customer:
        angles.append(f"Speak directly to the described customer: {target_customer}.")
    if problem:
        angles.append(f"Frame the message around the stated problem: {problem}.")
    if offer:
        angles.append(f"Keep the offer easy to understand: {offer}.")
    if not angles:
        angles.append("Clarify target customer, problem, and offer before drafting marketing angles.")
    angles.append("No posts, ads, emails, messages, account actions, or external campaigns were created.")
    return angles[:5]


def _swot(
    business_idea: str,
    offer: str,
    resources: list[str],
    constraints: list[str],
    risks: list[str],
    goals: list[str],
    thin_input: bool,
) -> dict[str, list[str]]:
    return {
        "strengths": resources[:3] or [f"The idea is available for manual shaping: {business_idea}."],
        "weaknesses": constraints[:3] or ["Key constraints are not yet specified."],
        "opportunities": goals[:3] or [f"Clarify the offer and test interest manually: {offer or business_idea}."],
        "threats": risks[:3] or [_thin_risk_note(thin_input)],
    }


def _lean_canvas(
    business_idea: str,
    target_customer: str,
    problem: str,
    offer: str,
    pricing_notes: str,
    operations_notes: str,
    marketing_notes: str,
    resources: list[str],
    goals: list[str],
    thin_input: bool,
) -> dict[str, Any]:
    return {
        "problem": problem or "Problem not yet specified.",
        "customerSegments": [target_customer] if target_customer else ["Customer segment not yet specified."],
        "uniqueValueProposition": _value_proposition(offer, problem, target_customer, business_idea),
        "solution": offer or business_idea,
        "channels": [marketing_notes] if marketing_notes else ["Manual channel assumptions not yet specified."],
        "revenueStreams": [pricing_notes] if pricing_notes else ["Revenue stream not yet specified."],
        "costConsiderations": [operations_notes] if operations_notes else ["Cost and delivery assumptions need manual review."],
        "keyMetrics": goals[:3] or ["Define one manual metric before treating progress as meaningful."],
        "unfairAdvantageOrGap": resources[:3] if resources else [_thin_gap_note(thin_input)],
    }


def _launch_checklist(
    desired_output_type: str,
    goals: list[str],
    constraints: list[str],
    resources: list[str],
    risks: list[str],
    thin_input: bool,
) -> list[str]:
    checklist = [
        "Restate the target customer, problem, offer, and manual success criteria.",
        "Confirm the offer can be explained without external claims or unsupported guarantees.",
        "Review pricing, costs, capacity, and compliance questions with qualified humans where needed.",
    ]
    if goals:
        checklist.append(f"Check the first goal manually: {goals[0]}.")
    if constraints:
        checklist.append(f"Check the first constraint manually: {constraints[0]}.")
    if resources:
        checklist.append(f"Confirm the first resource is actually available: {resources[0]}.")
    if risks:
        checklist.append(f"Decide how to reduce or monitor the first stated risk: {risks[0]}.")
    if desired_output_type == "launch_checklist" or thin_input:
        checklist.append("Add missing customer, problem, offer, operations, pricing, marketing, and risk details.")
    checklist.append("Do not create tasks, calendar events, emails, posts, purchases, invoices, files, or records from this response.")
    return checklist[:8]


def _risks(risks: list[str], constraints: list[str], thin_input: bool) -> list[str]:
    output = []
    output.extend(risks[:4])
    if constraints:
        output.append(f"Constraint may limit feasibility: {constraints[0]}.")
    if thin_input:
        output.append("Thin input can hide demand, profitability, delivery, compliance, tax, accounting, or customer-fit risks.")
    if not output:
        output.append("No specific risk was provided, so risks remain unknown and require manual review.")
    output.append("No legal, tax, financial, accounting, compliance, investment, market, demand, revenue, or profitability outcome is validated.")
    return output


def _next_actions(desired_output_type: str, thin_input: bool) -> list[str]:
    if thin_input:
        return [
            "Add the target customer, problem, offer, pricing notes, operations notes, marketing notes, risks, resources, and constraints.",
            "Use the response as a prompt for manual business planning only.",
        ]
    if desired_output_type == "lean_canvas":
        return ["Review each lean-canvas field manually.", "Fill any unknown canvas field before acting."]
    if desired_output_type == "swot":
        return ["Manually review each SWOT item for evidence and uncertainty.", "Choose one risk or gap to clarify next."]
    if desired_output_type == "offer_plan":
        return ["Rewrite the offer in one sentence.", "Check whether the offer matches the stated customer problem."]
    if desired_output_type == "marketing_plan":
        return ["Draft manual positioning notes outside the agent.", "Review claims for support before posting or sending anything."]
    if desired_output_type == "operations_plan":
        return ["Map the delivery steps manually.", "Check capacity, costs, ownership, and review points."]
    if desired_output_type == "risk_review":
        return ["Pick the highest-risk assumption.", "Decide what human review or manual evidence is needed."]
    if desired_output_type == "launch_checklist":
        return ["Work the checklist manually.", "Pause on any legal, tax, finance, accounting, or compliance uncertainty."]
    return ["Clarify the biggest unknown.", "Manually review the brief before using it for any business action."]


def _open_questions(
    target_customer: str,
    problem: str,
    offer: str,
    pricing_notes: str,
    operations_notes: str,
    marketing_notes: str,
) -> list[str]:
    questions = []
    if not target_customer:
        questions.append("Who is the specific target customer?")
    if not problem:
        questions.append("What concrete problem does the business solve?")
    if not offer:
        questions.append("What exactly is being offered?")
    if not pricing_notes:
        questions.append("What pricing or revenue assumption should be reviewed manually?")
    if not operations_notes:
        questions.append("How will the offer be delivered without overextending capacity?")
    if not marketing_notes:
        questions.append("What manual channel or positioning angle should be considered first?")
    return questions or ["What evidence would change this business direction?"]


def _warnings(thin_input: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Business planning input is thin; output is a provisional local planning scaffold.")
    warnings.append("This response does not validate demand, revenue, profitability, market size, compliance, taxes, or investment outcomes.")
    return warnings


def _limitations(thin_input: bool) -> list[str]:
    limitations = [
        "Based only on user-provided business planning inputs.",
        "No external market validation, revenue validation, legal advice, tax advice, financial advice, accounting validation, compliance certification, payment processing, CRM access, connector access, files, database records, task records, emails, posts, purchases, shell commands, or external services were used or performed.",
        "No profitability, market size, demand, revenue, compliance, tax, accounting, payment, investment, or legal outcome is verified.",
        "For legal, tax, financial, accounting, compliance, investment, or other high-stakes business decisions, obtain qualified human or professional review.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add customer, problem, offer, pricing, operations, marketing, risks, resources, and constraints for a stronger brief.")
    return limitations


def _thin_risk_note(thin_input: bool) -> str:
    if thin_input:
        return "The concept is under-specified, so major business risks may be missing."
    return "No explicit threat was provided; review demand, costs, compliance, and capacity manually."


def _thin_gap_note(thin_input: bool) -> str:
    if thin_input:
        return "No advantage or gap can be inferred from the thin input."
    return "No specific advantage was provided; identify one manual edge or gap."
