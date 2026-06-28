from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_health_fitness_agent"
STATUS = "local_only"
MODE = "response_only_user_provided_health_fitness_planning"
SUPPORTED_OUTPUT_TYPES = (
    "fitness_brief",
    "workout_plan",
    "habit_plan",
    "nutrition_guidance",
    "recovery_plan",
    "weekly_routine",
    "progress_review",
    "safety_review",
)


@dataclass(frozen=True)
class LocalHealthFitnessRequest:
    primary_goal: str
    profile_name: str = ""
    current_fitness_level: str = ""
    age_range: str = ""
    height_weight_notes: str = ""
    schedule_notes: str = ""
    equipment_available: list[str] = field(default_factory=list)
    preferred_activities: list[str] = field(default_factory=list)
    disliked_activities: list[str] = field(default_factory=list)
    nutrition_notes: str = ""
    sleep_recovery_notes: str = ""
    constraints: list[str] = field(default_factory=list)
    injuries_or_limitations: list[str] = field(default_factory=list)
    habits_to_build: list[str] = field(default_factory=list)
    habits_to_reduce: list[str] = field(default_factory=list)
    desired_output_type: str = "fitness_brief"


class LocalHealthFitnessAgentService:
    def create_plan(self, request: LocalHealthFitnessRequest) -> dict[str, Any]:
        profile_name = _clean_text(request.profile_name) or "Untitled local wellness profile"
        primary_goal = _clean_text(request.primary_goal) or "Untitled local fitness goal"
        current_fitness_level = _clean_text(request.current_fitness_level)
        age_range = _clean_text(request.age_range)
        height_weight_notes = _clean_text(request.height_weight_notes)
        schedule_notes = _clean_text(request.schedule_notes)
        nutrition_notes = _clean_text(request.nutrition_notes)
        sleep_recovery_notes = _clean_text(request.sleep_recovery_notes)
        equipment_available = _clean_list(request.equipment_available)
        preferred_activities = _clean_list(request.preferred_activities)
        disliked_activities = _clean_list(request.disliked_activities)
        constraints = _clean_list(request.constraints)
        injuries_or_limitations = _clean_list(request.injuries_or_limitations)
        habits_to_build = _clean_list(request.habits_to_build)
        habits_to_reduce = _clean_list(request.habits_to_reduce)
        desired_output_type = _normalize_output_type(request.desired_output_type)
        combined_text = " ".join(
            [
                primary_goal,
                nutrition_notes,
                sleep_recovery_notes,
                " ".join(constraints),
                " ".join(injuries_or_limitations),
                " ".join(habits_to_build),
                " ".join(habits_to_reduce),
            ]
        )
        thin_input = _thin_input(
            current_fitness_level,
            age_range,
            height_weight_notes,
            schedule_notes,
            equipment_available,
            preferred_activities,
            nutrition_notes,
            sleep_recovery_notes,
            constraints,
            injuries_or_limitations,
            habits_to_build,
            habits_to_reduce,
        )
        injury_context = bool(injuries_or_limitations)
        unsafe_context = _looks_unsafe(combined_text)

        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "profileName": profile_name,
            "primaryGoal": primary_goal,
            "desiredOutputType": desired_output_type,
            "fitnessFocus": _fitness_focus(primary_goal, desired_output_type, preferred_activities, thin_input, unsafe_context),
            "baselineSummary": _baseline_summary(
                current_fitness_level,
                age_range,
                height_weight_notes,
                schedule_notes,
                equipment_available,
                constraints,
                injuries_or_limitations,
                thin_input,
            ),
            "goalSummary": _goal_summary(primary_goal, desired_output_type, unsafe_context),
            "scheduleStrategy": _schedule_strategy(schedule_notes, constraints, injury_context, unsafe_context),
            "workoutPlan": _workout_plan(
                primary_goal,
                current_fitness_level,
                equipment_available,
                preferred_activities,
                disliked_activities,
                constraints,
                injuries_or_limitations,
                unsafe_context,
            ),
            "habitPlan": _habit_plan(habits_to_build, habits_to_reduce, schedule_notes, thin_input),
            "nutritionGuidance": _nutrition_guidance(nutrition_notes, primary_goal, unsafe_context),
            "recoveryGuidance": _recovery_guidance(sleep_recovery_notes, constraints, injuries_or_limitations, unsafe_context),
            "progressReview": _progress_review(primary_goal, desired_output_type, unsafe_context),
            "safetyReview": _safety_review(constraints, injuries_or_limitations, unsafe_context),
            "nextActions": _next_actions(desired_output_type, thin_input, injury_context, unsafe_context),
            "openQuestions": _open_questions(
                current_fitness_level,
                schedule_notes,
                equipment_available,
                preferred_activities,
                nutrition_notes,
                sleep_recovery_notes,
                constraints,
                injuries_or_limitations,
            ),
            "warnings": _warnings(thin_input, injury_context, unsafe_context),
            "limitations": _limitations(thin_input, injury_context, unsafe_context),
            "safety": local_health_fitness_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_health_fitness_dashboard_summary()


