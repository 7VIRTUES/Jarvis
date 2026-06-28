import inspect

import pytest
from pydantic import ValidationError

import jarvis_core.app as app_module
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.local_food_cooking_grocery_agent import (
    LocalFoodCookingGroceryAgentService,
    LocalFoodCookingGroceryRequest,
)


def test_local_food_cooking_grocery_endpoint_returns_structured_local_plan():
    payload = app_module.LocalFoodCookingGroceryInput(
        request="Turn these pantry items into a simple 30-minute dinner.",
        outputType="simple_recipe",
        mealGoal="Make a quick dinner from pantry items.",
        availableIngredients=["Rice", "Eggs", "Frozen vegetables"],
        pantryItems=["Soy sauce", "Garlic powder"],
        groceryItemsNeeded=["Green onions"],
        dietaryPreferences=["Simple high-protein meals"],
        allergiesOrAvoidances=["No known allergies provided"],
        budgetLevel="low",
        budgetNotes="Use pantry items first.",
        servings="2 servings",
        timeAvailableMinutes=30,
        cookingSkillLevel="beginner",
        kitchenEquipment=["Stove", "Skillet"],
        mealType="dinner",
        cuisinePreferences=["Flexible"],
        leftoversOrBatchPrepGoal="Use leftovers for lunch.",
        constraintsOrNotes="Manual planning only.",
    )

    result = app_module.create_local_food_cooking_grocery_plan(payload)

    assert result["agent_id"] == "local_food_cooking_grocery"
    assert result["agentId"] == "local_food_cooking_grocery"
    assert result["status"] == "local_only"
    assert result["mode"] == "response_only_user_provided_food_cooking_grocery_planning"
    assert result["output_type"] == "simple_recipe"
    assert result["title"]
    assert result["summary"]
    assert result["assumptions"]
    assert result["recommended_plan"]
    assert result["ingredients_or_items"]
    assert result["step_by_step"]
    assert result["grocery_list"]
    assert result["budget_notes"]
    assert result["time_estimate"]
    assert result["safety_notes"]
    assert result["limitations"]
    assert result["follow_up_questions"]
    assert result["safety"]["localOnly"] is True


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("meal_idea", "meal_idea"),
        ("simple_recipe", "simple_recipe"),
        ("grocery_list", "grocery_list"),
        ("pantry_plan", "pantry_plan"),
        ("meal_prep_plan", "meal_prep_plan"),
        ("leftover_plan", "leftover_plan"),
        ("cooking_steps", "cooking_steps"),
        ("budget_grocery_plan", "budget_grocery_plan"),
        ("kitchen_workflow", "kitchen_workflow"),
        ("comparison", "comparison"),
        ("checklist", "checklist"),
        ("summary", "summary"),
        (" SIMPLE_RECIPE ", "simple_recipe"),
    ],
)
def test_local_food_cooking_grocery_supported_output_types_normalize(requested, expected):
    service = LocalFoodCookingGroceryAgentService()

    result = service.create_plan(
        LocalFoodCookingGroceryRequest(
            request="Plan dinner.",
            output_type=requested,
            available_ingredients=["Rice"],
        )
    )

    assert result["output_type"] == expected


def test_local_food_cooking_grocery_unsupported_output_type_falls_back_safely():
    service = LocalFoodCookingGroceryAgentService()

    result = service.create_plan(
        LocalFoodCookingGroceryRequest(
            request="Order groceries from an app.",
            output_type="delivery_order",
        )
    )

    assert result["output_type"] == "summary"
    assert result["safety"]["groceryAppAccess"] is False
    assert result["safety"]["orders"] is False
    assert result["safety"]["purchases"] is False


def test_local_food_cooking_grocery_response_includes_local_manual_limitations():
    service = LocalFoodCookingGroceryAgentService()

    result = service.create_plan(
        LocalFoodCookingGroceryRequest(
            request="Make a cheap grocery list for 5 dinners.",
            output_type="budget_grocery_plan",
            available_ingredients=["Rice", "Eggs", "Chicken", "Frozen vegetables", "Beans"],
            budget_level="low",
        )
    )
    output_text = str(result).lower()

    assert "based only on user-provided" in output_text
    assert "no grocery app" in output_text
    assert "delivery app" in output_text
    assert "payment system" in output_text
    assert "no grocery order" in output_text
    assert "purchase" in output_text
    assert "external service" in output_text


