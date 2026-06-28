from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_creator_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_creator_planning"
SUPPORTED_OUTPUT_TYPES = (
    "creator_brief",
    "channel_plan",
    "content_calendar",
    "video_outline",
    "script_draft",
    "title_thumbnail_ideas",
    "production_checklist",
    "repurposing_plan",
)


@dataclass(frozen=True)
class LocalCreatorRequest:
    content_idea: str
    creator_name: str = ""
    platforms: list[str] = field(default_factory=list)
    niche: str = ""
    audience: str = ""
    goals: list[str] = field(default_factory=list)
    tone: str = ""
    format_notes: str = ""
    production_resources: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    existing_content_notes: str = ""
    desired_output_type: str = "creator_brief"


class LocalCreatorAgentService:
    def create_plan(self, request: LocalCreatorRequest) -> dict[str, Any]:
        creator_name = _clean_text(request.creator_name) or "Untitled local creator"
        platforms = _clean_list(request.platforms)
        niche = _clean_text(request.niche)
        audience = _clean_text(request.audience)
        content_idea = _clean_text(request.content_idea)
        goals = _clean_list(request.goals)
        tone = _clean_text(request.tone)
        format_notes = _clean_text(request.format_notes)
        production_resources = _clean_list(request.production_resources)
        constraints = _clean_list(request.constraints)
        existing_content_notes = _clean_text(request.existing_content_notes)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            content_idea,
            platforms,
            niche,
            audience,
            goals,
            tone,
            format_notes,
            production_resources,
            constraints,
            existing_content_notes,
        )
        sensitive_context = _looks_sensitive(
            content_idea,
            niche,
            audience,
            " ".join(goals),
            format_notes,
            " ".join(constraints),
            existing_content_notes,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "creatorName": creator_name,
            "platforms": platforms,
            "desiredOutputType": desired_output_type,
            "creatorFocus": _creator_focus(creator_name, desired_output_type, content_idea, platforms, thin_input, sensitive_context),
            "audienceSummary": _audience_summary(audience, niche, platforms, goals, thin_input),
            "positioningSummary": _positioning_summary(creator_name, niche, content_idea, goals, tone, existing_content_notes),
            "channelPlan": _channel_plan(platforms, niche, audience, goals, tone, constraints),
            "contentCalendar": _content_calendar(content_idea, goals, platforms, format_notes, constraints),
            "videoOutline": _video_outline(content_idea, audience, tone, format_notes, constraints),
            "scriptDraft": _script_draft(content_idea, audience, tone, format_notes, constraints),
            "titleThumbnailIdeas": _title_thumbnail_ideas(content_idea, audience, tone, constraints),
            "productionChecklist": _production_checklist(production_resources, format_notes, constraints),
            "repurposingPlan": _repurposing_plan(content_idea, platforms, goals, constraints),
            "nextActions": _next_actions(desired_output_type, thin_input, sensitive_context),
            "openQuestions": _open_questions(
                content_idea,
                platforms,
                niche,
                audience,
                goals,
                tone,
                format_notes,
                production_resources,
                constraints,
                existing_content_notes,
            ),
            "warnings": _warnings(thin_input, sensitive_context),
            "limitations": _limitations(thin_input, sensitive_context),
            "safety": local_creator_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_creator_dashboard_summary()


def local_creator_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Creator Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/creator/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "youtubeAccess": False,
        "socialPlatformAccess": False,
        "analyticsAccess": False,
        "scraping": False,
        "upload": False,
        "publicPosting": False,
        "scheduling": False,
        "messaging": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "copyrightClearance": False,
        "platformComplianceValidation": False,
        "monetizationGuarantee": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided creator planning and drafting inputs"],
    }


def local_creator_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "connectors": False,
        "oauth": False,
        "accountAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "youtubeAccess": False,
        "socialPlatformAccess": False,
        "analyticsAccess": False,
        "scraping": False,
        "upload": False,
        "publicPosting": False,
        "scheduling": False,
        "messaging": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "copyrightClearance": False,
        "platformComplianceValidation": False,
        "monetizationGuarantee": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "creator_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "creator_brief"


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
    content_idea: str,
    platforms: list[str],
    niche: str,
    audience: str,
    goals: list[str],
    tone: str,
    format_notes: str,
    production_resources: list[str],
    constraints: list[str],
    existing_content_notes: str,
) -> bool:
    return not any(
        [content_idea, platforms, niche, audience, goals, tone, format_notes, production_resources, constraints, existing_content_notes]
    )


