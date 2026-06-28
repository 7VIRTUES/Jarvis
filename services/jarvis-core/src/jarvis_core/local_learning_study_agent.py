from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_learning_study_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_learning_study_planning"
SUPPORTED_OUTPUT_TYPES = (
    "learning_brief",
    "study_plan",
    "learning_roadmap",
    "active_recall_plan",
    "feynman_drills",
    "spaced_repetition_plan",
    "weekly_review",
    "boss_test",
)


@dataclass(frozen=True)
class LocalLearningStudyRequest:
    learning_goal: str
    learner_name: str = ""
    topics: list[str] = field(default_factory=list)
    current_level: str = ""
    timeline: str = ""
    available_time: str = ""
    resources: list[str] = field(default_factory=list)
    weak_areas: list[str] = field(default_factory=list)
    preferred_methods: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    motivation_notes: str = ""
    desired_output_type: str = "learning_brief"


class LocalLearningStudyAgentService:
    def create_plan(self, request: LocalLearningStudyRequest) -> dict[str, Any]:
        learner_name = _clean_text(request.learner_name) or "Local learner"
        learning_goal = _clean_text(request.learning_goal)
        topics = _clean_list(request.topics, limit=12)
        current_level = _clean_text(request.current_level)
        timeline = _clean_text(request.timeline)
        available_time = _clean_text(request.available_time)
        resources = _clean_list(request.resources, limit=12)
        weak_areas = _clean_list(request.weak_areas, limit=12)
        preferred_methods = _clean_list(request.preferred_methods)
        constraints = _clean_list(request.constraints)
        motivation_notes = _clean_text(request.motivation_notes)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            learning_goal,
            topics,
            current_level,
            timeline,
            available_time,
            resources,
            weak_areas,
            preferred_methods,
            constraints,
            motivation_notes,
        )
        high_stakes_context = _high_stakes_context(learning_goal, topics, resources, weak_areas, constraints, motivation_notes)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "learnerName": learner_name,
            "learningGoal": learning_goal,
            "desiredOutputType": desired_output_type,
            "learningFocus": _learning_focus(learning_goal, topics, current_level, desired_output_type, thin_input),
            "baselineSummary": _baseline_summary(current_level, available_time, timeline, motivation_notes, thin_input),
            "topicMap": _topic_map(topics, weak_areas, resources),
            "studyPlan": _study_plan(learning_goal, topics, available_time, preferred_methods, constraints, timeline),
            "learningRoadmap": _learning_roadmap(learning_goal, topics, current_level, weak_areas, resources, timeline),
            "activeRecallPlan": _active_recall_plan(topics, weak_areas, preferred_methods),
            "feynmanDrills": _feynman_drills(topics, weak_areas, learning_goal),
            "spacedRepetitionPlan": _spaced_repetition_plan(topics, weak_areas, available_time, constraints),
            "weeklyReview": _weekly_review(learning_goal, topics, timeline, available_time, motivation_notes),
            "bossTest": _boss_test(learning_goal, topics, weak_areas, resources),
            "progressChecklist": _progress_checklist(learning_goal, topics, weak_areas, resources, timeline),
            "nextActions": _next_actions(desired_output_type, thin_input, high_stakes_context),
            "openQuestions": _open_questions(
                learning_goal,
                topics,
                current_level,
                timeline,
                available_time,
                resources,
                weak_areas,
                preferred_methods,
                constraints,
                motivation_notes,
            ),
            "warnings": _warnings(thin_input, high_stakes_context),
            "limitations": _limitations(thin_input, high_stakes_context),
            "safety": local_learning_study_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_learning_study_dashboard_summary()


def local_learning_study_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Learning / Study Coach Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/learning-study/local-plan",
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
        "schoolPortalAccess": False,
        "lmsAccess": False,
        "calendarAccess": False,
        "taskPersistence": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "externalAppWrites": False,
        "assignmentSubmission": False,
        "shellExecution": False,
        "mutation": False,
        "officialAcademicValidation": False,
        "gradeGuarantee": False,
        "examScoreGuarantee": False,
        "masteryCertification": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided learning and study notes"],
    }