def test_local_food_cooking_grocery_prohibited_actions_are_not_capabilities():
    service = LocalFoodCookingGroceryAgentService()

    result = service.create_plan(LocalFoodCookingGroceryRequest(request="Compare groceries versus eating out."))
    safety = result["safety"]

    assert safety["localOnly"] is True
    assert safety["responseOnly"] is True
    assert safety["manualInputOnly"] is True
    assert safety["externalServices"] is False
    assert safety["connectors"] is False
    assert safety["connectorExecution"] is False
    assert safety["oauth"] is False
    assert safety["accountAccess"] is False
    assert safety["groceryAppAccess"] is False
    assert safety["deliveryAppAccess"] is False
    assert safety["restaurantAppAccess"] is False
    assert safety["healthAppAccess"] is False
    assert safety["locationAccess"] is False
    assert safety["mapAccess"] is False
    assert safety["paymentAccess"] is False
    assert safety["webBrowsing"] is False
    assert safety["paidApis"] is False
    assert safety["fileReads"] is False
    assert safety["fileWrites"] is False
    assert safety["dbWrites"] is False
    assert safety["taskPersistence"] is False
    assert safety["shellExecution"] is False
    assert safety["orders"] is False
    assert safety["purchases"] is False
    assert safety["reservations"] is False
    assert safety["messages"] is False
    assert safety["mutation"] is False


def test_local_food_cooking_grocery_allergy_medical_and_food_safety_disclaimers():
    service = LocalFoodCookingGroceryAgentService()

    result = service.create_plan(
        LocalFoodCookingGroceryRequest(
            request="I have a peanut allergy, diabetes, and raw chicken thawing questions.",
            output_type="cooking_steps",
            allergies_or_avoidances=["Peanut allergy"],
            available_ingredients=["Raw chicken", "Rice"],
            constraints_or_notes="Need blood sugar friendly food.",
        )
    )
    output_text = str(result).lower()

    assert "allergy" in output_text
    assert "cannot guarantee allergy safety" in output_text
    assert "diabetes" in output_text
    assert "qualified medical or dietary professionals" in output_text
    assert "food-safety reminders are general" in output_text
    assert "does not certify" in output_text


def test_local_food_cooking_grocery_output_does_not_claim_validation_or_certification():
    service = LocalFoodCookingGroceryAgentService()

    result = service.create_plan(
        LocalFoodCookingGroceryRequest(
            request="Plan beginner chicken rice bowls.",
            output_type="meal_prep_plan",
        )
    )
    output_text = str(result).lower()
    forbidden_claims = [
        "medical nutrition advice provided",
        "allergy safety guaranteed",
        "clinical diet prescribed",
        "weight-loss guaranteed",
        "food-safety certified",
        "nutritionist validated",
        "grocery order created",
        "delivery order created",
        "reservation booked",
    ]

    assert all(claim not in output_text for claim in forbidden_claims)
    assert "no medical nutrition advice" in output_text
    assert "food-safety certification" in output_text
    assert "nutritionist validation" in output_text


def test_local_food_cooking_grocery_source_has_no_network_file_shell_api_or_persistence_calls():
    source = inspect.getsource(__import__("jarvis_core.local_food_cooking_grocery_agent").local_food_cooking_grocery_agent).lower()
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
        "gmail.",
        "google_calendar",
        "openai",
        "anthropic",
        "gemini",
    ]

    assert all(token not in source for token in forbidden)


def test_local_food_cooking_grocery_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        app_module.LocalFoodCookingGroceryInput.model_validate(
            {
                "request": "Plan dinner.",
                "groceryAccount": "not allowed",
            }
        )


def test_local_food_cooking_grocery_endpoint_is_guarded_by_dashboard_lan_guard():
    route = next(
        route for route in app_module.app.routes if getattr(route, "path", None) == "/agents/food-cooking-grocery/local-plan"
    )
    dependency_calls = {dependency.call for dependency in route.dependant.dependencies}

    assert require_dashboard_lan_access in dependency_calls
