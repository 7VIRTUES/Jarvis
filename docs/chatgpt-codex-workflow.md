# ChatGPT and Codex Workflow

Jarvis uses ChatGPT Project for planning, review, architecture, safety, sequencing, and prompt writing. Codex is reserved for implementation.

## Core Split

ChatGPT Project is the planner, reviewer, validator, scope-controller, safety reviewer, architecture guard, GitHub reader, affected-file mapper, implementation sequencer, and Codex-prompt writer.

Codex is the implementation worker only.

## Full-Scope Codex-Limit Conservation

The project scope remains the full Jarvis app/project.

Do not reduce the final implementation target to an MVP. Do not shrink features, roadmap, polish, hardening, safety, or integration goals because of Codex-limit conservation.

Saving Codex limits means reducing waste:

- fewer tiny prompts
- fewer validation-only prompts
- less broad discovery by Codex
- less status-only command execution
- more ChatGPT-side planning and affected-file mapping
- larger concrete implementation batches

## ChatGPT Project Responsibilities

ChatGPT handles:

- planning
- architecture decisions
- safety analysis
- scope control
- GitHub read-only repo inspection when current pushed state is needed
- source inspection when available
- affected-file mapping
- implementation sequencing
- risk review
- validation reasoning when pasted outputs or GitHub state are enough
- closeout reasoning
- Codex prompt writing
- digesting Codex reports
- next-step decisions

ChatGPT must not directly edit GitHub files, create commits, push branches, merge changes, delete files, or perform implementation work for Jarvis.

## Codex Responsibilities

Codex handles only implementation work:

- code changes
- documentation changes when explicitly requested
- test changes when explicitly requested
- file edits
- narrow refactors
- local mechanical inspection needed to safely complete the requested edit
- one coherent commit/push after a large completed batch when the active prompt explicitly allows it

Codex must not decide the roadmap, choose architecture, plan broadly, run broad discovery, or spend limits on status-only checks.

## Default Codex Prompt Rules

Unless the prompt explicitly says otherwise, Codex must:

- implement the requested batch
- edit only files needed for that batch
- inspect only targeted files needed to make edits safely
- avoid broad repo scans
- avoid unnecessary commands
- avoid validation-only tasks
- avoid tests, typecheck, build, lint, package-manager commands, dependency installs, and long verification commands
- avoid branch creation
- avoid PR creation
- avoid merge, rebase, reset, force-push, and history rewrite
- avoid destructive commands
- leave changes uncommitted unless the prompt explicitly allows commit/push

## Commit and Push Policy

The updated workflow allows Codex to create one coherent commit and push after a large completed batch, or when ChatGPT needs GitHub-visible repository state before planning the next major batch.

This is allowed only if the active prompt explicitly includes a commit/push rule.

This is a repo-development workflow exception. It does not authorize Jarvis runtime automatic push, merge, posting, messaging, account linking, cloud sync, or external service actions.

When the active prompt allows commit/push, Codex may run only minimal final git inspection:

- `git status --short`
- `git diff --name-only`
- `git branch --show-current`

Codex may commit and push only if:

- the batch is complete
- changed files match the allowed scope
- current branch is `main`
- no protected files changed
- no unexpected dependency/package/lock files changed
- no tests/docs changed unless explicitly allowed
- no unrelated files changed
- no stop condition was triggered

If anything is unexpected, Codex must not commit or push and must report why.

## July 6 Implementation Mode

Until the user's higher ChatGPT/Codex capacity changes on July 6:

- maximize durable code implementation
- use larger concrete bounded Codex batches
- avoid tiny prompts unless needed for a narrow blocker
- skip manual validation prompts
- skip tests/test edits unless explicitly requested
- skip broad audits
- skip smoke checks
- skip clean VM validation
- skip packaging verification
- skip manual-review checkpoints
- reserve Codex High for security-critical runtime work only

## Model Guidance

Use Codex Medium by default.

Use Codex High only for security-critical runtime work:

- Safe Action Runtime
- Permission Engine
- Codex execution
- LAN/token protection
- path validation
- diagnostics redaction
- database migrations
- installer/build/signing
- stop/cancel execution

Use Codex Low only for tiny documentation or prompt cleanup when explicitly requested.

## Current Jarvis Status

v0.1A, v0.1B, and v0.1C are closed readiness foundations.

Last verified GitHub state before local-only response-agent work:

`123fce3275ecd83e4a1b3c4a2868a3042792c883`

Commit:

`Add local Response Agents dashboard examples`

Local reports after that describe many unvalidated local-only dashboard/response-agent changes, including 37 local response-agent endpoints.

Expected local response-agent count: 37.

Do not add response agents unless the user explicitly asks.

## Current Implementation Lane

The current lane is not production release or v0.2. It is a pre-July-6 implementation-maximization sprint for local-only dashboard and response-agent usability.

Allowed focus:

- dashboard-only UI improvements
- response-only local agents
- manual composition helpers
- session-only result/context workflows
- safer high-stakes warnings
- source/evidence display improvements
- no-persistence productivity improvements
- local-only code organization

Do not implement production packaging, real desktop release, real connectors, account linking, cloud sync, external automation, email sending, public posting, purchases, or payment actions unless the user explicitly approves a dedicated future phase.

## Current Priority Queue

Prioritize:

1. Local Response Agent Productivity Batch
   - Command Center
   - search/filter
   - pinned/recent agents
   - quick actions
   - workflow presets/playbooks
   - context kit builder
   - request quality coach
   - high-stakes banner

2. Result Board and Decision Batch
   - session-only tagging
   - scoring/marking
   - better comparison matrix
   - best-output selector
   - decision summary composer
   - review packet improvements

3. Source and Evidence UX Batch
   - source quality grouping
   - recency labels
   - missing-source warnings
   - source-to-answer trace helpers
   - high-stakes source reminders

4. Manual Multi-Agent Workflow Polish
   - step cards
   - sequence preview
   - manual handoff controls
   - context insertion helpers
   - no auto-run or auto-chain behavior

5. Dashboard Layout / Empty-State Batch
   - collapsible sections
   - clearer hierarchy
   - empty states
   - error/fallback messages
   - responsive cleanup

6. Dashboard Code Organization Batch
   - reduce repeated inline helpers
   - keep behavior unchanged
   - no architecture redesign

## Stop Rule

Tell the user to stop Jarvis Codex work only when remaining Jarvis work is mainly manual validation, tests, manual review, packaging verification, environment setup, or decisions requiring user input.

Use this exact wording:

`STOP JARVIS CODEX HERE — remaining work is mainly manual validation/tests/manual review, so use Codex on another project.`