def _looks_sensitive(*values: str) -> bool:
    text = " ".join(values).lower()
    terms = (
        "copyright",
        "reputation",
        "legal",
        "sponsorship",
        "sponsored",
        "brand deal",
        "sensitive",
        "medical",
        "financial",
        "minor",
        "harassment",
        "public accusation",
    )
    return any(term in text for term in terms)


def _creator_focus(
    creator_name: str,
    desired_output_type: str,
    content_idea: str,
    platforms: list[str],
    thin_input: bool,
    sensitive_context: bool,
) -> str:
    if sensitive_context:
        return "Draft cautiously from user-provided creator notes and route copyright, reputation, legal, sponsorship, or sensitive concerns to human review."
    if thin_input:
        return f"Clarify creator inputs for {creator_name} before treating the output as a usable creator plan."
    if desired_output_type == "channel_plan":
        return "Shape a manual channel plan from the supplied niche, audience, platforms, goals, and constraints."
    if desired_output_type == "content_calendar":
        return "Organize the supplied idea into a manual content calendar without scheduling or posting."
    if desired_output_type == "video_outline":
        return "Outline a video from the supplied idea without verifying trends or platform demand."
    if desired_output_type == "script_draft":
        return "Draft script copy for manual review only."
    if desired_output_type == "title_thumbnail_ideas":
        return "Generate title and thumbnail concepts from supplied notes without platform analytics or trend checks."
    if desired_output_type == "production_checklist":
        return "Create a manual production checklist without creating files, uploads, or tasks."
    if desired_output_type == "repurposing_plan":
        return "Plan manual repurposing ideas without posting, scheduling, or external-service access."
    if platforms:
        return f"Create a response-only creator brief for {platforms[0]} and related user-named platforms."
    if content_idea:
        return f"Start from the supplied content idea: {content_idea}."
    return f"Create a local response-only creator brief for {creator_name}."


def _audience_summary(audience: str, niche: str, platforms: list[str], goals: list[str], thin_input: bool) -> list[str]:
    summary = ["Audience assumptions are based only on the request body."]
    summary.append(f"Audience: {audience}." if audience else "Audience is not specified.")
    if niche:
        summary.append(f"Niche: {niche}.")
    if platforms:
        summary.append(f"Platforms named by user: {', '.join(platforms[:5])}.")
    if goals:
        summary.append(f"Audience should support goal: {goals[0]}.")
    if thin_input:
        summary.append("Input is thin; add platform, niche, audience, idea, goals, tone, format notes, resources, constraints, or existing content notes.")
    return summary


def _positioning_summary(
    creator_name: str,
    niche: str,
    content_idea: str,
    goals: list[str],
    tone: str,
    existing_content_notes: str,
) -> list[str]:
    summary = [f"Creator being shaped: {creator_name}."]
    if niche:
        summary.append(f"Position around niche: {niche}.")
    if content_idea:
        summary.append(f"Core content idea: {content_idea}.")
    if goals:
        summary.append(f"Primary goal to reflect: {goals[0]}.")
    if tone:
        summary.append(f"Tone requested by user: {tone}.")
    if existing_content_notes:
        summary.append("Existing content notes were supplied for manual context only.")
    if len(summary) == 1:
        summary.append("Positioning details are sparse; add a niche, audience, idea, tone, goals, or existing content notes.")
    return summary


def _channel_plan(platforms: list[str], niche: str, audience: str, goals: list[str], tone: str, constraints: list[str]) -> list[str]:
    plan = [
        f"Define the channel promise around {niche}." if niche else "Define the channel promise in one sentence.",
        f"Speak to {audience}." if audience else "Name the intended audience before finalizing positioning.",
        f"Use tone consistently: {tone}." if tone else "Choose a tone before drafting public copy.",
    ]
    if platforms:
        plan.append(f"Adapt manually for platform context: {platforms[0]}.")
    if goals:
        plan.append(f"Prioritize content that supports: {goals[0]}.")
    if constraints:
        plan.append(f"Respect constraint: {constraints[0]}.")
    plan.append("No account, analytics, comments, messages, or platform settings were accessed.")
    return plan


