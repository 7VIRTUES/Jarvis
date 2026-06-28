# Local Health/Fitness Agent

The Local Health/Fitness Agent turns user-provided wellness, workout, habit, nutrition, schedule, recovery, preference, constraint, and limitation notes into structured local planning guidance.

It is local-only, response-only, and manual-input-only.

## Purpose

- Help organize user-provided fitness goals, activity preferences, available equipment, schedule notes, nutrition context, recovery notes, habit goals, constraints, and training limitations.
- Return manual wellness, workout, habit, nutrition, recovery, weekly routine, progress-review, and safety-review planning support.
- Keep outputs based only on the request body.

## Scope

- Does not browse, call paid APIs, use connectors, access accounts, read files, write files, write database records, create tasks, create reminders, create calendar events, send email, post publicly, make purchases, or mutate local state.
- Does not access Apple Health, Google Fit, Samsung Health, Fitbit, Garmin, Oura, Strava, insurance, pharmacy, hospital, clinic, EHR, lab, wearable, health-app, or external health-data accounts.
- Does not create persistent health records.

## Endpoint

`POST /agents/health-fitness/local-plan`

## Request Body Example

```json
{
  "profileName": "Local Wellness Plan",
  "primaryGoal": "Build a steady beginner strength and walking routine.",
  "currentFitnessLevel": "Beginner returning to consistent activity.",
  "ageRange": "adult",
  "heightWeightNotes": "General body-composition goals only; no clinical interpretation requested.",
  "scheduleNotes": "Three short weekday sessions and one longer weekend walk.",
  "equipmentAvailable": ["Adjustable dumbbells", "Yoga mat"],
  "preferredActivities": ["Walking", "Strength training"],
  "dislikedActivities": ["High-impact jumping"],
  "nutritionNotes": "Wants simple balanced meal planning ideas for busy days.",
  "sleepRecoveryNotes": "Wants to improve sleep consistency and avoid overdoing workouts.",
  "constraints": ["Keep sessions short", "No calendar or reminder creation"],
  "injuriesOrLimitations": ["Use conservative intensity and seek professional review for pain."],
  "habitsToBuild": ["Walk after lunch", "Prepare simple breakfast options"],
  "habitsToReduce": ["Skipping movement on busy days"],
  "desiredOutputType": "fitness_brief"
}
```

## Supported Output Types

- `fitness_brief`
- `workout_plan`
- `habit_plan`
- `nutrition_guidance`
- `recovery_plan`
- `weekly_routine`
- `progress_review`
- `safety_review`

## Safety Boundaries

- Not a medical, clinical, wearable, health-app, insurance, pharmacy, lab, or EHR connector.
- Does not diagnose, treat, prescribe, interpret labs, provide emergency triage, validate medical safety, provide clinical validation, provide nutritionist review, provide trainer certification, or guarantee weight loss, muscle gain, recovery, disease prevention, injury prevention, or other outcomes.
- Does not provide medication advice or supplement prescriptions.
- Pain, injury, medical conditions, eating-disorder concerns, medication questions, alarming symptoms, or emergency symptoms require a qualified professional or emergency service as appropriate.

## Limitations

- Outputs are based only on user-provided inputs.
- General nutrition guidance is non-clinical and non-prescriptive.
- Workout, habit, nutrition, and recovery guidance is manual planning support only.
- No tasks, reminders, calendar events, health records, files, database records, purchases, posts, messages, connectors, accounts, or external services are created or accessed.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

These linked smoke and evidence docs are read-only docs/manual evidence aids and do not prove validation or certification.
