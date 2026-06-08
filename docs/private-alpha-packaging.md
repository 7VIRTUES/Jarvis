# Private Alpha Packaging Placeholder

Status: placeholder/readiness only.

Jarvis does not produce an installer artifact yet. v0.1C Slice 8 adds documentation and dashboard status metadata only.

Current boundaries:

- No MSI or EXE installer is produced.
- No Tauri production build is implemented.
- No code signing is implemented.
- No auto-updater is enabled.
- No telemetry is enabled.
- No GitHub release automation is added.
- No public release or public download page exists.
- No external accounts, paid APIs, or connector activation are part of packaging readiness.
- Manual local run remains the current path.

Before any future private-alpha build, Jarvis must pass fresh Windows VM validation. LAN dashboard testing must use `JARVIS_LAN_DASHBOARD_TOKEN`; setup pages must remain loopback-only; stop task must remain Jarvis-task-record-only; the desktop shell and first-run wizard must remain placeholder-only until their own implementation slices are approved.
