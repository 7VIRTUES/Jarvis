# Local Life Dashboard / Cross-Agent Coordinator

Back to the [Local Response Agents Index](local-response-agents-index.md).

Manual examples live in the [Local Response Agents Manual Smoke Runbook](local-response-agents-smoke-runbook.md). Manual evidence aids live in the [Local Response Agents Smoke Evidence Template](local-response-agents-smoke-evidence-template.md); they do not prove validation or certification.

## Boundary

- Manual-input-only.
- Local-only.
- Response-only.
- Non-persistent.
- Outputs are based only on user-provided life-area, goal, project, urgent-item, time, energy, priority, decision-context, weekly-focus, and risk/stress text.
- Does not automatically run, invoke, hand off to, or query other local agents.
- Recommended agents are suggestions only.
- Does not access connectors, accounts, files, notes, memory, email, calendar, contacts, cloud services, browser history, payment systems, or external services.
- Does not create tasks, schedule reminders, persist dashboards, mutate records, send messages, post publicly, buy, book, pay, submit forms, file official documents, call emergency services, make legal actions, make medical decisions, or make financial transactions.
- High-stakes topics are planning notes only; verify with qualified professionals or official sources.
- If there is immediate danger, contact local emergency services.

## Endpoint

`POST /agents/life-dashboard-coordinator/local-plan`

## Supported Output Types

- `life_dashboard`
- `cross_agent_plan`
- `agent_routing_plan`
- `priority_map`
- `weekly_operating_plan`
- `daily_focus_plan`
- `decision_map`
- `project_life_alignment`
- `risk_review`
- `next_action_stack`
- `checklist`
- `summary`
