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
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener, urlopen
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
REQUEST_TIMEOUT_SECONDS = 120.0
PULL_TIMEOUT_SECONDS = 1800.0

# Track processes started by this bootstrap run for graceful teardown
_STARTED_OLLAMA_PROCESS: subprocess.Popen[object] | None = None
_STARTED_JARVIS_PROCESS: subprocess.Popen[object] | None = None


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
            [str(venv_python), "-I", "-B", "-c", "import sys; assert sys.version_info >= (3, 10); import fastapi; import uvicorn; import starlette"],
            cwd=root,
            shell=False,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
        )
        return completed.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
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


def is_winget_available() -> bool:
    return shutil.which("winget") is not None


def install_ollama_via_winget() -> bool:
    if not is_winget_available():
        return False
    print("[Bootstrap] Installing official Ollama via Windows Package Manager (winget)...")
    try:
        res = subprocess.run(
            [
                "winget",
                "install",
                "--id",
                "Ollama.Ollama",
                "--scope",
                "user",
                "--exact",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ],
            shell=False,
            check=False,
        )
        return res.returncode == 0
    except OSError:
        return False


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


class LocalNoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        return None


_LOCAL_OPENER = build_opener(ProxyHandler({}), LocalNoRedirect())


def is_ollama_running(host: str = DEFAULT_HOST, port: int = DEFAULT_OLLAMA_PORT) -> bool:
    try:
        req = Request(f"http://{host}:{port}/api/tags", headers={"User-Agent": APP_NAME})
        with _LOCAL_OPENER.open(req, timeout=1.5) as res:
            return res.status == 200
    except (HTTPError, URLError, OSError, ValueError):
        return False


def start_ollama_service(ollama_bin: str) -> subprocess.Popen[object] | None:
    global _STARTED_OLLAMA_PROCESS
    if is_ollama_running():
        return None

    print("[Bootstrap] Starting background Ollama model server...")
    try:
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
        _STARTED_OLLAMA_PROCESS = process
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


def list_ollama_models(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_OLLAMA_PORT,
    timeout: float = REQUEST_TIMEOUT_SECONDS,
) -> list[str]:
    try:
        req = Request(f"http://{host}:{port}/api/tags", headers={"User-Agent": APP_NAME})
        with _LOCAL_OPENER.open(req, timeout=timeout) as res:
            if res.status != 200:
                return []
            payload = res.read(1024 * 1024 + 1)
            if len(payload) > 1024 * 1024:
                return []
            data = json.loads(payload)
            models = []
            if not isinstance(data, dict):
                return []
            for item in data.get("models", []):
                if not isinstance(item, dict):
                    continue
                name = item.get("name") or item.get("model")
                if name:
                    models.append(name)
            return models
    except (HTTPError, URLError, OSError, ValueError, json.JSONDecodeError):
        return []


def is_exact_model_match(target_model: str, candidate_model: str) -> bool:
    """Check if candidate model matches target model accurately.

    - qwen3:8b matches qwen3:8b or qwen3:8b:latest
    - qwen3:4b or qwen3:14b does NOT match qwen3:8b
    - nomic-embed-text matches nomic-embed-text or nomic-embed-text:latest
    """
    target = target_model.strip().lower()
    candidate = candidate_model.strip().lower()
    if target == candidate:
        return True

    t_clean = target[:-7] if target.endswith(":latest") else target
    c_clean = candidate[:-7] if candidate.endswith(":latest") else candidate
    return t_clean == c_clean


def pull_ollama_model(
    model_name: str,
    ollama_bin: str | None = None,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_OLLAMA_PORT,
) -> tuple[bool, str]:
    print(f"[Bootstrap] Pulling local AI model '{model_name}' (this may take several minutes)...")
    if ollama_bin and os.path.isfile(ollama_bin):
        try:
            completed = subprocess.run(
                [ollama_bin, "pull", model_name],
                shell=False,
                check=False,
            )
            if completed.returncode == 0:
                return True, f"Model '{model_name}' successfully downloaded."
            return False, f"Model pull failed with exit code {completed.returncode}."
        except OSError as exc:
            print(f"[Bootstrap] CLI pull error ({exc}), attempting HTTP fallback...", file=sys.stderr)

    url = f"http://{host}:{port}/api/pull"
    payload = json.dumps({"name": model_name, "stream": False}).encode("utf-8")
    req = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": APP_NAME},
        method="POST",
    )
    try:
        with _LOCAL_OPENER.open(req, timeout=PULL_TIMEOUT_SECONDS) as res:
            if res.status == 200:
                return True, f"Model '{model_name}' successfully downloaded."
            return False, f"Model download returned status code {res.status}."
    except Exception as exc:
        return False, f"Failed to pull model '{model_name}': {exc}"


