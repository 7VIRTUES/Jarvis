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
- Create dry-run task plans and action receipts through the workflow foundation.
- Create Codex future-run plans, safe command previews, approval requests, and receipts without executing Codex.
- Execute approved Codex plans through the controlled official-CLI path.

## Limits

Generic Codex CLI execution is explicitly not implemented. v0.1B allows only approved-plan controlled execution; repair loops, review loops, and dashboard workflows remain excluded.