def _content_calendar(content_idea: str, goals: list[str], platforms: list[str], format_notes: str, constraints: list[str]) -> list[dict[str, str]]:
    base = content_idea or "Refine the creator concept"
    topics = [
        ("idea_1", base),
        ("idea_2", f"Behind the idea: {base}"),
        ("idea_3", f"Practical lesson from {base}"),
    ]
    calendar: list[dict[str, str]] = []
    for slot, topic in topics:
        angle_parts = ["Manual planning slot only."]
        if goals:
            angle_parts.append(f"Connect to goal: {goals[0]}.")
        if platforms:
            angle_parts.append(f"Adapt for {platforms[0]} manually.")
        if format_notes:
            angle_parts.append(f"Format note: {format_notes}.")
        if constraints:
            angle_parts.append(f"Constraint: {constraints[0]}.")
        calendar.append({"slot": slot, "topic": topic, "angle": " ".join(angle_parts)})
    return calendar


def _video_outline(content_idea: str, audience: str, tone: str, format_notes: str, constraints: list[str]) -> list[str]:
    idea = content_idea or "the supplied creator idea"
    outline = [
        f"Hook: name the viewer problem or promise around {idea}.",
        f"Context: explain why {idea} matters.",
        "Main points: give three concrete points or examples.",
        "Close: invite manual reflection or a next piece of content without claiming outcomes.",
    ]
    if audience:
        outline.append(f"Audience fit: keep examples useful for {audience}.")
    if tone:
        outline.append(f"Tone: {tone}.")
    if format_notes:
        outline.append(f"Format: {format_notes}.")
    if constraints:
        outline.append(f"Constraint: {constraints[0]}.")
    return outline


def _script_draft(content_idea: str, audience: str, tone: str, format_notes: str, constraints: list[str]) -> list[dict[str, str]]:
    idea = content_idea or "this idea"
    audience_note = f" for {audience}" if audience else ""
    tone_note = f" Tone: {tone}." if tone else ""
    format_note = f" Format: {format_notes}." if format_notes else ""
    constraint_note = f" Constraint: {constraints[0]}." if constraints else ""
    return [
        {
            "section": "hook",
            "draft": f"Here is the simple reason {idea} matters{audience_note}.",
            "note": f"Draft text only; no recording, upload, posting, or scheduling occurred.{tone_note}",
        },
        {
            "section": "body",
            "draft": f"Start with the problem, show one practical example, and explain what someone can take away from {idea}.",
            "note": f"Manual review recommended before use.{format_note}{constraint_note}",
        },
        {
            "section": "close",
            "draft": "Wrap with one clear takeaway and one next question for the audience.",
            "note": "No monetization, follower growth, trend validation, or algorithm outcome is claimed.",
        },
    ]


def _title_thumbnail_ideas(content_idea: str, audience: str, tone: str, constraints: list[str]) -> list[dict[str, str]]:
    idea = content_idea or "Creator idea"
    audience_part = f" for {audience}" if audience else ""
    tone_part = f" Tone: {tone}." if tone else ""
    constraint_part = f" Constraint: {constraints[0]}." if constraints else ""
    return [
        {
            "title": f"What {idea} Changes{audience_part}",
            "thumbnailConcept": "One clear object or phrase that represents the main takeaway.",
            "note": f"Concept only; no trend, click-through, copyright, or platform validation performed.{tone_part}",
        },
        {
            "title": f"The Practical Guide to {idea}",
            "thumbnailConcept": "Before/after framing with simple, non-misleading copy.",
            "note": f"Manual review needed before use.{constraint_part}",
        },
    ]


def _production_checklist(production_resources: list[str], format_notes: str, constraints: list[str]) -> list[str]:
    checklist = [
        "Confirm the content idea and intended audience.",
        "Draft outline and script text manually.",
        "Review claims, examples, and sensitive topics before recording or publishing elsewhere.",
    ]
    if production_resources:
        checklist.append(f"Resource named by user: {production_resources[0]}.")
    if format_notes:
        checklist.append(f"Format note to follow manually: {format_notes}.")
    if constraints:
        checklist.append(f"Constraint: {constraints[0]}.")
    checklist.append("No file, task, upload, schedule, post, or external-service action was created.")
    return checklist


