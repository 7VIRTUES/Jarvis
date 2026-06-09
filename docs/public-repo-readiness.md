# Public Repository Readiness

Use this checklist before making the repository public:

- Git status is clean.
- There are no unpushed local commits.
- There are no important untracked files.
- There are no stashes that contain repository work.
- No secrets or protected files are tracked.
- No private local paths are tracked.
- No local SQLite, log, or runtime files are tracked.
- Documentation makes no production claims.
- Future connectors are still disabled placeholders.
- No paid AI APIs are implemented or required.
- No browser automation is implemented.
- No public installer or release claims are present.
- GitHub secret scanning and push protection are enabled before the visibility change, if available.
- If any secret was ever committed, rotate or revoke it first and do not rely only on deletion.

This checklist does not replace a history review. If a real secret or private artifact appears in history, stop and handle rotation, revocation, and history-cleanup decisions outside Codex.
