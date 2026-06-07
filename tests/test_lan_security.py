from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import jarvis_core.app as app_module
import jarvis_core.lan_security as lan_security
from jarvis_core.lan_security import (
    LAN_TOKEN_ENV_VAR,
    MIN_LAN_TOKEN_LENGTH,
    constant_time_token_match,
    extract_request_token,
    is_lan_request_authorized,
    is_loopback_host,
    lan_protection_status,
    require_dashboard_lan_access,
)


def sample_token() -> str:
    return "x" * MIN_LAN_TOKEN_LENGTH


def request_from(host: str, headers: dict[str, str] | None = None):
    return SimpleNamespace(client=SimpleNamespace(host=host), headers=headers or {})


def test_loopback_host_is_allowed_without_token(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    require_dashboard_lan_access(request_from("127.0.0.1"))
    require_dashboard_lan_access(request_from("::1"))
    require_dashboard_lan_access(request_from("localhost"))


def test_non_loopback_host_is_denied_when_no_token_configured(monkeypatch):
    monkeypatch.delenv(LAN_TOKEN_ENV_VAR, raising=False)

    with pytest.raises(HTTPException) as exc_info:
        require_dashboard_lan_access(request_from("192.168.1.10"))

    assert exc_info.value.status_code == 403


def test_non_loopback_host_is_denied_when_configured_token_is_too_short(monkeypatch):
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, "short")

    with pytest.raises(HTTPException) as exc_info:
        require_dashboard_lan_access(request_from("192.168.1.10", {"X-Jarvis-LAN-Token": "short"}))

    assert exc_info.value.status_code == 403


def test_non_loopback_host_is_denied_when_request_token_is_missing(monkeypatch):
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, sample_token())

    with pytest.raises(HTTPException) as exc_info:
        require_dashboard_lan_access(request_from("192.168.1.10"))

    assert exc_info.value.status_code == 403


def test_non_loopback_host_is_denied_when_token_is_wrong(monkeypatch):
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, sample_token())

    with pytest.raises(HTTPException) as exc_info:
        require_dashboard_lan_access(request_from("192.168.1.10", {"X-Jarvis-LAN-Token": "y" * MIN_LAN_TOKEN_LENGTH}))

    assert exc_info.value.status_code == 403


def test_non_loopback_host_allows_x_jarvis_lan_token(monkeypatch):
    token = sample_token()
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, token)

    require_dashboard_lan_access(request_from("192.168.1.10", {"X-Jarvis-LAN-Token": token}))


def test_non_loopback_host_allows_authorization_bearer(monkeypatch):
    token = sample_token()
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, token)

    require_dashboard_lan_access(request_from("192.168.1.10", {"Authorization": f"Bearer {token}"}))


def test_query_string_token_is_not_accepted(monkeypatch):
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, sample_token())

    assert extract_request_token({}) is None
    assert is_lan_request_authorized({}) is False


def test_constant_time_token_comparison_helper_uses_compare_digest(monkeypatch):
    calls = []

    def fake_compare_digest(presented: str, configured: str) -> bool:
        calls.append((presented, configured))
        return True

    monkeypatch.setattr(lan_security.secrets, "compare_digest", fake_compare_digest)

    assert constant_time_token_match("presented", "configured") is True
    assert calls == [("presented", "configured")]


def test_safe_status_never_includes_token_value(monkeypatch):
    token = sample_token()
    monkeypatch.setenv(LAN_TOKEN_ENV_VAR, token)

    status = lan_protection_status()
    status_text = str(status)

    assert status["lanProtectionImplemented"] is True
    assert status["lanTokenConfigured"] is True
    assert status["lanTokenValidLength"] is True
    assert status["queryStringTokensAccepted"] is False
    assert status["tokenValueExposed"] is False
    assert token not in status_text


def test_loopback_detection_is_limited_to_loopback_hosts():
    assert is_loopback_host("127.0.0.1") is True
    assert is_loopback_host("::1") is True
    assert is_loopback_host("localhost") is True
    assert is_loopback_host("192.168.1.10") is False
    assert is_loopback_host("example.local") is False


def test_dashboard_related_routes_have_lan_guard_dependency():
    protected_paths = {
        "/dashboard",
        "/api/dashboard/summary",
        "/api/safety/summary",
        "/api/settings/summary",
        "/api/reports",
        "/api/reports/{report_id:path}",
    }

    routes = {route.path: route for route in app_module.app.routes if getattr(route, "path", None) in protected_paths}

    assert set(routes) == protected_paths
    for route in routes.values():
        dependency_calls = {dependency.call for dependency in route.dependant.dependencies}
        assert require_dashboard_lan_access in dependency_calls
