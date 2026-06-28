# Local Emotional Reflection / Resilience Agent

The Local Emotional Reflection / Resilience Agent is a manual-input only, local-only, response-only helper for user-provided emotional reflection, stress, motivation, discipline recovery, confidence, journaling, red/yellow-day planning, and resilience notes.

Endpoint: `POST /agents/emotional-reflection/local-reflect`

Mode: `response_only_user_provided_emotional_reflection`

## Request Fields

- `profileName` optional string
- `reflectionGoal` required string
- `currentMoodNotes` optional string
- `stressors` optional list of strings
- `energyNotes` optional string
- `recentWins` optional list of strings
- `currentChallenges` optional list of strings
- `patternsNoticed` optional list of strings
- `supportOptions` optional list of strings
- `constraints` optional list of strings
- `desiredOutputType` optional string

Supported output types: `reflection_brief`, `stress_review`, `motivation_reset`, `discipline_recovery`, `confidence_plan`, `journal_prompts`, `resilience_plan`, and `red_yellow_day_plan`.

Unsupported output types fall back to `reflection_brief`.

## Response Shape

The response includes reflection focus, situation summary, stress review, motivation reset, discipline recovery, confidence plan, journal prompts, resilience plan, red/yellow-day plan, next actions, open questions, warnings, limitations, and safety flags.

Output is based only on user-provided input.

## Boundaries

- Not therapy, not diagnosis, not treatment, not crisis service, not medical advice, not psychiatric advice, not medication advice, and not mental-health, medical, or psychiatric validation.
- No health, journal, file, message, contact, account, calendar, task, wearable, connector, paid API, browsing, or external-service behavior.
- No persistence, task creation, reminder creation, scheduling, messaging, appointment scheduling, contact action, file mutation, database writes, shell execution, outcome guarantees, production readiness, or certification claims.
- Self-harm, suicidal thoughts, abuse, violence, immediate danger, severe distress, medical issues, or crisis language should be handled with immediate human, professional, medical, safety, or emergency support as appropriate.
- The agent does not provide instructions that encourage self-harm, harm to others, abuse, coercion, evasion, or isolation from support.

## Related Docs

- [Local Response Agents Index](local-response-agents-index.md)
- [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md)
- [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md)

## Manual Evidence Aids

Manual evidence aids can record the endpoint, local-only response shape, safety flags, warnings, and limitations for later review. They do not prove validation or certification.