def local_health_fitness_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Health/Fitness Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/health-fitness/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "healthConnectorAccess": False,
        "wearableAccess": False,
        "medicalRecordAccess": False,
        "pharmacyAccess": False,
        "insuranceAccess": False,
        "calendarAccess": False,
        "taskPersistence": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "shellExecution": False,
        "purchases": False,
        "emailSending": False,
        "publicPosting": False,
        "medicalDiagnosis": False,
        "treatmentPlan": False,
        "medicationAdvice": False,
        "supplementPrescription": False,
        "emergencyTriage": False,
        "clinicalValidation": False,
        "mutation": False,
        "limitations": ["based only on user-provided wellness, workout, habit, and nutrition-planning inputs"],
    }


def local_health_fitness_safety() -> dict[str, bool]:
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
        "healthConnectorAccess": False,
        "wearableAccess": False,
        "medicalRecordAccess": False,
        "pharmacyAccess": False,
        "insuranceAccess": False,
        "calendarAccess": False,
        "taskPersistence": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "shellExecution": False,
        "purchases": False,
        "emailSending": False,
        "publicPosting": False,
        "medicalDiagnosis": False,
        "treatmentPlan": False,
        "medicationAdvice": False,
        "supplementPrescription": False,
        "emergencyTriage": False,
        "clinicalValidation": False,
        "mutation": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "fitness_brief").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "fitness_brief"


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
    current_fitness_level: str,
    age_range: str,
    height_weight_notes: str,
    schedule_notes: str,
    equipment_available: list[str],
    preferred_activities: list[str],
    nutrition_notes: str,
    sleep_recovery_notes: str,
    constraints: list[str],
    injuries_or_limitations: list[str],
    habits_to_build: list[str],
    habits_to_reduce: list[str],
) -> bool:
    return not any(
        [
            current_fitness_level,
            age_range,
            height_weight_notes,
            schedule_notes,
            equipment_available,
            preferred_activities,
            nutrition_notes,
            sleep_recovery_notes,
            constraints,
            injuries_or_limitations,
            habits_to_build,
            habits_to_reduce,
        ]
    )


def _looks_unsafe(text: str) -> bool:
    lowered = text.lower()
    unsafe_terms = (
        "extreme weight loss",
        "rapid weight loss",
        "lose weight fast",
        "starve",
        "no food",
        "skip all meals",
        "dehydrate",
        "water cut",
        "overtrain",
        "two workouts a day",
        "train through pain",
        "ignore pain",
        "disordered eating",
        "purge",
        "laxative",
        "stimulant",
        "fat burner",
        "supplement stack",
        "injury but keep training",
    )
    return any(term in lowered for term in unsafe_terms)


