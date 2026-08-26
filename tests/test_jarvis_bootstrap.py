from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

_bootstrap_path = Path(__file__).resolve().parent.parent / "scripts" / "jarvis_bootstrap.py"
_spec = importlib.util.spec_from_file_location("jarvis_bootstrap", _bootstrap_path)
bootstrap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bootstrap)


def test_bootstrap_constants():
    assert bootstrap.APP_NAME == "Jarvis PC Local"
    assert bootstrap.DEFAULT_HOST == "127.0.0.1"
    assert bootstrap.DEFAULT_JARVIS_PORT == 8000
    assert bootstrap.DEFAULT_OLLAMA_PORT == 11434
    assert bootstrap.DEFAULT_GENERATION_MODEL == "qwen3:8b"
    assert bootstrap.DEFAULT_EMBEDDING_MODEL == "nomic-embed-text"
    assert bootstrap.MIN_FREE_DISK_GB == 10.0


def test_validate_python_version():
    ok, msg = bootstrap.validate_python_version()
    assert ok is True
    assert "detected" in msg


def test_check_disk_space_pass(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(bootstrap, "get_free_disk_space_gb", lambda path: 50.0)
    ok, msg = bootstrap.check_disk_space(tmp_path, min_gb=10.0)
    assert ok is True
    assert "50.0 GB" in msg


def test_check_disk_space_fail(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(bootstrap, "get_free_disk_space_gb", lambda path: 4.2)
    ok, msg = bootstrap.check_disk_space(tmp_path, min_gb=10.0)
    assert ok is False
    assert "Insufficient free disk space" in msg
    assert "4.2 GB" in msg


def test_find_venv_python():
    root = bootstrap.repository_root()
    expected = root / ".venv" / "Scripts" / "python.exe"
    assert bootstrap.find_venv_python(root) == expected


def test_is_exact_model_match():
    # Exact tag matches
    assert bootstrap.is_exact_model_match("qwen3:8b", "qwen3:8b") is True
    assert bootstrap.is_exact_model_match("qwen3:8b", "qwen3:8b:latest") is True
    assert bootstrap.is_exact_model_match("nomic-embed-text", "nomic-embed-text") is True
    assert bootstrap.is_exact_model_match("nomic-embed-text", "nomic-embed-text:latest") is True

    # Parameter mismatch / different variants must NOT match
    assert bootstrap.is_exact_model_match("qwen3:8b", "qwen3:4b") is False
    assert bootstrap.is_exact_model_match("qwen3:8b", "qwen3:14b") is False
    assert bootstrap.is_exact_model_match("qwen3:8b", "llama3:8b") is False
    assert bootstrap.is_exact_model_match("nomic-embed-text", "all-minilm") is False


def test_find_ollama_binary(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: "C:\\Windows\\System32\\ollama.exe" if name == "ollama" else None)
    assert bootstrap.find_ollama_binary() == "C:\\Windows\\System32\\ollama.exe"


def test_is_ollama_running_true(monkeypatch):
    mock_res = MagicMock()
    mock_res.status = 200
    mock_res.__enter__.return_value = mock_res
    monkeypatch.setattr(bootstrap, "urlopen", lambda req, timeout=1.5: mock_res)
    assert bootstrap.is_ollama_running() is True


def test_is_ollama_running_false(monkeypatch):
    def _raise(*args, **kwargs):
        raise OSError("Connection refused")
    monkeypatch.setattr(bootstrap, "urlopen", _raise)
    assert bootstrap.is_ollama_running() is False


def test_list_ollama_models(monkeypatch):
    mock_res = MagicMock()
    mock_res.status = 200
    mock_res.__enter__.return_value = mock_res
    monkeypatch.setattr(bootstrap, "urlopen", lambda req, timeout=10.0: mock_res)
    monkeypatch.setattr("json.load", lambda res: {"models": [{"name": "qwen3:8b"}, {"name": "nomic-embed-text:latest"}]})

    models = bootstrap.list_ollama_models()
    assert models == ["qwen3:8b", "nomic-embed-text:latest"]


def test_ensure_ollama_model_already_present(monkeypatch):
    monkeypatch.setattr(bootstrap, "list_ollama_models", lambda host, port: ["qwen3:8b", "nomic-embed-text:latest"])
    ok, msg = bootstrap.ensure_ollama_model("qwen3:8b")
    assert ok is True
    assert "already available" in msg


def test_ensure_ollama_model_pulls_when_missing(monkeypatch):
    monkeypatch.setattr(bootstrap, "list_ollama_models", lambda host, port: ["qwen3:4b"])
    monkeypatch.setattr(bootstrap, "pull_ollama_model", lambda name, ollama_bin=None, host=None, port=None: (True, f"Model '{name}' successfully downloaded."))

    ok, msg = bootstrap.ensure_ollama_model("qwen3:8b")
    assert ok is True
    assert "successfully downloaded" in msg


def test_is_jarvis_healthy_true(monkeypatch):
    mock_res = MagicMock()
    mock_res.status = 200
    mock_res.__enter__.return_value = mock_res
    monkeypatch.setattr(bootstrap, "urlopen", lambda req, timeout=1.5: mock_res)
    monkeypatch.setattr("json.load", lambda res: {"status": "ok", "app": "Jarvis PC Local"})
    assert bootstrap.is_jarvis_healthy(8000) is True


def test_is_jarvis_healthy_false(monkeypatch):
    def _raise(*args, **kwargs):
        raise OSError("Connection refused")
    monkeypatch.setattr(bootstrap, "urlopen", _raise)
    assert bootstrap.is_jarvis_healthy(8000) is False


def test_configure_jarvis_services_exact_api_contracts(monkeypatch):
    recorded_requests: list[dict] = []

    def mock_urlopen(req, timeout=10.0):
        url = req.full_url
        data = json.loads(req.data.decode("utf-8")) if req.data else {}
        recorded_requests.append({"url": url, "data": data, "method": req.get_method()})

        mock_res = MagicMock()
        mock_res.status = 200
        mock_res.__enter__.return_value = mock_res

        if "/api/generation/configure" in url:
            return mock_res
        elif "/api/generation/probe" in url:
            return mock_res
        elif "/api/knowledge/embeddings/configure" in url:
            return mock_res
        elif "/api/knowledge/embeddings/probe" in url:
            return mock_res
        elif "/api/knowledge/embeddings/rebuild-preview" in url:
            return mock_res
        elif "/api/knowledge/embeddings/rebuild" in url:
            return mock_res
        return mock_res

    def mock_json_load(res):
        last_url = recorded_requests[-1]["url"]
        if "/api/generation/configure" in last_url:
            return {"enabled": True, "modelName": "qwen3:8b"}
        elif "/api/generation/probe" in last_url:
            return {"status": "ok", "modelName": "qwen3:8b"}
        elif "/api/knowledge/embeddings/configure" in last_url:
            return {"enabled": True, "modelName": "nomic-embed-text"}
        elif "/api/knowledge/embeddings/probe" in last_url:
            return {"status": "ok", "modelName": "nomic-embed-text"}
        elif "/api/knowledge/embeddings/rebuild-preview" in last_url:
            return {"previewCount": 2, "items": [{"id": 1}, {"id": 2}]}
        elif "/api/knowledge/embeddings/rebuild" in last_url:
            return {"rebuiltCount": 2}
        return {}

    monkeypatch.setattr(bootstrap, "is_ollama_running", lambda host, port: True)
    monkeypatch.setattr(bootstrap, "list_ollama_models", lambda host, port: ["qwen3:8b", "nomic-embed-text"])
    monkeypatch.setattr(bootstrap, "urlopen", mock_urlopen)
    monkeypatch.setattr("json.load", mock_json_load)

    results = bootstrap.configure_jarvis_services(8000)

    assert results["generation"]["status"] == "ready"
    assert results["embeddings"]["status"] == "ready"

    # Verify exact endpoints and payloads
    gen_cfg_req = next(r for r in recorded_requests if "/api/generation/configure" in r["url"])
    assert gen_cfg_req["data"]["modelName"] == "qwen3:8b"
    assert gen_cfg_req["data"]["confirmation"] == "ENABLE LOCAL GENERATION"
    assert gen_cfg_req["data"]["actor"] == "local_user"
    assert "enabled" not in gen_cfg_req["data"]  # Must NOT include forbidden extra fields

    gen_probe_req = next(r for r in recorded_requests if "/api/generation/probe" in r["url"])
    assert gen_probe_req["data"]["modelName"] == "qwen3:8b"
    assert gen_probe_req["data"]["actor"] == "local_user"

    emb_cfg_req = next(r for r in recorded_requests if "/api/knowledge/embeddings/configure" in r["url"])
    assert emb_cfg_req["data"]["modelName"] == "nomic-embed-text"
    assert emb_cfg_req["data"]["confirmation"] == "ENABLE EMBEDDINGS"

    emb_probe_req = next(r for r in recorded_requests if "/api/knowledge/embeddings/probe" in r["url"])
    assert emb_probe_req["data"]["modelName"] == "nomic-embed-text"

    emb_preview_req = next(r for r in recorded_requests if "/api/knowledge/embeddings/rebuild-preview" in r["url"])
    assert emb_preview_req["data"]["onlyMissing"] is True

    emb_rebuild_req = next(
        r for r in recorded_requests
        if "/api/knowledge/embeddings/rebuild" in r["url"] and "rebuild-preview" not in r["url"]
    )
    assert emb_rebuild_req["data"]["confirmation"] == "EMBED"
    assert emb_rebuild_req["data"]["actor"] == "local_user"


def test_configure_jarvis_services_failure_reporting(monkeypatch):
    monkeypatch.setattr(bootstrap, "is_ollama_running", lambda host, port: False)

    results = bootstrap.configure_jarvis_services(8000)
    assert results["generation"]["status"] == "unavailable"
    assert results["embeddings"]["status"] == "unavailable"
    assert "not reachable" in results["generation"]["message"]


def test_ensure_virtualenv_does_not_upgrade_pip(monkeypatch, tmp_path: Path):
    executed_commands: list[list[str]] = []

    def mock_run(cmd, *args, **kwargs):
        executed_commands.append(cmd)
        mock_completed = MagicMock()
        mock_completed.returncode = 0
        return mock_completed

    venv_py = tmp_path / ".venv" / "Scripts" / "python.exe"
    venv_py.parent.mkdir(parents=True, exist_ok=True)
    venv_py.touch()

    req_file = tmp_path / "requirements.txt"
    req_file.write_text("fastapi==0.115.0\n", encoding="utf-8")

    monkeypatch.setattr(bootstrap, "find_venv_python", lambda root: venv_py)
    monkeypatch.setattr(bootstrap, "is_venv_complete", lambda root: False)
    monkeypatch.setattr(subprocess, "run", mock_run)

    # After run, simulate complete venv
    monkeypatch.setattr(bootstrap, "is_venv_complete", lambda root: True)

    ok, msg = bootstrap.ensure_virtualenv(tmp_path)
    assert ok is True

    # Verify pip --upgrade pip was NOT called
    for cmd in executed_commands:
        cmd_str = " ".join(str(c) for c in cmd)
        assert "--upgrade pip" not in cmd_str
        assert "pip install --upgrade" not in cmd_str


def test_parse_args():
    args = bootstrap.parse_args(["--no-browser", "--port", "8080", "--skip-models", "--check-only", "--prepare-only"])
    assert args.no_browser is True
    assert args.port == 8080
    assert args.skip_models is True
    assert args.check_only is True
    assert args.prepare_only is True


def test_run_bootstrap_pipeline_check_only(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(bootstrap, "check_disk_space", lambda root: (True, "OK"))
    monkeypatch.setattr(bootstrap, "ensure_virtualenv", lambda root: (True, "OK"))
    monkeypatch.setattr(bootstrap, "is_ollama_running", lambda host=None, port=None: False)
    monkeypatch.setattr(bootstrap, "find_ollama_binary", lambda: None)
    monkeypatch.setattr(bootstrap, "is_winget_available", lambda: False)

    exit_code = bootstrap.run_bootstrap_pipeline(root=tmp_path, check_only=True)
    assert exit_code == 0