def local_learning_study_safety() -> dict[str, bool]:
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
        "schoolPortalAccess": False,
        "lmsAccess": False,
        "calendarAccess": False,
        "taskPersistence": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "externalAppWrites": False,
        "assignmentSubmission": False,
        "shellExecution": False,
        "mutation": False,
        "officialAcademicValidation": False,
        "gradeGuarantee": False,
        "examScoreGuarantee": False,
        "masteryCertification": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "learning_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "learning_brief"


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
    learning_goal: str,
    topics: list[str],
    current_level: str,
    timeline: str,
    available_time: str,
    resources: list[str],
    weak_areas: list[str],
    preferred_methods: list[str],
    constraints: list[str],
    motivation_notes: str,
) -> bool:
    return not any(
        [
            learning_goal,
            topics,
            current_level,
            timeline,
            available_time,
            resources,
            weak_areas,
            preferred_methods,
            constraints,
            motivation_notes,
        ]
    )


def _high_stakes_context(
    learning_goal: str,
    topics: list[str],
    resources: list[str],
    weak_areas: list[str],
    constraints: list[str],
    motivation_notes: str,
) -> bool:
    text = " ".join(
        [learning_goal, " ".join(topics), " ".join(resources), " ".join(weak_areas), " ".join(constraints), motivation_notes]
    ).lower()
    terms = (
        "exam",
        "grade",
        "accommodation",
        "disability",
        "health",
        "medical",
        "official requirement",
        "course credit",
        "certification",
        "license",
        "graduation",
        "placement",
        "discipline",
        "academic probation",
    )
    return any(term in text for term in terms)


def _learning_focus(
    learning_goal: str,
    topics: list[str],
    current_level: str,
    desired_output_type: str,
    thin_input: bool,
) -> list[str]:
    if thin_input:
        return [
            "Capture the learning goal, topics, current level, available time, resources, weak areas, constraints, and review needs before choosing a study strategy.",
            "Keep the result as manual planning and prompts only because no school portal, LMS, file, calendar, task app, or external learning site is accessed.",
        ]
    focus = [f"Primary learning goal: {learning_goal}.", f"Requested output shape: {desired_output_type}."]
    if topics:
        focus.append("Topics to organize: " + "; ".join(topics) + ".")
    if current_level:
        focus.append(f"Current level from user input: {current_level}.")
    focus.append("Use this as a study-planning aid, not official tutoring, grade prediction, exam-score certainty, or mastery certification.")
    return focus


def _baseline_summary(
    current_level: str,
    available_time: str,
    timeline: str,
    motivation_notes: str,
    thin_input: bool,
) -> list[str]:
    if thin_input:
        return ["Baseline summary is limited until the user provides skill level, time, timeline, and motivation notes."]
    summary = []
    if current_level:
        summary.append(f"Starting level: {current_level}.")
    if available_time:
        summary.append(f"Available study time: {available_time}.")
    if timeline:
        summary.append(f"Timeline: {timeline}.")
    if motivation_notes:
        summary.append(f"Motivation notes: {motivation_notes}.")
    if not summary:
        summary.append("Add baseline notes so the study plan can match the learner's time and confidence.")
    return summary


def _topic_map(topics: list[str], weak_areas: list[str], resources: list[str]) -> list[dict[str, str]]:
    mapped_topics = topics or ["Topic to define manually"]
    topic_map: list[dict[str, str]] = []
    for topic in mapped_topics[:8]:
        topic_map.append(
            {
                "topic": topic,
                "studyPurpose": "Explain the concept, practice retrieval, and connect it to the learning goal.",
                "weakAreaLens": "; ".join(weak_areas) if weak_areas else "Add weak areas manually.",
                "resourcesToUse": "; ".join(resources) if resources else "Use only user-provided resources; no textbooks, files, websites, or LMS content are accessed.",
                "manualCheck": "Confirm official requirements, exam scope, accommodations, and grading expectations outside Jarvis.",
            }
        )
    return topic_map


def _study_plan(
    learning_goal: str,
    topics: list[str],
    available_time: str,
    preferred_methods: list[str],
    constraints: list[str],
    timeline: str,
) -> list[str]:
    plan = [
        "Start each session with a quick retrieval warmup before rereading notes.",
        "Study one small topic block at a time, then produce a short explanation from memory.",
        "End each session with a mistake log and one next-step question.",
    ]
    if learning_goal:
        plan.insert(0, f"Study plan anchor: {learning_goal}.")
    if topics:
        plan.append("Rotate through topics: " + "; ".join(topics[:8]) + ".")
    if available_time:
        plan.append(f"Fit sessions into the stated available time: {available_time}.")
    if preferred_methods:
        plan.append("Preferred methods to include: " + "; ".join(preferred_methods) + ".")
    if constraints:
        plan.append("Constraints to respect: " + "; ".join(constraints) + ".")
    if timeline:
        plan.append(f"Use the timeline as a manual pacing guide: {timeline}.")
    return plan