def _fitness_focus(primary_goal: str, desired_output_type: str, preferred_activities: list[str], thin_input: bool, unsafe_context: bool) -> str:
    if unsafe_context:
        return "Reframe the goal toward gradual, sustainable, recovery-aware habits and professional review where needed."
    if thin_input:
        return f"Clarify a safe manual fitness plan for: {primary_goal}."
    if desired_output_type == "workout_plan":
        return f"Create a conservative manual workout outline for {primary_goal} using user-provided preferences."
    if desired_output_type == "habit_plan":
        return f"Turn {primary_goal} into small repeatable habits instead of a persistent task system."
    if desired_output_type == "nutrition_guidance":
        return f"Provide general non-clinical nutrition planning support for {primary_goal}."
    if desired_output_type == "recovery_plan":
        return f"Emphasize sleep, rest, soreness awareness, and recovery constraints for {primary_goal}."
    if desired_output_type == "weekly_routine":
        return f"Arrange a weekly manual routine for {primary_goal} without creating calendar items."
    if desired_output_type == "progress_review":
        return f"Define simple manual check-in prompts for {primary_goal}."
    if desired_output_type == "safety_review":
        return f"Review safety boundaries and professional-review triggers for {primary_goal}."
    if preferred_activities:
        return f"Build around preferred activity: {preferred_activities[0]}."
    return f"Create a local response-only fitness brief for: {primary_goal}."


def _baseline_summary(
    current_fitness_level: str,
    age_range: str,
    height_weight_notes: str,
    schedule_notes: str,
    equipment_available: list[str],
    constraints: list[str],
    injuries_or_limitations: list[str],
    thin_input: bool,
) -> list[str]:
    summary = ["Baseline is based only on the request body."]
    if current_fitness_level:
        summary.append(f"Current fitness level noted by user: {current_fitness_level}.")
    if age_range:
        summary.append(f"Age range noted by user: {age_range}.")
    if height_weight_notes:
        summary.append("Height/weight notes were provided but not clinically interpreted.")
    if schedule_notes:
        summary.append(f"Schedule note: {schedule_notes}.")
    if equipment_available:
        summary.append(f"Equipment available: {', '.join(equipment_available[:4])}.")
    if constraints:
        summary.append(f"Constraint to respect manually: {constraints[0]}.")
    if injuries_or_limitations:
        summary.append("Injury or limitation notes require conservative planning and qualified review when pain, uncertainty, or medical conditions are involved.")
    if thin_input:
        summary.append("Fitness baseline is thin; add schedule, activity, equipment, nutrition, recovery, and limitation details before relying on the plan.")
    return summary


def _goal_summary(primary_goal: str, desired_output_type: str, unsafe_context: bool) -> list[str]:
    if unsafe_context:
        return [
            f"Original goal: {primary_goal}.",
            "Safer framing: prioritize sustainable progress, adequate food and hydration, recovery, and stopping for pain or concerning symptoms.",
        ]
    return [
        f"Primary goal: {primary_goal}.",
        f"Requested output shape: {desired_output_type}.",
        "No weight-loss, muscle-gain, recovery, injury-prevention, disease-prevention, or medical outcome is guaranteed.",
    ]


def _schedule_strategy(schedule_notes: str, constraints: list[str], injury_context: bool, unsafe_context: bool) -> list[str]:
    strategy = []
    if schedule_notes:
        strategy.append(f"Use the stated schedule as a planning boundary: {schedule_notes}.")
    else:
        strategy.append("Choose a small number of realistic sessions before adding volume.")
    if constraints:
        strategy.append(f"Respect the first stated constraint: {constraints[0]}.")
    if injury_context or unsafe_context:
        strategy.append("Keep intensity conservative and pause for pain, worsening symptoms, dizziness, chest pain, fainting, or uncertainty.")
    strategy.append("No calendar event, reminder, task, health record, or persistent schedule was created.")
    return strategy


