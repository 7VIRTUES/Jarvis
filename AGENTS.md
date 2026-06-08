# Jarvis Agent Workflow

This repository uses a strict ChatGPT/Codex split with extreme Codex capability budgeting.

## ChatGPT Project Role

ChatGPT Project handles planning, architecture, safety review, scope control, GitHub read-only inspection, diff/commit/PR review, validation review, prompt writing, review triage, and next-step decisions.

When ChatGPT needs current repo state, the user should push local updates to GitHub or paste local outputs. After the user pushes, ChatGPT may inspect GitHub read-only. ChatGPT must not directly edit GitHub files, create commits, push branches, merge changes, or delete files for Jarvis.

## Codex Role

Codex handles implementation only: code changes, documentation changes, test changes, file edits, and local commands needed to complete a narrow implementation task.

Codex must not be used for validation-only passes, broad repo audits, closeout-only reviews, checking commits, checking PR status, planning, architecture, roadmap decisions, or product-direction decisions. If a task requires those decisions, Codex should stop and ask for ChatGPT/user direction.

## Default Codex Prompt Rules

- Work on local `main` during pre-MVP unless instructed otherwise.
- Do not create a branch unless explicitly requested.
- Do not push.
- Do not merge.
- Do not rebase.
- Do not reset hard.
- Do not delete files.
- Do not commit by default.
- Do not run broad validation-only tasks.
- Run only targeted checks needed for the implementation unless explicitly asked.
- Keep implementation slices narrow, reviewable, and aligned with the approved plan.

## Current Status

v0.1A is closed.
v0.1B is closed.
v0.1C is closed as a private-alpha readiness foundation.

Post-v0.1C work must be planned before implementation. Do not start v0.2, production Tauri, real installer packaging, full pairing, QR/mobile pairing, future connectors, paid APIs, or browser automation unless explicitly planned and approved.

## Repository Boundaries

- Jarvis is the active product; Skynet is reference only.
- Do not copy Skynet code, data, configs, memory, logs, `.env` files, SQLite files, private paths, or roadmap.
- Non-coding connectors remain placeholders only with `implemented=false` and `defaultEnabled=false`.
- Preserve local changes and inspect the worktree before editing.
