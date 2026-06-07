# Tauri Readiness Notes

Status: placeholder_only.

This slice records readiness expectations for a future Tauri shell without adding a working desktop application.

Future implementation requirements:

- Wrap the local Jarvis dashboard URL served by `jarvis_core.app`.
- Keep LAN/token protection in force; the shell must not become a bypass for remote access rules.
- Keep all sensitive actions behind the existing Safe Action Runtime, approvals, and audit events.
- Do not add auto-update or telemetry in v0.1.
- Do not add installer/private-alpha packaging in this slice.
- Do not request OS-level permissions for host-PC control unless a later approved security review explicitly allows them.

Non-goals for this placeholder:

- No `tauri.conf.json`.
- No `package.json`.
- No Rust crate.
- No installer scripts.
- No launch, install, update, or service-control commands.
