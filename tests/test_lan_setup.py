from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
from jarvis_core.lan_security import (
    LAN_TOKEN_ENV_VAR,
    MIN_LAN_TOKEN_LENGTH,
    lan_setup_status,
    require_loopback_request,
)


def request_from(host: str, headers: dict[str, str] | None = None):
    return SimpleNamespace(client=SimpleNamespace(host=host), headers=headers or {})


def sample_token() -> str:
    return "s" * MIN_LAN_TOKEN_LENGTH


def test_loopback_can_access_setup_status_without_token(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    require_loopback_request(request_from("127.0.0.1"))


def test_non_loopback_cannot_access_setup_status_without_token(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    with pytest.raises(HTTPException) as exc_info:
        require_loopback_request(request_from("192.168.1.10"))

    assert exc_info.value.status_code == 403


def test_non_loopback_cannot_access_setup_status_even_with_token(monkeypatch):
    token = sample_token()
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, token)

    with pytest.raises(HTTPException) as exc_info:
        require_loopback_request(request_from("192.168.1.10", {"X-Jarvis-LAN-Token": token}))

    assert exc_info.value.status_code == 403


def test_setup_status_shows_token_configured_without_exposing_token(monkeypatch):
    token = sample_token()
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, token)

    status = lan_setup_status()
    status_text = str(status)

    assert status["tokenConfigured"] is True
    assert status["tokenValueExposed"] is False
    assert status["tokenPrefixExposed"] is False
    assert status["tokenSuffixExposed"] is False
    assert status["tokenHashExposed"] is False
    assert token not in status_text


def test_setup_status_shows_token_minimum_length_validity(monkeypatch):
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, "short")

    status = lan_setup_status()

    assert status["tokenConfigured"] is True
    assert status["tokenMeetsMinimumLength"] is False
    assert status["minimumTokenLength"] == MIN_LAN_TOKEN_LENGTH


def test_setup_status_lists_safe_accepted_header_names(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    status = lan_setup_status()

    assert status["acceptedHeaderNames"] == ["X-Jarvis-LAN-Token", "Authorization: Bearer"]
    assert status["queryStringTokensAccepted"] is False
    assert status["cookieTokensAccepted"] is False


def test_setup_status_marks_pairing_variants_future(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    status = lan_setup_status()

    assert status["pairingWizardStatus"] == "not_implemented_yet"
    assert status["qrPairingStatus"] == "not_implemented_yet"
    assert status["mobilePairingStatus"] == "not_implemented_yet"


def test_loopback_can_access_setup_page_without_token(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    page = app_module.lan_setup_page()

    assert page.status_code == 200
    assert "LAN Setup Guidance" in page.body.decode("utf-8")


def test_setup_page_does_not_expose_token_value(monkeypatch):
    token = sample_token()
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, token)

    page_text = app_module.lan_setup_page().body.decode("utf-8")

    assert token not in page_text


def test_setup_page_has_no_token_input_or_write_controls(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    page_text = app_module.lan_setup_page().body.decode("utf-8").lower()

    assert "<input" not in page_text
    assert "<button" not in page_text
    assert "save" not in page_text
    assert "edit" not in page_text
    assert "generate" not in page_text


def test_setup_page_explains_manual_environment_setup_safely(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    page_text = app_module.lan_setup_page().body.decode("utf-8")

    assert "JARVIS_LAN_DASHBOARD_TOKEN" in page_text
    assert "environment variable" in page_text
    assert "Query-string tokens and cookie tokens are not accepted" in page_text
    assert "Full pairing wizard, QR pairing, and mobile pairing are not implemented yet" in page_text


def test_setup_routes_have_loopback_dependency():
    protected_paths = {"/setup/lan", "/api/setup/lan/status"}
    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_loopback_request in dependency_calls
