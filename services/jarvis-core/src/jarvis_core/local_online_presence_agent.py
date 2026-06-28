from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_online_presence_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_online_presence_planning"
SUPPORTED_OUTPUT_TYPES = (
    "presence_brief",
    "bio_draft",
    "profile_review",
    "content_plan",
    "portfolio_positioning",
    "personal_brand_plan",
    "reputation_review",
    "posting_drafts",
)


@dataclass(frozen=True)
class LocalOnlinePresenceRequest:
    profile_name: str = ""
    platforms: list[str] = field(default_factory=list)
    current_bio: str = ""
    goals: list[str] = field(default_factory=list)
    target_audience: str = ""
    tone: str = ""
    strengths: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    content_ideas: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    reputation_concerns: list[str] = field(default_factory=list)
    desired_output_type: str = "presence_brief"


class LocalOnlinePresenceAgentService:
    def create_plan(self, request: LocalOnlinePresenceRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Untitled local profile"
        platforms = _clean_list(request.platforms)
        current_bio = _clean_text(request.current_bio)
        goals = _clean_list(request.goals)
        target_audience = _clean_text(request.target_audience)
        tone = _clean_text(request.tone)
        strengths = _clean_list(request.strengths)
        projects = _clean_list(request.projects)
        content_ideas = _clean_list(request.content_ideas)
        constraints = _clean_list(request.constraints)
        reputation_concerns = _clean_list(request.reputation_concerns)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            platforms,
            current_bio,
            goals,
            target_audience,
            tone,
            strengths,
            projects,
            content_ideas,
            constraints,
            reputation_concerns,
        )
        sensitive_context = _looks_sensitive(
            profile_name,
            current_bio,
            " ".join(goals),
            target_audience,
            " ".join(strengths),
            " ".join(projects),
            " ".join(content_ideas),
            " ".join(constraints),
            " ".join(reputation_concerns),
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "platforms": platforms,
            "desiredOutputType": desired_output_type,
            "presenceFocus": _presence_focus(profile_name, desired_output_type, platforms, goals, thin_input, sensitive_context),
            "audienceSummary": _audience_summary(target_audience, platforms, goals, thin_input),
            "positioningSummary": _positioning_summary(profile_name, current_bio, strengths, projects, tone),
            "bioDrafts": _bio_drafts(profile_name, current_bio, target_audience, tone, strengths, projects, constraints),
            "profileRecommendations": _profile_recommendations(platforms, current_bio, goals, strengths, projects, constraints, reputation_concerns),
            "contentPlan": _content_plan(content_ideas, goals, target_audience, tone, constraints),
            "portfolioPositioning": _portfolio_positioning(projects, strengths, target_audience, goals),
            "personalBrandPlan": _personal_brand_plan(profile_name, goals, strengths, tone, platforms),
            "reputationReview": _reputation_review(reputation_concerns, constraints, sensitive_context),
            "postingDrafts": _posting_drafts(content_ideas, goals, target_audience, tone, constraints),
            "nextActions": _next_actions(desired_output_type, thin_input, sensitive_context),
            "openQuestions": _open_questions(platforms, current_bio, goals, target_audience, tone, strengths, projects, content_ideas, constraints, reputation_concerns),
            "warnings": _warnings(thin_input, sensitive_context),
            "limitations": _limitations(thin_input, sensitive_context),
            "safety": local_online_presence_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_online_presence_dashboard_summary()


def local_online_presence_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Online Presence Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/online-presence/local-plan",
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
        "socialPosting": False,
        "scheduling": False,
        "messaging": False,
        "scraping": False,
        "analyticsAccess": False,
        "emailSending": False,
        "publicPosting": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided online presence planning and drafting inputs"],
    }


def local_online_presence_safety() -> dict[str, bool]:
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
        "socialPosting": False,
        "scheduling": False,
        "messaging": False,
        "scraping": False,
        "analyticsAccess": False,
        "emailSending": False,
        "publicPosting": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "mutation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "presence_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "presence_brief"


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
    platforms: list[str],
    current_bio: str,
    goals: list[str],
    target_audience: str,
    tone: str,
    strengths: list[str],
    projects: list[str],
    content_ideas: list[str],
    constraints: list[str],
    reputation_concerns: list[str],
) -> bool:
    return not any([platforms, current_bio, goals, target_audience, tone, strengths, projects, content_ideas, constraints, reputation_concerns])


