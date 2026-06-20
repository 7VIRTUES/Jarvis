# Public Safety Boundaries

Jarvis PC Local is the active product in this repository. Skynet is reference-only and must not be copied into Jarvis as code, configuration, data, memory, logs, credentials, token caches, private paths, or roadmap.

The public repository boundary is:

- No secrets or local data in the repo
- Disabled future connectors
- No browser automation
- No paid APIs
- No Git push, merge, or delete automation
- No production release artifacts
- No installer
- No full pairing or OAuth/cloud setup
- No public telemetry or auto-updater

The Validation Agent is local evidence tracking only. It records manual validation runbook results and redacted notes/reports, but it does not run commands, automate VirtualBox, install dependencies, create installers, push, merge, delete files, call external services, or read protected secret file contents.

The Private-Alpha Readiness Snapshot Agent is local evidence aggregation only. It reads safe local metadata and existing report metadata, writes local Markdown readiness reports, and does not build installers, create release artifacts, run commands, automate VirtualBox, push to GitHub, call external services, read protected secret file contents, or certify security or production readiness.

The Redacted Diagnostics Bundle Agent is local troubleshooting evidence aggregation only. It reads safe metadata and summaries, writes local redacted Markdown/JSON diagnostics reports, and does not upload diagnostics, run commands, call external services, read protected secret file contents, or certify security or production readiness.

The Evidence Report Center is local report visibility only. It indexes bounded safe metadata from allowed Markdown/JSON reports under the Jarvis reports directory, redacts summaries/detail, and does not upload, send, share, edit, delete, rewrite, certify, browse arbitrary folders, call external services, or read protected secret file contents.

These boundaries should remain visible in documentation, tests, and connector status until future work is separately planned and reviewed.
