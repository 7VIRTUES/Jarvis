# Implementation Roadmap

Planning and roadmap decisions are owned by ChatGPT Project and the user. Codex implements bounded local tasks only; see [chatgpt-codex-workflow.md](chatgpt-codex-workflow.md).

## v0.1A

Implement local service foundation, registries, safety policy, audit logs, project inspection, disabled connector placeholders, and tests.

## Later Versions

Future versions may add controlled execution, UI surfaces, and external connectors only after safety boundaries are expanded deliberately. Those features are not implemented in v0.1A.

## v0.1B Workflow Foundation

Status: complete after v0.1B closeout validation. v0.1C is next, but it must be planned and approved through ChatGPT Project and the user before implementation begins.

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

Do not start v0.1C from Codex implementation work. v0.1C scope must be planned and approved through ChatGPT Project and the user before any implementation begins.
