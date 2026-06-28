from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


AGENT_ID = "local_food_cooking_grocery"
STATUS = "local_only"
MODE = "response_only_user_provided_food_cooking_grocery_planning"
SUPPORTED_OUTPUT_TYPES = (
    "meal_idea",
    "simple_recipe",
    "grocery_list",
    "pantry_plan",
    "meal_prep_plan",
    "leftover_plan",
    "cooking_steps",
    "budget_grocery_plan",
    "kitchen_workflow",
    "comparison",
    "checklist",
    "summary",
)


@dataclass(frozen=True)
class LocalFoodCookingGroceryRequest:
    request: str = ""
    prompt_text: str = ""
    output_type: str = "summary"
    meal_goal: str = ""
    available_ingredients: list[str] = field(default_factory=list)
    pantry_items: list[str] = field(default_factory=list)
    grocery_items_needed: list[str] = field(default_factory=list)
    dietary_preferences: list[str] = field(default_factory=list)
    allergies_or_avoidances: list[str] = field(default_factory=list)
    budget_level: str = ""
    budget_notes: str = ""
    servings: str = ""
    time_available_minutes: int | None = None
    cooking_skill_level: str = ""
    kitchen_equipment: list[str] = field(default_factory=list)
    meal_type: str = ""
    cuisine_preferences: list[str] = field(default_factory=list)
    leftovers_or_batch_prep_goal: str = ""
    constraints_or_notes: str = ""


class LocalFoodCookingGroceryAgentService:
    def create_plan(self, request: LocalFoodCookingGroceryRequest) -> dict[str, Any]:
        request_text = _clean_text(request.request or request.prompt_text)
        meal_goal = _clean_text(request.meal_goal) or request_text or "Untitled meal planning request"
        output_type = _normalize_output_type(request.output_type)
        available = _clean_list(request.available_ingredients)
        pantry = _clean_list(request.pantry_items)
        needed = _clean_list(request.grocery_items_needed)
        preferences = _clean_list(request.dietary_preferences)
        avoidances = _clean_list(request.allergies_or_avoidances)
        budget_level = _clean_text(request.budget_level)
        budget_notes = _clean_text(request.budget_notes)
        servings = _clean_text(request.servings)
        skill = _clean_text(request.cooking_skill_level)
        equipment = _clean_list(request.kitchen_equipment)
        meal_type = _clean_text(request.meal_type)
        cuisines = _clean_list(request.cuisine_preferences)
        batch_goal = _clean_text(request.leftovers_or_batch_prep_goal)
        notes = _clean_text(request.constraints_or_notes)
        minutes = _normalize_minutes(request.time_available_minutes)
        combined_text = " ".join(
            [
                request_text,
                meal_goal,
                " ".join(available),
                " ".join(pantry),
                " ".join(needed),
                " ".join(preferences),
                " ".join(avoidances),
                budget_level,
                budget_notes,
                servings,
                skill,
                " ".join(equipment),
                meal_type,
                " ".join(cuisines),
                batch_goal,
                notes,
            ]
        )
        medical_context = _has_medical_or_clinical_context(combined_text)
        allergy_context = _has_allergy_context(avoidances, combined_text)
        safety_context = _has_food_safety_context(combined_text)
        thin_input = _thin_input(
            request_text,
            available,
            pantry,
            needed,
            preferences,
            avoidances,
            budget_level,
            budget_notes,
            servings,
            skill,
            equipment,
            meal_type,
            cuisines,
            batch_goal,
            notes,
            minutes,
        )

        assumptions = _assumptions(meal_goal, available, pantry, needed, servings, minutes, thin_input)
        recommended_plan = _recommended_plan(output_type, meal_goal, available, pantry, needed, minutes, skill, batch_goal)
        ingredients_or_items = _ingredients_or_items(available, pantry, needed, preferences, avoidances)
        step_by_step = _step_by_step(output_type, meal_goal, available, pantry, minutes, skill, equipment)
        grocery_list = _grocery_list(available, pantry, needed, meal_goal, budget_level, preferences)
        budget_review = _budget_notes(output_type, budget_level, budget_notes, available, pantry, needed)
        safety_notes = _safety_notes(allergy_context, medical_context, safety_context)
        limitations = _limitations(thin_input, allergy_context, medical_context, safety_context)
        follow_up_questions = _follow_up_questions(
            available,
            pantry,
            needed,
            preferences,
            avoidances,
            budget_level,
            servings,
            skill,
            equipment,
            meal_type,
            minutes,
        )

        return {
            "agent_id": AGENT_ID,
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "title": _title(output_type, meal_goal),
            "summary": _summary(output_type, meal_goal, meal_type, cuisines, thin_input),
            "assumptions": assumptions,
            "recommended_plan": recommended_plan,
            "ingredients_or_items": ingredients_or_items,
            "step_by_step": step_by_step,
            "grocery_list": grocery_list,
            "budget_notes": budget_review,
            "time_estimate": _time_estimate(minutes, output_type),
            "safety_notes": safety_notes,
            "limitations": limitations,
            "follow_up_questions": follow_up_questions,
            "output_type": output_type,
            "safety": local_food_cooking_grocery_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return local_food_cooking_grocery_dashboard_summary()


def local_food_cooking_grocery_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "Local Food / Cooking / Grocery Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/food-cooking-grocery/local-plan",
        "outputTypes": list(SUPPORTED_OUTPUT_TYPES),
        "responseOnly": True,
        "manualInputOnly": True,
        "localOnly": True,
        "externalServices": False,
        "connectors": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "groceryAppAccess": False,
        "deliveryAppAccess": False,
        "restaurantAppAccess": False,
        "healthAppAccess": False,
        "locationAccess": False,
        "mapAccess": False,
        "paymentAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "orders": False,
        "purchases": False,
        "reservations": False,
        "messages": False,
        "medicalNutritionAdvice": False,
        "allergySafetyCertainty": False,
        "foodSafetyCertification": False,
        "mutation": False,
        "certificationClaims": False,
        "limitations": ["based only on user-provided food, cooking, pantry, grocery, budget, and kitchen-planning inputs"],
    }


