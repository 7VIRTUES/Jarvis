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


def require_loopback_request(request: Request) -> None:
    client_host = request.client.host if request.client else None
    if is_loopback_host(client_host):
        return
    raise HTTPException(status_code=403, detail="LAN setup is available only from loopback")


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


def lan_setup_status() -> dict[str, Any]:
    token = configured_lan_token()
    return {
        "lanProtectionImplemented": True,
        "setupPageImplemented": True,
        "setupPageLoopbackOnly": True,
        "tokenConfigured": token is not None,
        "tokenMeetsMinimumLength": is_configured_token_valid(token),
        "minimumTokenLength": MIN_LAN_TOKEN_LENGTH,
        "acceptedHeaderNames": ["X-Jarvis-LAN-Token", "Authorization: Bearer"],
        "queryStringTokensAccepted": False,
        "cookieTokensAccepted": False,
        "tokenValueExposed": False,
        "tokenPrefixExposed": False,
        "tokenSuffixExposed": False,
        "tokenHashExposed": False,
        "pairingWizardStatus": "not_implemented_yet",
        "qrPairingStatus": "not_implemented_yet",
        "mobilePairingStatus": "not_implemented_yet",
        "envVarName": LAN_TOKEN_ENV_VAR,
        "notes": [
            "Setup guidance is available from loopback only.",
            "Set the environment variable before starting Jarvis.",
            "Keep the token outside the repository and outside URLs.",
        ],
    }


def lan_setup_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jarvis LAN Setup</title>
  <style>
    body { margin: 0; font-family: Segoe UI, Arial, sans-serif; background: #f6f7f9; color: #1d2733; }
    header { background: #ffffff; border-bottom: 1px solid #d8dde5; padding: 18px 28px; }
    main { max-width: 920px; margin: 0 auto; padding: 24px; display: grid; gap: 18px; }
    section { background: #ffffff; border: 1px solid #d8dde5; border-radius: 8px; padding: 18px; }
    h1, h2 { margin: 0 0 10px; }
    code, pre { background: #eef1f5; border-radius: 4px; padding: 2px 4px; }
    .muted { color: #5e6b7a; }
  </style>
</head>
<body>
  <header>
    <h1>LAN Setup Guidance</h1>
    <div class="muted">Loopback-only status and manual environment setup help</div>
  </header>
  <main>
    <section>
      <h2>Status</h2>
      <pre id="setup-status">Loading LAN setup status...</pre>
    </section>
    <section>
      <h2>Manual Setup</h2>
      <p>LAN dashboard access uses <code>JARVIS_LAN_DASHBOARD_TOKEN</code>.</p>
      <p>Set the environment variable before starting Jarvis. Keep the token outside this repository, outside URLs, and outside shared logs.</p>
      <p>Accepted request headers are <code>X-Jarvis-LAN-Token</code> and <code>Authorization: Bearer</code>.</p>
      <p>Query-string tokens and cookie tokens are not accepted. Full pairing wizard, QR pairing, and mobile pairing are not implemented yet.</p>
    </section>
  </main>
  <script>
    async function loadSetupStatus() {
      const status = await fetch('/api/setup/lan/status').then((response) => response.json());
      document.getElementById('setup-status').textContent = JSON.stringify(status, null, 2);
    }
    loadSetupStatus();
  </script>
</body>
</html>"""


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