def _workout_plan(
    primary_goal: str,
    current_fitness_level: str,
    equipment_available: list[str],
    preferred_activities: list[str],
    disliked_activities: list[str],
    constraints: list[str],
    injuries_or_limitations: list[str],
    unsafe_context: bool,
) -> dict[str, list[str]]:
    activity = preferred_activities[0] if preferred_activities else "low-to-moderate activity"
    equipment = ", ".join(equipment_available[:3]) if equipment_available else "bodyweight or available household equipment"
    avoid_note = f"Avoid or replace disliked activity: {disliked_activities[0]}." if disliked_activities else "Avoid movements that feel painful or unsafe."
    limitation_note = (
        "Use only pain-free ranges and seek professional evaluation for injury, pain, medical conditions, or uncertainty."
        if injuries_or_limitations
        else "Scale effort so technique, breathing, and recovery stay manageable."
    )
    if unsafe_context:
        progression = "Do not add intensity to chase extreme outcomes; choose gradual progress and adequate recovery."
    else:
        progression = f"Progress slowly from the current level: {current_fitness_level or 'not specified'}."
    return {
        "warmup": [
            "Start with easy movement and mobility before harder work.",
            limitation_note,
        ],
        "strength": [
            f"Use {equipment} for basic controlled strength patterns.",
            avoid_note,
        ],
        "cardio": [
            f"Use {activity} at a conversational effort unless the user later provides a safer detailed baseline.",
            "Stop and seek appropriate help for alarming symptoms.",
        ],
        "mobility": [
            "Include gentle mobility for areas that feel stiff, without forcing range.",
            "Do not treat mobility notes as rehabilitation instructions.",
        ],
        "cooldown": [
            "Finish with easy breathing and light movement.",
            "Record subjective effort manually if useful.",
        ],
        "progressionNotes": [
            progression,
            f"Keep the plan aligned with the goal: {primary_goal}.",
            "No certified training plan, clinical safety validation, or outcome guarantee is provided.",
        ],
    }


def _habit_plan(habits_to_build: list[str], habits_to_reduce: list[str], schedule_notes: str, thin_input: bool) -> dict[str, list[str]]:
    build = habits_to_build or ["Choose one small wellness or movement habit to practice consistently."]
    reduce = habits_to_reduce or ["Choose one friction point to reduce without using shame, punishment, or extreme restriction."]
    daily_minimums = [
        "Pick a minimum action that can be completed safely on a low-energy day.",
        "Pair the habit with an existing routine if the user-provided schedule supports it.",
    ]
    if schedule_notes:
        daily_minimums.append(f"Anchor the habit around the stated schedule: {schedule_notes}.")
    if thin_input:
        daily_minimums.append("Add current habit context before treating this as a full habit plan.")
    return {
        "habitsToBuild": build[:5],
        "habitsToReduce": reduce[:5],
        "dailyMinimums": daily_minimums,
        "weeklyReview": [
            "Review what was realistic, what felt safe, and what should be simplified.",
            "Adjust manually without creating persistent tasks, reminders, or records.",
        ],
    }


def _nutrition_guidance(nutrition_notes: str, primary_goal: str, unsafe_context: bool) -> dict[str, list[str]]:
    principles = [
        "Use general balanced-meal planning rather than clinical calorie, macro, supplement, or medication prescriptions.",
        "Include enough food to support daily life, training, recovery, and mood.",
    ]
    if nutrition_notes:
        principles.append(f"User-provided nutrition context: {nutrition_notes}.")
    if unsafe_context:
        principles.append("Avoid extreme restriction, dehydration, stimulant misuse, purging, or training plans tied to unsafe food rules.")
    return {
        "generalPrinciples": principles,
        "mealStructureIdeas": [
            "Build simple meals around protein-containing foods, fiber-rich carbohydrates, fats, and preferred fruits or vegetables where appropriate.",
            "Plan convenient options for busy days instead of skipping meals by default.",
            f"Keep meal planning aligned with the stated goal without guaranteeing an outcome: {primary_goal}.",
        ],
        "hydrationNotes": [
            "Hydrate consistently and avoid intentional dehydration for appearance or scale changes.",
            "Seek qualified advice for medical conditions, heat exposure, faintness, or unusual symptoms.",
        ],
        "cautionNotes": [
            "No exact clinical calories, macros, supplements, medications, treatment, or eating-disorder guidance is prescribed.",
            "Medication questions, eating-disorder concerns, medical conditions, pregnancy, illness, or significant symptoms require qualified professional support.",
        ],
    }


