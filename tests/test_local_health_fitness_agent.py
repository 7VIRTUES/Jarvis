import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_health_fitness_agent import LocalHealthFitnessAgentService, LocalHealthFitnessRequest


def test_local_health_fitness_endpoint_returns_structured_local_plan():
    payload = app_module.LocalHealthFitnessInput(
        profileName="Local Wellness Plan",
        primaryGoal="Build a steady beginner strength and walking routine.",
        currentFitnessLevel="Beginner returning to consistent activity.",
        ageRange="adult",
        heightWeightNotes="General body-composition goals only.",
        scheduleNotes="Three short weekday sessions and one longer weekend walk.",
        equipmentAvailable=["Adjustable dumbbells", "Yoga mat"],
        preferredActivities=["Walking", "Strength training"],
        dislikedActivities=["High-impact jumping"],
        nutritionNotes="Wants simple balanced meal planning ideas.",
        sleepRecoveryNotes="Wants to improve sleep consistency.",
        constraints=["Keep sessions short"],
        injuriesOrLimitations=["Use conservative intensity and seek professional review for pain."],
        habitsToBuild=["Walk after lunch"],
        habitsToReduce=["Skipping movement on busy days"],
        desiredOutputType="fitness_brief",
    )

    result = app_module.create_local_health_fitness_plan(payload)

    assert result["agentId"] == "local_health_fitness_agent"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_health_fitness_planning"
    assert result["profileName"] == "Local Wellness Plan"
    assert result["primaryGoal"] == "Build a steady beginner strength and walking routine."
    assert result["desiredOutputType"] == "fitness_brief"
    assert result["fitnessFocus"]
    assert result["baselineSummary"]
    assert result["goalSummary"]
    assert result["scheduleStrategy"]
    assert result["workoutPlan"]
    assert result["habitPlan"]
    assert result["nutritionGuidance"]
    assert result["recoveryGuidance"]
    assert result["progressReview"]
    assert result["safetyReview"]
    assert result["nextActions"]
    assert result["openQuestions"]
    assert result["warnings"]
    assert "Based only on user-provided wellness" in result["limitations"][0]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("fitness_brief", "fitness_brief"),
        ("workout_plan", "workout_plan"),
        ("habit_plan", "habit_plan"),
        ("nutrition_guidance", "nutrition_guidance"),
        ("recovery_plan", "recovery_plan"),
        ("weekly_routine", "weekly_routine"),
        ("progress_review", "progress_review"),
        ("safety_review", "safety_review"),
        (" WORKOUT_PLAN ", "workout_plan"),
    ],
)
def test_local_health_fitness_supported_output_types_normalize(requested, expected):
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Build consistency",
            current_fitness_level="Beginner",
            desired_output_type=requested,
        )
    )

    assert result["desiredOutputType"] == expected


def test_local_health_fitness_unsupported_output_type_falls_back_safely():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Build consistency",
            current_fitness_level="Beginner",
            desired_output_type="clinically_validated_plan",
        )
    )

    assert result["desiredOutputType"] == "fitness_brief"
    assert result["safety"]["clinicalValidation"] is False
    assert result["safety"]["medicalDiagnosis"] is False


def test_local_health_fitness_thin_input_reports_warnings_and_limitations():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(LocalHealthFitnessRequest(primary_goal="Get healthier"))

    assert any("Health/fitness input is thin" in warning for warning in result["warnings"])
    assert any("Thin input limits specificity" in limitation for limitation in result["limitations"])
    assert result["openQuestions"]
    assert result["fitnessFocus"]
    assert result["nextActions"]


def test_local_health_fitness_workout_plan_contains_required_sections():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Build a beginner workout routine",
            current_fitness_level="Beginner",
            equipment_available=["Dumbbells"],
            preferred_activities=["Walking"],
            desired_output_type="workout_plan",
        )
    )

    assert set(result["workoutPlan"]) == {
        "warmup",
        "strength",
        "cardio",
        "mobility",
        "cooldown",
        "progressionNotes",
    }
    assert all(result["workoutPlan"][key] for key in result["workoutPlan"])


def test_local_health_fitness_habit_plan_contains_required_sections():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Build consistent daily movement",
            habits_to_build=["Walk after lunch"],
            habits_to_reduce=["Long inactive stretches"],
            desired_output_type="habit_plan",
        )
    )

    assert set(result["habitPlan"]) == {"habitsToBuild", "habitsToReduce", "dailyMinimums", "weeklyReview"}
    assert "Walk after lunch" in result["habitPlan"]["habitsToBuild"]
    assert "Long inactive stretches" in result["habitPlan"]["habitsToReduce"]


def test_local_health_fitness_nutrition_guidance_is_general_not_clinical_prescription():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Support workouts with better meals",
            nutrition_notes="Needs simple meal ideas for busy days.",
            desired_output_type="nutrition_guidance",
        )
    )
    guidance = result["nutritionGuidance"]
    guidance_text = str(guidance).lower()

    assert set(guidance) == {"generalPrinciples", "mealStructureIdeas", "hydrationNotes", "cautionNotes"}
    assert "general balanced-meal planning" in guidance_text
    assert "no exact clinical calories" in guidance_text
    assert "supplements" in guidance_text
    assert "medications" in guidance_text


