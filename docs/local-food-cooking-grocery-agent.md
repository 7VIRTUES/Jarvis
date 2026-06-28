# Local Food / Cooking / Grocery Agent

The Local Food / Cooking / Grocery Agent turns user-provided meal, pantry, cooking, grocery, preference, budget, time, skill, equipment, leftover, and constraint notes into structured local planning guidance.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help reason about meal ideas, simple recipes, grocery lists, pantry use, leftovers, meal prep, beginner cooking steps, kitchen workflow, and food preference tradeoffs.
- Keep grocery and meal planning budget-aware when the user provides budget context.
- Return structured suggestions based only on the request body.

## Scope

- Does not browse, call paid APIs, use connectors, access accounts, read files, write files, write database records, create tasks, create reminders, send messages, post publicly, make purchases, book reservations, order groceries, create delivery orders, or mutate local state.
- Does not access grocery apps, delivery apps, restaurant apps, health apps, payment systems, browser data, location, maps, GPS, or external services.
- Does not create persistent food, pantry, grocery, health, budget, or kitchen records.

## Endpoint

`POST /agents/food-cooking-grocery/local-plan`

## Request Body Example

```json
{
  "request": "Make a cheap grocery list for 5 dinners using rice, eggs, chicken, frozen vegetables, and beans.",
  "outputType": "budget_grocery_plan",
  "mealGoal": "Plan 5 simple low-cost dinners.",
  "availableIngredients": ["Rice", "Eggs", "Chicken", "Frozen vegetables", "Beans"],
  "pantryItems": ["Soy sauce", "Garlic powder", "Pasta"],
  "groceryItemsNeeded": ["Tortillas", "Canned tomatoes", "Yogurt"],
  "dietaryPreferences": ["Simple high-protein meals"],
  "allergiesOrAvoidances": ["No known allergies provided"],
  "budgetLevel": "low",
  "budgetNotes": "Use pantry items first and avoid specialty ingredients.",
  "servings": "5 dinners for 1 adult",
  "timeAvailableMinutes": 30,
  "cookingSkillLevel": "beginner",
  "kitchenEquipment": ["Stove", "Skillet", "Rice cooker"],
  "mealType": "dinner",
  "cuisinePreferences": ["Flexible"],
  "leftoversOrBatchPrepGoal": "Reuse cooked rice and chicken across meals.",
  "constraintsOrNotes": "Manual planning only; no shopping app or delivery order."
}
```

## Supported Output Types

- `meal_idea`
- `simple_recipe`
- `grocery_list`
- `pantry_plan`
- `meal_prep_plan`
- `leftover_plan`
- `cooking_steps`
- `budget_grocery_plan`
- `kitchen_workflow`
- `comparison`
- `checklist`
- `summary`

## Safety Boundaries

- Not a grocery, delivery, restaurant, health, payment, map, GPS, browser, file, account, or external-service connector.
- Does not order groceries, create delivery orders, make purchases, book reservations, send messages, persist records, mutate files, or connect accounts.
- Does not provide medical nutrition advice, allergy safety certainty, clinical diet prescriptions, weight-loss guarantees, food-safety certification, nutritionist validation, or other certification claims.
- Allergies, pregnancy, diabetes, eating disorders, kidney disease, heart disease, serious food reactions, clinical nutrition needs, and medical diets require qualified medical or dietary professionals.
- Food-safety reminders are conservative general reminders only and do not certify that a food, leftover, ingredient, cooking method, or storage condition is safe.

## Example Prompts

- Make a cheap grocery list for 5 dinners using rice, eggs, chicken, frozen vegetables, and beans.
- Turn these pantry items into a simple 30-minute dinner.
- Give me beginner cooking steps for meal-prepping chicken rice bowls.
- Compare buying ingredients versus eating out for this week.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