def ensure_ollama_model(
    model_name: str,
    ollama_bin: str | None = None,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_OLLAMA_PORT,
) -> tuple[bool, str]:
    models = list_ollama_models(host, port)
    for candidate in models:
        if is_exact_model_match(model_name, candidate):
            return True, f"Model '{model_name}' is already available locally."

    return pull_ollama_model(model_name, ollama_bin=ollama_bin, host=host, port=port)


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
    ollama_host: str = DEFAULT_HOST,
    ollama_port: int = DEFAULT_OLLAMA_PORT,
) -> dict[str, Any]:
    """Auto-configure local generation and knowledge embeddings using exact API contracts."""
    summary: dict[str, Any] = {
        "generation": {
            "status": "unavailable",
            "model": generation_model,
            "message": "Local generation not configured.",
        },
        "embeddings": {
            "status": "unavailable",
            "model": embedding_model,
            "message": "Knowledge embeddings not configured.",
        },
    }

    ollama_up = is_ollama_running(ollama_host, ollama_port)
    if not ollama_up:
        summary["generation"]["message"] = "Ollama model server is not reachable on loopback."
        summary["embeddings"]["message"] = "Ollama model server is not reachable on loopback."
        return summary

    models = list_ollama_models(ollama_host, ollama_port)
    has_gen_model = any(is_exact_model_match(generation_model, m) for m in models)
    has_emb_model = any(is_exact_model_match(embedding_model, m) for m in models)

    # 1. Configure & Probe Generation
    if has_gen_model:
        gen_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/generation/configure"
        gen_body = json.dumps({
            "modelName": generation_model,
            "contextCharacterLimit": 24000,
            "maximumOutputCharacters": 4000,
            "temperature": 0.2,
            "keepAliveSeconds": 300,
            "confirmation": "ENABLE LOCAL GENERATION",
            "actor": "local_user",
        }).encode("utf-8")
        try:
            req = Request(gen_url, data=gen_body, headers={"Content-Type": "application/json", "User-Agent": APP_NAME}, method="POST")
            with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
                json.load(res)

            probe_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/generation/probe"
            probe_body = json.dumps({
                "modelName": generation_model,
                "actor": "local_user",
            }).encode("utf-8")
            probe_req = Request(probe_url, data=probe_body, headers={"Content-Type": "application/json", "User-Agent": APP_NAME}, method="POST")
            with urlopen(probe_req, timeout=REQUEST_TIMEOUT_SECONDS) as probe_res:
                probe_data = json.load(probe_res)

            if probe_data.get("status") == "ok":
                summary["generation"] = {
                    "status": "ready",
                    "model": generation_model,
                    "message": f"Local generation active and probed ({generation_model}).",
                }
            else:
                summary["generation"] = {
                    "status": "failed",
                    "model": generation_model,
                    "message": f"Generation probe failed: {probe_data}",
                }
        except Exception as exc:
            summary["generation"] = {
                "status": "failed",
                "model": generation_model,
                "message": f"Generation configuration failed: {exc}",
            }
    else:
        summary["generation"]["message"] = f"Required generation model '{generation_model}' not found in local Ollama."

    # 2. Configure & Probe Embeddings
    if has_emb_model:
        embed_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/knowledge/embeddings/configure"
        embed_body = json.dumps({
            "modelName": embedding_model,
            "confirmation": "ENABLE EMBEDDINGS",
            "actor": "local_user",
        }).encode("utf-8")
        try:
            req = Request(embed_url, data=embed_body, headers={"Content-Type": "application/json", "User-Agent": APP_NAME}, method="POST")
            with urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
                json.load(res)

            probe_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/knowledge/embeddings/probe"
            probe_body = json.dumps({
                "modelName": embedding_model,
                "privateSession": False,
            }).encode("utf-8")
            probe_req = Request(probe_url, data=probe_body, headers={"Content-Type": "application/json", "User-Agent": APP_NAME}, method="POST")
            with urlopen(probe_req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
                json.load(res)

            # Rebuild preview
            preview_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/knowledge/embeddings/rebuild-preview"
            preview_body = json.dumps({
                "onlyMissing": True,
                "limit": 32,
                "includeSensitive": False,
                "privateSession": False,
            }).encode("utf-8")
            preview_req = Request(preview_url, data=preview_body, headers={"Content-Type": "application/json", "User-Agent": APP_NAME}, method="POST")
            with urlopen(preview_req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
                preview_data = json.load(res)

            if preview_data.get("previewCount", 0) > 0 or len(preview_data.get("items", [])) > 0:
                rebuild_url = f"http://{DEFAULT_HOST}:{jarvis_port}/api/knowledge/embeddings/rebuild"
                rebuild_body = json.dumps({
                    "onlyMissing": True,
                    "limit": 32,
                    "includeSensitive": False,
                    "privateSession": False,
                    "confirmation": "EMBED",
                    "actor": "local_user",
                }).encode("utf-8")
                rebuild_req = Request(rebuild_url, data=rebuild_body, headers={"Content-Type": "application/json", "User-Agent": APP_NAME}, method="POST")
                with urlopen(rebuild_req, timeout=REQUEST_TIMEOUT_SECONDS) as res:
                    json.load(res)

            summary["embeddings"] = {
                "status": "ready",
                "model": embedding_model,
                "message": f"Knowledge embeddings active ({embedding_model}).",
            }
        except Exception as exc:
            summary["embeddings"] = {
                "status": "failed",
                "model": embedding_model,
                "message": f"Embeddings configuration failed: {exc}",
            }
    else:
        summary["embeddings"]["message"] = f"Required embedding model '{embedding_model}' not found in local Ollama."

    return summary


def preflight_environment(root: Path | None = None) -> dict[str, Any]:
    """Inspect desktop prerequisites without changing the machine."""
    root = root or repository_root()
    missing: list[dict[str, str]] = []

    def require(code: str, message: str) -> None:
        missing.append({"code": code, "message": message})

    python_ok, python_message = validate_python_version()
    if not python_ok:
        require("python", python_message)
    venv_python = find_venv_python(root)
    if not venv_python.is_file():
        require("venv", "The repository-local .venv\\Scripts\\python.exe is missing.")
    elif not is_venv_complete(root):
        require("venv_dependencies", "The local .venv is present but required Jarvis Python packages are incomplete.")

    ollama_bin = find_ollama_binary()
    if not ollama_bin:
        require("ollama", "Ollama is not installed in a supported local location.")
    if not is_ollama_running():
        require("ollama_service", "The local Ollama service is not running on 127.0.0.1:11434.")
    else:
        models = list_ollama_models(timeout=3.0)
        for code, model in (
            ("generation_model", DEFAULT_GENERATION_MODEL),
            ("embedding_model", DEFAULT_EMBEDDING_MODEL),
        ):
            if not any(is_exact_model_match(model, candidate) for candidate in models):
                require(code, f"The local Ollama model '{model}' is missing.")
        if any(item["code"].endswith("_model") for item in missing):
            disk_ok, disk_message = check_disk_space(root)
            if not disk_ok:
                require("disk", disk_message)

    return {"ready": not missing, "missing": missing, "python_executable": sys.executable}


def desktop_port_available(port: int = DEFAULT_JARVIS_PORT) -> bool:
    try:
        with socket.create_connection((DEFAULT_HOST, port), timeout=1.5):
            return False
    except ConnectionRefusedError:
        return True
    except OSError:
        return False


def prepare_desktop_environment(root: Path | None = None) -> int:
    """Prepare prerequisites after an explicit desktop action; never start Jarvis Core."""
    root = root or repository_root()

    def stage(label: str) -> None:
        print(f"[Prepare] {label}", flush=True)

    def guard_instance() -> bool:
        if desktop_port_available():
            return True
        print(
            "Jarvis or another service is already using port 8000. "
            "Preparation stopped without changing that instance.",
            file=sys.stderr, flush=True,
        )
        return False

    if not guard_instance():
        return 1
    python_ok, python_message = validate_python_version()
    if not python_ok:
        print(python_message, file=sys.stderr, flush=True)
        return 1
    stage("Checking the local Python environment...")
    ok, message = ensure_virtualenv(root)
    if not ok:
        print(message, file=sys.stderr, flush=True)
        return 1
    if not guard_instance():
        return 1

    stage("Checking Ollama installation...")
    ollama_bin = find_ollama_binary()
    if not ollama_bin and os.name == "nt":
        if not is_winget_available():
            print("Ollama is missing and Windows Package Manager is unavailable.", file=sys.stderr, flush=True)
            return 1
        if not install_ollama_via_winget():
            print("Ollama installation did not complete. Retry preparation.", file=sys.stderr, flush=True)
            return 1
        ollama_bin = find_ollama_binary()
    if not ollama_bin:
        print("Ollama is still unavailable after installation.", file=sys.stderr, flush=True)
        return 1
    if not guard_instance():
        return 1

    stage("Checking the local Ollama service...")
    if not is_ollama_running():
        start_ollama_service(ollama_bin)
        if not wait_for_ollama(timeout=15.0):
            print("Ollama did not become ready on 127.0.0.1:11434.", file=sys.stderr, flush=True)
            return 1
    models = list_ollama_models()
    for model in (DEFAULT_GENERATION_MODEL, DEFAULT_EMBEDDING_MODEL):
        if any(is_exact_model_match(model, candidate) for candidate in models):
            continue
        if not guard_instance():
            return 1
        disk_ok, disk_message = check_disk_space(root)
        if not disk_ok:
            print(disk_message, file=sys.stderr, flush=True)
            return 1
        stage(f"Downloading local model {model}...")
        ok, message = ensure_ollama_model(model, ollama_bin=ollama_bin)
        if not ok:
            print(message, file=sys.stderr, flush=True)
            return 1
    if not guard_instance():
        return 1
    readiness = preflight_environment(root)
    if not readiness["ready"]:
        for item in readiness["missing"]:
            print(item["message"], file=sys.stderr, flush=True)
        return 1
    stage("Preparation complete. Starting Jarvis...")
    return 0


def run_bootstrap_pipeline(
    root: Path | None = None,
    jarvis_port: int = DEFAULT_JARVIS_PORT,
    no_browser: bool = False,
    skip_models: bool = False,
    check_only: bool = False,
    prepare_only: bool = False,
    landing_path: str = "/assistant",
) -> int:
    global _STARTED_JARVIS_PROCESS
    if root is None:
        root = repository_root()
    if check_only:
        readiness = preflight_environment(root)
        for item in readiness["missing"]:
            print(item["message"])
        return 0 if readiness["ready"] else 1

    print("==================================================")
    print(f"  {APP_NAME} — Automatic Setup & Bootstrap")
    print("==================================================")

    # 1. Python check
    ok, msg = validate_python_version()
    print(f"[1/7] Python Environment: {msg}")
    if not ok:
        print(f"Error: {msg}", file=sys.stderr)
        return 1

    # 2. Virtualenv check & setup
    ok, msg = ensure_virtualenv(root)
    print(f"[2/7] Python Virtualenv: {msg}")
    if not ok:
        print(f"Error: {msg}", file=sys.stderr)
        return 1

    # 3. Ollama detection, installation & startup
    ollama_bin = find_ollama_binary()
    if not ollama_bin and os.name == "nt" and is_winget_available():
        print("[3/7] Ollama Binary: Not found. Attempting automatic installation via winget...")
        if install_ollama_via_winget():
            ollama_bin = find_ollama_binary()

    if ollama_bin:
        print(f"[3/7] Ollama Binary: Found at {ollama_bin}")
        if not is_ollama_running():
            start_ollama_service(ollama_bin)
            if not wait_for_ollama(timeout=15.0):
                print("[3/7] Notice: Ollama service did not respond within timeout.")
                if prepare_only:
                    print("\n==================================================", file=sys.stderr)
                    print("  Jarvis setup incomplete.", file=sys.stderr)
                    print("  Reason: Ollama background service did not respond on port 11434.", file=sys.stderr)
                    print("==================================================\n", file=sys.stderr)
                    return 1
            else:
                print("[3/7] Ollama Service: Running and healthy on port 11434.")
        else:
            print("[3/7] Ollama Service: Already running on port 11434.")
    else:
        print("[3/7] Ollama Binary: Not found. Jarvis will operate in deterministic fallback mode.")
        if prepare_only:
            print("\n==================================================", file=sys.stderr)
            print("  Jarvis setup incomplete.", file=sys.stderr)
            print("  Reason: Ollama binary not found and automatic installation did not succeed.", file=sys.stderr)
            print("==================================================\n", file=sys.stderr)
            return 1

    # 4. Local Model Pulling & Disk Check
    if is_ollama_running() and not skip_models:
        existing_models = list_ollama_models()
        needs_gen = not any(is_exact_model_match(DEFAULT_GENERATION_MODEL, m) for m in existing_models)
        needs_emb = not any(is_exact_model_match(DEFAULT_EMBEDDING_MODEL, m) for m in existing_models)

        if needs_gen or needs_emb:
            disk_ok, disk_msg = check_disk_space(root, MIN_FREE_DISK_GB)
            print(f"[4/7] Free Disk Space: {disk_msg}")
            if not disk_ok:
                print(f"Notice: Disk space insufficient for model downloads.")
                if prepare_only:
                    print("\n==================================================", file=sys.stderr)
                    print("  Jarvis setup incomplete.", file=sys.stderr)
                    print(f"  Reason: Insufficient disk space for required model downloads ({disk_msg}).", file=sys.stderr)
                    print("==================================================\n", file=sys.stderr)
                    return 1
            else:
                print(f"[4/7] Verifying AI Models ({DEFAULT_GENERATION_MODEL}, {DEFAULT_EMBEDDING_MODEL})...")
                if needs_gen:
                    ok_gen, msg_gen = ensure_ollama_model(DEFAULT_GENERATION_MODEL, ollama_bin=ollama_bin)
                    print(f"      - Generation Model: {msg_gen}")
                    if not ok_gen and prepare_only:
                        print("\n==================================================", file=sys.stderr)
                        print("  Jarvis setup incomplete.", file=sys.stderr)
                        print(f"  Reason: Generation model pull failed: {msg_gen}", file=sys.stderr)
                        print("==================================================\n", file=sys.stderr)
                        return 1
                else:
                    print(f"      - Generation Model: Already present ({DEFAULT_GENERATION_MODEL}).")

                if needs_emb:
                    ok_emb, msg_emb = ensure_ollama_model(DEFAULT_EMBEDDING_MODEL, ollama_bin=ollama_bin)
                    print(f"      - Embedding Model:  {msg_emb}")
                    if not ok_emb and prepare_only:
                        print("\n==================================================", file=sys.stderr)
                        print("  Jarvis setup incomplete.", file=sys.stderr)
                        print(f"  Reason: Embedding model pull failed: {msg_emb}", file=sys.stderr)
                        print("==================================================\n", file=sys.stderr)
                        return 1
                else:
                    print(f"      - Embedding Model:  Already present ({DEFAULT_EMBEDDING_MODEL}).")
        else:
            print(f"[4/7] AI Models: Both required models are already installed locally.")
    else:
        print("[4/7] AI Models: Skipped (Ollama unavailable or model downloads skipped).")
        if prepare_only and not skip_models:
            print("\n==================================================", file=sys.stderr)
            print("  Jarvis setup incomplete.", file=sys.stderr)
            print("  Reason: Ollama is unavailable for AI model verification.", file=sys.stderr)
            print("==================================================\n", file=sys.stderr)
            return 1


    # 5. Jarvis Core Server Readiness
    print(f"[5/7] Jarvis Core Server: Checking port {jarvis_port}...")
    started_child = False
    if not is_jarvis_healthy(jarvis_port):
        print(f"[5/7] Starting Jarvis Core on port {jarvis_port}...")
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
            _STARTED_JARVIS_PROCESS = jarvis_process
            started_child = True
            if not wait_for_jarvis(jarvis_port):
                print("Error: Jarvis Core did not become healthy within timeout.", file=sys.stderr)
                jarvis_process.terminate()
                if prepare_only:
                    print("\n==================================================", file=sys.stderr)
                    print("  Jarvis setup incomplete.", file=sys.stderr)
                    print("  Reason: Jarvis Core service failed to start.", file=sys.stderr)
                    print("==================================================\n", file=sys.stderr)
                return 1
            print(f"[5/7] Jarvis Core is running and healthy at http://{DEFAULT_HOST}:{jarvis_port}/health.")
        except OSError as exc:
            print(f"Error starting Jarvis Core: {exc}", file=sys.stderr)
            if prepare_only:
                print("\n==================================================", file=sys.stderr)
                print("  Jarvis setup incomplete.", file=sys.stderr)
                print(f"  Reason: Error starting Jarvis Core: {exc}", file=sys.stderr)
                print("==================================================\n", file=sys.stderr)
            return 1
    else:
        print(f"[5/7] Jarvis Core is already active and healthy on port {jarvis_port}.")

    # 6. Auto-configure local generation & embedding endpoints
    print("[6/7] Auto-configuring local generation & knowledge embeddings...")
    cfg_res = configure_jarvis_services(jarvis_port)
    gen_status = cfg_res.get("generation", {}).get("status", "unavailable")
    emb_status = cfg_res.get("embeddings", {}).get("status", "unavailable")

    if gen_status == "ready":
        print(f"      - Local Generation: Ready ({DEFAULT_GENERATION_MODEL})")
    else:
        reason = cfg_res.get("generation", {}).get("message", "unknown reason")
        print("      - Local Generation: Off · Deterministic fallback mode")
        print(f"        Notice: {reason}")

    if emb_status == "ready":
        print(f"      - Knowledge Embeddings: Ready ({DEFAULT_EMBEDDING_MODEL})")
    else:
        reason = cfg_res.get("embeddings", {}).get("message", "unknown reason")
        print("      - Knowledge Embeddings: Off")
        print(f"        Notice: {reason}")

    # 7. Validation for --prepare-only (Fail-Closed)
    if prepare_only:
        if started_child and _STARTED_JARVIS_PROCESS is not None:
            _STARTED_JARVIS_PROCESS.terminate()
            try:
                _STARTED_JARVIS_PROCESS.wait(timeout=3.0)
            except subprocess.TimeoutExpired:
                _STARTED_JARVIS_PROCESS.kill()

        if gen_status != "ready" or emb_status != "ready":
            reasons = []
            if gen_status != "ready":
                reasons.append(f"Generation ({DEFAULT_GENERATION_MODEL}): {cfg_res.get('generation', {}).get('message', 'not ready')}")
            if emb_status != "ready":
                reasons.append(f"Embeddings ({DEFAULT_EMBEDDING_MODEL}): {cfg_res.get('embeddings', {}).get('message', 'not ready')}")
            print("\n==================================================", file=sys.stderr)
            print("  Jarvis setup incomplete.", file=sys.stderr)
            print(f"  Reason: {'; '.join(reasons)}", file=sys.stderr)
            print("==================================================\n", file=sys.stderr)
            return 1

        normalized_path = landing_path if landing_path.startswith("/") else f"/{landing_path}"
        landing_full_url = f"http://{DEFAULT_HOST}:{jarvis_port}{normalized_path}"
        print("\n==================================================")
        print(f"  {APP_NAME} is Ready!")
        print(f"  Landing UI: {landing_full_url}")
        print("==================================================\n")
        print("[Bootstrap] Environment preparation completed.")
        return 0

    # 7. Browser Landing (Normal Runtime Launch)
    normalized_path = landing_path if landing_path.startswith("/") else f"/{landing_path}"
    landing_full_url = f"http://{DEFAULT_HOST}:{jarvis_port}{normalized_path}"

    print("\n==================================================")
    print(f"  {APP_NAME} is Ready!")
    print(f"  Landing UI: {landing_full_url}")
    print("==================================================\n")

    if not no_browser:
        try:
            webbrowser.open_new_tab(landing_full_url)
        except Exception:
            pass

    if started_child and _STARTED_JARVIS_PROCESS is not None:
        try:
            print("Jarvis is running. Press Ctrl+C to stop this instance.")
            return _STARTED_JARVIS_PROCESS.wait()
        except KeyboardInterrupt:
            print("\nStopping Jarvis Core instance...")
            _STARTED_JARVIS_PROCESS.terminate()
            try:
                _STARTED_JARVIS_PROCESS.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                _STARTED_JARVIS_PROCESS.kill()
            return 0

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
        "--path",
        type=str,
        default="/assistant",
        help="Landing path to open in the browser (default: /assistant).",
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip pulling Ollama generation and embedding models.",
    )
    parser.add_argument(
        "--preflight-json",
        action="store_true",
        help="Print read-only desktop readiness as JSON.",
    )
    parser.add_argument(
        "--desktop-prepare",
        action="store_true",
        help="Prepare local prerequisites after an explicit desktop request; do not start Jarvis Core.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run environment and prerequisite checks without starting services.",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Run full preparation (Python, .venv, Ollama, models, service config) without running the server loop.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.preflight_json:
        print(json.dumps(preflight_environment()))
        return 0
    if args.desktop_prepare:
        return prepare_desktop_environment()
    return run_bootstrap_pipeline(
        jarvis_port=args.port,
        no_browser=args.no_browser,
        skip_models=args.skip_models,
        check_only=args.check_only,
        prepare_only=args.prepare_only,
        landing_path=args.path,
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
