# Validation Dashboard Workflow

The Validation Agent dashboard workflow helps record manual validation evidence for Jarvis PC Local. It uses the existing guarded local Validation Agent API and does not automate the VM or host machine.

## What The Workflow Does

- Shows available validation runbooks.
- Shows the clean Windows VM validation runbook steps.
- Creates a manual validation run.
- Lists recent validation runs.
- Opens a validation run detail view.
- Records manual step status, notes, and evidence.
- Completes a validation evidence record.
- Generates a local Markdown validation report.

## Create A Manual VM Validation Run

Open the local dashboard and use the Validation Agent section. The target environment field defaults to `Clean Windows VM manual validation`; replace it with a concise manual environment summary, such as Windows version and VM resource notes.

Use **Create manual validation run**. This creates a local Jarvis validation record only.

## Record A Step Result

Load the runbook steps, open a run, choose a step, choose one of the supported statuses, and enter concise notes/evidence.

Supported step statuses are:

- `passed`
- `failed`
- `blocked`
- `skipped`
- `not_started`

Use **Record step result** to save the manual evidence. The backend redacts likely token, password, API key, bearer token, GitHub token, OpenAI-style token, `.env`-like, and private-key content before storage and report generation.

Do not paste raw `.env` files, private keys, token values, credential dumps, protected file contents, screenshots, uploads, or long sensitive logs.

## Complete A Run

Use **Complete evidence record** after manual step results are recorded. Completion computes the run status from required step results. Failed required steps produce `failed`; blocked or incomplete required steps produce `blocked`; passed or intentionally skipped required steps can produce `passed`.

## Generate A Report

Use **Generate local report** to write a Markdown report under the local Jarvis reports directory. The report is validation evidence only. It is not certification, warranty, or production-readiness approval.

## Safety Boundaries

The dashboard workflow does not:

- Run commands.
- Control VirtualBox.
- Install dependencies.
- Create installers.
- Build production Tauri.
- Push, merge, rebase, reset hard, force push, or delete files.
- Call paid AI APIs or external services.
- Use OAuth, cloud sync, telemetry, email, public posting, or payment actions.
- Read protected secret file contents.
- Certify security or production readiness.

## Local And LAN Guard Behavior

The dashboard and Validation Agent endpoints use the dashboard/LAN guard. Loopback access works without a token. Non-loopback access requires the configured LAN dashboard token. Do not put tokens in URLs.
