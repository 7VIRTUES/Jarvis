# Safety

Jarvis v0.1A is read-only-first and local-first. Agents request actions, the runtime validates them, and blocked decisions are logged to `security.jsonl`.

The v0.1B workflow foundation keeps that model. Tasks may be created and dry-run plans may be validated. Controlled Codex execution exists only for approved plans through the official local CLI; generic shell execution, unrestricted repair loops, and future connectors remain disabled.

Codex planning may create a command preview and approval request. Controlled execution is a separate endpoint and requires an already approved plan.

The first v0.1C dashboard slices expose local status, settings/status placeholders, safety, connector placeholder, report visibility, LAN setup guidance, and a narrow stop-task boundary. Unsupported actions such as push, merge, deletion, dependency installation, connector enablement, email, public posting, purchases, arbitrary process killing, and OS service control must remain absent or unavailable.

Settings/status visibility is not configuration editing. This slice does not create settings persistence, auth tokens, passwords, pairing codes, LAN pairing, desktop shell behavior, first-run wizard behavior, or installer packaging.

LAN setup guidance is loopback-only. Non-loopback requests to setup status and setup HTML are denied even with a valid dashboard token until a real pairing UX exists. The setup surface does not expose token values, token prefixes, token suffixes, token hashes, environment dumps, input fields, persistence, or token creation controls.

## LAN Dashboard Threat Model

Threats for the LAN protection slice:

- A user starts Jarvis bound to `0.0.0.0` or another LAN-reachable host.
- Another device on the LAN tries to read dashboard/API state.
- Report contents are accessed remotely without permission.
- Token leakage through URLs if query-string tokens are accepted.

Mitigations in this slice:

- Loopback dashboard/API requests are allowed without a token.
- Non-loopback dashboard/API requests require `JARVIS_LAN_DASHBOARD_TOKEN`.
- Missing or too-short tokens deny non-loopback access.
- Tokens are accepted only through `X-Jarvis-LAN-Token` or `Authorization: Bearer` headers.
- Query-string tokens and cookie tokens are not accepted.
- Token comparisons use constant-time comparison.
- Token values are not returned in dashboard HTML or JSON responses.

Non-goals for this slice: full pairing UX, user accounts, remote internet access, HTTPS/TLS termination, production-grade public-network authentication, and mobile app pairing.

## Stop-Task Boundary

Stop-task controls apply only to Jarvis-owned task records in the local task table. The API accepts a Jarvis `task_id` path parameter for active task statuses only: `queued`, `running`, and `waiting_for_approval`.

Stopping a Jarvis task marks that task record as `canceled`, emits the existing `task.canceled` event, and releases its Jarvis project lock. It is not a process manager. It must not accept PID, process name, shell command, executable path, or Windows service identifiers, and it must not kill unrelated user applications.

Dashboard, task-status, and stop-task endpoints remain LAN-protected: loopback is allowed without a token, while non-loopback access requires the configured dashboard token.

## Hard Blocks

Jarvis blocks dangerous commands such as `git push`, `git merge`, `git reset --hard`, `rm -rf`, `del /s`, `format`, `diskpart`, `reg delete`, `Disable-WindowsDefender`, unrestricted execution policy changes, downloaded script execution, file deletion automation, secret reads, browser session access, email sending, public posting, and payments.

## Protected Files

Protected paths such as `.env`, `.pem`, `.key`, SSH keys, service account files, browser sessions, cookies, token caches, and password manager exports may be detected by name only. Their contents must not be read or printed.

## Exclusions

Current v0.1 scope does not allow generic Codex execution, automate browsers, use paid AI APIs, access external accounts, or silently escalate permissions.

## Approvals

Approvals are auditable records. Approval can resolve approval-required actions, but it does not bypass hard-blocked actions such as Codex execution, destructive commands, secret reads, email sending, public posting, payments, or future connector execution.

## Codex Planning

Codex command previews must use `workspace-write`, a registered project path, prompt paths under `.jarvis/prompts`, and output paths under `.jarvis/reports`. Generic execution action types such as `codex.execute`, `codex.exec`, `codex.run`, and `run_codex_exec_workspace_write` remain blocked. The only execution path is `codex.execute_approved_plan` through the official CLI after approval.

Execution uses fixed subprocess argv with `shell=False`; no arbitrary shell command endpoint exists.

After Codex returns, Jarvis reviews the git diff before checks are allowed. The review counts changed files and diff lines, detects protected file paths without reading contents, and flags dependency/package files such as `package.json`, lockfiles, `pyproject.toml`, and requirements files. If the review exceeds budget or needs user review, the workflow stops before checks or repair.

If the review passes, Jarvis may execute only the generated safe check plan. Check execution uses fixed argv entries from detected `package.json` scripts, validates each command through the Safe Action Runtime, records receipts, stores redacted command results, and stops on the first failed or blocked check.

If an executed safe check fails, Jarvis may run at most two controlled Codex repair attempts while staying within `maxCodexRunsPerTask`. Each repair uses a validated prompt under `.jarvis/prompts`, fixed Codex argv with `shell=False`, redacted failed-check context, post-repair policy review, and then safe checks again. Repair stops on repeated failures, protected/dependency changes, risk-budget issues, Codex repair failure, or user-review requirements.

## Risk Budgets

Default limits are `maxChangedFiles=10`, `maxDiffLines=700`, `maxRepairAttempts=2`, `maxCodexRunsPerTask=3`, and `maxNewDependenciesWithoutApproval=0`. Plans that exceed these limits require approval before any future execution slice can proceed.

The post-Codex review and repair loop reuse these limits. Dependency/package file changes require user review in this slice because the allowed number of new dependency changes without approval is zero.

## Dashboard Report Safety

Report listing and detail are limited to Markdown files directly under `data/jarvis/reports`. Report detail rejects traversal, absolute paths, nested paths, unexpected extensions, and protected paths before reading content.
