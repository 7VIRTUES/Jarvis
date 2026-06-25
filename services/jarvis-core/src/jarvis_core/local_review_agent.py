from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_review_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_review"
SUPPORTED_REVIEW_TYPES = ("general", "clarity", "risk", "completeness", "safety", "actionability")
SUPPORTED_SEVERITIES = ("gentle", "balanced", "strict")


@dataclass(frozen=True)
class LocalReviewRequest:
    subject: str
    content: str
    review_type: str = "general"
    audience: str = ""
    criteria: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    severity: str = "balanced"


class LocalReviewAgentService:
    def create_review(self, request: LocalReviewRequest) -> dict[str, Any]:
        subject = request.subject.strip() or "Untitled local review subject"
        content = request.content.strip()
        review_type = _normalize_review_type(request.review_type)
        severity = _normalize_severity(request.severity)
        audience = request.audience.strip()
        criteria = _clean_list(request.criteria)
        constraints = _clean_list(request.constraints)
        points = _extract_points(content)
        thin_content = len(content) < 80 or len(points) < 2

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "subject": subject,
            "reviewType": review_type,
            "severity": severity,
            "audience": audience,
            "reviewFocus": _review_focus(subject, review_type, audience, criteria, constraints, thin_content),
            "strengths": _strengths(points, criteria, thin_content),
            "issues": _issues(points, review_type, severity, thin_content),
            "missingInformation": _missing_information(review_type, audience, criteria, constraints, thin_content),
            "riskFlags": _risk_flags(review_type, constraints, thin_content),
            "improvementSuggestions": _improvement_suggestions(review_type, severity, criteria, constraints, thin_content),
            "actionItems": _action_items(review_type, severity, thin_content),
            "reviewQuestions": _review_questions(review_type, audience, thin_content),
            "warnings": _warnings(thin_content),
            "limitations": _limitations(thin_content),
            "safety": local_review_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_review_dashboard_summary()


def local_review_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Review Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/review/local-review",
        "reviewTypes": list(SUPPORTED_REVIEW_TYPES),
        "severityLevels": list(SUPPORTED_SEVERITIES),
        "responseOnly": True,
        "reviewPersistence": False,
        "sourceValidation": False,
        "citationValidation": False,
        "testExecution": False,
        "repoInspection": False,
        "taskPersistence": False,
        "dbWrites": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "gmailCalendarSocialAccess": False,
        "postingOrSending": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "uploads": False,
        "mutation": False,
        "limitations": ["based only on user-provided review content"],
    }


def local_review_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "reviewPersistence": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "gmailAccess": False,
        "calendarAccess": False,
        "socialAccess": False,
        "postingOrSending": False,
        "emailSending": False,
        "publicPosting": False,
        "taskPersistence": False,
        "dbWrites": False,
        "fileReads": False,
        "fileWrites": False,
        "shellExecution": False,
        "uploads": False,
        "mutation": False,
        "repoInspection": False,
        "testExecution": False,
        "sourceValidation": False,
        "citationValidation": False,
    }


def _normalize_review_type(value: str) -> str:
    normalized = (value or "general").strip().lower()
    return normalized if normalized in SUPPORTED_REVIEW_TYPES else "general"


def _normalize_severity(value: str) -> str:
    normalized = (value or "balanced").strip().lower()
    return normalized if normalized in SUPPORTED_SEVERITIES else "balanced"


def _extract_points(content: str) -> list[str]:
    if not content:
        return []
    raw_parts = re.split(r"(?:\r?\n+|(?<=[.!?])\s+|[;:•]+)", content)
    points: list[str] = []
    seen: set[str] = set()
    for part in raw_parts:
        cleaned = re.sub(r"^\s*[-*#\d.)]+\s*", "", part).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        points.append(cleaned)
        if len(points) >= 10:
            break
    return points


def _clean_list(values: list[str]) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = re.sub(r"\s+", " ", value.strip())
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:10]


def _review_focus(
    subject: str,
    review_type: str,
    audience: str,
    criteria: list[str],
    constraints: list[str],
    thin_content: bool,
) -> str:
    audience_note = f" for {audience}" if audience else ""
    if thin_content:
        return f"Initial local review of {subject}{audience_note}; content is too thin for confident conclusions."
    if criteria:
        return f"Review {subject}{audience_note} against user-provided criteria, starting with {criteria[0]}."
    if constraints:
        return f"Review {subject}{audience_note} for {review_type} while respecting the stated constraints."
    return f"Review {subject}{audience_note} for {review_type}, using only the supplied content."


def _strengths(points: list[str], criteria: list[str], thin_content: bool) -> list[str]:
    if thin_content:
        return ["The subject and initial content are present, giving the review a starting point."]
    strengths = [
        "The content provides enough material for a local response-only review.",
        f"The main thread is visible: {points[0].rstrip('.')}.",
    ]
    if criteria:
        strengths.append("User-provided criteria give the review an explicit evaluation frame.")
    return strengths[:4]