def _repurposing_plan(content_idea: str, platforms: list[str], goals: list[str], constraints: list[str]) -> list[str]:
    idea = content_idea or "the creator idea"
    plan = [
        f"Turn {idea} into a short outline.",
        f"Turn {idea} into a concise post draft for manual review.",
        f"Turn {idea} into a checklist or carousel-style note outside this agent if desired.",
    ]
    if platforms:
        plan.append(f"Adapt manually for platform context: {platforms[0]}.")
    if goals:
        plan.append(f"Keep repurposed versions aligned with: {goals[0]}.")
    if constraints:
        plan.append(f"Respect: {constraints[0]}.")
    plan.append("No upload, post, schedule, message, analytics read, or account action occurred.")
    return plan


def _next_actions(desired_output_type: str, thin_input: bool, sensitive_context: bool) -> list[str]:
    actions = []
    if thin_input:
        actions.append("Add platforms, niche, audience, content idea, goals, tone, format notes, resources, constraints, or existing content notes.")
    if sensitive_context:
        actions.append("Get human review for copyright, reputation, legal, sponsorship, or sensitive content concerns before using drafts publicly.")
    if desired_output_type == "script_draft":
        actions.append("Manually revise the script for accuracy, ownership, and audience fit.")
    elif desired_output_type == "content_calendar":
        actions.append("Choose one calendar idea and draft it manually outside any scheduling system.")
    elif desired_output_type == "title_thumbnail_ideas":
        actions.append("Review title and thumbnail concepts manually before use.")
    elif desired_output_type == "production_checklist":
        actions.append("Use the checklist manually; do not treat it as task creation or production execution.")
    else:
        actions.append("Use this as local creator planning and drafting support only.")
    actions.append("Do not upload, post, schedule, scrape, browse, read analytics, message, create accounts, or persist content from this response.")
    return actions[:5]


def _open_questions(
    content_idea: str,
    platforms: list[str],
    niche: str,
    audience: str,
    goals: list[str],
    tone: str,
    format_notes: str,
    production_resources: list[str],
    constraints: list[str],
    existing_content_notes: str,
) -> list[str]:
    questions = []
    if not content_idea:
        questions.append("What creator, channel, video, or content idea should be developed?")
    if not platforms:
        questions.append("Which platforms or formats should the plan consider?")
    if not niche:
        questions.append("What niche or topic area should anchor the content?")
    if not audience:
        questions.append("Who is the intended audience?")
    if not goals:
        questions.append("What should the content help accomplish?")
    if not tone:
        questions.append("What tone should the content use?")
    if not format_notes:
        questions.append("What format or length constraints matter?")
    if not production_resources:
        questions.append("What production resources are available?")
    if not constraints:
        questions.append("What claims, topics, styles, or risks should be avoided?")
    if not existing_content_notes:
        questions.append("What existing content or channel context should be preserved?")
    return questions


def _warnings(thin_input: bool, sensitive_context: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Creator input is thin; output is a provisional local planning and drafting scaffold.")
    if sensitive_context:
        warnings.append("Copyright, reputation, legal, sponsorship, or sensitive content wording detected; use human review before public use.")
    warnings.append("This response drafts and plans only; it does not upload, post, schedule, scrape, browse, verify trends, read analytics, message, persist, or access accounts.")
    return warnings


def _limitations(thin_input: bool, sensitive_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided creator planning and drafting inputs.",
        "No YouTube, TikTok, Instagram, X/Twitter, Twitch, analytics, comments, direct messages, accounts, websites, files, or external services were accessed.",
        "No upload, posting, scheduling, scraping, browsing, live trend verification, analytics access, messaging, account creation, file access, database write, task persistence, external API, or connector behavior was performed.",
        "No follower growth, monetization success, trend validation, copyright clearance, brand deal validation, platform compliance, algorithm certainty, certification, or outcome guarantee is claimed.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add platform, niche, audience, idea, goals, tone, format notes, resources, constraints, or existing content notes.")
    if sensitive_context:
        limitations.append("Copyright, reputation, legal, sponsorship, or sensitive content concerns should receive human review before public use.")
    return limitations
