import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

_launcher_path = Path(__file__).resolve().parent.parent / "scripts" / "jarvis_launcher.py"
_spec = importlib.util.spec_from_file_location("jarvis_launcher", _launcher_path)
launcher = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(launcher)


def test_launcher_constants_and_default_landing_path():
    assert launcher.APP_NAME == "Jarvis PC Local"
    assert launcher.DEFAULT_HOST == "127.0.0.1"
    assert launcher.DEFAULT_PORT == 8000
    assert launcher.DEFAULT_LANDING_PATH == "/assistant"
    assert launcher.MIN_PORT == 1024
    assert launcher.MAX_PORT == 65535


def test_launcher_parse_args_defaults():
    args = launcher.parse_args([])
    assert args.no_browser is False
    assert args.port == 8000
    assert args.path == "/assistant"
    assert args.setup is False


def test_launcher_parse_args_custom_values():
    args = launcher.parse_args(["--no-browser", "--port", "9000", "--path", "/dashboard", "--setup"])
    assert args.no_browser is True
    assert args.port == 9000
    assert args.path == "/dashboard"
    assert args.setup is True


def test_launcher_valid_port_validation():
    assert launcher.valid_port("8000") == 8000
    assert launcher.valid_port("1024") == 1024
    assert launcher.valid_port("65535") == 65535

    with pytest.raises(argparse.ArgumentTypeError, match="port must be an integer"):
        launcher.valid_port("invalid")

    with pytest.raises(argparse.ArgumentTypeError, match="port must be between"):
        launcher.valid_port("80")

    with pytest.raises(argparse.ArgumentTypeError, match="port must be between"):
        launcher.valid_port("70000")


def test_launcher_repository_root():
    root = launcher.repository_root()
    assert (root / "requirements.txt").is_file()
    assert (root / "services" / "jarvis-core" / "src" / "jarvis_core" / "app.py").is_file()
    assert launcher.validate_repository(root) is True


def test_launcher_validate_repository_fails_on_missing_files(tmp_path: Path):
    assert launcher.validate_repository(tmp_path) is False


def test_launcher_url_helpers():
    assert launcher.health_url(8000) == "http://127.0.0.1:8000/health"
    assert launcher.landing_url(8000) == "http://127.0.0.1:8000/assistant"
    assert launcher.landing_url(8000, "/dashboard") == "http://127.0.0.1:8000/dashboard"
    assert launcher.landing_url(8000, "assistant") == "http://127.0.0.1:8000/assistant"
    assert launcher.dashboard_url(8000) == "http://127.0.0.1:8000/dashboard"
    assert launcher.assistant_url(8000) == "http://127.0.0.1:8000/assistant"


def test_launcher_existing_instance_when_healthy(monkeypatch):
    monkeypatch.setattr(launcher, "jarvis_health_ready", lambda port: True)
    monkeypatch.setattr(launcher, "configure_services_if_available", lambda port: {"generation": {"status": "ready"}})
    opened = []
    monkeypatch.setattr(launcher, "open_landing_page", lambda port, path: opened.append((port, path)))

    status = launcher.existing_instance_status(8000, no_browser=False, path="/assistant")
    assert status == 0
    assert opened == [(8000, "/assistant")]

    # When no_browser is True, do not open browser
    opened.clear()
    status_no_browser = launcher.existing_instance_status(8000, no_browser=True, path="/assistant")
    assert status_no_browser == 0
    assert opened == []


def test_launcher_existing_instance_when_port_collides(monkeypatch):
    monkeypatch.setattr(launcher, "jarvis_health_ready", lambda port: False)
    monkeypatch.setattr(launcher, "port_accepts_connection", lambda port: True)

    status = launcher.existing_instance_status(8000, no_browser=False, path="/assistant")
    assert status == 1


def test_launcher_existing_instance_when_port_is_free(monkeypatch):
    monkeypatch.setattr(launcher, "jarvis_health_ready", lambda port: False)
    monkeypatch.setattr(launcher, "port_accepts_connection", lambda port: False)

    status = launcher.existing_instance_status(8000, no_browser=False, path="/assistant")
    assert status is None


def test_launcher_confirm_setup_non_interactive(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    assert launcher.confirm_setup("Confirm? ") is False


def test_launcher_stop_owned_child():
    mock_child = MagicMock()
    mock_child.poll.return_value = None
    launcher.stop_owned_child(mock_child)
    mock_child.terminate.assert_called_once()
    mock_child.wait.assert_called_once()
