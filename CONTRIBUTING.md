# Contributing

Jarvis uses a strict ChatGPT/Codex workflow split.

ChatGPT Project handles planning, architecture, safety review, scope control, prompt writing, review triage, and next-step decisions. Codex is implementation-only: code edits, documentation edits, tests, and narrow local commands needed for an approved implementation task.

Codex must not push, merge, reset hard, delete files, install dependencies, or read secrets by default. Contributors should preserve that boundary when preparing prompts, reviews, and pull requests.

## Public Repository Hygiene

Do not add secrets, API keys, tokens, local paths, private user data, runtime logs, SQLite databases, generated packages, installer artifacts, or hidden local configuration.

Future connectors must remain placeholder-only unless a separate planning and review step approves implementation. Pull requests should preserve v0.1 boundaries and include safety notes for any behavior that affects execution, permissions, logging, connector status, local files, or user approval.