def _recovery_guidance(sleep_recovery_notes: str, constraints: list[str], injuries_or_limitations: list[str], unsafe_context: bool) -> dict[str, list[str]]:
    return {
        "sleepFocus": [
            f"User-provided recovery note: {sleep_recovery_notes}." if sleep_recovery_notes else "Make sleep and recovery context explicit before increasing training volume.",
            "Use rest and energy levels as manual feedback.",
        ],
        "restDays": [
            "Include rest or easier days rather than pushing intensity every day.",
            f"Respect constraint during recovery planning: {constraints[0]}." if constraints else "Add constraints if rest-day planning needs more boundaries.",
        ],
        "sorenessGuidance": [
            "Mild soreness can be treated as a cue to scale effort, not as a reason to force more work.",
            "Pain, worsening symptoms, numbness, dizziness, chest pain, fainting, or uncertainty require stopping and seeking appropriate help.",
        ],
        "warningSigns": _professional_review_triggers(injuries_or_limitations, unsafe_context),
    }


def _progress_review(primary_goal: str, desired_output_type: str, unsafe_context: bool) -> dict[str, list[str]]:
    return {
        "simpleMetrics": [
            "Manual consistency notes.",
            "Subjective energy and recovery.",
            "Session difficulty.",
            "Pain-free movement quality.",
        ],
        "checkInQuestions": [
            f"Is the plan still aligned with {primary_goal}?",
            "What felt sustainable this week?",
            "What should be simplified before adding more?",
        ],
        "adjustmentRules": [
            "If recovery worsens, reduce volume or intensity and review basics.",
            "If pain or concerning symptoms appear, stop the relevant activity and seek appropriate professional review.",
            "If unsafe patterns appear, reframe toward gradual habits, adequate food, hydration, and rest.",
            f"Use the {desired_output_type} output as manual planning support only.",
        ],
    }


def _safety_review(constraints: list[str], injuries_or_limitations: list[str], unsafe_context: bool) -> dict[str, list[str]]:
    return {
        "constraints": constraints or ["No constraints were provided; add time, equipment, recovery, medical, or preference boundaries before relying on the plan."],
        "injuryOrLimitationNotes": injuries_or_limitations
        or ["No injury or limitation notes were provided; this does not mean activity is medically safe."],
        "professionalReviewTriggers": _professional_review_triggers(injuries_or_limitations, unsafe_context),
        "unsafePatternsToAvoid": [
            "Extreme dieting, dehydration, stimulant misuse, supplement prescription seeking, or skipping meals as a default.",
            "Training through pain, injury, severe fatigue, dizziness, chest pain, fainting, or alarming symptoms.",
            "Treating this response as diagnosis, treatment, emergency triage, medical clearance, rehabilitation, or clinical validation.",
        ],
    }


def _professional_review_triggers(injuries_or_limitations: list[str], unsafe_context: bool) -> list[str]:
    triggers = [
        "Pain, injury, medical conditions, medication questions, eating-disorder concerns, pregnancy, illness, or uncertainty.",
        "Emergency symptoms require emergency services or urgent local help as appropriate.",
    ]
    if injuries_or_limitations:
        triggers.append("User-provided injury or limitation notes should be reviewed by an appropriate qualified professional when pain, function, safety, or diagnosis is unclear.")
    if unsafe_context:
        triggers.append("Unsafe or extreme goal framing should be replaced with gradual, sustainable, professional-reviewed steps.")
    return triggers


