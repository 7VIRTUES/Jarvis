import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService, dashboard_html
from jarvis_core.dashboard_surface_health import DashboardSurfaceHealthService
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    data_root = tmp_path / "data" / "jarvis"
    connector_root = workspace / "connectors"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    return dashboard


def service_for_app(dashboard):
    return DashboardSurfaceHealthService(app_module.app.routes, dashboard.summary(), dashboard_html())


def by_id(summary):
    return {surface["surfaceId"]: surface for surface in summary["surfaces"]}


def test_health_summary_endpoint_exists(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    result = app_module.get_dashboard_surface_health()

    assert result["agentId"] == "dashboard_surface_health_agent"
    assert result["totalSurfaces"] >= 7
    assert "/dashboard/surface-health" in {
        endpoint for surface in result["surfaces"] for endpoint in surface["requiredEndpoints"]
    }


def test_per_surface_endpoint_exists(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    result = app_module.get_dashboard_surface_health_detail("docs-runbook-center")

    assert result["surfaceId"] == "docs-runbook-center"
    assert result["name"] == "Docs/Runbook Center"


def test_required_dashboard_sections_detected(tmp_path, monkeypatch):
    dashboard = app_services(tmp_path, monkeypatch)

    surfaces = by_id(service_for_app(dashboard).surface_health())

    assert surfaces["validation-workflow"]["missingSections"] == []
    assert surfaces["private-alpha-readiness-snapshot"]["missingSections"] == []
    assert surfaces["redacted-diagnostics-bundle"]["missingSections"] == []
    assert surfaces["evidence-report-center"]["missingSections"] == []
    assert surfaces["agent-manifest-health-center"]["missingSections"] == []
    assert surfaces["docs-runbook-center"]["missingSections"] == []
    assert surfaces["dashboard-surface-health-center"]["missingSections"] == []
    assert surfaces["dashboard-surface-health-center"]["missingDocs"] == []


def test_required_guarded_endpoints_detected(tmp_path, monkeypatch):
    dashboard = app_services(tmp_path, monkeypatch)

    for surface in service_for_app(dashboard).surface_health()["surfaces"]:
        assert surface["missingEndpoints"] == []
        assert surface["unguardedEndpoints"] == []


def test_missing_surface_produces_warning_in_service_level_test():
    service = DashboardSurfaceHealthService(routes=[], dashboard_summary={}, dashboard_html="<main></main>")

    surface = service.surface_detail("evidence-report-center")

    assert surface["status"] == "warning"
    assert "dashboard section missing" in surface["warnings"]
    assert "guarded endpoint missing" in surface["warnings"]
    assert "safety note missing" in surface["warnings"]


def test_surface_detail_blocks_traversal(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_dashboard_surface_health_detail("..%2Fdocs-runbook-center")

    assert exc_info.value.status_code == 400
    assert "known dashboard surface id" in exc_info.value.detail


def test_dashboard_surface_health_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/dashboard/surface-health",
        "/dashboard/surface-health/{surface_id}",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls


def test_no_mutation_external_call_or_command_behavior_in_source():
    source = (app_module.WORKSPACE_ROOT / "services/jarvis-core/src/jarvis_core/dashboard_surface_health.py").read_text(
        encoding="utf-8"
    )
    forbidden_source = ["subprocess", "requests.", "httpx", "urllib.request", "open(", ".write(", "unlink(", "remove("]

    assert all(token not in source for token in forbidden_source)
    summary = DashboardSurfaceHealthService([], {}, "").surface_health()
    assert summary["routeMutation"] is False
    assert summary["reportMutation"] is False
    assert summary["docMutation"] is False
    assert summary["manifestMutation"] is False
    assert summary["settingsMutation"] is False
    assert summary["commandExecution"] is False
    assert summary["externalServices"] is False
    assert summary["uploads"] is False
