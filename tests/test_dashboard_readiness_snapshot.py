from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access
from jarvis_core.readiness_snapshot_agent import PrivateAlphaReadinessSnapshotService
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
    write_text(
        workspace / "connectors" / "placeholders" / "gmail.json",
        PLACEHOLDER_CONNECTOR_JSON,
    )
    write_text(
        workspace / "connectors" / "agents" / "security-safety-agent.json",
        '{"id":"security_safety_agent","implemented":true}',
    )
    write_text(
        workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "project_profiles.py",
        "project profile capability",
    )
    write_text(
        workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "workspace_boundary.py",
        "workspace boundary validator",
    )
    write_text(
        workspace / "services" / "jarvis-core" / "src" / "jarvis_core" / "dashboard.py",
        "api_reports /api/reports settings-status project-profiles security-safety-review validation-agent-status Generate local report private-alpha-readiness-snapshot",
    )
    return workspace


def readiness_app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = create_workspace(tmp_path)
    data_root = tmp_path / "data" / "jarvis"
    reports_root = data_root / "reports"
    connector_root = workspace / "connectors"
    readiness = PrivateAlphaReadinessSnapshotService(conn, reports_root, workspace, connector_root)
    validation = ValidationAgentService(conn, reports_root)
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "readiness_snapshots", readiness)
    monkeypatch.setattr(app_module, "validation_agent", validation)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return readiness, dashboard


def test_dashboard_snapshot_endpoint_works(tmp_path, monkeypatch):
    readiness_app_services(tmp_path, monkeypatch)

    snapshot = app_module.get_readiness_snapshot()

    assert snapshot["agentId"] == "private_alpha_readiness_agent"
    assert snapshot["overallVerdict"] in {"ready_for_manual_vm_validation", "needs_evidence", "needs_review", "blocked"}
    assert snapshot["sections"]["connector_and_cost_boundary"]["items"]["futureConnectorsPlaceholderOnly"] is True


def test_dashboard_report_endpoint_writes_local_report(tmp_path, monkeypatch):
    readiness_app_services(tmp_path, monkeypatch)

    report = app_module.write_readiness_snapshot_report()

    assert report["reportId"].startswith("private-alpha-readiness-snapshot-")
    assert (tmp_path / "data" / "jarvis" / "reports" / report["reportId"]).exists()
    latest = app_module.get_latest_readiness_snapshot()
    assert latest["available"] is True
    assert latest["reportId"] == report["reportId"]


def test_dashboard_summary_includes_readiness_snapshot(tmp_path, monkeypatch):
    readiness_app_services(tmp_path, monkeypatch)

    summary = app_module.dashboard_summary()
    readiness = summary["privateAlphaReadinessSnapshot"]

    assert summary["capabilities"]["privateAlphaReadinessSnapshot"] == "local_readiness_snapshot"
    assert readiness["agentId"] == "private_alpha_readiness_agent"
    assert readiness["commandExecution"] is False
    assert readiness["virtualBoxAutomation"] is False
    assert readiness["installerCreation"] is False
    assert readiness["githubWrites"] is False
    assert readiness["externalServices"] is False
    assert readiness["certification"] is False


def test_dashboard_readiness_section_appears_in_html(tmp_path, monkeypatch):
    readiness_app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert 'id="private-alpha-readiness-snapshot"' in page_text
    assert "private-alpha readiness snapshot" in page_text
    assert "generate local readiness report" in page_text
    assert "/readiness/snapshot" in page_text
    assert "local readiness summary only" in page_text
    assert "does not create installer artifacts" in page_text
    assert "does not run vm automation" in page_text
    assert "does not push to github" in page_text


def test_dashboard_does_not_include_forbidden_fake_automation_controls(tmp_path, monkeypatch):
    readiness_app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8")
    lowered = page_text.lower()

    forbidden = [
        "build installer",
        "package release",
        "publish release",
        "deploy",
        "certify",
        "run vm validation",
        "fix blockers",
        "push to github",
    ]
    assert all(f">{label}<" not in lowered for label in forbidden)
    assert ">generate local readiness report<" in lowered


def test_readiness_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/readiness/snapshot",
        "/readiness/snapshot/report",
        "/readiness/snapshot/latest",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_unknown_readiness_report_read_is_safe(tmp_path, monkeypatch):
    readiness, _dashboard = readiness_app_services(tmp_path, monkeypatch)

    try:
        readiness.read_markdown_report("missing.md")
    except PermissionError as exc:
        assert "readiness snapshot report id" in str(exc)
    else:
        raise AssertionError("non-generated report ids should be rejected")