def _next_actions(desired_output_type: str, thin_input: bool, injury_context: bool, unsafe_context: bool) -> list[str]:
    actions = []
    if thin_input:
        actions.append("Add fitness level, schedule, equipment, preferences, nutrition, recovery, constraints, and limitation context.")
    if injury_context:
        actions.append("Get qualified review for pain, injury, medical conditions, or uncertain limitations before increasing activity.")
    if unsafe_context:
        actions.append("Replace extreme or risky goals with gradual training, adequate food, hydration, rest, and conservative progression.")
    if desired_output_type == "workout_plan":
        actions.append("Choose the smallest safe first workout and keep it easy enough to recover from.")
    elif desired_output_type == "habit_plan":
        actions.append("Pick one habit to build and one friction point to reduce manually.")
    elif desired_output_type == "nutrition_guidance":
        actions.append("Plan a few balanced meal ideas without clinical calorie, macro, supplement, or medication targets.")
    elif desired_output_type == "recovery_plan":
        actions.append("Choose a rest and sleep focus before adding more training.")
    elif desired_output_type == "progress_review":
        actions.append("Review consistency, energy, recovery, and pain-free movement manually.")
    elif desired_output_type == "safety_review":
        actions.append("Resolve safety uncertainties before using any workout or nutrition suggestion.")
    else:
        actions.append("Use this response as local manual planning support only.")
    actions.append("Do not create tasks, reminders, calendar events, health records, files, purchases, posts, or messages from this response.")
    return actions[:6]


def _open_questions(
    current_fitness_level: str,
    schedule_notes: str,
    equipment_available: list[str],
    preferred_activities: list[str],
    nutrition_notes: str,
    sleep_recovery_notes: str,
    constraints: list[str],
    injuries_or_limitations: list[str],
) -> list[str]:
    questions = []
    if not current_fitness_level:
        questions.append("What is the current fitness level or recent activity baseline?")
    if not schedule_notes:
        questions.append("What weekly schedule is realistically available?")
    if not equipment_available:
        questions.append("What equipment or spaces are available?")
    if not preferred_activities:
        questions.append("Which activities feel enjoyable or acceptable?")
    if not nutrition_notes:
        questions.append("What general meal-planning context should be considered?")
    if not sleep_recovery_notes:
        questions.append("What sleep, soreness, stress, or recovery patterns matter?")
    if not constraints:
        questions.append("What constraints should the plan respect?")
    if not injuries_or_limitations:
        questions.append("Are there pain, injuries, medical conditions, or limitations that require professional review?")
    return questions


def _warnings(thin_input: bool, injury_context: bool, unsafe_context: bool) -> list[str]:
    warnings = []
    if thin_input:
        warnings.append("Health/fitness input is thin; output is a provisional local wellness planning scaffold.")
    if injury_context:
        warnings.append("Injury or limitation notes were provided; keep planning conservative and seek qualified evaluation for pain, medical conditions, or uncertainty.")
    if unsafe_context:
        warnings.append("Potentially unsafe goal framing detected; use safer gradual habits, adequate food, hydration, rest, and professional review where appropriate.")
    warnings.append("This response does not diagnose, treat, prescribe, provide emergency triage, validate medical safety, or guarantee outcomes.")
    return warnings


def _limitations(thin_input: bool, injury_context: bool, unsafe_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided wellness, workout, habit, and nutrition-planning inputs.",
        "No medical diagnosis, treatment plan, medication advice, supplement prescription, emergency triage, clinical interpretation, lab interpretation, medical safety validation, nutritionist review, trainer certification, wearable validation, health connector access, or outcome guarantee is provided.",
        "No Apple Health, Google Fit, Samsung Health, Fitbit, Garmin, Oura, Strava, insurance, pharmacy, hospital, clinic, EHR, lab, account, file, database, calendar, task, message, purchase, post, connector, or external service was accessed or changed.",
        "Pain, injury, medical conditions, eating-disorder concerns, medication questions, alarming symptoms, or emergency symptoms require qualified professional help or emergency services as appropriate.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add baseline, schedule, activity preferences, equipment, nutrition, recovery, constraints, and limitation context.")
    if injury_context:
        limitations.append("Injury or limitation notes are not interpreted clinically and should not be treated as medical clearance.")
    if unsafe_context:
        limitations.append("Unsafe or extreme inputs are reframed toward gradual, sustainable, recovery-aware planning rather than aggressive outcome chasing.")
    return limitations
