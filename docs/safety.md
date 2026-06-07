# Safety

Jarvis v0.1A is read-only-first and local-first. Agents request actions, the runtime validates them, and blocked decisions are logged to `security.jsonl`.

The v0.1B workflow foundation keeps that model. Tasks may be created and dry-run plans may be validated. Controlled Codex execution exists only for approved plans through the official local CLI; generic shell execution, unrestricted repair loops, and future connectors remain disabled.

Codex planning may create a command preview and approval request. Controlled execution is a separate endpoint and requires an already approved plan.

The first v0.1C dashboard slice is read-only. It exposes local status, safety, connector placeholder, and report visibility only. Unsupported actions such as push, merge, deletion, dependency installation, connector enablement, email, public posting, and purchases must remain absent or unavailable.

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
