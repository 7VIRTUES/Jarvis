from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Sequence
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import webbrowser


APP_NAME = "Jarvis PC Local"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_LANDING_PATH = "/assistant"
MIN_PORT = 1024
MAX_PORT = 65535
READINESS_TIMEOUT_SECONDS = 30.0
POLL_INTERVAL_SECONDS = 0.5
HEALTH_TIMEOUT_SECONDS = 1.5
SHUTDOWN_TIMEOUT_SECONDS = 10.0


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the repository-local Jarvis PC Local service on loopback."
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start Jarvis without opening the landing page in the default browser.",
    )
    parser.add_argument(
        "--port",
        type=valid_port,
        default=DEFAULT_PORT,
        metavar="PORT",
        help=f"Loopback port to use ({MIN_PORT}-{MAX_PORT}; default: {DEFAULT_PORT}).",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=DEFAULT_LANDING_PATH,
        metavar="PATH",
        help=f"Landing path to open in the browser (default: {DEFAULT_LANDING_PATH}).",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Request a confirmed local environment setup or requirements repair before startup.",
    )
    return parser.parse_args(argv)


def valid_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be an integer") from exc
    if not MIN_PORT <= port <= MAX_PORT:
        raise argparse.ArgumentTypeError(
            f"port must be between {MIN_PORT} and {MAX_PORT}"
        )
    return port


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def validate_repository(root: Path) -> bool:
    expected_paths = (
        root / "requirements.txt",
        root / "services" / "jarvis-core" / "src" / "jarvis_core" / "app.py",
    )
    missing = [path for path in expected_paths if not path.is_file()]
    if not missing:
        return True

    print(f"Jarvis repository structure was not found at: {root}", file=sys.stderr)
    for path in missing:
        print(f"Expected file is missing: {path}", file=sys.stderr)
    return False


def confirm_setup(prompt: str) -> bool:
    if not sys.stdin.isatty():
        print("Interactive confirmation is required before changing the local environment.", file=sys.stderr)
        return False
    try:
        answer = input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nLocal environment setup was not confirmed.", file=sys.stderr)
        return False
    return answer.strip().lower() in {"y", "yes"}


def run_setup_command(command: Sequence[str], root: Path, failure_message: str) -> bool:
    try:
        completed = subprocess.run(list(command), cwd=root, shell=False, check=False)
    except OSError as exc:
        print(f"{failure_message}: {exc}", file=sys.stderr)
        return False
    if completed.returncode == 0:
        return True
    print(f"{failure_message} (exit code {completed.returncode}).", file=sys.stderr)
    return False


def runtime_imports_available(venv_python: Path, root: Path) -> bool:
    try:
        completed = subprocess.run(
            [str(venv_python), "-c", "import fastapi; import uvicorn"],
            cwd=root,
            shell=False,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return False
    return completed.returncode == 0


def ensure_environment(root: Path, system_python: str, setup_requested: bool) -> bool:
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    requirements = root / "requirements.txt"

    if not venv_python.is_file():
        print("Jarvis needs a repository-local virtual environment at .venv.")
        print(f"Setup will run: {system_python} -m venv .venv")
        print("Then it will install the committed requirements.txt with the new .venv interpreter.")
        if not confirm_setup("Create the local Jarvis environment and install requirements.txt? [y/N] "):
            print("Setup was declined. Rerun .\\jarvis when you are ready to create the local environment.", file=sys.stderr)
            return False
        if not run_setup_command([system_python, "-m", "venv", ".venv"], root, "Virtual-environment creation failed"):
            return False
        if not venv_python.is_file():
            print("Virtual-environment creation completed without .venv\\Scripts\\python.exe.", file=sys.stderr)
            return False
        return run_setup_command(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements)],
            root,
            "Requirements installation failed",
        )

    needs_repair = setup_requested or not runtime_imports_available(venv_python, root)
    if not needs_repair:
        return True

    if setup_requested:
        print("Setup will install the committed requirements.txt into the existing local .venv.")
        prompt = "Install requirements.txt into the existing local Jarvis environment? [y/N] "
    else:
        print("The local environment appears incomplete because FastAPI or Uvicorn could not be imported.", file=sys.stderr)
        print("Repair will install the committed requirements.txt into the existing local .venv.")
        prompt = "Repair the local Jarvis environment from requirements.txt? [y/N] "
    if not confirm_setup(prompt):
        print("Setup was declined. Rerun .\\jarvis --setup when you are ready to repair the environment.", file=sys.stderr)
        return False
    return run_setup_command(
        [str(venv_python), "-m", "pip", "install", "-r", str(requirements)],
        root,
        "Requirements installation failed",
    )


def health_url(port: int) -> str:
    return f"http://{DEFAULT_HOST}:{port}/health"


def landing_url(port: int, path: str = DEFAULT_LANDING_PATH) -> str:
    normalized = path if path.startswith("/") else f"/{path}"
    return f"http://{DEFAULT_HOST}:{port}{normalized}"


def dashboard_url(port: int) -> str:
    return landing_url(port, "/dashboard")


def assistant_url(port: int) -> str:
    return landing_url(port, "/assistant")


def jarvis_health_ready(port: int) -> bool:
    try:
        with urlopen(health_url(port), timeout=HEALTH_TIMEOUT_SECONDS) as response:
            if response.status != 200:
                return False
            payload = json.load(response)
    except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError):
        return False
    return (
        isinstance(payload, dict)
        and payload.get("status") == "ok"
        and payload.get("app") == APP_NAME
        and payload.get("mode") == "local"
        and bool(payload.get("version"))
    )


