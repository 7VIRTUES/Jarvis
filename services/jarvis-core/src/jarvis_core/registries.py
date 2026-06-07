from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import load_json_config


COST_MODES = {
    "local_free",
    "official_free_quota",
    "bring_your_own_account",
    "paid_provider_required",
    "disabled",
}


def validate_agent_manifest(data: dict[str, Any]) -> None:
    required = {"id", "name", "implemented", "capabilities"}
    _require(data, required, "agent")
    if not isinstance(data["capabilities"], list):
        raise ValueError("agent capabilities must be a list")


def validate_tool_manifest(data: dict[str, Any]) -> None:
    required = {"id", "name", "implemented", "approvalRequired", "capabilities"}
    _require(data, required, "tool")
    if not isinstance(data["approvalRequired"], bool):
        raise ValueError("tool approvalRequired must be boolean")


def validate_connector_manifest(data: dict[str, Any]) -> None:
    required = {
        "id",
        "provider",
        "implemented",
        "defaultEnabled",
        "readinessLevel",
        "costMode",
        "authType",
        "privacyClass",
        "dataAccess",
        "approvalRequired",
        "tokenStorage",
        "dataRetention",
        "notes",
    }
    _require(data, required, "connector")
    if data["costMode"] not in COST_MODES:
        raise ValueError(f"unsupported cost mode: {data['costMode']}")
    if data["implemented"] is not False:
        raise ValueError("connectors must remain unimplemented placeholders in v0.1A")
    if data["defaultEnabled"] is not False:
        raise ValueError("connectors must be disabled by default in v0.1A")
    if data["readinessLevel"] != "placeholder_only":
        raise ValueError("connectors must be placeholder_only in v0.1A")


def load_manifest(path: Path, manifest_type: str) -> dict[str, Any]:
    data = load_json_config(path)
    if manifest_type == "agent":
        validate_agent_manifest(data)
    elif manifest_type == "tool":
        validate_tool_manifest(data)
    elif manifest_type == "connector":
        validate_connector_manifest(data)
    else:
        raise ValueError(f"unknown manifest type: {manifest_type}")
    return data


def _require(data: dict[str, Any], required: set[str], label: str) -> None:
    missing = required - set(data)
    if missing:
        raise ValueError(f"{label} manifest missing fields: {', '.join(sorted(missing))}")
