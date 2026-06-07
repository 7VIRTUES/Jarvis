# Safety

Jarvis v0.1A is read-only-first and local-first. Agents request actions, the runtime validates them, and blocked decisions are logged to `security.jsonl`.

The v0.1B workflow foundation keeps that model. Tasks may be created and dry-run plans may be validated, but Codex, shell execution, repair loops, and future connectors remain disabled.

Codex planning may create a command preview and approval request. Controlled execution is a separate endpoint and requires an already approved plan.

## Hard Blocks

Jarvis blocks dangerous commands such as `git push`, `git merge`, `git reset --hard`, `rm -rf`, `del /s`, `format`, `diskpart`, `reg delete`, `Disable-WindowsDefender`, unrestricted execution policy changes, downloaded script execution, file deletion automation, secret reads, browser session access, email sending, public posting, and payments.

## Protected Files

Protected paths such as `.env`, `.pem`, `.key`, SSH keys, service account files, browser sessions, cookies, token caches, and password manager exports may be detected by name only. Their contents must not be read or printed.

## Exclusions

Current v0.1 scope does not execute Codex, automate browsers, use paid AI APIs, access external accounts, or silently escalate permissions.

## Approvals

Approvals are auditable records. Approval can resolve approval-required actions, but it does not bypass hard-blocked actions such as Codex execution, destructive commands, secret reads, email sending, public posting, payments, or future connector execution.

## Codex Planning

Codex command previews must use `workspace-write`, a registered project path, prompt paths under `.jarvis/prompts`, and output paths under `.jarvis/reports`. Generic execution action types such as `codex.execute`, `codex.exec`, `codex.run`, and `run_codex_exec_workspace_write` remain blocked. The only execution path is `codex.execute_approved_plan` through the official CLI after approval.

Execution uses fixed subprocess argv with `shell=False`; no arbitrary shell command endpoint exists.

## Risk Budgets

Default limits are `maxChangedFiles=10`, `maxDiffLines=700`, `maxRepairAttempts=2`, `maxCodexRunsPerTask=3`, and `maxNewDependenciesWithoutApproval=0`. Plans that exceed these limits require approval before any future execution slice can proceed.
