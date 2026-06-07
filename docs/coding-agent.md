# Coding Agent

The Coding Agent is the only implemented agent manifest in v0.1A.

## Capabilities

- Inspect a registered project.
- Detect git availability, repository status, and current branch when available.
- Detect `package.json` and package scripts.
- Detect README, docs, `AGENTS.md`, and `.jarvis/project.md` presence.
- Detect protected file presence by path/name without reading values.
- Detect whether the official Codex CLI command exists.
- Generate a check plan from detected package scripts.
- Write a Markdown report.

## Limits

Codex CLI execution is explicitly not implemented. Repair loops, review loops, task queues, and dashboard workflows are excluded from v0.1A.