def _looks_sensitive(*values: str) -> bool:
    text = " ".join(values).lower()
    terms = (
        "legal",
        "lawsuit",
        "defamation",
        "harassment",
        "employment",
        "hiring",
        "firing",
        "background check",
        "reputation crisis",
        "public accusation",
        "sensitive",
        "confidential",
        "security",
        "medical",
        "financial",
    )
    return any(term in text for term in terms)


def _presence_focus(profile_name: str, desired_output_type: str, platforms: list[str], goals: list[str], thin_input: bool, sensitive_context: bool) -> str:
    if sensitive_context:
        return "Draft cautiously from user-provided inputs and route sensitive, legal, employment, or reputation issues to human review."
    if thin_input:
        return f"Clarify local online presence goals for {profile_name} before treating the output as a usable profile plan."
    if desired_output_type == "bio_draft":
        return f"Draft local bio options for {profile_name} without posting or updating any account."
    if desired_output_type == "profile_review":
        return "Review user-provided profile text and positioning only; no live profile verification is performed."
    if desired_output_type == "content_plan":
        return "Organize content ideas into a manual plan without scheduling or publishing."
    if desired_output_type == "portfolio_positioning":
        return "Connect projects and strengths into portfolio positioning based only on supplied notes."
    if desired_output_type == "personal_brand_plan":
        return "Shape a simple personal-brand plan from supplied audience, tone, strengths, and goals."
    if desired_output_type == "reputation_review":
        return "Review user-provided reputation concerns without scraping, monitoring, or verifying live public results."
    if desired_output_type == "posting_drafts":
        return "Draft possible post text for manual review only; nothing is posted or scheduled."
    if platforms:
        return f"Create a response-only presence brief for {platforms[0]} and related supplied platforms."
    if goals:
        return f"Start from the first stated goal: {goals[0]}."
    return f"Create a local response-only online presence brief for {profile_name}."


def _audience_summary(target_audience: str, platforms: list[str], goals: list[str], thin_input: bool) -> list[str]:
    summary = ["Audience assumptions are based only on the request body."]
    if target_audience:
        summary.append(f"Target audience: {target_audience}.")
    else:
        summary.append("Target audience is not specified.")
    if platforms:
        summary.append(f"Platforms named by user: {', '.join(platforms[:5])}.")
    if goals:
        summary.append(f"Audience should support goal: {goals[0]}.")
    if thin_input:
        summary.append("Input is thin; add platforms, goals, audience, tone, strengths, projects, content ideas, and constraints.")
    return summary


def _positioning_summary(profile_name: str, current_bio: str, strengths: list[str], projects: list[str], tone: str) -> list[str]:
    summary = [f"Profile being shaped: {profile_name}."]
    if current_bio:
        summary.append("Current bio was supplied and can be revised manually.")
    if strengths:
        summary.append(f"Strength to foreground: {strengths[0]}.")
    if projects:
        summary.append(f"Project proof point to consider: {projects[0]}.")
    if tone:
        summary.append(f"Tone requested by user: {tone}.")
    if len(summary) == 1:
        summary.append("Positioning details are sparse; add strengths, projects, audience, tone, or profile text.")
    return summary


def _bio_drafts(profile_name: str, current_bio: str, target_audience: str, tone: str, strengths: list[str], projects: list[str], constraints: list[str]) -> list[dict[str, str]]:
    audience = target_audience or "the intended audience"
    tone_note = tone or "clear"
    strength = strengths[0] if strengths else "practical value"
    project = projects[0] if projects else "recent work"
    constraint_note = f" Keep constraint in mind: {constraints[0]}." if constraints else ""
    source_note = " Current bio supplied for local revision." if current_bio else ""
    return [
        {
            "type": "short",
            "draft": f"{profile_name} helps {audience} understand {strength} through {project}.",
            "note": f"Tone target: {tone_note}.{constraint_note}{source_note}",
        },
        {
            "type": "medium",
            "draft": f"{profile_name} focuses on {strength}, with examples from {project}. The profile can be refined for {audience} while staying specific and easy to scan.",
            "note": "Manual draft only; no profile update, account access, or posting occurred.",
        },
    ]


