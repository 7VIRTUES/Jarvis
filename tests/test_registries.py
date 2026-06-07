import json
from pathlib import Path

import pytest

from jarvis_core.registries import COST_MODES, load_manifest, validate_connector_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_connector_manifests_validate():
    for path in (ROOT / "connectors" / "placeholders").glob("*.json"):
        manifest = load_manifest(path, "connector")
        assert manifest["implemented"] is False
        assert manifest["defaultEnabled"] is False
        assert manifest["readinessLevel"] == "placeholder_only"


def test_cost_modes_validate():
    for mode in COST_MODES:
        data = _connector("example", mode)
        validate_connector_manifest(data)
    with pytest.raises(ValueError):
        validate_connector_manifest(_connector("example", "surprise_paid_mode"))


def test_connectors_cannot_be_implemented_or_enabled():
    implemented = _connector("github", "bring_your_own_account")
    implemented["implemented"] = True
    with pytest.raises(ValueError):
        validate_connector_manifest(implemented)

    enabled = _connector("gmail", "official_free_quota")
    enabled["defaultEnabled"] = True
    with pytest.raises(ValueError):
        validate_connector_manifest(enabled)


def test_agent_manifests_validate():
    for path in (ROOT / "connectors" / "agents").glob("*.json"):
        manifest = load_manifest(path, "agent")
        assert manifest["id"]
        assert isinstance(manifest["capabilities"], list)


def test_tool_manifests_validate():
    for path in (ROOT / "connectors" / "tools").glob("*.json"):
        manifest = load_manifest(path, "tool")
        assert manifest["id"]
        assert isinstance(manifest["approvalRequired"], bool)


def _connector(connector_id: str, cost_mode: str) -> dict[str, object]:
    return {
        "id": connector_id,
        "provider": connector_id,
        "implemented": False,
        "defaultEnabled": False,
        "readinessLevel": "placeholder_only",
        "costMode": cost_mode,
        "authType": "not_implemented",
        "privacyClass": "external_account",
        "dataAccess": "none",
        "approvalRequired": True,
        "tokenStorage": "not_implemented",
        "dataRetention": "none",
        "notes": "test",
    }
