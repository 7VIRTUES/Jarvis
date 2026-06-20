import json

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.agent_manifest_health import AgentManifestHealthService
from jarvis_core.dashboard import DashboardService
from jarvis_core.db import init_db
from jarvis_core.lan_security import require_dashboard_lan_access


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def app_services(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    workspace = tmp_path / "workspace"
    connector_root = workspace / "connectors"
    data_root = tmp_path / "data" / "jarvis"
    dashboard = DashboardService(conn, workspace, data_root, connector_root)
    health = AgentManifestHealthService(connector_root)
    monkeypatch.setattr(app_module, "dashboard", dashboard)
    monkeypatch.setattr(app_module, "agent_manifest_health", health)
    return dashboard, health


def local_agent(**overrides):
    data = {
        "id": "local_agent",
        "name": "Local Agent",
        "implemented": True,
        "defaultEnabled": True,
        "mode": "local_only",
        "purpose": "Read local metadata only.",
        "capabilities": ["summarize"],
        "uploads": False,
        "externalServices": False,
        "commandExecution": False,
        "gitWrites": False,
        "fileDeletion": False,
        "protectedSecretReads": False,
        "safetyNotes": ["Local only."],
    }
    data.update(overrides)
    return data


def test_manifest_health_endpoint_returns_safe_metadata(tmp_path, monkeypatch):
    _dashboard, health = app_services(tmp_path, monkeypatch)
    write_json(health.agent_root / "local-agent.json", local_agent())

    result = app_module.get_agent_manifest_health()

    assert result["totalManifests"] == 1
    assert result["implementedLocalAgents"] == 1
    assert result["manifests"][0]["manifestId"] == "local-agent.json"


def test_manifest_health_detail_endpoint_blocks_traversal(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    with pytest.raises(HTTPException) as exc_info:
        app_module.get_agent_manifest_detail("..%2Fsecret.json")

    assert exc_info.value.status_code == 400
    assert "single JSON manifest filename" in exc_info.value.detail


def test_dashboard_summary_includes_agent_manifest_health(tmp_path, monkeypatch):
    _dashboard, health = app_services(tmp_path, monkeypatch)
    write_json(health.agent_root / "local-agent.json", local_agent())

    summary = app_module.dashboard_summary()
    center = summary["agentManifestHealth"]

    assert summary["capabilities"]["agentManifestHealth"] == "local_manifest_metadata_only"
    assert center["agentId"] == "agent_manifest_health_agent"
    assert center["totalManifests"] == 1
    assert center["manifestMutation"] is False
    assert center["connectorMutation"] is False
    assert center["commandExecution"] is False
    assert center["externalServices"] is False
    assert center["uploads"] is False


def test_dashboard_manifest_health_section_exists(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()

    assert 'id="agent-manifest-health-center"' in page_text
    assert "agent manifest health center" in page_text
    assert "refresh manifest health" in page_text
    assert "/agents/manifest-health" in page_text
    assert "known local manifest directories only" in page_text


def test_dashboard_manifest_health_section_has_no_forbidden_controls(tmp_path, monkeypatch):
    app_services(tmp_path, monkeypatch)

    page_text = app_module.local_dashboard().body.decode("utf-8").lower()
    start = page_text.index('id="agent-manifest-health-center"')
    end = page_text.index('id="project-profiles"')
    section = page_text[start:end]
    forbidden_labels = ["enable", "disable", "connect", "upload", "send", "share", "publish", "certify", "fix", "run"]

    assert all(f">{label}<" not in section for label in forbidden_labels)
    assert ">refresh manifest health<" in section


def test_manifest_health_endpoints_are_guarded_by_dashboard_lan_guard():
    protected_paths = {
        "/agents/manifest-health",
        "/agents/manifest-health/{manifest_id}",
    }
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls
