from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_emotional_reflection_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_emotional_reflection"
SUPPORTED_OUTPUT_TYPES = (
    "reflection_brief",
    "stress_review",
    "motivation_reset",
    "discipline_recovery",
    "confidence_plan",
    "journal_prompts",
    "resilience_plan",
    "red_yellow_day_plan",
)


@dataclass(frozen=True)
class LocalEmotionalReflectionRequest:
    reflection_goal: str
    profile_name: str = ""
    current_mood_notes: str = ""
    stressors: list[str] = field(default_factory=list)
    energy_notes: str = ""
    recent_wins: list[str] = field(default_factory=list)
    current_challenges: list[str] = field(default_factory=list)
    patterns_noticed: list[str] = field(default_factory=list)
    support_options: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    desired_output_type: str = "reflection_brief"


class LocalEmotionalReflectionAgentService:
    def create_plan(self, request: LocalEmotionalReflectionRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Local emotional reflection profile"
        reflection_goal = _clean_text(request.reflection_goal)
        current_mood_notes = _clean_text(request.current_mood_notes)
        stressors = _clean_list(request.stressors)
        energy_notes = _clean_text(request.energy_notes)
        recent_wins = _clean_list(request.recent_wins)
        current_challenges = _clean_list(request.current_challenges)
        patterns_noticed = _clean_list(request.patterns_noticed)
        support_options = _clean_list(request.support_options)
        constraints = _clean_list(request.constraints)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        thin_input = _thin_input(
            reflection_goal,
            current_mood_notes,
            stressors,
            energy_notes,
            recent_wins,
            current_challenges,
            patterns_noticed,
            support_options,
            constraints,
        )
        high_risk_context = _high_risk_context(
            reflection_goal,
            current_mood_notes,
            stressors,
            energy_notes,
            current_challenges,
            patterns_noticed,
            support_options,
            constraints,
        )
        harmful_context = _harmful_context(
            reflection_goal,
            current_mood_notes,
            stressors,
            current_challenges,
            patterns_noticed,
            constraints,
        )

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "reflectionGoal": reflection_goal,
            "desiredOutputType": desired_output_type,
            "reflectionFocus": _reflection_focus(reflection_goal, desired_output_type, thin_input, high_risk_context, harmful_context),
            "situationSummary": _situation_summary(current_mood_notes, stressors, energy_notes, recent_wins, current_challenges, patterns_noticed, support_options, constraints, thin_input),
            "stressReview": _stress_review(stressors, current_challenges, energy_notes, high_risk_context),
            "motivationReset": _motivation_reset(reflection_goal, recent_wins, energy_notes, constraints),
            "disciplineRecovery": _discipline_recovery(reflection_goal, current_challenges, patterns_noticed, constraints),
            "confidencePlan": _confidence_plan(recent_wins, current_challenges, support_options, harmful_context),
            "journalPrompts": _journal_prompts(reflection_goal, current_mood_notes, patterns_noticed, support_options, high_risk_context),
            "resiliencePlan": _resilience_plan(stressors, current_challenges, support_options, constraints, high_risk_context, harmful_context),
            "redYellowDayPlan": _red_yellow_day_plan(energy_notes, stressors, support_options, constraints, high_risk_context),
            "nextActions": _next_actions(desired_output_type, thin_input, high_risk_context, harmful_context),
            "openQuestions": _open_questions(reflection_goal, current_mood_notes, stressors, energy_notes, recent_wins, current_challenges, patterns_noticed, support_options, constraints),
            "warnings": _warnings(thin_input, high_risk_context, harmful_context),
            "limitations": _limitations(thin_input, high_risk_context, harmful_context),
            "safety": local_emotional_reflection_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_emotional_reflection_dashboard_summary()


def local_emotional_reflection_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Emotional Reflection / Resilience Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/emotional-reflection/local-reflect",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
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
        "dbWrites": False,
        "taskPersistence": False,
        "calendarAccess": False,
        "messageSending": False,
        "contactAccess": False,
        "healthDataAccess": False,
        "wearableAccess": False,
        "shellExecution": False,
        "mutation": False,
        "therapyClaims": False,
        "diagnosis": False,
        "treatmentPlan": False,
        "crisisIntervention": False,
        "medicalValidation": False,
        "psychiatricValidation": False,
        "medicationAdvice": False,
        "outcomeGuarantee": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided emotional reflection and resilience notes"],
    }


def local_emotional_reflection_safety() -> dict[str, bool]:
    summary = local_emotional_reflection_dashboard_summary().copy()
    summary.pop("agentId", None)
    summary.pop("name", None)
    summary.pop("status", None)
    summary.pop("mode", None)
    summary.pop("endpoint", None)
    summary.pop("outputTypes", None)
    summary.pop("limitations", None)
    return summary


def _normalize_output_type(value: str) -> str:
    normalized = (value or "reflection_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "reflection_brief"


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
    reflection_goal: str,
    current_mood_notes: str,
    stressors: list[str],
    energy_notes: str,
    recent_wins: list[str],
    current_challenges: list[str],
    patterns_noticed: list[str],
    support_options: list[str],
    constraints: list[str],
) -> bool:
    return not any([reflection_goal, current_mood_notes, stressors, energy_notes, recent_wins, current_challenges, patterns_noticed, support_options, constraints])


def _high_risk_context(*parts: object) -> bool:
    text = _joined_text(parts)
    terms = (
        "self-harm",
        "suicide",
        "suicidal",
        "kill myself",
        "hurt myself",
        "abuse",
        "violence",
        "immediate danger",
        "crisis",
        "severe distress",
        "medical issue",
        "panic attack",
        "unsafe",
    )
    return any(term in text for term in terms)


def _harmful_context(*parts: object) -> bool:
    text = _joined_text(parts)
    terms = (
        "harm others",
        "hurt someone",
        "abuse someone",
        "coerce",
        "evade help",
        "avoid support",
        "isolate from support",
        "hide from everyone",
    )
    return any(term in text for term in terms)


def _joined_text(parts: object) -> str:
    flattened: list[str] = []
    for part in parts:
        if isinstance(part, list):
            flattened.extend(str(item) for item in part)
        else:
            flattened.append(str(part))
    return " ".join(flattened).lower()


def _reflection_focus(reflection_goal: str, desired_output_type: str, thin_input: bool, high_risk_context: bool, harmful_context: bool) -> list[str]:
    if thin_input:
        return [
            "Capture the reflection goal, mood notes, stressors, energy notes, wins, challenges, patterns, support options, and constraints before relying on the plan.",
            "Keep this as local reflection and resilience planning only, not therapy, diagnosis, treatment, crisis intervention, or validation.",
        ]
    if high_risk_context:
        return [
            "Prioritize immediate human, professional, or emergency support where self-harm, suicidal thoughts, abuse, violence, immediate danger, severe distress, medical issues, or crisis language is present.",
            "Use the rest of the response only as a non-clinical support-prep checklist based on user-provided notes.",
        ]
    if harmful_context:
        return [
            "Redirect the reflection toward safety, accountability, non-harm, and staying connected to appropriate support.",
            "Do not use this plan to encourage harm, abuse, coercion, evasion, or isolation from support.",
        ]
    return [
        f"Reflection goal: {reflection_goal}.",
        f"Requested output shape: {desired_output_type}.",
        "Use this as non-clinical reflection, resilience planning, and next-step organization from user-provided notes only.",
    ]


def _situation_summary(
    current_mood_notes: str,
    stressors: list[str],
    energy_notes: str,
    recent_wins: list[str],
    current_challenges: list[str],
    patterns_noticed: list[str],
    support_options: list[str],
    constraints: list[str],
    thin_input: bool,
) -> list[str]:
    if thin_input:
        return ["Situation summary is limited until the user provides mood, stress, energy, wins, challenges, patterns, support options, or constraints."]
    summary = []
    if current_mood_notes:
        summary.append(f"Current mood notes: {current_mood_notes}.")
    if stressors:
        summary.append("Stressors: " + "; ".join(stressors) + ".")
    if energy_notes:
        summary.append(f"Energy notes: {energy_notes}.")
    if recent_wins:
        summary.append("Recent wins: " + "; ".join(recent_wins) + ".")
    if current_challenges:
        summary.append("Current challenges: " + "; ".join(current_challenges) + ".")
    if patterns_noticed:
        summary.append("Patterns noticed: " + "; ".join(patterns_noticed) + ".")
    if support_options:
        summary.append("Support options from user input: " + "; ".join(support_options) + ".")
    if constraints:
        summary.append("Constraints: " + "; ".join(constraints) + ".")
    return summary


def _stress_review(stressors: list[str], current_challenges: list[str], energy_notes: str, high_risk_context: bool) -> list[str]:
    review = [
        "Separate what is happening, what it means emotionally, and what small step is controllable today.",
        "Look for stress load, recovery gap, avoided decision, unclear expectation, or overcommitment patterns.",
    ]
    if stressors:
        review.insert(0, "Stressors to review: " + "; ".join(stressors) + ".")
    if current_challenges:
        review.append("Current challenges to sort: " + "; ".join(current_challenges) + ".")
    if energy_notes:
        review.append(f"Energy context: {energy_notes}.")
    if high_risk_context:
        review.append("High-risk distress should be handled with immediate human, professional, or emergency support as appropriate.")
    return review


