# Agent Manifest Health Runbook

Use the Agent Manifest Health Center when reviewing whether Jarvis local agents and future connector placeholders remain bounded.

## Refresh Manifest Health

1. Open the guarded local dashboard.
2. Find the Agent Manifest Health Center section.
3. Use `Refresh manifest health`.
4. Review warning count and flagged manifests.

The refresh reads known local manifest JSON files only. It does not mutate files, change connector state, execute tools, or contact external services.

## Review Warnings

Warnings are review aids. A warning can indicate missing required fields, missing safety notes, unsafe safety booleans on implemented local agents, unexpected placeholder state, or an unknown JSON shape.

## Boundaries

- Only `connectors/agents/*.json` and `connectors/placeholders/*.json` are read.
- Future connector placeholders must remain `implemented=false` and `defaultEnabled=false`.
- The health center does not claim production, security, or release readiness.
