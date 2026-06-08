from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.dashboard import DashboardService, first_run_setup_html
from jarvis_core.db import init_db
from jarvis_core.lan_security import LAN_TOKEN_ENV_VAR, MIN_LAN_TOKEN_LENGTH, require_loopback_request


def request_from(host: str, headers: dict[str, str] | None = None):
    return SimpleNamespace(client=SimpleNamespace(host=host), headers=headers or {})


def dashboard_service(tmp_path, monkeypatch):
    conn = init_db(tmp_path / "jarvis.sqlite")
    service = DashboardService(conn, tmp_path, tmp_path / "data" / "jarvis", tmp_path / "connectors")
    monkeypatch.setattr(app_module, "dashboard", service)
    return service


def sample_token() -> str:
    return "f" * MIN_LAN_TOKEN_LENGTH


def test_first_run_placeholder_status_reports_safe_defaults(tmp_path, monkeypatch):
    service = dashboard_service(tmp_path, monkeypatch)

    status = service.first_run_wizard_summary()

    assert status["firstRunWizardStatus"] == "placeholder_only"
    assert status["firstRunWizardImplemented"] is False
    assert status["setupPageImplemented"] is True
    assert status["setupPageLoopbackOnly"] is True
    assert status["setupStatePersistenceImplemented"] is False
    assert status["writesConfigFiles"] is False
    assert status["tokenGenerationImplemented"] is False
    assert status["tokenPersistenceImplemented"] is False
    assert status["accountSetupImplemented"] is False
    assert status["oauthImplemented"] is False
    assert status["cloudSyncEnabled"] is False
    assert status["telemetryEnabled"] is False
    assert status["autoUpdaterEnabled"] is False
    assert status["installerPackagingStatus"] == "not_implemented_yet"
    assert status["desktopShellStatus"] == "placeholder_only"
    assert status["lanSetupGuidanceAvailable"] is True
    assert status["stopTaskBoundaryAvailable"] is True


def test_first_run_placeholder_checklist_is_informational_only(tmp_path, monkeypatch):
    service = dashboard_service(tmp_path, monkeypatch)

    status = service.first_run_wizard_summary()

    assert status["futureChecklist"] == [
        "confirm_local_service",
        "review_lan_token_setup",
        "register_first_project",
        "review_safety_boundaries",
        "open_dashboard",
        "export_diagnostics",
    ]
    assert status["checklistIsInformationalOnly"] is True
    assert status["mutationEndpointsImplemented"] is False


def test_first_run_setup_status_endpoint_returns_placeholder_status(tmp_path, monkeypatch):
    dashboard_service(tmp_path, monkeypatch)

    status = app_module.first_run_setup_status_endpoint()

    assert status["firstRunWizardStatus"] == "placeholder_only"
    assert status["writesConfigFiles"] is False


def test_loopback_can_access_first_run_setup_without_token(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    require_loopback_request(request_from("127.0.0.1"))
    page = app_module.first_run_setup_page()

    assert page.status_code == 200
    assert "First-Run Setup Placeholder" in page.body.decode("utf-8")


def test_non_loopback_cannot_access_first_run_setup_even_with_token(monkeypatch):
    token = sample_token()
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, token)

    with pytest.raises(HTTPException) as exc_info:
        require_loopback_request(request_from("192.168.1.10", {"X-Jarvis-LAN-Token": token}))

    assert exc_info.value.status_code == 403


def test_first_run_setup_page_does_not_expose_token_value(monkeypatch):
    token = sample_token()
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, token)

    page_text = app_module.first_run_setup_page().body.decode("utf-8")

    assert token not in page_text


def test_first_run_setup_page_has_no_setup_action_controls(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    page_text = first_run_setup_html().lower()

    assert "<input" not in page_text
    assert "<button" not in page_text
    assert "<form" not in page_text
    assert "save" not in page_text
    assert "edit" not in page_text
    assert "generate token" not in page_text
    assert "create account" not in page_text
    assert "connect account" not in page_text
    assert "install now" not in page_text
    assert "update now" not in page_text
    assert "finish setup" not in page_text


def test_first_run_setup_routes_have_loopback_dependency():
    protected_paths = {"/setup/first-run", "/api/setup/first-run/status"}
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_loopback_request in dependency_calls
