# Implementation Roadmap

Planning and roadmap decisions are owned by ChatGPT Project and the user. Codex implements bounded local tasks only; see [chatgpt-codex-workflow.md](chatgpt-codex-workflow.md).

## v0.1A

Implement local service foundation, registries, safety policy, audit logs, project inspection, disabled connector placeholders, and tests.

## Later Versions

Future versions may add controlled execution, UI surfaces, and external connectors only after safety boundaries are expanded deliberately. Those features are not implemented in v0.1A.

## v0.1B Workflow Foundation

Status: complete after v0.1B closeout validation. v0.1C is complete as a private-alpha readiness foundation with dashboard, report, settings/status, LAN token protection, loopback-only setup guidance, stop-task control boundary, desktop-shell placeholder, first-run wizard placeholder, and private-alpha packaging readiness foundations. Post-v0.1C work must be planned and approved through ChatGPT Project and the user before implementation begins.

The first v0.1B slice adds task orchestration, event history, approval records, project locks, dry-run planning, action receipts, risk budget checks, diagnostics export, and report validation. It does not execute Codex or shell commands.

## Completed v0.1B Slices

The reviewed v0.1B slices added controlled execution only after the approval and receipt model was proven. Generic shell execution remains out of scope.

## v0.1B Codex Execution Planning

This slice adds Codex plan records, safe command previews, prompt planning, risk-budget validation, approval linkage, receipts, events, and diagnostics summaries. The approved status means approved for a future execution slice only.

## v0.1B Controlled Codex Execution

This slice adds one approved-plan execution path through the official local Codex CLI. It validates approval, command preview, project paths, prompt/output boundaries, run limits, and project locks before execution. Generic shell execution remains out of scope.

## v0.1B Post-Codex Review and Check Planning

This slice adds a post-execution review gate. After an approved Codex run returns, Jarvis inspects git status and diff stats, enforces changed-file and diff-line budgets, detects protected-file and dependency/package-file path changes without reading protected contents, and stops for user review when policy requires it.

If the review passes, Jarvis generates a planned-check list from detected package scripts only. It prefers typecheck, lint, test, then build. Execution of that planned-check list is handled by the later check execution receipts slice.

## v0.1B Check Execution Receipts

This slice executes only the generated safe check plan after Codex succeeds and post-Codex review passes. Each check is validated through the Safe Action Runtime, run with fixed argv and `shell=False`, recorded with a receipt, and stored on the Codex execution record with redacted output excerpts.

Failed or blocked checks stop the remaining planned checks. Failed executed checks can enter the controlled repair loop.

## v0.1B Controlled Repair Loop

This slice runs at most two Codex repair attempts after failed safe checks. Each attempt uses the official local Codex CLI with fixed argv and `shell=False`, writes the repair prompt under `.jarvis/prompts`, includes redacted failed-check context, reruns post-Codex review, and reruns safe checks only if review passes.

Repair stops on passing checks, repeated failures, max attempts, max Codex runs per task, Codex repair failure, protected/dependency-file changes, or changed-file/diff-line budget issues.

## v0.1B Final Reporting Polish

Final implementation reports must include the post-Codex review findings, safe check results, repair attempts/results, blocked actions or safety decisions, known risks, build-safety status, and recommended next task.

## v0.1C Boundary

v0.1C Slice 1 added read-only dashboard and report visibility. It added local status, safety summary, connector placeholder summary, report listing, report detail, and path-safe report reads only.

v0.1C Slice 2 adds read-only settings/status visibility. Settings are placeholders in this slice: visible as status fields only, not editable controls, and not persisted as user changes.

v0.1C Slice 3 adds LAN dashboard/API token protection foundation. Loopback dashboard/API access remains allowed without a token, while non-loopback access requires a valid `JARVIS_LAN_DASHBOARD_TOKEN` supplied through an accepted header. Missing or too-short tokens deny non-loopback access. Query-string tokens are not accepted and token values are not exposed.

v0.1C Slice 4 adds loopback-only LAN setup guidance and status. It explains manual environment variable setup and accepted headers without exposing token values, token fragments, token hashes, token input fields, token persistence, or token generation.

v0.1C Slice 5 adds a stop-task status/control boundary. It exposes active Jarvis task records and a stop endpoint for known active task IDs only. The stop operation is state-only inside Jarvis: it marks the task canceled, emits `task.canceled`, and releases the Jarvis project lock. It does not stop arbitrary OS processes and does not accept PID, process-name, shell-command, or Windows service identifiers. Dashboard/task endpoints remain LAN-protected.

v0.1C Slice 6 adds a Tauri desktop shell placeholder/readiness foundation. `apps/desktop` contains documentation only, and dashboard/settings status reports the shell as `placeholder_only`. This slice does not install Tauri, add dependencies, launch a desktop app, add an auto-updater, add telemetry, add OS-level permissions, or implement installer/private-alpha packaging. A future shell must respect LAN/token protection and Safe Action Runtime boundaries.

v0.1C Slice 7 adds a first-run wizard placeholder/readiness foundation. The loopback-only page and status expose placeholder metadata and an informational future checklist. This slice does not persist setup state, write config files, generate or store tokens, create accounts, use OAuth, enable cloud sync, add telemetry, add an auto-updater, or implement installer/private-alpha packaging. A future first-run wizard must respect LAN/token protection and Safe Action Runtime boundaries.

v0.1C Slice 8 adds private-alpha packaging documentation/readiness only. It adds short packaging and VM validation checklists plus dashboard/settings metadata. No installer artifact, Tauri production build, code signing, auto-updater, telemetry, GitHub release automation, public release, or cloud distribution is implemented. Manual local run remains the current path.

Post-v0.1C future work must be planned before implementation: full pairing wizard, QR/mobile pairing, production first-run setup, and real installer/private-alpha packaging after readiness validation. Unsupported dashboard controls must remain disabled or absent.