def _profile_recommendations(platforms: list[str], current_bio: str, goals: list[str], strengths: list[str], projects: list[str], constraints: list[str], reputation_concerns: list[str]) -> list[str]:
    recommendations = [
        "Review profile text manually before using it anywhere.",
        "Keep claims specific, supportable, and aligned with user-provided strengths and projects.",
    ]
    if platforms:
        recommendations.append(f"Adapt wording manually for platform context: {platforms[0]}.")
    if current_bio:
        recommendations.append("Compare the current bio against the desired audience and goals.")
    if goals:
        recommendations.append(f"Make the first goal visible in the profile: {goals[0]}.")
    if strengths:
        recommendations.append(f"Use strength as a positioning anchor: {strengths[0]}.")
    if projects:
        recommendations.append(f"Use a project as evidence: {projects[0]}.")
    if constraints:
        recommendations.append(f"Respect constraint: {constraints[0]}.")
    if reputation_concerns:
        recommendations.append("Handle reputation concerns carefully and seek human review for sensitive claims.")
    recommendations.append("No live profile, analytics, comments, direct messages, or account settings were accessed.")
    return recommendations[:8]


def _content_plan(content_ideas: list[str], goals: list[str], target_audience: str, tone: str, constraints: list[str]) -> list[dict[str, str]]:
    ideas = content_ideas or ["Introduce the profile focus", "Share a project lesson", "Explain a useful perspective"]
    plan: list[dict[str, str]] = []
    for index, idea in enumerate(ideas[:5], start=1):
        plan.append(
            {
                "slot": f"idea_{index}",
                "topic": idea,
                "angle": _content_angle(idea, goals, target_audience, tone, constraints),
            }
        )
    return plan


def _content_angle(idea: str, goals: list[str], target_audience: str, tone: str, constraints: list[str]) -> str:
    parts = [f"Draft about {idea}."]
    if target_audience:
        parts.append(f"Speak to {target_audience}.")
    if goals:
        parts.append(f"Connect to goal: {goals[0]}.")
    if tone:
        parts.append(f"Use tone: {tone}.")
    if constraints:
        parts.append(f"Respect: {constraints[0]}.")
    parts.append("Manual draft only; no schedule or post is created.")
    return " ".join(parts)


def _portfolio_positioning(projects: list[str], strengths: list[str], target_audience: str, goals: list[str]) -> list[str]:
    positioning = []
    if projects:
        positioning.extend([f"Use project as portfolio proof: {project}." for project in projects[:4]])
    else:
        positioning.append("Add projects or examples before treating this as portfolio positioning.")
    if strengths:
        positioning.append(f"Connect projects to strength: {strengths[0]}.")
    if target_audience:
        positioning.append(f"Explain why the work matters to {target_audience}.")
    if goals:
        positioning.append(f"Prioritize proof that supports: {goals[0]}.")
    positioning.append("No website, repository, file, or external portfolio was read or changed.")
    return positioning


def _personal_brand_plan(profile_name: str, goals: list[str], strengths: list[str], tone: str, platforms: list[str]) -> list[str]:
    plan = [
        f"Define what {profile_name} should be known for in one sentence.",
        f"Use first goal as the brand direction: {goals[0]}." if goals else "Choose one primary brand goal.",
        f"Anchor the brand in strength: {strengths[0]}." if strengths else "Add strengths before finalizing positioning.",
        f"Keep tone consistent: {tone}." if tone else "Choose a tone before drafting public copy.",
    ]
    if platforms:
        plan.append(f"Adapt manually for platform context: {platforms[0]}.")
    plan.append("No brand success, follower growth, hiring result, or platform outcome is guaranteed.")
    return plan


def _reputation_review(reputation_concerns: list[str], constraints: list[str], sensitive_context: bool) -> list[str]:
    review = []
    if reputation_concerns:
        review.extend([f"User-provided concern to review manually: {concern}." for concern in reputation_concerns[:4]])
    else:
        review.append("No reputation concerns were provided.")
    if constraints:
        review.append(f"Review concern under constraint: {constraints[0]}.")
    if sensitive_context:
        review.append("Sensitive, legal, employment, or reputation-impacting claims should receive human review before use.")
    review.append("No live reputation search, monitoring, scraping, comment review, or public verification was performed.")
    return review