def local_food_cooking_grocery_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "responseOnly": True,
        "manualInputOnly": True,
        "externalServices": False,
        "connectors": False,
        "connectorExecution": False,
        "oauth": False,
        "accountAccess": False,
        "groceryAppAccess": False,
        "deliveryAppAccess": False,
        "restaurantAppAccess": False,
        "healthAppAccess": False,
        "locationAccess": False,
        "mapAccess": False,
        "paymentAccess": False,
        "webBrowsing": False,
        "paidApis": False,
        "fileReads": False,
        "fileWrites": False,
        "dbWrites": False,
        "taskPersistence": False,
        "shellExecution": False,
        "orders": False,
        "purchases": False,
        "reservations": False,
        "messages": False,
        "medicalNutritionAdvice": False,
        "allergySafetyCertainty": False,
        "clinicalDietPrescription": False,
        "weightLossGuarantee": False,
        "foodSafetyCertification": False,
        "nutritionistValidation": False,
        "mutation": False,
        "certificationClaims": False,
    }


def _normalize_output_type(value: str) -> str:
    normalized = (value or "summary").strip().lower()
    return normalized if normalized in SUPPORTED_OUTPUT_TYPES else "summary"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def _clean_list(values: list[str], limit: int = 14) -> list[str]:
    cleaned: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean_text(value)
        key = item.lower()
        if item and key not in seen:
            cleaned.append(item)
            seen.add(key)
    return cleaned[:limit]


def _normalize_minutes(value: int | None) -> int | None:
    if value is None:
        return None
    return min(max(int(value), 1), 720)


