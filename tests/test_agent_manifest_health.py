import inspect
import json

import pytest

from jarvis_core.agent_manifest_health import AgentManifestHealthService
import jarvis_core.agent_manifest_health as health_module


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def service(tmp_path):
    return AgentManifestHealthService(tmp_path / "connectors")


def by_id(health):
    return {manifest["manifestId"]: manifest for manifest in health["manifests"]}


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


def placeholder(**overrides):
    data = {
        "id": "gmail",
        "provider": "Gmail",
        "implemented": False,
        "defaultEnabled": False,
        "readinessLevel": "placeholder_only",
        "notes": "Placeholder only.",
    }
    data.update(overrides)
    return data


def test_indexes_valid_local_agent_manifests(tmp_path):
    health = service(tmp_path)
    write_json(health.agent_root / "local-agent.json", local_agent())

    result = health.manifest_health()

    assert result["totalManifests"] == 1
    assert result["implementedLocalAgents"] == 1
    assert result["warningCount"] == 0
    assert result["manifests"][0]["localOnly"] is True


def test_handles_empty_manifest_directory(tmp_path):
    result = service(tmp_path).manifest_health()

    assert result["totalManifests"] == 0
    assert result["manifests"] == []
    assert result["warningCount"] == 0


def test_warns_on_missing_required_fields(tmp_path):
    health = service(tmp_path)
    write_json(health.agent_root / "incomplete.json", {"id": "incomplete", "implemented": True})

    manifest = by_id(health.manifest_health())["incomplete.json"]

    assert manifest["warningCount"] >= 1
    assert "missing required fields" in manifest["warnings"][0]


def test_warns_on_unsafe_implemented_manifest_booleans(tmp_path):
    health = service(tmp_path)
    write_json(health.agent_root / "unsafe.json", local_agent(uploads=True, commandExecution=True))

    manifest = by_id(health.manifest_health())["unsafe.json"]

    assert any("missing false safety booleans" in warning for warning in manifest["warnings"])
    assert manifest["safetyBooleanStatus"]["uploads"] is True
    assert manifest["safetyBooleanStatus"]["commandExecution"] is True


def test_confirms_future_placeholder_rule(tmp_path):
    health = service(tmp_path)
    write_json(health.placeholder_root / "gmail.json", placeholder())
    write_json(health.placeholder_root / "calendar.json", placeholder(id="calendar", provider="Calendar", defaultEnabled=True))

    manifests = by_id(health.manifest_health())

    assert manifests["gmail.json"]["warningCount"] == 0
    assert manifests["gmail.json"]["implemented"] is False
    assert manifests["gmail.json"]["defaultEnabled"] is False
    assert any("must remain implemented=false" in warning for warning in manifests["calendar.json"]["warnings"])


def test_redacts_synthetic_token_secret_values(tmp_path):
    health = service(tmp_path)
    raw_secret = "sk-" + "a" * 24
    raw_pat = "github_pat_" + "b" * 24
    write_json(
        health.agent_root / "secret.json",
        local_agent(purpose=f"OPENAI_API_KEY={raw_secret} access_token={raw_pat}"),
    )

    text = json.dumps(health.manifest_health(), sort_keys=True)

    assert raw_secret not in text
    assert raw_pat not in text
    assert "<redacted" in text


def test_blocks_path_traversal_manifest_id(tmp_path):
    health = service(tmp_path)

    with pytest.raises(PermissionError):
        health.manifest_detail("..%2Fsecret.json")


def test_unknown_json_shape_warns_instead_of_failing(tmp_path):
    health = service(tmp_path)
    health.agent_root.mkdir(parents=True)
    (health.agent_root / "array.json").write_text("[]", encoding="utf-8")

    manifest = by_id(health.manifest_health())["array.json"]

    assert manifest["warningCount"] == 1
    assert "unknown JSON shape" in manifest["warnings"][0]


def test_manifest_detail_returns_safe_metadata(tmp_path):
    health = service(tmp_path)
    write_json(health.agent_root / "local-agent.json", local_agent())

    detail = health.manifest_detail("local-agent.json")

    assert detail["manifestId"] == "local-agent.json"
    assert "summary" in detail
    assert "capabilities" not in detail


def test_no_manifest_mutation_external_calls_or_command_execution_implemented():
    source = inspect.getsource(health_module)

    assert "subprocess" not in source
    assert "requests" not in source
    assert ".write_text(" not in source
    assert ".unlink(" not in source
    assert "rmtree" not in source
    assert "remove(" not in source
