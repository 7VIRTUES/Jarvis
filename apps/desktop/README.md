# Jarvis Desktop Shell Placeholder

This folder is a v0.1C Slice 6 placeholder for a future Tauri desktop shell.

The future shell is expected to wrap the local Jarvis dashboard. It is not implemented as a production desktop app in this slice. No Tauri dependencies, Rust tooling, package scripts, installer packaging, auto-updater, telemetry, system tray behavior, or OS-level permissions are added here.

Future desktop work must preserve the existing Jarvis boundaries:

- Respect dashboard LAN/token protection.
- Do not bypass the Safe Action Runtime or Permission Engine.
- Do not add generic shell execution, OS automation, process management, Windows service control, cloud sync, or external connector execution.
- Keep installer/private-alpha packaging and first-run wizard work in later planned slices.

This folder intentionally contains documentation only until a later approved slice adds a real desktop shell.

Packaging readiness is also documentation-only. See `PACKAGING_PLACEHOLDER.md`; it does not define a build, installer, updater, signing, or release process.
