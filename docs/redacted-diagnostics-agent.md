# Redacted Diagnostics Bundle Agent

The Redacted Diagnostics Bundle Agent creates local troubleshooting bundles for Jarvis PC Local. It aggregates safe metadata and summaries from app status, dashboard status, safety/settings status, validation evidence metadata, readiness snapshot metadata, security review report metadata, project summaries, recent task/event/approval metadata, connector placeholder status, and diagnostics limitations.

The agent is local-only. It writes redacted Markdown and JSON reports under the existing Jarvis reports directory and exposes guarded dashboard/API surfaces for viewing current bundle JSON and generating local reports.

## What It Does

- Produces a structured redacted diagnostics bundle.
- Generates local Markdown reports named `diagnostics-bundle-YYYYMMDDTHHMMSSZ.md`.
- Generates local JSON reports named `diagnostics-bundle-YYYYMMDDTHHMMSSZ.json`.
- Summarizes validation runs without raw notes or evidence dumps.
- Summarizes readiness and security review report metadata without raw findings or secret snippets.
- Summarizes connector boundaries and confirms future connectors remain placeholder-only.
- Redacts synthetic or real-looking secret patterns before returning API responses or writing reports.

## What It Does Not Do

- Does not upload diagnostics.
- Does not call external services.
- Does not run shell commands, Git commands, tests, Codex, browser automation, or VirtualBox automation.
- Does not install dependencies, create installers, create release artifacts, send email, post publicly, or write to GitHub.
- Does not read protected secret file contents, private keys, token stores, browser/session stores, raw SQLite bytes, or full raw logs.
- Does not certify production readiness or security readiness.

## Bundle Sections

- App Metadata
- Dashboard/Safety/Settings Summary
- Project/Profile Summary
- Validation Evidence Summary
- Readiness Snapshot Metadata
- Security Review Metadata
- Recent Task/Event/Approval Summary
- Connector Boundary Summary
- Redaction Summary
- Warnings
- Limitations
- Safety Note

## Redaction

The bundle redacts API-key assignments, password-like assignments, bearer tokens, GitHub token patterns, OpenAI-style `sk-` tokens, private key blocks, long token-looking strings, `.env`-like lines, and known private local path patterns.

Reports and API responses must not include raw matched secret values. If a real secret was ever exposed outside this agent, rotate it manually; redaction is not credential cleanup.

## API Endpoints

- `GET /diagnostics/bundle`
- `POST /diagnostics/bundle/report`
- `GET /diagnostics/bundle/latest`

All diagnostics bundle endpoints use dashboard LAN access protection.

## Dashboard Surface

The dashboard includes a Redacted Diagnostics Bundle section with safe status fields, latest report metadata, endpoint references, and one action: `Generate local diagnostics report`.

The dashboard does not expose upload, send-to-support, publish, command-running, deploy, fix automatically, or certify controls.

## Safety Boundaries

The diagnostics bundle is local troubleshooting evidence only. It is not uploaded, not a complete audit, not history review, not credential rotation, and not production/security certification.