def _posting_drafts(content_ideas: list[str], goals: list[str], target_audience: str, tone: str, constraints: list[str]) -> list[dict[str, str]]:
    ideas = content_ideas or goals or ["Share a concise profile update"]
    drafts: list[dict[str, str]] = []
    for index, idea in enumerate(ideas[:3], start=1):
        audience = f" for {target_audience}" if target_audience else ""
        tone_note = f" Tone: {tone}." if tone else ""
        constraint_note = f" Constraint: {constraints[0]}." if constraints else ""
        drafts.append(
            {
                "label": f"draft_{index}",
                "text": f"Draft idea{audience}: {idea}. Add a specific example, one clear takeaway, and a manual review before using it.",
                "note": f"Drafting only; no post, schedule, upload, message, or account action occurred.{tone_note}{constraint_note}",
            }
        )
    return drafts


def _next_actions(desired_output_type: str, thin_input: bool, sensitive_context: bool) -> list[str]:
    actions = []
    if thin_input:
        actions.append("Add platforms, current bio, goals, target audience, tone, strengths, projects, content ideas, constraints, or reputation concerns.")
    if sensitive_context:
        actions.append("Get human review for sensitive, legal, employment, reputation, or high-impact claims before using any draft.")
    if desired_output_type == "bio_draft":
        actions.append("Pick one bio draft and manually revise it for accuracy.")
    elif desired_output_type == "content_plan":
        actions.append("Choose one content idea and draft it outside any posting system.")
    elif desired_output_type == "posting_drafts":
        actions.append("Review drafts manually and decide whether they are appropriate to use elsewhere.")
    elif desired_output_type == "profile_review":
        actions.append("Compare the recommendations against the user-provided profile text.")
    elif desired_output_type == "reputation_review":
        actions.append("Separate factual concerns, tone concerns, and claims needing human review.")
    else:
        actions.append("Use this as local planning and drafting support only.")
    actions.append("Do not post, schedule, message, scrape, upload, connect accounts, or verify live profiles from this response.")
    return actions[:5]


def _open_questions(
    platforms: list[str],
    current_bio: str,
    goals: list[str],
    target_audience: str,
    tone: str,
    strengths: list[str],
    projects: list[str],
    content_ideas: list[str],
    constraints: list[str],
    reputation_concerns: list[str],
) -> list[str]:
    questions = []
    if not platforms:
        questions.append("Which platforms or profile contexts should this copy fit?")
    if not current_bio:
        questions.append("What current bio or profile copy should be revised?")
    if not goals:
        questions.append("What should the online presence help accomplish?")
    if not target_audience:
        questions.append("Who should understand or care about this profile?")
    if not tone:
        questions.append("What tone should the profile use?")
    if not strengths:
        questions.append("What strengths should be visible?")
    if not projects:
        questions.append("What projects or examples support the positioning?")
    if not content_ideas:
        questions.append("What content ideas should be developed?")
    if not constraints:
        questions.append("What claims, topics, or styles should be avoided?")
    if not reputation_concerns:
        questions.append("Are there reputation or sensitivity concerns to review?")
    return questions


def _warnings(thin_input: bool, sensitive_context: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Online-presence input is thin; output is a provisional local planning and drafting scaffold.")
    if sensitive_context:
        warnings.append("Sensitive, reputation, legal, employment, or high-impact wording detected; use human review before using drafts publicly.")
    warnings.append("This response drafts and plans only; it does not post, schedule, message, scrape, verify, upload, persist, or access accounts.")
    return warnings


def _limitations(thin_input: bool, sensitive_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided online presence planning and drafting inputs.",
        "Drafting is allowed, but no posting, scheduling, messaging, account action, scraping, analytics access, live verification, file access, database write, task persistence, upload, web browsing, external API, or connector behavior was performed.",
        "No LinkedIn, X/Twitter, Instagram, TikTok, YouTube, GitHub, website, analytics, direct message, comment, email, contact, or external account was accessed or changed.",
        "No brand success, follower growth, hiring result, reputation verification, platform compliance review, public posting, certification, or outcome guarantee is claimed.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add platforms, current bio, goals, audience, tone, strengths, projects, content ideas, constraints, or reputation concerns.")
    if sensitive_context:
        limitations.append("Sensitive, reputation, legal, or employment-related claims should receive human review before use.")
    return limitations
