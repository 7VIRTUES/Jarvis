# ChatGPT and Codex Workflow

Jarvis uses ChatGPT Project for planning, review, validation reasoning, and prompt writing. Codex is reserved for local implementation only.

## ChatGPT Project Role

ChatGPT Project handles:

- planning and architecture
- safety review and risk decisions
- scope control
- GitHub read-only repo inspection after the user pushes
- commit/diff/PR review
- validation review when GitHub state or pasted outputs are enough
- prompt writing for implementation tasks
- review triage and next-step decisions

When ChatGPT needs current repository state, the user should push local updates to GitHub or paste local outputs. After the push, ChatGPT may inspect GitHub read-only. ChatGPT must not directly edit GitHub files, create commits, push branches, merge changes, delete files, or perform implementation work for Jarvis.

## Codex Role

Codex handles implementation only:

- code changes
- documentation changes
- test changes
- file edits
- narrow refactors
- local commands needed to complete an implementation task

Codex must not make broad planning, architecture, roadmap, or product-direction decisions. Codex should not be used for validation-only passes, repo audits, closeout-only reviews, checking commits, checking PR status, or confirming file existence. If a task requires planning or review, Codex should stop and ask for ChatGPT/user direction.

## Extreme Codex Budgeting

Default Codex prompt rules:

- no branch creation unless explicitly requested
- no push
- no merge
- no rebase
- no reset hard
- no deletion automation
- no commits by default
- no broad validation-only scope
- no full test suite unless needed or explicitly requested
- run only targeted checks needed for the edit
- stop if the task becomes planning, architecture, or scope decision-making

## Handoff Pattern

During pre-MVP development, Jarvis may use direct local work on `main` instead of feature branches. The user manually pushes after review.

1. ChatGPT plans or reviews in GitHub read-only mode.
2. ChatGPT decides whether Codex is truly needed.
3. If implementation is needed, ChatGPT writes a bounded implementation prompt.
4. Codex edits files locally and reports exact changes.
5. The user reviews and manually pushes from VS Code/Git.
6. ChatGPT inspects GitHub read-only after the push and decides the next task.

## Current Status

v0.1A is closed.
v0.1B is closed.
v0.1C is closed as a private-alpha readiness foundation.

Post-v0.1C work must be planned before implementation: clean Windows VM validation, optional security-hardening review, full pairing/QR/mobile pairing, production first-run setup, real Tauri app, real private-alpha packaging, and v0.2 planning.

## Boundaries

- No future connector implementation in v0.1.
- No paid AI APIs or API keys.
- No browser automation of ChatGPT or Codex.
- No package/dependency changes unless explicitly approved for the current implementation task.
- No pushing, merging, hard resets, or deleting files.
- No Codex validation-only prompts when ChatGPT/GitHub mode can perform the review.