def _thin_input(
    request_text: str,
    available: list[str],
    pantry: list[str],
    needed: list[str],
    preferences: list[str],
    avoidances: list[str],
    budget_level: str,
    budget_notes: str,
    servings: str,
    skill: str,
    equipment: list[str],
    meal_type: str,
    cuisines: list[str],
    batch_goal: str,
    notes: str,
    minutes: int | None,
) -> bool:
    return not any(
        [
            request_text,
            available,
            pantry,
            needed,
            preferences,
            avoidances,
            budget_level,
            budget_notes,
            servings,
            skill,
            equipment,
            meal_type,
            cuisines,
            batch_goal,
            notes,
            minutes,
        ]
    )


def _has_medical_or_clinical_context(text: str) -> bool:
    lowered = text.lower()
    terms = (
        "pregnant",
        "pregnancy",
        "diabetes",
        "kidney disease",
        "heart disease",
        "eating disorder",
        "ed recovery",
        "medical diet",
        "clinical diet",
        "doctor told me",
        "dietitian",
        "nutritionist",
        "weight loss",
        "lose weight",
        "blood sugar",
        "hypertension",
        "celiac",
    )
    return any(term in lowered for term in terms)


def _has_allergy_context(avoidances: list[str], text: str) -> bool:
    lowered = text.lower()
    allergy_terms = ("allergy", "allergic", "anaphylaxis", "reaction", "cross-contamination", "cross contamination")
    return bool(avoidances) and any(term in lowered for term in allergy_terms)


def _has_food_safety_context(text: str) -> bool:
    lowered = text.lower()
    terms = ("raw chicken", "raw meat", "left out", "expired", "mold", "thaw", "reheat", "food poisoning", "undercooked")
    return any(term in lowered for term in terms)


def _title(output_type: str, meal_goal: str) -> str:
    label = output_type.replace("_", " ").title()
    return f"{label}: {meal_goal[:80]}"


def _summary(output_type: str, meal_goal: str, meal_type: str, cuisines: list[str], thin_input: bool) -> str:
    if thin_input:
        return "Local manual food planning scaffold; add ingredients, budget, servings, time, equipment, and constraints for more specific guidance."
    parts = [f"Manual {output_type.replace('_', ' ')} for {meal_goal}."]
    if meal_type:
        parts.append(f"Meal type: {meal_type}.")
    if cuisines:
        parts.append(f"Cuisine preference: {cuisines[0]}.")
    parts.append("No grocery app, delivery app, restaurant app, health app, payment system, map, account, file, or external service was accessed.")
    return " ".join(parts)


def _assumptions(
    meal_goal: str,
    available: list[str],
    pantry: list[str],
    needed: list[str],
    servings: str,
    minutes: int | None,
    thin_input: bool,
) -> list[str]:
    assumptions = ["Uses only manually supplied food, cooking, pantry, grocery, and kitchen notes."]
    if available or pantry:
        assumptions.append("Prioritize items already on hand before adding groceries.")
    if needed:
        assumptions.append("Treat listed grocery needs as user-provided, not as a live store inventory.")
    if servings:
        assumptions.append(f"Plan around the stated serving target: {servings}.")
    if minutes:
        assumptions.append(f"Keep active planning within about {minutes} minutes where realistic.")
    if thin_input:
        assumptions.append(f"The goal is under-specified: {meal_goal}.")
    return assumptions


def _recommended_plan(
    output_type: str,
    meal_goal: str,
    available: list[str],
    pantry: list[str],
    needed: list[str],
    minutes: int | None,
    skill: str,
    batch_goal: str,
) -> list[str]:
    staples = available + pantry
    anchor = staples[0] if staples else "the simplest suitable staple"
    plan = [f"Start with {anchor} as the meal anchor for: {meal_goal}."]
    if output_type in {"grocery_list", "budget_grocery_plan"}:
        plan.append("Separate must-buy items from flexible swaps before going to a store manually.")
    elif output_type == "simple_recipe":
        plan.append("Use a simple base, a protein or hearty item, vegetables or fruit where suitable, and one seasoning direction.")
    elif output_type == "meal_prep_plan":
        plan.append("Batch one base, one main component, and one flexible topping or sauce instead of over-planning every meal.")
    elif output_type == "leftover_plan":
        plan.append("Rework leftovers into a bowl, wrap, soup, skillet, or salad only if they have been stored safely.")
    elif output_type == "kitchen_workflow":
        plan.append("Stage ingredients, prep equipment, cook longest items first, and clean as idle time allows.")
    elif output_type == "comparison":
        plan.append("Compare ingredient reuse, time, cost control, leftovers, and convenience against eating out.")
    else:
        plan.append("Choose one realistic meal path and one backup option.")
    if needed:
        plan.append(f"First grocery need to review manually: {needed[0]}.")
    if minutes:
        plan.append(f"Prefer steps that fit the stated time limit: {minutes} minutes.")
    if skill:
        plan.append(f"Match instructions to cooking skill level: {skill}.")
    if batch_goal:
        plan.append(f"Batch or leftover goal: {batch_goal}.")
    return plan[:6]


