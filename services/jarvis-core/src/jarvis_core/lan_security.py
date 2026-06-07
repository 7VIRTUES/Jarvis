from __future__ import annotations

import ipaddress
import os
import secrets
from collections.abc import Mapping
from typing import Any

from fastapi import HTTPException, Request


LAN_TOKEN_ENV_VAR = "JARVIS_LAN_DASHBOARD_TOKEN"
MIN_LAN_TOKEN_LENGTH = 20


def require_dashboard_lan_access(request: Request) -> None:
    client_host = request.client.host if request.client else None
    if is_loopback_host(client_host):
        return
    if is_lan_request_authorized(request.headers):
        return
    raise HTTPException(status_code=403, detail="LAN dashboard access requires a configured token")


def is_loopback_host(host: str | None) -> bool:
    if not host:
        return False
    normalized = host.strip().lower()
    if normalized == "localhost":
        return True
    if normalized.startswith("[") and normalized.endswith("]"):
        normalized = normalized[1:-1]
    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


def is_lan_request_authorized(headers: Mapping[str, str]) -> bool:
    configured = configured_lan_token()
    if not is_configured_token_valid(configured):
        return False
    presented = extract_request_token(headers)
    if not presented:
        return False
    return constant_time_token_match(presented, configured or "")


def configured_lan_token() -> str | None:
    return os.environ.get(LAN_TOKEN_ENV_VAR)


def is_configured_token_valid(token: str | None) -> bool:
    return token is not None and len(token) >= MIN_LAN_TOKEN_LENGTH


def extract_request_token(headers: Mapping[str, str]) -> str | None:
    lan_header = _header_value(headers, "x-jarvis-lan-token")
    if lan_header:
        return lan_header.strip()
    authorization = _header_value(headers, "authorization")
    if not authorization:
        return None
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        return None
    return value.strip()


def constant_time_token_match(presented: str, configured: str) -> bool:
    return secrets.compare_digest(presented, configured)


def lan_protection_status() -> dict[str, Any]:
    token = configured_lan_token()
    return {
        "lanProtectionImplemented": True,
        "lanTokenConfigured": token is not None,
        "lanTokenValidLength": is_configured_token_valid(token),
        "loopbackAllowedWithoutToken": True,
        "nonLoopbackRequiresToken": True,
        "queryStringTokensAccepted": False,
        "cookieTokensAccepted": False,
        "tokenValueExposed": False,
        "pairingWizardStatus": "not_implemented_yet",
        "envVarName": LAN_TOKEN_ENV_VAR,
    }


def _header_value(headers: Mapping[str, str], key: str) -> str | None:
    if hasattr(headers, "get"):
        value = headers.get(key)
        if value is not None:
            return value
    lowered = key.lower()
    for candidate_key, candidate_value in headers.items():
        if candidate_key.lower() == lowered:
            return candidate_value
    return None
