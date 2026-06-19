import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.readiness_snapshot_agent import PrivateAlphaReadinessSnapshotService
from jarvis_core.redacted_diagnostics_agent import RedactedDiagnosticsBundleService
from jarvis_core.validation_agent import ValidationAgentService


PLACEHOLDER_CONNECTOR_JSON = """{
  "id": "gmail",
  "provider": "Gmail",
  "implemented": false,
  "defaultEnabled": false,
  "readinessLevel": "placeholder_only",
  "costMode": "official_free_quota",
  "authType": "oauth_future",
  "privacyClass": "external_account",
  "dataAccess": "none_in_current_v0.1",
  "approvalRequired": true,
  "tokenStorage": "not_implemented",
  "dataRetention": "none",
  "notes": "Placeholder only."
}"""


def write_text(path, text="placeholder"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    for relative in [
        "README.md",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "docs/public-repo-readiness.md",
        "docs/public-safety-boundaries.md",
        "docs/security-safety-agent.md",
        "docs/project-profiles.md",
        "docs/dashboard-profile-security-surfaces.md",
        "docs/validation-agent.md",
        "docs/validation-dashboard-workflow.md",
        "docs/vm-validation-runbook.md",
    ]:
        write_text(workspace / relative, "Jarvis local readiness boundary. This is not production-ready.")
    write_text(workspace / "connectors" / "placeholders" / "gmail.json", PLACEHOLDER_CONNECTOR_JSON)
    write_text(workspace / "connectors" / "agents" / "redacted-diagnostics-agent.json", '{"implemented":true}')
    write_text(workspace / "connectors" / "agents" / "security-safety-agent.json", '{"implemented":true}')
    write_text(workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "project_profiles.py", "profile")
    write_text(workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "workspace_boundary.py", "boundary")
    write_text(
        workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "dashboard.py",
        "api_reports /api/reports settings-status project-profiles security-safety-review validation-agent-status Generate local report private-alpha-readiness-snapshot redacted-diagnostics-bundle",
    )
    return workspace


def diagnostics_app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = create_workspace(tmp_path)
    data_root = tmp_path / "data" / "jarvis"
    reports_root = data_root / "reports"
    connector_root = workspace / "connectors"
    diagnostics = RedactedDiagnosticsBundleService(conn, reports_root, workspace, connector_root)
    validation = ValidationAgentService(conn, reports_root)
    readiness = PrivateAlphaReadinessSnapshotService(conn, reports_root, workspace, connector_root)
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "redacted_diagnostics", diagnostics)
    monkeypatch.setattr(app_module, "validation_agent", validation)
    monkeypatch.setattr(app_module, "readiness_snapshots", readiness)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return diagnostics, dashboard


def test_diagnostics_bundle_endpoint_returns_redacted_bundle(tmp_path, monkeypatch):
    diagnostics_app_services(tmp_path, monkeypatch)

    bundle = app_module.get_redacted_diagnostics_bundle()

    assert bundle["agentId"] == "redacted_diagnostics_agent"
    assert bundle["summary"]["localOnly"] is True
    assert bundle["summary"]["commandExecution"] is False
    assert bundle["sections"]["dashboardSafetySettingsSummary"]["safety"]["browserAutomation"] is False


def test_diagnostics_bundle_report_endpoint_writes_local_reports(tmp_path, monkeypatch):
    diagnostics_app_services(tmp_path, monkeypatch)

    report = app_module.write_redacted_diagnostics_bundle_report()

    assert report["reportId"].startswith("diagnostics-bundle-")
    assert report["jsonReportId"].startswith("diagnostics-bundle-")
    latest = app_module.get_latest_redacted_diagnostics_bundle()
    assert latest["available"] is True
    assert latest["reportId"] == report["reportId"]


def test_dashboard_summary_includes_diagnostics_bundle(tmp_path, monkeypatch):
    diagnostics_app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    diagnostics = summary["redactedDiagnosticsBundle"]

    assert summary["capabilities"]["redactedDiagnosticsBundle"] == "local_redacted_diagnostics"
    assert diagnostics["agentId"] == "redacted_diagnostics_agent"
    assert diagnostics["commandExecution"] is False
    assert diagnostics["externalServices"] is False
    assert diagnostics["uploads"] is False
    assert diagnostics["protectedSecretReads"] is False
    assert diagnostics["certification"] is False


def test_dashboard_diagnostics_bundle_section_appears(tmp_path, monkeypatch):
    diagnostics_app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert 'id="redacted-diagnostics-bundle"' in page_text
    assert "redacted diagnostics bundle" in page_text
    assert "generate local diagnostics report" in page_text
    assert "/diagnostics/bundle" in page_text
    assert "local redacted diagnostics only" in page_text
    assert "does not upload" in page_text
    assert "does not run commands" in page_text
    assert "does not read protected secrets" in page_text


def test_dashboard_diagnostics_bundle_does_not_include_forbidden_controls(tmp_path, monkeypatch):
    diagnostics_app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    forbidden_button_labels = [
        "upload diagnostics",
        "send to support",
        "publish logs",
        "run diagnostics commands",
        "fix automatically",
        "deploy",
        "certify",
    ]
    assert all(f">{label}<" not in page_text for label in forbidden_button_labels)
    assert ">generate local diagnostics report<" in page_text


def test_diagnostics_bundle_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/diagnostics/bundle",
        "/diagnostics/bundle/report",
        "/diagnostics/bundle/latest",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls
