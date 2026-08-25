"""Jarvis PC Local — Self-Bootstrapping Engine.

Orchestrates automatic prerequisite discovery, environment setup, model-server
lifecycle, model verification, Jarvis Core startup, and service auto-configuration
without manual user configuration.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import webbrowser


APP_NAME = "Jarvis PC Local"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_JARVIS_PORT = 8000
DEFAULT_OLLAMA_PORT = 11434
DEFAULT_GENERATION_MODEL = "qwen3:8b"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
MIN_FREE_DISK_GB = 10.0
OLLAMA_TIMEOUT_SECONDS = 30.0
JARVIS_READINESS_TIMEOUT_SECONDS = 30.0
POLL_INTERVAL_SECONDS = 0.5
REQUEST_TIMEOUT_SECONDS = 10.0
PULL_TIMEOUT_SECONDS = 300.0


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_free_disk_space_gb(path: Path) -> float:
    try:
        stat = shutil.disk_usage(str(path))
        return stat.free / (1024.0 ** 3)
    except OSError:
        return 0.0


def check_disk_space(root: Path, min_gb: float = MIN_FREE_DISK_GB) -> tuple[bool, str]:
    free_gb = get_free_disk_space_gb(root)
    if free_gb >= min_gb:
        return True, f"Free disk space: {free_gb:.1f} GB (minimum: {min_gb:.1f} GB required)."
    return (
        False,
        f"Insufficient free disk space ({free_gb:.1f} GB available, {min_gb:.1f} GB required). "
        f"Please free up disk space on drive {root.drive or 'root'} and restart Jarvis.",
    )


def validate_python_version() -> tuple[bool, str]:
    if sys.version_info < (3, 10):
        return (
            False,
            f"Python {sys.version_info.major}.{sys.version_info.minor} detected. "
            "Jarvis PC Local requires Python 3.10 or newer (Python 3.11-3.13 recommended).",
        )
    return True, f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected."


def find_venv_python(root: Path) -> Path:
    return root / ".venv" / "Scripts" / "python.exe"


def is_venv_complete(root: Path) -> bool:
    venv_python = find_venv_python(root)
    if not venv_python.is_file():
        return False
    try:
        completed = subprocess.run(
            [str(venv_python), "-c", "import fastapi; import uvicorn; import starlette"],
            cwd=root,
            shell=False,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return completed.returncode == 0
    except OSError:
        return False


def ensure_virtualenv(root: Path, system_python: str = sys.executable) -> tuple[bool, str]:
    venv_python = find_venv_python(root)
    requirements = root / "requirements.txt"

    if is_venv_complete(root):
        return True, f"Virtual environment ready at: {venv_python}"

    print("[Bootstrap] Setting up local Python virtual environment (.venv)...")
    if not venv_python.is_file():
        try:
            res = subprocess.run([system_python, "-m", "venv", ".venv"], cwd=root, check=False)
            if res.returncode != 0:
                return False, f"Failed to create virtual environment (exit code {res.returncode})."
        except OSError as exc:
            return False, f"Error creating virtual environment: {exc}"

    if not venv_python.is_file():
        return False, "Virtual environment created but python.exe not found in .venv\\Scripts."

    print("[Bootstrap] Installing dependencies from requirements.txt...")
    try:
        res = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
            cwd=root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        res = subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements)],
            cwd=root,
            check=False,
        )
        if res.returncode != 0:
            return False, f"Failed to install dependencies (exit code {res.returncode})."
    except OSError as exc:
        return False, f"Error installing dependencies: {exc}"

    if not is_venv_complete(root):
        return False, "Dependencies installed but required packages could not be imported."

    return True, "Virtual environment and dependencies successfully configured."


def find_ollama_binary() -> str | None:
    # 1. PATH lookup
    ollama_path = shutil.which("ollama")
    if ollama_path:
        return ollama_path

    # 2. Standard Windows user installation locations
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        cand = Path(local_app_data) / "Programs" / "Ollama" / "ollama.exe"
        if cand.is_file():
            return str(cand)

    program_files = os.environ.get("PROGRAMFILES", "")
    if program_files:
        cand = Path(program_files) / "Ollama" / "ollama.exe"
        if cand.is_file():
            return str(cand)

    return None


def is_ollama_running(host: str = DEFAULT_HOST, port: int = DEFAULT_OLLAMA_PORT) -> bool:
    try:
        req = Request(f"http://{host}:{port}/api/tags", headers={"User-Agent": APP_NAME})
        with urlopen(req, timeout=1.5) as res:
            return res.status == 200
    except (HTTPError, URLError, OSError, ValueError):
        return False


def start_ollama_service(ollama_bin: str) -> subprocess.Popen[object] | None:
    if is_ollama_running():
        return None

    print("[Bootstrap] Starting background Ollama model server...")
    try:
        # Create detached background process on Windows
        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)

        process = subprocess.Popen(
            [ollama_bin, "serve"],
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        return process
    except OSError as exc:
        print(f"[Bootstrap] Warning: Could not start Ollama service: {exc}", file=sys.stderr)
        return None


def wait_for_ollama(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_OLLAMA_PORT,
    timeout: float = OLLAMA_TIMEOUT_SECONDS,
) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if is_ollama_running(host, port):
            return True
        time.sleep(POLL_INTERVAL_SECONDS)
    return False


def list_ollama_models(host: str = DEFAULT_HOST, port: int = DEFAULT_OLLAMA_PORT) -> list[str]:
    try:
        req = Request(f"http://{host}:{port}/api/tags", headers={"User-Agent": APP_NAME})
        with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
            if res.status != 200:
                return []
            data = json.load(res)
            models = []
            for item in data.get("models", []):
                name = item.get("name") or item.get("model")
                if name:
                    models.append(name)
            return models
    except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError):
        return []


def pull_ollama_model(
    model_name: str,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_OLLAMA_PORT,
) -> tuple[bool, str]:
    print(f"[Bootstrap] Pulling local AI model '{model_name}' (this may take a few minutes)...")
    url = f"http://{host}:{port}/api/pull"
    payload = json.dumps({"name": model_name, "stream": False}).encode("utf-8")
    req = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": APP_NAME},
        method="POST",
    )
    try:
        with urlopen(req, timeout=PULL_TIMEOUT_SECONDS) as res:
            if res.status == 200:
                return True, f"Model '{model_name}' successfully downloaded."
            return False, f"Model download returned status code {res.status}."
    except Exception as exc:
        return False, f"Failed to pull model '{model_name}': {exc}"


def ensure_ollama_model(
    model_name: str,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_OLLAMA_PORT,
) -> tuple[bool, str]:
    models = list_ollama_models(host, port)
    # Check exact match or base tag match (e.g. qwen3:8b vs qwen3:8b-latest)
    normalized = [m.lower() for m in models]
    target = model_name.lower()
    target_base = target.split(":")[0]

    for m in normalized:
        if m == target or m.startswith(target_base + ":"):
            return True, f"Model '{model_name}' is already available locally."

    return pull_ollama_model(model_name, host, port)


def is_jarvis_healthy(port: int = DEFAULT_JARVIS_PORT) -> bool:
    url = f"http://{DEFAULT_HOST}:{port}/health"
    try:
        req = Request(url, headers={"User-Agent": APP_NAME})
        with urlopen(req, timeout=1.5) as res:
            if res.status != 200:
                return False
            data = json.load(res)
            return (
                isinstance(data, dict)
                and data.get("status") == "ok"
                and data.get("app") == APP_NAME
            )
    except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError):
        return False


def wait_for_jarvis(
    port: int = DEFAULT_JARVIS_PORT,
    timeout: float = JARVIS_READINESS_TIMEOUT_SECONDS,
) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if is_jarvis_healthy(port):
            return True
        time.sleep(POLL_INTERVAL_SECONDS)
    return False


def configure_jarvis_services(
    jarvis_port: int = DEFAULT_JARVIS_PORT,
    generation_model: str = DEFAULT_GENERATION_MODEL,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ollama_port: int = DEFAULT_OLLAMA_PORT,
) -> dict[str, Any]:
    results = {}
    ollama_endpoint = f"http://{DEFAULT_HOST}:{ollama_port}"

    # 1. Configure Generation
    gen_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/generation/configure"
    gen_body = json.dumps({
        "enabled": True,
        "provider": "ollama",
        "modelName": generation_model,
        "endpoint": ollama_endpoint,
    }).encode("utf-8")
    try:
        req = Request(gen_url, data=gen_body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
            results["generation_config"] = json.load(res)
    except Exception as exc:
        results["generation_config"] = {"error": str(exc)}

    # 2. Probe Generation
    probe_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/generation/probe"
    try:
        req = Request(probe_url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
            results["generation_probe"] = json.load(res)
    except Exception as exc:
        results["generation_probe"] = {"error": str(exc)}

    # 3. Configure Embeddings
    embed_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/embeddings/configure"
    embed_body = json.dumps({
        "enabled": True,
        "model": embedding_model,
        "endpoint": ollama_endpoint,
    }).encode("utf-8")
    try:
        req = Request(embed_url, data=embed_body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
            results["embeddings_config"] = json.load(res)
    except Exception as exc:
        results["embeddings_config"] = {"error": str(exc)}

    # 4. Rebuild Missing Embeddings
    rebuild_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/embeddings/rebuild-missing"
    try:
        req = Request(rebuild_url, data=b"{}", headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
            results["embeddings_rebuild"] = json.load(res)
    except Exception as exc:
        results["embeddings_rebuild"] = {"error": str(exc)}

    return results


def run_bootstrap_pipeline(
    root: Path | None = None,
    jarvis_port: int = DEFAULT_JARVIS_PORT,
    no_browser: bool = False,
    skip_models: bool = False,
    check_only: bool = False,
) -> int:
    if root is None:
        root = repository_root()

    print("==================================================")
    print(f"  {APP_NAME} — Automatic Setup & Bootstrap")
    print("==================================================")

    # 1. Python check
    ok, msg = validate_python_version()
    print(f"[1/7] Python Environment: {msg}")
    if not ok:
        print(f"Error: {msg}", file=sys.stderr)
        return 1

    # 2. Disk space check
    ok, msg = check_disk_space(root)
    print(f"[2/7] Free Disk Space: {msg}")
    if not ok:
        print(f"Error: {msg}", file=sys.stderr)
        return 1

    # 3. Virtualenv check & setup
    ok, msg = ensure_virtualenv(root)
    print(f"[3/7] Python Virtualenv: {msg}")
    if not ok:
        print(f"Error: {msg}", file=sys.stderr)
        return 1

    # 4. Ollama detection & startup
    ollama_bin = find_ollama_binary()
    if ollama_bin:
        print(f"[4/7] Ollama Binary: Found at {ollama_bin}")
        if not is_ollama_running():
            start_ollama_service(ollama_bin)
            if not wait_for_ollama(timeout=15.0):
                print("[4/7] Warning: Ollama service did not respond within timeout. Continuing in deterministic mode.")
            else:
                print("[4/7] Ollama Service: Running and healthy on port 11434.")
        else:
            print("[4/7] Ollama Service: Already running on port 11434.")
    else:
        print("[4/7] Ollama Binary: Not installed. Jarvis will operate in deterministic offline mode.")

    # 5. Local Model Pulling (if Ollama is active)
    if is_ollama_running() and not skip_models:
        print(f"[5/7] Verifying AI Models ({DEFAULT_GENERATION_MODEL}, {DEFAULT_EMBEDDING_MODEL})...")
        ok_gen, msg_gen = ensure_ollama_model(DEFAULT_GENERATION_MODEL)
        print(f"      - Generation Model: {msg_gen}")
        ok_emb, msg_emb = ensure_ollama_model(DEFAULT_EMBEDDING_MODEL)
        print(f"      - Embedding Model:  {msg_emb}")
    else:
        print("[5/7] AI Models: Skipped (Ollama unavailable or model pull skipped).")

    if check_only:
        print("\n[Bootstrap] Preflight check completed successfully.")
        return 0

    # 6. Jarvis Core Server Readiness
    print(f"[6/7] Jarvis Core Server: Checking port {jarvis_port}...")
    if not is_jarvis_healthy(jarvis_port):
        print(f"[6/7] Starting Jarvis Core on port {jarvis_port}...")
        venv_python = find_venv_python(root)
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
            str(jarvis_port),
        ]
        try:
            jarvis_process = subprocess.Popen(command, cwd=root, shell=False)
            if not wait_for_jarvis(jarvis_port):
                print("Error: Jarvis Core did not become healthy within timeout.", file=sys.stderr)
                jarvis_process.terminate()
                return 1
            print(f"[6/7] Jarvis Core is running and healthy at http://{DEFAULT_HOST}:{jarvis_port}/health.")
        except OSError as exc:
            print(f"Error starting Jarvis Core: {exc}", file=sys.stderr)
            return 1
    else:
        print(f"[6/7] Jarvis Core is already active and healthy on port {jarvis_port}.")

    # 7. Auto-configure local generation & embedding endpoints
    print("[7/7] Auto-configuring local generation & knowledge embeddings...")
    cfg_res = configure_jarvis_services(jarvis_port)
    gen_ok = cfg_res.get("generation_config", {}).get("enabled", False)
    emb_ok = cfg_res.get("embeddings_config", {}).get("enabled", False)
    print(f"      - Local Generation: {'Active' if gen_ok else 'Deterministic Mode'}")
    print(f"      - Knowledge Embeddings: {'Active' if emb_ok else 'Off'}")

    print("\n==================================================")
    print(f"  {APP_NAME} is Ready!")
    print(f"  Landing UI: http://{DEFAULT_HOST}:{jarvis_port}/assistant")
    print("==================================================\n")

    if not no_browser:
        try:
            webbrowser.open_new_tab(f"http://{DEFAULT_HOST}:{jarvis_port}/assistant")
        except Exception:
            pass

    return 0


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap and run the self-contained Jarvis PC Local application."
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not open the landing page in the default web browser.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_JARVIS_PORT,
        help=f"Port for Jarvis Core (default: {DEFAULT_JARVIS_PORT}).",
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip pulling Ollama generation and embedding models.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run environment and prerequisite checks without starting services.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    return run_bootstrap_pipeline(
        jarvis_port=args.port,
        no_browser=args.no_browser,
        skip_models=args.skip_models,
        check_only=args.check_only,
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nBootstrap cancelled by user.")
        sys.exit(130)
    except Exception as exc:
        print(f"\nBootstrap failed unexpectedly: {exc}", file=sys.stderr)
        sys.exit(1)