def port_accepts_connection(port: int) -> bool:
    try:
        with socket.create_connection((DEFAULT_HOST, port), timeout=HEALTH_TIMEOUT_SECONDS):
            return True
    except OSError:
        return False


def open_landing_page(port: int, path: str = DEFAULT_LANDING_PATH) -> None:
    url = landing_url(port, path)
    print(f"Jarvis UI: {url}")
    try:
        opened = webbrowser.open_new_tab(url)
    except Exception as exc:
        print(f"Warning: could not open the default browser ({exc}). Open the URL manually.", file=sys.stderr)
        return
    if not opened:
        print("Warning: could not open the default browser. Open the URL manually.", file=sys.stderr)


def open_dashboard(port: int, path: str = DEFAULT_LANDING_PATH) -> None:
    open_landing_page(port, path)


def stop_owned_child(child: subprocess.Popen[object]) -> None:
    if child.poll() is not None:
        return
    child.terminate()
    try:
        child.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()


def wait_for_readiness(child: subprocess.Popen[object], port: int) -> bool:
    deadline = time.monotonic() + READINESS_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        exit_code = child.poll()
        if exit_code is not None:
            print(f"Jarvis stopped before becoming ready (exit code {exit_code}).", file=sys.stderr)
            return False
        if jarvis_health_ready(port):
            return True
        time.sleep(POLL_INTERVAL_SECONDS)
    print(f"Jarvis readiness was not confirmed at {health_url(port)}.", file=sys.stderr)
    return False


def configure_services_if_available(port: int) -> None:
    try:
        root = repository_root()
        bootstrap_py = root / "scripts" / "jarvis_bootstrap.py"
        if bootstrap_py.is_file():
            sys.path.insert(0, str(root))
            from scripts.jarvis_bootstrap import configure_jarvis_services
            configure_jarvis_services(jarvis_port=port)
    except Exception:
        pass


def start_jarvis(root: Path, port: int, no_browser: bool, path: str = DEFAULT_LANDING_PATH) -> int:
    if jarvis_health_ready(port):
        print(f"Jarvis is already running on port {port}.")
        configure_services_if_available(port)
        if not no_browser:
            open_landing_page(port, path)
        return 0
    if port_accepts_connection(port):
        print(
            f"Port {port} is occupied by an unknown or unhealthy service. "
            f"Close the conflicting application or rerun with .\\jarvis --port {port + 10 if port <= 65525 else 8010}.",
            file=sys.stderr,
        )
        return 1

    venv_python = root / ".venv" / "Scripts" / "python.exe"
    app_dir = root / "services" / "jarvis-core" / "src"
    command = [
        str(venv_python),
        "-m",
        "uvicorn",
        "--app-dir",
        str(app_dir),
        "jarvis_core.app:app",
        "--host",
        DEFAULT_HOST,
        "--port",
        str(port),
    ]
    try:
        child: subprocess.Popen[object] = subprocess.Popen(command, cwd=root, shell=False)
    except OSError as exc:
        print(f"Jarvis could not be started: {exc}", file=sys.stderr)
        return 1

    try:
        if not wait_for_readiness(child, port):
            stop_owned_child(child)
            return 1
        configure_services_if_available(port)
        if not no_browser:
            open_landing_page(port, path)
        else:
            print(f"Jarvis UI: {landing_url(port, path)}")
        print("Jarvis is running. Press Ctrl+C to stop this launcher-owned instance.")
        exit_code = child.wait()
        if exit_code:
            print(f"Jarvis stopped with exit code {exit_code}.", file=sys.stderr)
        return exit_code
    except KeyboardInterrupt:
        print("\nStopping launcher-owned Jarvis instance.")
        stop_owned_child(child)
        return 0


def existing_instance_status(port: int, no_browser: bool, path: str = DEFAULT_LANDING_PATH) -> int | None:
    if jarvis_health_ready(port):
        print(f"Jarvis is already running on port {port}.")
        configure_services_if_available(port)
        if not no_browser:
            open_landing_page(port, path)
        return 0
    if port_accepts_connection(port):
        print(
            f"Port {port} is occupied by an unknown or unhealthy service. "
            f"Close the conflicting application or rerun with .\\jarvis --port {port + 10 if port <= 65525 else 8010}.",
            file=sys.stderr,
        )
        return 1
    return None


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if os.name != "nt":
        print(
            "This repository launcher is Windows-specific. Use the existing manual developer command on this platform.",
            file=sys.stderr,
        )
        return 1
    if sys.version_info < (3, 10):
        print("Python 3.10 or newer is required to run the Jarvis launcher.", file=sys.stderr)
        return 1

    root = repository_root()
    if not validate_repository(root):
        return 1
    landing_path = getattr(args, "path", DEFAULT_LANDING_PATH)
    existing_status = existing_instance_status(args.port, args.no_browser, landing_path)
    if existing_status is not None:
        return existing_status
    if not ensure_environment(root, sys.executable, args.setup):
        return 1
    return start_jarvis(root, args.port, args.no_browser, landing_path)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nLauncher interrupted.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(f"Jarvis launcher failed unexpectedly: {exc}", file=sys.stderr)
        raise SystemExit(1)