def _learning_roadmap(
    learning_goal: str,
    topics: list[str],
    current_level: str,
    weak_areas: list[str],
    resources: list[str],
    timeline: str,
) -> list[str]:
    roadmap = [
        "Define the outcome in learner language.",
        "Build foundation concepts before speed or exam-style practice.",
        "Convert weak areas into short practice loops.",
        "Schedule weekly review before adding more topics.",
    ]
    if learning_goal:
        roadmap.insert(0, f"Outcome: {learning_goal}.")
    if current_level:
        roadmap.append(f"Starting point: {current_level}.")
    if topics:
        roadmap.append("Topic order to refine manually: " + " -> ".join(topics[:8]) + ".")
    if weak_areas:
        roadmap.append("Weak-area focus: " + "; ".join(weak_areas) + ".")
    if resources:
        roadmap.append("User-provided resources to consult manually: " + "; ".join(resources) + ".")
    if timeline:
        roadmap.append(f"Roadmap pacing: {timeline}.")
    return roadmap


def _active_recall_plan(topics: list[str], weak_areas: list[str], preferred_methods: list[str]) -> list[dict[str, str]]:
    recall_topics = topics or weak_areas or ["Study topic to define manually"]
    prompts: list[dict[str, str]] = []
    for topic in recall_topics[:8]:
        prompts.append(
            {
                "topic": topic,
                "prompt": f"Without looking anything up, explain the key idea behind {topic}, then list two examples and one common mistake.",
                "check": "Compare the answer against user-provided notes or official materials outside Jarvis.",
                "methodFit": "; ".join(preferred_methods) if preferred_methods else "Use short written recall, spoken explanation, or practice questions.",
            }
        )
    return prompts


def _feynman_drills(topics: list[str], weak_areas: list[str], learning_goal: str) -> list[dict[str, str]]:
    drill_topics = topics or weak_areas or [learning_goal or "Study concept to define manually"]
    drills: list[dict[str, str]] = []
    for topic in drill_topics[:6]:
        drills.append(
            {
                "topic": topic,
                "simpleExplanation": f"Explain {topic} as if teaching a younger student.",
                "gapCheck": "Circle any sentence that uses jargon without explanation, then rewrite it with a concrete example.",
                "teachBack": "Record or write a two-minute teach-back from memory and compare it to trusted materials manually.",
            }
        )
    return drills


def _spaced_repetition_plan(
    topics: list[str],
    weak_areas: list[str],
    available_time: str,
    constraints: list[str],
) -> list[str]:
    plan = [
        "Review new material the same day with a short recall prompt.",
        "Review again after one day, three days, one week, and two weeks, adjusting manually for difficulty.",
        "Move missed items back to a shorter interval and mark easy items for lighter review.",
    ]
    if topics:
        plan.append("Items to schedule manually: " + "; ".join(topics[:8]) + ".")
    if weak_areas:
        plan.append("Give weak areas extra early repetitions: " + "; ".join(weak_areas) + ".")
    if available_time:
        plan.append(f"Keep review blocks inside available time: {available_time}.")
    if constraints:
        plan.append("Constraints to respect: " + "; ".join(constraints) + ".")
    plan.append("No cards are created in Anki, Notion, calendars, task apps, or external systems.")
    return plan


def _weekly_review(
    learning_goal: str,
    topics: list[str],
    timeline: str,
    available_time: str,
    motivation_notes: str,
) -> list[str]:
    review = [
        "Pick three concepts that felt strongest and three that still need work.",
        "Redo one hard prompt without notes.",
        "Update the next week's topic order based on mistakes, not vibes.",
        "Write one sentence explaining why the goal still matters.",
    ]
    if learning_goal:
        review.insert(0, f"Weekly review goal: {learning_goal}.")
    if topics:
        review.append("Topics to review: " + "; ".join(topics[:8]) + ".")
    if timeline:
        review.append(f"Timeline pressure to consider manually: {timeline}.")
    if available_time:
        review.append(f"Available review time: {available_time}.")
    if motivation_notes:
        review.append(f"Motivation reminder: {motivation_notes}.")
    return review


def _boss_test(
    learning_goal: str,
    topics: list[str],
    weak_areas: list[str],
    resources: list[str],
) -> list[dict[str, str]]:
    test_topics = topics or weak_areas or [learning_goal or "Study area to define manually"]
    tests: list[dict[str, str]] = []
    for topic in test_topics[:6]:
        tests.append(
            {
                "topic": topic,
                "challenge": f"Solve or explain a mixed problem involving {topic} without notes, then justify each step.",
                "passSignal": "The learner can explain the why, spot one trap, and correct one mistake without prompting.",
                "manualEvidence": "; ".join(resources) if resources else "Compare against user-provided notes or official materials outside Jarvis.",
            }
        )
    return tests


