# Jarvis Agent Workflow

This repository uses a strict ChatGPT/Codex split.

## ChatGPT Project Role

ChatGPT Project handles planning, architecture, safety review, prompt writing, review triage, and next-step decisions.

When ChatGPT needs current repo state for planning or review, it should ask the user to push local updates to GitHub. After the user pushes, ChatGPT may inspect GitHub read-only. ChatGPT must not directly edit GitHub files, create commits, push branches, or merge changes for Jarvis.

## Codex Role

Codex handles implementation only: code changes, documentation changes, file edits, tests, local command execution, and approved local commits.

Codex must not make broad planning, architecture, roadmap, or product-direction decisions. If a task requires those decisions, Codex should stop and ask for ChatGPT/user direction.

## Repository Boundaries

- Do not start v0.1C unless explicitly requested.
- Do not add dashboard work, external connectors, paid APIs, browser automation, push/merge automation, or dependency changes unless explicitly approved for the current task.
- Preserve local changes and inspect the worktree before editing.
- Keep implementation slices narrow, reviewable, and aligned with the current approved plan.
