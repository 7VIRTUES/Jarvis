# VM Private Alpha Readiness Checklist

This checklist is informational only. It is not release automation and does not produce an installer.

- Use a fresh Windows VM.
- Clone the repository.
- Create a Python virtual environment.
- Install the documented local Python dependencies already present in the repo setup.
- Run the test suite.
- Start Jarvis Core.
- Verify `/dashboard` on loopback.
- Configure `JARVIS_LAN_DASHBOARD_TOKEN` for LAN testing.
- Verify LAN dashboard access is denied without the token.
- Verify LAN dashboard access is allowed with the token.
- Verify setup pages are loopback-only.
- Verify reports view.
- Verify settings/status view.
- Verify stop-task boundary remains Jarvis-task-record-only.
- Verify diagnostic export.
- Confirm future connectors remain disabled.
- Confirm no paid AI APIs are enabled.
- Confirm no browser automation is enabled.
- Confirm no push, merge, or delete automation is exposed.