def _progress_checklist(
    learning_goal: str,
    topics: list[str],
    weak_areas: list[str],
    resources: list[str],
    timeline: str,
) -> list[str]:
    checklist = [
        "Goal can be stated in one sentence.",
        "Topics are ranked by importance and weakness.",
        "Each study session includes recall before review.",
        "Weak areas have specific practice prompts.",
        "Weekly review changes the next plan.",
        "Official requirements are confirmed outside Jarvis.",
    ]
    if learning_goal:
        checklist.append(f"Goal tracked manually: {learning_goal}.")
    if topics:
        checklist.append("Topic checklist: " + "; ".join(topics[:8]) + ".")
    if weak_areas:
        checklist.append("Weak-area checklist: " + "; ".join(weak_areas) + ".")
    if resources:
        checklist.append("Resource checklist from user input: " + "; ".join(resources) + ".")
    if timeline:
        checklist.append(f"Timeline checkpoint: {timeline}.")
    return checklist


def _next_actions(desired_output_type: str, thin_input: bool, high_stakes_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and mark which study claims need official confirmation.",
        "Add missing manual notes for topics, level, timeline, available time, resources, weak areas, methods, constraints, and motivation.",
        "Confirm course rules, exam scope, accommodations, and official requirements outside Jarvis before relying on the plan.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual learning context before using this for coursework, exams, certifications, or high-stakes decisions.")
    if high_stakes_context:
        actions.append("Ask official academic, accessibility, health, exam, or qualified professional sources to confirm high-stakes details.")
    return actions


def _open_questions(
    learning_goal: str,
    topics: list[str],
    current_level: str,
    timeline: str,
    available_time: str,
    resources: list[str],
    weak_areas: list[str],
    preferred_methods: list[str],
    constraints: list[str],
    motivation_notes: str,
) -> list[str]:
    questions = []
    if not learning_goal:
        questions.append("What learning goal should this plan support?")
    if not topics:
        questions.append("Which topics should be studied or reviewed?")
    if not current_level:
        questions.append("What is the learner's current level or confidence?")
    if not timeline:
        questions.append("What deadline, exam date, course timeline, or pacing window matters?")
    if not available_time:
        questions.append("How much study time is realistically available?")
    if not resources:
        questions.append("Which user-provided notes, books, classes, videos, or practice sets should be used manually?")
    if not weak_areas:
        questions.append("Which weak areas, mistakes, or confusing topics need extra practice?")
    if not preferred_methods:
        questions.append("Which methods fit best: recall, practice problems, teaching, summaries, flashcards, or review blocks?")
    if not constraints:
        questions.append("What schedule, access, accommodation, energy, or course constraints apply?")
    if not motivation_notes:
        questions.append("What motivation reminder should the plan preserve?")
    return questions[:8]


def _warnings(thin_input: bool, high_stakes_context: bool) -> list[str]:
    warnings = [
        "No school portals, LMS systems, textbooks, websites, files, calendars, task apps, Anki, Notion, Google Drive, GitHub, accounts, or external services are accessed.",
        "The response does not create flashcards, calendar events, tasks, study records, downloads, submissions, official validation, grade guarantees, exam score guarantees, or mastery certification.",
    ]
    if thin_input:
        warnings.insert(0, "The learning and study input is thin; results are a planning scaffold rather than a specific study recommendation.")
    if high_stakes_context:
        warnings.append("Official academic requirements, exams, accommodations, health concerns, and high-stakes education decisions need official or professional confirmation.")
    return warnings


def _limitations(thin_input: bool, high_stakes_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided learning goal, topics, level, schedule, resource, weak-area, method, constraint, and motivation notes.",
        "No school portal, LMS, calendar, task, file, app, account, Anki, Notion, Google Drive, GitHub, textbook, website, connector, browsing, scraping, download, persistence, submission, shell execution, or mutation behavior.",
        "No official tutoring, course credit, grade improvement certainty, exam score certainty, certification, academic validation, mastery validation, official validation, production readiness, or security certification claim.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete topics, timing, resources, weak areas, and constraints.")
    if high_stakes_context:
        limitations.append("Official academic requirements, exams, accommodations, health concerns, and high-stakes education decisions should be confirmed with official sources or qualified professionals.")
    return limitations
