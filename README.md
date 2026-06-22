# Jarvis PC Local

Jarvis PC Local is a Windows-first, local-first assistant platform for safely supervising AI-assisted computer and coding workflows. It is designed around user approval, local execution, audit logs, and safe tool boundaries.

## What Jarvis Is

Jarvis is a supervised local assistant foundation. It routes user requests through safe agents and tools so work can happen with visibility, approvals, and reports instead of hidden background automation.

The first supported agent is the Coding Agent. Its goal is to help users manage coding tasks while keeping execution local, bounded, and auditable.

## Current Status

v0.1A, v0.1B, and v0.1C are closed.

v0.1C is a private-alpha readiness foundation. This repository is not yet a production app, polished installer, app-store product, or public release artifact. Clean Windows VM validation is still recommended before any real private-alpha packaging.

## What Works Today

- Local FastAPI service
- Project registry
- Coding Agent foundation
- Official Codex CLI integration boundary
- Safe Action Runtime
- Permission checks
- Audit/event logs
- Dashboard/report visibility
- Settings/status visibility
- Local validation evidence tracking
- LAN dashboard token protection
- Loopback-only setup guidance
- Stop-task boundary for Jarvis-owned task records
- Disabled placeholder future connectors

## What Is Not Included Yet

- No production desktop app
- No real installer
- No public release build
- No mobile app
- No full pairing or QR/mobile pairing
- No production first-run setup
- No cloud sync
- No paid AI APIs
- No OpenAI, Anthropic, or Gemini API keys
- No browser automation of ChatGPT or Codex web UI
- No external account connectors
- No email/social/payment actions
- No future connector implementation

## Safety Model

Jarvis validates actions before execution. Dangerous commands are blocked, protected secret files are not read by default, and future connectors remain disabled placeholders.

Push, merge, and delete automation is blocked. Meaningful actions are logged so users can see what happened, what was blocked, and what still needs review. Jarvis is meant to be user-controlled and auditable.

## Quick Start for Developers

From Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn --app-dir services/jarvis-core/src jarvis_core.app:app --reload
```

Run tests:

```powershell
python -m pytest
```

## Project Documentation

- [Security Policy](SECURITY.md)
- [Contributing Guide](CONTRIBUTING.md)
- [ChatGPT and Codex Workflow](docs/chatgpt-codex-workflow.md)
- [Public Repository Readiness](docs/public-repo-readiness.md)
- [Public Safety Boundaries](docs/public-safety-boundaries.md)
- [Security/Safety Review Agent](docs/security-safety-agent.md)
- [Validation Agent](docs/validation-agent.md)
- [Validation Dashboard Workflow](docs/validation-dashboard-workflow.md)
- [Private-Alpha Readiness Snapshot Agent](docs/private-alpha-readiness-snapshot-agent.md)
- [Private-Alpha Readiness Snapshot Runbook](docs/private-alpha-readiness-snapshot-runbook.md)
- [Redacted Diagnostics Bundle Agent](docs/redacted-diagnostics-agent.md)
- [Diagnostics Bundle Runbook](docs/diagnostics-bundle-runbook.md)
- [Evidence Report Center](docs/evidence-report-center.md)
- [Evidence Report Center Runbook](docs/evidence-report-center-runbook.md)
- [Agent Manifest Health Center](docs/agent-manifest-health-center.md)
- [Agent Manifest Health Runbook](docs/agent-manifest-health-runbook.md)
- [Docs/Runbook Center](docs/docs-runbook-center.md)
- [Docs/Runbook Center Runbook](docs/docs-runbook-center-runbook.md)
- [Clean Windows VM Validation Runbook](docs/vm-validation-runbook.md)
- [Clean Windows VM Validation Runbook Pack](docs/vm-validation-runbook-pack.md)
- [Project Profiles and Workspace Boundaries](docs/project-profiles.md)
- [Dashboard Project Profile and Security Review Surfaces](docs/dashboard-profile-security-surfaces.md)
- [Dashboard Home Navigation](docs/dashboard-home-navigation.md)
- [Dashboard Section Search](docs/dashboard-section-search.md)
- [Dashboard Accessibility And Keyboard Navigation](docs/dashboard-accessibility-keyboard.md)
- [Recent Activity / Audit Trail Center](docs/activity-timeline.md)
- [Recent Activity / Audit Trail Runbook](docs/activity-timeline-runbook.md)
- [Backup Readiness Checklist Center](docs/backup-readiness-center.md)
- [Backup Readiness Runbook](docs/backup-readiness-runbook.md)
- [Clean Windows VM Validation Prep Center](docs/vm-validation-prep-center.md)
- [Clean Windows VM Validation Prep Runbook](docs/vm-validation-prep-runbook.md)

## Roadmap Note

Future work such as real private-alpha packaging, production Tauri, full pairing/QR, production first-run setup, and v0.2 require separate planning and review before implementation.
