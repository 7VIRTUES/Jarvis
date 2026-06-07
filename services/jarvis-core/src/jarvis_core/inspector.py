from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .permissions import is_protected_path


CHECK_ORDER = ["typecheck", "lint", "test", "build"]
SKIP_PROTECTED_SCAN_DIRS = {".git", ".pytest_cache", "__pycache__", "data", "dist", "node_modules"}


def inspect_project(path: Path) -> dict[str, Any]:
    root = path.resolve()
    package_json = root / "package.json"
    scripts: dict[str, str] = {}
    if package_json.exists() and not is_protected_path(package_json):
        with package_json.open("r", encoding="utf-8") as handle:
            package_data = json.load(handle)
        scripts = package_data.get("scripts", {}) if isinstance(package_data.get("scripts"), dict) else {}

    return {
        "path": str(root),
        "git": _git_summary(root),
        "packageJson": package_json.exists(),
        "packageScripts": scripts,
        "docsPresence": {
            "README.md": (root / "README.md").exists(),
            "docs": (root / "docs").exists(),
            "AGENTS.md": (root / "AGENTS.md").exists(),
            ".jarvis/project.md": (root / ".jarvis" / "project.md").exists(),
        },
        "protectedFilesPresent": _protected_file_names(root),
        "codexCli": {"available": shutil.which("codex") is not None},
        "checkPlan": plan_checks(scripts),
    }


def plan_checks(scripts: dict[str, str]) -> list[str]:
    return [f"npm run {name}" for name in CHECK_ORDER if name in scripts]


def write_markdown_report(inspection: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Jarvis Coding Agent Report",
        "",
        "## Project",
        inspection["path"],
        "",
        "## Git",
        json.dumps(inspection["git"], indent=2),
        "",
        "## Package Scripts",
        json.dumps(inspection["packageScripts"], indent=2),
        "",
        "## Protected Files Present",
        json.dumps(inspection["protectedFilesPresent"], indent=2),
        "",
        "## Check Plan",
        "\n".join(f"- {command}" for command in inspection["checkPlan"]) or "No detected checks.",
        "",
        "## Codex CLI",
        json.dumps(inspection["codexCli"], indent=2),
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def _git_summary(root: Path) -> dict[str, Any]:
    if not (root / ".git").exists() and not _inside_git(root):
        return {"available": shutil.which("git") is not None, "isRepository": False}
    return {
        "available": shutil.which("git") is not None,
        "isRepository": True,
        "branch": _git(root, ["branch", "--show-current"]),
        "status": _git(root, ["status", "--short"]),
    }


def _inside_git(root: Path) -> bool:
    try:
        result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root, capture_output=True, text=True, timeout=5)
        return result.returncode == 0 and result.stdout.strip() == "true"
    except (OSError, subprocess.TimeoutExpired):
        return False


def _git(root: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _protected_file_names(root: Path) -> list[str]:
    found: list[str] = []
    stack = [root]
    while stack:
        current = stack.pop()
        for path in current.iterdir():
            if path.is_dir():
                if path.name not in SKIP_PROTECTED_SCAN_DIRS:
                    stack.append(path)
                continue
            if path.is_file() and is_protected_path(path):
                found.append(str(path.relative_to(root)))
    return sorted(found)
