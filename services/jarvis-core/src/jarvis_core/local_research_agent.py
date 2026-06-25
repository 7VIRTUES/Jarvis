from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_research_agent"
STATUS = "local_only"
SUPPORTED_OUTPUT_TYPES = ("brief", "outline", "comparison", "reading_plan")


@dataclass(frozen=True)
class LocalResearchBriefRequest:
    topic: str
    user_provided_notes: str
    source_titles: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    desired_output_type: str = "brief"


class LocalResearchAgentService:
    def create_brief(self, request: LocalResearchBriefRequest) -> dict[str, Any]:
        topic = request.topic.strip() or "Untitled local research topic"
        desired_output_type = _normalize_output_type(request.desired_output_type)
        notes = request.user_provided_notes.strip()
        points = _extract_points(notes)
        thin_notes = len(notes) < 80 or len(points) < 2

        key_points = points if points else ["No substantive user-provided notes were available to extract key points."]
        synthesis_notes = _synthesis_notes(topic, key_points, desired_output_type, thin_notes)
        open_questions = _open_questions(request.questions, thin_notes)
        source_gaps = _source_gaps(request.source_titles, thin_notes)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "topic": topic,
            "desiredOutputType": desired_output_type,
            "thesisOrFocus": _thesis_or_focus(topic, key_points, thin_notes),
            "keyPoints": key_points,
            "synthesisNotes": synthesis_notes,
            "openQuestions": open_questions,
            "sourceGaps": source_gaps,
            "suggestedLocalNextSteps": _suggested_local_next_steps(desired_output_type, thin_notes),
            "limitations": [
                "Based only on user-provided notes.",
                "No web browsing or source verification was performed.",
                "No citations are generated or verified.",
                "No local files were read or written.",
            ],
            "safety": local_research_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_research_dashboard_summary()


def local_research_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Research Agent",
        "status": "implemented_local_only",
        "mode": "user_provided_notes_only",
        "endpoint": "/agents/research/local-brief",
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "fileMutation": False,
        "citationVerification": False,
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "limitations": ["based only on user-provided input"],
    }


def local_research_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "postingOrSending": False,
        "fileMutation": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "brief"


def _extract_points(notes: str) -> list[str]:
    if not notes:
        return []
    raw_parts = re.split(r"(?:\r?\n+|(?<=[.!?])\s+|[;•]+)", notes)
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
        if len(points) >= 8:
            break
    return points


def _thesis_or_focus(topic: str, key_points: list[str], thin_notes: bool) -> str:
    if thin_notes:
        return f"Initial local focus for {topic}: organize the limited user-provided notes before drawing conclusions."
    return f"Local focus for {topic}: synthesize the provided notes around {key_points[0].rstrip('.')}."


def _synthesis_notes(topic: str, key_points: list[str], desired_output_type: str, thin_notes: bool) -> list[str]:
    if thin_notes:
        return [
            f"The current brief for {topic} is limited because the supplied notes are thin.",
            "Treat these points as a local organizing draft, not as verified research findings.",
        ]
    notes = [
        f"The provided notes suggest {topic} should be framed around {key_points[0].rstrip('.')}.",
        "The extracted points can be grouped into claims, mechanisms, constraints, and next questions.",
    ]
    if desired_output_type == "outline":
        notes.append("A useful outline should separate background, mechanisms, evidence to verify later, and remaining questions.")
    elif desired_output_type == "comparison":
        notes.append("A useful comparison should define dimensions before contrasting claims from the provided notes.")
    elif desired_output_type == "reading_plan":
        notes.append("A useful reading plan should prioritize fundamentals, then methods, then gaps identified in the notes.")
    return notes


def _open_questions(questions: list[str], thin_notes: bool) -> list[str]:
    cleaned = [question.strip() for question in questions if question.strip()]
    if cleaned:
        return cleaned
    if thin_notes:
        return ["What additional notes, source excerpts, or local observations should be added before synthesis?"]
    return ["Which extracted points are claims that need later source verification outside this local-only agent?"]


def _source_gaps(source_titles: list[str], thin_notes: bool) -> list[str]:
    titles = [title.strip() for title in source_titles if title.strip()]
    gaps = [
        "No source verification was performed.",
        "No citations are provided because this agent only uses user-provided notes.",
    ]
    if titles:
        gaps.append("User-provided source titles were treated as unverified labels: " + "; ".join(titles[:5]))
    if thin_notes:
        gaps.append("More user-provided notes are needed before comparing evidence or confidence.")
    return gaps


def _suggested_local_next_steps(desired_output_type: str, thin_notes: bool) -> list[str]:
    steps = [
        "Add more user-provided notes or excerpts if deeper synthesis is needed.",
        "Mark any claims that should be verified manually outside this local-only agent.",
    ]
    if desired_output_type == "outline":
        steps.append("Turn the extracted points into headings and subheadings.")
    elif desired_output_type == "comparison":
        steps.append("Create comparison dimensions from the notes before adding any conclusions.")
    elif desired_output_type == "reading_plan":
        steps.append("Order the provided topics from fundamentals to open gaps.")
    else:
        steps.append("Revise the brief after adding more local notes.")
    if thin_notes:
        steps.append("Provide at least a paragraph of notes for a more useful local brief.")
    return steps
