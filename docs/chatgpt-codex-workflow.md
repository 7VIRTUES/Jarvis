# ChatGPT and Codex Workflow

Jarvis uses ChatGPT Project for planning and review, and Codex for local implementation.

## ChatGPT Project

ChatGPT Project owns:

- planning and architecture
- safety review and risk decisions
- prompt writing for implementation tasks
- review triage and next-step decisions
- deciding when current GitHub state is needed for planning or review

If ChatGPT needs the current repository state, it should ask the user to push local updates to GitHub. After the push, ChatGPT may inspect GitHub read-only. ChatGPT must not directly edit GitHub files, create commits, push branches, merge changes, or perform implementation work for Jarvis.

## Codex

Codex owns local implementation:

- code changes
- documentation changes
- file edits
- local test and verification commands
- local commits when explicitly approved

Codex should work from a clear task or prompt. Codex must not make broad planning, architecture, roadmap, product-scope, or next-phase decisions. If implementation reveals a planning question, Codex should stop and report the decision needed.

## Handoff Pattern

1. ChatGPT plans or reviews the work and writes a bounded implementation prompt.
2. The user gives that prompt to Codex.
3. Codex implements locally, verifies, and reports exact changes and command results.
4. Codex may create an approved local commit, but does not push.
5. If ChatGPT needs to review current code, ChatGPT asks the user to push the local branch.
6. ChatGPT inspects GitHub read-only after the push and decides the next task with the user.

## Boundaries

- No v0.1C work unless explicitly requested.
- No dashboard work unless explicitly requested.
- No connector implementation unless explicitly requested.
- No paid AI APIs or API keys.
- No browser automation of ChatGPT or Codex.
- No package or dependency changes unless explicitly approved for the current task.
- No pushing, merging, hard resets, or deleting files unless explicitly requested and verified as safe.
