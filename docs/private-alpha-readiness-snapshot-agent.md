# Private-Alpha Readiness Snapshot Agent

The Private-Alpha Readiness Snapshot Agent produces a guarded local readiness snapshot for Jarvis PC Local. It aggregates existing local evidence and status so a human can see what is still missing before any separately planned private-alpha packaging or clean Windows VM release validation.

## What It Does

- Summarizes current milestone status.
- Summarizes Validation Agent runbook, run, and report metadata.
- Summarizes Security/Safety Review report metadata.
- Summarizes Project Profile and workspace boundary status.
- Summarizes dashboard readiness surfaces.
- Checks known public-readiness documentation presence.
- Checks future connector placeholder and cost boundaries.
- Records explicit non-release boundaries.
- Writes a local Markdown readiness report under the Jarvis reports directory.

## What It Does Not Do

- It does not build installers.
- It does not package Tauri.
- It does not create release artifacts.
- It does not publish anything.
- It does not push to GitHub.
- It does not run commands.
- It does not control VirtualBox.
- It does not automate tests.
- It does not call external services or paid AI APIs.
- It does not read protected secret file contents.
- It does not certify security or production readiness.

## Snapshot Sections

- Current milestone status
- Validation evidence
- Security/Safety Review status
- Project Profile / Workspace Boundary status
- Dashboard readiness surfaces
- Public repository readiness
- Connector and cost boundary
- Explicit non-release boundary

## Verdict Meanings

- `blocked`: A safety or readiness blocker must be resolved before continuing packaging planning.
- `needs_review`: Human review is needed before relying on the snapshot.
- `needs_evidence`: VM validation evidence or local validation reports are missing or incomplete.
- `ready_for_manual_vm_validation`: Foundations are present for manual VM validation planning. This does not mean release readiness.

The agent never returns `production_ready`, `release_ready`, `installer_ready`, or `certified_secure`.

## API Endpoints

- `GET /readiness/snapshot`
- `POST /readiness/snapshot/report`
- `GET /readiness/snapshot/latest`

All endpoints are guarded by the dashboard/LAN access guard. The report endpoint writes only a local Markdown readiness report.

## Dashboard Surface

The dashboard shows a Private-Alpha Readiness Snapshot section with overall verdict, blocker count, warning count, validation evidence status, security review status, public docs status, connector/cost boundary status, and endpoint references.

The only dashboard action is **Generate local readiness report**.

## Safety Boundaries

The readiness snapshot is evidence aggregation only. It is not production certification, security certification, an installer, a release artifact, GitHub automation, command execution, VM automation, telemetry, OAuth, cloud sync, or connector implementation.