def _motivation_reset(reflection_goal: str, recent_wins: list[str], energy_notes: str, constraints: list[str]) -> list[str]:
    plan = [
        "Lower the restart step until it is small enough to begin without bargaining.",
        "Define a ten-minute version, a normal version, and a recovery-only version.",
        "Treat motivation as a signal to support, not a requirement for action.",
    ]
    if reflection_goal:
        plan.insert(0, f"Motivation reset goal: {reflection_goal}.")
    if recent_wins:
        plan.append("Use recent wins as evidence: " + "; ".join(recent_wins[:5]) + ".")
    if energy_notes:
        plan.append(f"Match the first step to current energy: {energy_notes}.")
    if constraints:
        plan.append("Constraints to respect: " + "; ".join(constraints) + ".")
    return plan


def _discipline_recovery(reflection_goal: str, current_challenges: list[str], patterns_noticed: list[str], constraints: list[str]) -> list[str]:
    plan = [
        "Name the lapse without turning it into identity evidence.",
        "Restart with one visible action and one environmental adjustment.",
        "Choose a repeatable minimum standard for red, yellow, and green days.",
    ]
    if reflection_goal:
        plan.insert(0, f"Discipline recovery focus: {reflection_goal}.")
    if current_challenges:
        plan.append("Challenges to recover around: " + "; ".join(current_challenges[:5]) + ".")
    if patterns_noticed:
        plan.append("Patterns to watch: " + "; ".join(patterns_noticed[:5]) + ".")
    if constraints:
        plan.append("Constraints: " + "; ".join(constraints) + ".")
    return plan


def _confidence_plan(recent_wins: list[str], current_challenges: list[str], support_options: list[str], harmful_context: bool) -> list[str]:
    if harmful_context:
        return ["Build confidence through non-harm, accountability, repair, and appropriate support rather than isolation, coercion, or evasion."]
    plan = [
        "List evidence before feelings: what has already worked, even partly.",
        "Choose one challenge where progress can be observed within a day.",
        "Use confidence as earned trust from kept promises, not as forced positivity.",
    ]
    if recent_wins:
        plan.insert(0, "Evidence from recent wins: " + "; ".join(recent_wins[:5]) + ".")
    if current_challenges:
        plan.append("Confidence practice area: " + current_challenges[0] + ".")
    if support_options:
        plan.append("Support that may reinforce confidence: " + "; ".join(support_options[:4]) + ".")
    return plan


def _journal_prompts(reflection_goal: str, current_mood_notes: str, patterns_noticed: list[str], support_options: list[str], high_risk_context: bool) -> list[str]:
    prompts = [
        "What am I feeling, and what evidence do I have for the story I am telling myself?",
        "What would make today one notch safer, steadier, or easier?",
        "What is one promise I can keep today without overreaching?",
    ]
    if reflection_goal:
        prompts.insert(0, f"What would progress on '{reflection_goal}' look like in plain behavior?")
    if current_mood_notes:
        prompts.append(f"What does the current mood note suggest I need: {current_mood_notes}?")
    if patterns_noticed:
        prompts.append("Which pattern is showing up again: " + "; ".join(patterns_noticed[:3]) + "?")
    if support_options:
        prompts.append("Which support option could I use without making this harder: " + "; ".join(support_options[:3]) + "?")
    if high_risk_context:
        prompts.append("Who can I contact right now for immediate human, professional, or emergency support?")
    return prompts


def _resilience_plan(stressors: list[str], current_challenges: list[str], support_options: list[str], constraints: list[str], high_risk_context: bool, harmful_context: bool) -> list[str]:
    plan = [
        "Reduce load where possible, restore basics, and take one grounded next step.",
        "Use support early enough that it is preventive, not only a last resort.",
        "Review what helped after the day is over and keep the next plan smaller than pride wants.",
    ]
    if stressors:
        plan.insert(0, "Stress load to reduce or contain: " + "; ".join(stressors[:5]) + ".")
    if current_challenges:
        plan.append("Challenge to approach in sequence: " + "; ".join(current_challenges[:4]) + ".")
    if support_options:
        plan.append("Support options: " + "; ".join(support_options[:5]) + ".")
    if constraints:
        plan.append("Constraints to honor: " + "; ".join(constraints) + ".")
    if high_risk_context:
        plan.append("High-risk language means this plan should be secondary to immediate human, professional, or emergency help.")
    if harmful_context:
        plan.append("Do not use resilience planning to isolate, evade support, coerce, abuse, or harm anyone.")
    return plan


