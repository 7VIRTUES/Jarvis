from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
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
    monkeypatch.setattr(bootstrap, "list_ollama_models", lambda host, port: ["qwen3:8b", "nomic-embed-text"])
    ok, msg = bootstrap.ensure_ollama_model("qwen3:8b")
    assert ok is True
    assert "already available" in msg


def test_ensure_ollama_model_pulls_when_missing(monkeypatch):
    monkeypatch.setattr(bootstrap, "list_ollama_models", lambda host, port: [])
    monkeypatch.setattr(bootstrap, "pull_ollama_model", lambda name, host, port: (True, f"Model '{name}' successfully downloaded."))

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


def test_configure_jarvis_services(monkeypatch):
    mock_res = MagicMock()
    mock_res.__enter__.return_value = mock_res
    monkeypatch.setattr(bootstrap, "urlopen", lambda req, timeout=10.0: mock_res)
    monkeypatch.setattr("json.load", lambda res: {"configured": True, "enabled": True})

    results = bootstrap.configure_jarvis_services(8000)
    assert results.get("generation_config") == {"configured": True, "enabled": True}
    assert results.get("embeddings_config") == {"configured": True, "enabled": True}


def test_parse_args():
    args = bootstrap.parse_args(["--no-browser", "--port", "8080", "--skip-models", "--check-only"])
    assert args.no_browser is True
    assert args.port == 8080
    assert args.skip_models is True
    assert args.check_only is True


def test_run_bootstrap_pipeline_check_only(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(bootstrap, "check_disk_space", lambda root: (True, "OK"))
    monkeypatch.setattr(bootstrap, "ensure_virtualenv", lambda root: (True, "OK"))
    monkeypatch.setattr(bootstrap, "is_ollama_running", lambda: False)
    monkeypatch.setattr(bootstrap, "find_ollama_binary", lambda: None)

    exit_code = bootstrap.run_bootstrap_pipeline(root=tmp_path, check_only=True)
    assert exit_code == 0