def _ingredients_or_items(
    available: list[str],
    pantry: list[str],
    needed: list[str],
    preferences: list[str],
    avoidances: list[str],
) -> dict[str, list[str]]:
    return {
        "available_ingredients": available or ["No available ingredients were provided."],
        "pantry_items": pantry or ["No pantry items were provided."],
        "grocery_items_needed": needed or ["Add groceries only after checking what is already on hand."],
        "dietary_preferences": preferences or ["No dietary preferences were provided."],
        "allergies_or_avoidances": avoidances or ["No allergies or avoidances were provided."],
    }


def _step_by_step(
    output_type: str,
    meal_goal: str,
    available: list[str],
    pantry: list[str],
    minutes: int | None,
    skill: str,
    equipment: list[str],
) -> list[str]:
    items = available + pantry
    steps = [
        "Review ingredients and remove anything that is spoiled, unsafe, or unsuitable.",
        f"Pick the main direction for: {meal_goal}.",
        f"Use {items[0]} first." if items else "Choose a simple staple before adding complexity.",
        f"Use available equipment: {equipment[0]}." if equipment else "Confirm required pan, knife, cutting board, and heat source manually.",
    ]
    if output_type == "cooking_steps":
        steps.extend(
            [
                "Prep ingredients before turning on heat.",
                "Cook high-risk foods thoroughly using conservative general food-safety habits.",
                "Taste and adjust seasoning only when safe to do so.",
            ]
        )
    if skill.lower() in {"beginner", "new", "basic"}:
        steps.append("Use short steps, moderate heat, and fewer ingredients.")
    if minutes:
        steps.append(f"Stop adding optional steps if the plan exceeds about {minutes} minutes.")
    steps.append("No cooking appliance, grocery service, timer, task, file, app, or account was controlled.")
    return steps[:8]


def _grocery_list(
    available: list[str],
    pantry: list[str],
    needed: list[str],
    meal_goal: str,
    budget_level: str,
    preferences: list[str],
) -> dict[str, list[str]]:
    base = needed[:]
    if not base:
        base = ["One flexible protein or hearty item", "One vegetable or fruit option", "One low-cost base or side", "One seasoning or sauce if needed"]
    return {
        "check_first": (available + pantry)[:8] or ["Check pantry, fridge, and freezer manually before shopping."],
        "must_buy": base[:8],
        "optional_swaps": [
            "Use beans, eggs, rice, pasta, potatoes, frozen vegetables, or canned tomatoes when they fit the meal and budget.",
            f"Keep preference in mind: {preferences[0]}." if preferences else "Swap based on taste, availability, and budget.",
        ],
        "do_not_do": [
            "Do not place orders, make purchases, reserve tables, contact stores, or use delivery apps from this response.",
            f"Keep the grocery list tied to the manual goal: {meal_goal}.",
        ],
        "budget_level": [budget_level or "No budget level was provided."],
    }


def _budget_notes(
    output_type: str,
    budget_level: str,
    budget_notes: str,
    available: list[str],
    pantry: list[str],
    needed: list[str],
) -> list[str]:
    notes = []
    if budget_level:
        notes.append(f"Budget level: {budget_level}.")
    if budget_notes:
        notes.append(f"Budget note: {budget_notes}.")
    if available or pantry:
        notes.append("Use on-hand ingredients first to reduce extra purchases.")
    if needed:
        notes.append("Group groceries into must-buy and flexible-swap items before shopping manually.")
    if output_type == "comparison":
        notes.append("Compare eating out against groceries using user-known local prices; no live prices were checked.")
    if not notes:
        notes.append("No budget details were supplied; keep the first pass simple and low-waste.")
    return notes