def _issues(points: list[str], review_type: str, severity: str, thin_content: bool) -> list[str]:
    if thin_content:
        return ["The content is thin, so issues may reflect missing context rather than a true weakness in the underlying work."]
    issues = []
    if review_type in {"clarity", "general"}:
        issues.append("Some claims may need clearer sequencing, definitions, or transitions for the intended reader.")
    if review_type in {"risk", "safety", "general"}:
        issues.append("Risks and boundaries should be named explicitly so the reader can tell what is and is not being claimed.")
    if review_type in {"completeness", "actionability", "general"}:
        issues.append("Next steps, owner, evidence needed, or completion criteria may need more specificity.")
    if severity == "strict":
        issues.append("Strict review: remove ambiguity before treating this as ready for decision or handoff.")
    elif severity == "gentle":
        issues.append("Gentle review: the main improvement is to add a small amount of clarifying context.")
    return issues[:5] or ["No major issue is apparent from the supplied content, but the review is local-only and unverified."]


def _missing_information(
    review_type: str,
    audience: str,
    criteria: list[str],
    constraints: list[str],
    thin_content: bool,
) -> list[str]:
    missing = []
    if thin_content:
        missing.append("More content is needed before making a confident review.")
    if not audience:
        missing.append("Intended audience was not specified.")
    if not criteria:
        missing.append("No explicit review criteria were provided.")
    if not constraints:
        missing.append("No review constraints were provided.")
    if review_type in {"risk", "safety"}:
        missing.append("Risk tolerance, safety boundaries, and unacceptable outcomes were not fully specified.")
    if review_type == "actionability":
        missing.append("Owner, deadline, and definition of done may need to be supplied.")
    if review_type == "completeness":
        missing.append("Required sections, decision inputs, or acceptance criteria may need to be supplied.")
    return missing[:7] or ["No obvious missing information was detected from the supplied review inputs."]


def _risk_flags(review_type: str, constraints: list[str], thin_content: bool) -> list[str]:
    flags = []
    if thin_content:
        flags.append("Thin content may hide important context, tradeoffs, or risks.")
    if review_type in {"risk", "safety", "general"}:
        flags.append("Any unsupported factual, legal, medical, financial, security, or operational claims should be checked outside this agent.")
    if constraints:
        flags.append("User-provided constraints should be checked manually before relying on the reviewed content.")
    return flags or ["No specific risk flag was detected from the supplied content, aside from local-only review limits."]


def _improvement_suggestions(
    review_type: str,
    severity: str,
    criteria: list[str],
    constraints: list[str],
    thin_content: bool,
) -> list[str]:
    if thin_content:
        return [
            "Add a paragraph of source content, decision context, or draft text before relying on the review.",
            "State the intended audience and what kind of feedback would be most useful.",
        ]
    suggestions = [
        "Add a one-sentence purpose statement near the top.",
        "Separate facts, assumptions, decisions, risks, and next actions.",
    ]
    if review_type == "clarity":
        suggestions.append("Replace broad wording with concrete examples or definitions.")
    elif review_type == "risk":
        suggestions.append("Add a risk section with likelihood, impact, mitigation, and owner.")
    elif review_type == "completeness":
        suggestions.append("Add a checklist of required sections or decision inputs.")
    elif review_type == "safety":
        suggestions.append("State boundaries, prohibited actions, and escalation conditions plainly.")
    elif review_type == "actionability":
        suggestions.append("Turn recommendations into owner, next step, and definition-of-done items.")
    if criteria:
        suggestions.append("Score or annotate the content against each user-provided criterion.")
    if constraints:
        suggestions.append("Add a short constraints check so readers can see what shaped the recommendation.")
    if severity == "strict":
        suggestions.append("Remove or qualify any claim that cannot be supported by the supplied content.")
    return suggestions[:7]


def _action_items(review_type: str, severity: str, thin_content: bool) -> list[str]:
    if thin_content:
        return ["Provide more content.", "Add audience, criteria, and constraints if they matter."]
    items = ["Revise the content using the issues and suggestions above."]
    if review_type in {"risk", "safety"}:
        items.append("Add explicit risk or safety boundaries before sharing.")
    if review_type in {"completeness", "actionability"}:
        items.append("Add missing owners, dates, acceptance criteria, or decision inputs.")
    if severity == "strict":
        items.append("Do a final manual pass for unsupported claims before treating the content as ready.")
    return items


def _review_questions(review_type: str, audience: str, thin_content: bool) -> list[str]:
    questions = [
        "What decision or next action should this content support?",
        "Which claim would be most costly if misunderstood?",
    ]
    if not audience:
        questions.append("Who is the intended reader?")
    if review_type == "clarity":
        questions.append("Which term or section is most likely to confuse the reader?")
    elif review_type == "risk":
        questions.append("What risk would change the recommendation if it were more severe than expected?")
    elif review_type == "completeness":
        questions.append("What required information would block approval or handoff?")
    elif review_type == "safety":
        questions.append("What action should the reader avoid after reading this?")
    elif review_type == "actionability":
        questions.append("Who owns the next step and how will completion be recognized?")
    if thin_content:
        questions.append("What additional content should be reviewed before relying on this output?")
    return questions[:6]


def _warnings(thin_content: bool) -> list[str]:
    if thin_content:
        return ["Review content is thin; output is a provisional local review."]
    return []


def _limitations(thin_content: bool) -> list[str]:
    limitations = [
        "Based only on user-provided review content.",
        "No external verification, web browsing, source validation, citation validation, repo inspection, code execution, or test execution was performed.",
        "No files, database records, tasks, drafts, emails, posts, uploads, connectors, accounts, shell commands, or external services were used.",
    ]
    if thin_content:
        limitations.append("Thin content limits specificity; add more content for a stronger review.")
    return limitations
