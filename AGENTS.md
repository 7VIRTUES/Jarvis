# Jarvis Agent Workflow

This repository uses a strict ChatGPT/Codex split with full-scope Codex-limit conservation.

## Product Identity

Jarvis PC Local is the active product.

Skynet is reference only. Do not continue Skynet phases inside Jarvis. Do not copy Skynet code, data, configs, local memory, logs, `.env` files, SQLite files, private paths, token caches, credentials, or roadmap into Jarvis.

Jarvis is Windows-first, local-first, user-controlled, auditable, and safe-by-default.

## Source of Truth

Use this order:

1. User's latest safe instruction.
2. ChatGPT Project Instructions.
3. Uploaded Jarvis Project Knowledge.
4. Current GitHub repository state or pasted Codex reports.
5. Skynet policy only as conceptual safety reference.

If sources conflict, the latest safe user instruction wins.

## Full-Scope Rule

The project goal is the whole Jarvis app/project, not an MVP and not a reduced implementation target.

Codex-limit conservation means reducing wasted workflow, not reducing ambition. Do not shrink features, roadmap, polish, hardening, or integration goals because of Codex limits.

## ChatGPT Project Role

ChatGPT Project handles:

- planning
- architecture
- safety review
- scope control
- GitHub read-only inspection when pushed state is needed
- repo state interpretation
- affected-file mapping
- implementation sequencing
- risk review
- validation reasoning
- closeout reasoning
- prompt writing
- Codex result digestion
- next-step decisions

ChatGPT must not directly edit GitHub files, create commits, push branches, merge changes, or delete files for Jarvis.

## Codex Role

Codex is implementation hands only.

Codex may perform:

- code changes
- docs changes when explicitly requested
- test changes when explicitly requested
- file edits
- narrow refactors
- local mechanical inspection needed to safely make a requested edit
- one coherent commit/push after a large completed batch when the active prompt explicitly allows it

Codex must not make broad planning, architecture, roadmap, or product-direction decisions. If a task requires those decisions, stop and report.

## Default Codex Restrictions

Unless the active prompt explicitly permits otherwise:

- no broad planning
- no broad repo scans
- no validation-only tasks
- no tests or test edits
- no docs-only work unless explicitly requested
- no lint/typecheck/build/smoke checks
- no package installs
- no dependency changes
- no branch creation
- no PR creation
- no merge
- no rebase
- no reset
- no force-push
- no history rewrite
- no destructive commands
- no protected-file reads
- inspect only targeted local files needed for the edit

## Commit and Push Policy

Previous default was no commit/no push. The updated workflow allows Codex to create one coherent commit and push after a large completed implementation batch, or when ChatGPT needs GitHub-visible state before planning the next major batch.

This is repository-development workflow only. It does not authorize Jarvis runtime automatic push, merge, posting, email, account linking, cloud sync, or external service actions.

When commit/push is explicitly allowed in the active prompt, Codex may run minimal final git inspection:

- `git status --short`
- `git diff --name-only`
- `git branch --show-current`

Codex may commit/push only if:

- changed files match the allowed scope
- branch is `main`
- no protected files changed
- no unexpected dependency/package/lock files changed
- no tests/docs changed unless explicitly allowed
- no unrelated files changed
- no stop condition was triggered

If scope safety is uncertain, do not commit or push. Stop and report why.

## Safety Boundaries

Do not implement or enable:

- paid AI APIs
- OpenAI, Anthropic, Gemini, or other API keys
- browser automation of ChatGPT/Codex web UI
- hidden account sharing
- credential collection
- secret reads
- OAuth/account linking
- cloud sync
- email sending
- public posting
- purchases/payment actions
- destructive automation
- real external connectors

Non-coding connectors remain placeholder-only with `implemented=false` and `defaultEnabled=false`.

Protected read-blocked patterns include `.env`, `.env.*`, `*.pem`, `*.key`, `id_rsa`, `id_ed25519`, service account files, browser cookies/session stores, token caches, password-manager exports, and private Skynet data.

## Current Jarvis Status

v0.1A, v0.1B, and v0.1C are closed readiness foundations.

The current implementation lane is pre-July-6 local-only dashboard and response-agent productivity work around the existing 37 local response agents.

Expected local response-agent count: 37.

Do not add agents unless the user explicitly asks.

## Current Implementation Focus

Prioritize durable implementation around:

- Local Response Agent Command Center
- workflow presets/playbooks
- context kit builder
- request quality/readiness coach
- result board and decision composer upgrades
- comparison matrix polish
- source/evidence UX
- high-stakes banners
- manual multi-agent workflow polish
- empty states/layout cleanup
- dashboard code organization if needed

Preserve local-only, manual-input-only, response-only, session-only, non-persistent behavior for dashboard helpers. No localStorage, sessionStorage, IndexedDB, cookies, files, downloads, automatic clipboard writes, background tasks, scheduling, automatic agent execution, automatic chaining, or automatic handoff.