def test_local_health_fitness_recovery_plan_contains_required_sections():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Recover better between workouts",
            sleep_recovery_notes="Sleep has been inconsistent.",
            desired_output_type="recovery_plan",
        )
    )

    assert set(result["recoveryGuidance"]) == {"sleepFocus", "restDays", "sorenessGuidance", "warningSigns"}
    assert result["recoveryGuidance"]["warningSigns"]


def test_local_health_fitness_progress_review_contains_required_sections():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Review weekly training consistency",
            desired_output_type="progress_review",
        )
    )

    assert set(result["progressReview"]) == {"simpleMetrics", "checkInQuestions", "adjustmentRules"}
    assert result["progressReview"]["simpleMetrics"]
    assert result["progressReview"]["checkInQuestions"]
    assert result["progressReview"]["adjustmentRules"]


def test_local_health_fitness_safety_review_contains_required_sections():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Review safe exercise boundaries",
            constraints=["Keep workouts low impact"],
            injuries_or_limitations=["Knee discomfort needs professional review if it persists."],
            desired_output_type="safety_review",
        )
    )

    assert set(result["safetyReview"]) == {
        "constraints",
        "injuryOrLimitationNotes",
        "professionalReviewTriggers",
        "unsafePatternsToAvoid",
    }
    assert result["safetyReview"]["constraints"] == ["Keep workouts low impact"]
    assert result["safetyReview"]["injuryOrLimitationNotes"]


def test_local_health_fitness_injury_inputs_produce_conservative_warnings():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Return to walking",
            injuries_or_limitations=["Ankle pain after longer walks"],
        )
    )

    assert any("Injury or limitation notes were provided" in warning for warning in result["warnings"])
    assert any("qualified evaluation" in warning for warning in result["warnings"])
    assert any("not interpreted clinically" in limitation for limitation in result["limitations"])


def test_local_health_fitness_unsafe_inputs_produce_safer_alternative_framing():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Extreme weight loss and train through pain",
            nutrition_notes="Skip all meals and dehydrate before weigh-in.",
            desired_output_type="safety_review",
        )
    )
    output_text = str(result).lower()

    assert any("Potentially unsafe goal framing detected" in warning for warning in result["warnings"])
    assert "safer framing" in output_text
    assert "gradual" in output_text
    assert "adequate food" in output_text
    assert "hydration" in output_text
    assert "recovery-aware" in output_text


def test_local_health_fitness_output_does_not_claim_medical_or_outcome_validation():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(
        LocalHealthFitnessRequest(
            primary_goal="Build strength safely",
            current_fitness_level="Beginner",
            nutrition_notes="Wants general meal planning support.",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "diagnosis provided",
        "treatment plan provided",
        "medication advice provided",
        "supplement prescription provided",
        "emergency triage provided",
        "clinically validated",
        "medical safety validated",
        "wearable validated",
        "health connector accessed",
        "guaranteed weight loss",
        "guaranteed muscle gain",
        "trainer certified",
        "nutritionist reviewed",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no medical diagnosis" in output_text
    assert "no apple health" in output_text
    assert "outcome guarantee" in output_text


def test_local_health_fitness_safety_flags_disable_external_health_and_mutation_behavior():
    service = LocalHealthFitnessAgentService()

    result = service.create_plan(LocalHealthFitnessRequest(primary_goal="Build a local routine"))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["paidApis"] is False
    assert safety["webBrowsing"] is False
    assert safety["connectorExecution"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["healthConnectorAccess"] is False
    assert safety["wearableAccess"] is False
    assert safety["medicalRecordAccess"] is False
    assert safety["pharmacyAccess"] is False
    assert safety["insuranceAccess"] is False
    assert safety["calendarAccess"] is False
    assert safety["taskPersistence"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["shellExecution"] is False
    assert safety["purchases"] is False
    assert safety["emailSending"] is False
    assert safety["publicPosting"] is False
    assert safety["medicalDiagnosis"] is False
    assert safety["treatmentPlan"] is False
    assert safety["medicationAdvice"] is False
    assert safety["supplementPrescription"] is False
    assert safety["emergencyTriage"] is False
    assert safety["clinicalValidation"] is False
    assert safety["mutation"] is False


def test_local_health_fitness_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_health_fitness_agent").local_health_fitness_agent).lower()
    forbidden = [
        "requests",
        "httpx",
        "urllib.request",
        "socket",
        "subprocess",
        "open(",
        "read_text",
        "read_bytes",
        "write_text",
        ".write(",
        "sqlite",
        "taskqueue",
        "gmail.",
        "google_calendar",
        "smtp.",
        "imap.",
        "openai",
        "anthropic",
        "gemini",
    ]

    assert all(token not in source for token in forbidden)


def test_local_health_fitness_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalHealthFitnessInput.model_validate(
            {
                "primaryGoal": "Build consistency",
                "wearableAccount": "not allowed",
            }
        )


def test_local_health_fitness_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/health-fitness/local-plan"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