def _time_estimate(minutes: int | None, output_type: str) -> str:
    if minutes:
        return f"User-stated time available: about {minutes} minutes; actual timing depends on kitchen setup and skill."
    if output_type in {"simple_recipe", "cooking_steps"}:
        return "No time limit was supplied; choose a simple meal before assuming timing."
    return "No time estimate was supplied; treat timing as a manual planning question."


def _safety_notes(allergy_context: bool, medical_context: bool, safety_context: bool) -> list[str]:
    notes = [
        "Use conservative general food-safety habits: clean hands and surfaces, avoid cross-contamination, cook high-risk foods thoroughly, chill leftovers promptly, and discard food that seems unsafe.",
        "This response does not certify that any ingredient, leftover, cooking method, or storage condition is safe.",
    ]
    if allergy_context:
        notes.append("Allergy inputs require qualified human review, ingredient-label checks, and cross-contact precautions; Jarvis cannot guarantee allergy safety.")
    if medical_context:
        notes.append("Pregnancy, diabetes, eating disorders, kidney disease, heart disease, serious food reactions, clinical diets, and other medical nutrition needs require qualified medical or dietary professionals.")
    if safety_context:
        notes.append("Food-safety uncertainty should be handled conservatively; when in doubt, do not eat questionable food.")
    return notes


def _limitations(thin_input: bool, allergy_context: bool, medical_context: bool, safety_context: bool) -> list[str]:
    limitations = [
        "Based only on user-provided food, cooking, pantry, grocery, budget, and kitchen-planning inputs.",
        "No grocery app, delivery app, restaurant app, health app, account, payment system, file, database, browser data, location, map, GPS, connector, or external service was accessed or changed.",
        "No grocery order, purchase, delivery order, restaurant booking, reservation, message, persistent record, file mutation, or account connection was created.",
        "No medical nutrition advice, allergy safety certainty, clinical diet prescription, weight-loss guarantee, food-safety certification, or nutritionist validation is provided.",
    ]
    if thin_input:
        limitations.append("Thin input limits specificity; add ingredients, pantry items, grocery needs, dietary preferences, allergies or avoidances, budget, servings, time, skill, equipment, meal type, cuisine, and constraints.")
    if allergy_context:
        limitations.append("Allergy-related planning is not safety validation; rely on labels, qualified professionals, and appropriate caution.")
    if medical_context:
        limitations.append("Medical or clinical nutrition situations require qualified medical or dietary professionals.")
    if safety_context:
        limitations.append("Food-safety reminders are general and conservative, not certification that a food is safe.")
    return limitations


def _follow_up_questions(
    available: list[str],
    pantry: list[str],
    needed: list[str],
    preferences: list[str],
    avoidances: list[str],
    budget_level: str,
    servings: str,
    skill: str,
    equipment: list[str],
    meal_type: str,
    minutes: int | None,
) -> list[str]:
    questions = []
    if not available and not pantry:
        questions.append("What ingredients are already available?")
    if not needed:
        questions.append("Which grocery items are truly needed after checking pantry and fridge?")
    if not preferences:
        questions.append("What dietary preferences should shape the plan?")
    if not avoidances:
        questions.append("Are there allergies, avoidances, or serious reactions to consider?")
    if not budget_level:
        questions.append("What budget level or budget note should constrain the list?")
    if not servings:
        questions.append("How many servings are needed?")
    if not minutes:
        questions.append("How much time is realistically available?")
    if not skill:
        questions.append("What cooking skill level should the steps assume?")
    if not equipment:
        questions.append("What kitchen equipment is available?")
    if not meal_type:
        questions.append("What meal type is this for?")
    return questions[:8]