def _red_yellow_day_plan(energy_notes: str, stressors: list[str], support_options: list[str], constraints: list[str], high_risk_context: bool) -> list[str]:
    plan = [
        "Green day: do the normal plan and capture one useful note.",
        "Yellow day: shrink the plan to one priority, one recovery step, and one support check.",
        "Red day: cover basics, avoid major optional decisions, and use support rather than isolation.",
    ]
    if energy_notes:
        plan.append(f"Energy cue: {energy_notes}.")
    if stressors:
        plan.append("Red/yellow triggers to watch: " + "; ".join(stressors[:4]) + ".")
    if support_options:
        plan.append("Support options for red/yellow days: " + "; ".join(support_options[:4]) + ".")
    if constraints:
        plan.append("Constraints: " + "; ".join(constraints[:4]) + ".")
    if high_risk_context:
        plan.append("If red-day notes include danger, self-harm, suicidal thoughts, abuse, violence, severe distress, or medical issues, seek immediate human, professional, or emergency support.")
    return plan


def _next_actions(desired_output_type: str, thin_input: bool, high_risk_context: bool, harmful_context: bool) -> list[str]:
    actions = [
        f"Review the {desired_output_type} response and remove anything that feels overclaimed, clinical, unsafe, or disconnected from the user-provided notes.",
        "Pick one small reflection prompt, one recovery step, and one support option to consider manually.",
        "Add missing mood, stress, energy, win, challenge, pattern, support, and constraint notes before relying on the plan.",
    ]
    if thin_input:
        actions.insert(0, "Add enough manual context before using this for stress, motivation, discipline, confidence, journaling, resilience, or red/yellow-day planning.")
    if high_risk_context:
        actions.append("Use immediate human, professional, medical, safety, or emergency support for self-harm, suicidal thoughts, abuse, violence, immediate danger, severe distress, medical issues, or crisis language.")
    if harmful_context:
        actions.append("Redirect away from harm, abuse, coercion, evasion, or isolation from support.")
    return actions


def _open_questions(
    reflection_goal: str,
    current_mood_notes: str,
    stressors: list[str],
    energy_notes: str,
    recent_wins: list[str],
    current_challenges: list[str],
    patterns_noticed: list[str],
    support_options: list[str],
    constraints: list[str],
) -> list[str]:
    questions = []
    if not reflection_goal:
        questions.append("What reflection, stress, motivation, confidence, discipline recovery, or resilience goal should this support?")
    if not current_mood_notes:
        questions.append("What mood notes should the plan consider?")
    if not stressors:
        questions.append("What stressors are currently active?")
    if not energy_notes:
        questions.append("What does energy feel like today?")
    if not recent_wins:
        questions.append("What recent wins or proof of effort should be included?")
    if not current_challenges:
        questions.append("What challenges or friction points need a recovery plan?")
    if not patterns_noticed:
        questions.append("What patterns have repeated recently?")
    if not support_options:
        questions.append("What safe support options are available?")
    if not constraints:
        questions.append("What time, privacy, energy, health, family, school, work, or safety constraints apply?")
    return questions[:8]


def _warnings(thin_input: bool, high_risk_context: bool, harmful_context: bool) -> list[str]:
    warnings = [
        "No journals, files, health records, messages, contacts, accounts, calendars, tasks, wearables, connectors, paid APIs, browsing, or external services are accessed.",
        "The response does not persist records, create tasks or reminders, send messages, contact anyone, schedule appointments, mutate files, or write to a database.",
        "No therapy, diagnosis, treatment, crisis intervention, medical advice, psychiatric advice, medication advice, mental-health validation, medical validation, outcome guarantee, production readiness, or certification is claimed.",
    ]
    if thin_input:
        warnings.insert(0, "The emotional reflection input is thin; results are a planning scaffold rather than specific emotional or resilience guidance.")
    if high_risk_context:
        warnings.append("Self-harm, suicidal thoughts, abuse, violence, immediate danger, severe distress, medical issues, or crisis language needs immediate human, professional, medical, safety, or emergency support as appropriate.")
    if harmful_context:
        warnings.append("Instructions encouraging self-harm, harm to others, abuse, coercion, evasion, or isolation from support are not supported.")
    return warnings


def _limitations(thin_input: bool, high_risk_context: bool, harmful_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided reflection goal, mood notes, stressors, energy notes, recent wins, challenges, patterns, support options, and constraints.",
        "No journal, file, health-record, message, contact, account, calendar, task, wearable, connector, browser, paid API, or external-service behavior.",
        "No persistence, task creation, reminder creation, messaging, appointment scheduling, contact action, database write, shell execution, file mutation, therapy claim, diagnosis, treatment plan, crisis intervention, medical validation, psychiatric validation, medication advice, mental-health validation, outcome guarantee, security certification, or certification claim.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity until the user supplies concrete mood, stress, energy, wins, challenges, patterns, support options, and constraints.")
    if high_risk_context:
        limitations.append("Self-harm, suicidal thoughts, abuse, violence, immediate danger, severe distress, medical issues, and crisis language should be handled with immediate human, professional, medical, safety, or emergency support as appropriate.")
    if harmful_context:
        limitations.append("Harm to self, harm to others, abuse, coercion, evasion, and isolation from support must be redirected toward safety and appropriate support.")
    return limitations
