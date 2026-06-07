from __future__ import annotations

import fnmatch
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .inspector import CHECK_ORDER
from .permissions import is_protected_path
from .risk import DEFAULT_RISK_BUDGET, validate_risk_budget


DEPENDENCY_FILE_PATTERNS = [
    "package.json",
    "package-lock.json",
    "npm-shrinkwrap.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "poetry.lock",
    "requirements.txt",
    "requirements-*.txt",
    "Pipfile",
    "Pipfile.lock",
    "setup.py",
    "setup.cfg",
    "Cargo.toml",
    "Cargo.lock",
    "composer.json",
    "composer.lock",
    "go.mod",
    "go.sum",
    "Gemfile",
    "Gemfile.lock",
]


def review_post_codex_diff(
    project_path: Path,
    package_scripts: dict[str, str] | None = None,
    budget: dict[str, int] | None = None,
) -> dict[str, Any]:
    root = project_path.resolve()
    effective_budget = {**DEFAULT_RISK_BUDGET, **(budget or {})}
    check_plan = build_safe_check_plan(package_scripts or {})
    if shutil.which("git") is None:
        return _blocked_review(
            "git is unavailable for post-Codex diff review",
            effective_budget,
            check_plan,
        )

    status_output = _git(root, ["status", "--porcelain=v1"])
    diff_stat = _git(root, ["diff", "--stat"])
    diff_numstat = _git(root, ["diff", "--numstat"])
    diff_names = _git(root, ["diff", "--name-only"])
    if status_output is None or diff_stat is None or diff_numstat is None or diff_names is None:
        return _blocked_review(
            "git diff inspection failed after Codex execution",
            effective_budget,
            check_plan,
        )

    status_paths, untracked_paths = _paths_from_status(status_output)
    changed_files = sorted({*status_paths, *_lines(diff_names)})
    added_lines, deleted_lines = _parse_numstat(diff_numstat)
    added_lines += _count_untracked_added_lines(root, untracked_paths)
    diff_lines = added_lines + deleted_lines
    protected_changed = [path for path in changed_files if is_protected_path(path)]
    dependency_changed = [path for path in changed_files if is_dependency_file(path)]
    risk = validate_risk_budget(
        {
            "changedFiles": len(changed_files),
            "diffLines": diff_lines,
            "newDependencies": len(dependency_changed),
        },
        effective_budget,
    )

    reasons: list[str] = []
    if not risk.allowed:
        reasons.append(risk.reason)
    if protected_changed:
        reasons.append("protected file changes require user review")
    if dependency_changed:
        reasons.append("dependency/package file changes require user review")

    requires_review = bool(reasons)
    return {
        "changedFiles": changed_files,
        "changedFileCount": len(changed_files),
        "diffStat": diff_stat.strip(),
        "addedLines": added_lines,
        "deletedLines": deleted_lines,
        "diffLines": diff_lines,
        "protectedFilesChanged": protected_changed,
        "dependencyFilesChanged": dependency_changed,
        "riskBudget": effective_budget,
        "budgetExceeded": not risk.allowed,
        "requiresUserReview": requires_review,
        "checksMayProceed": not requires_review,
        "reasons": reasons or ["post-Codex diff is within policy"],
        "checkPlan": check_plan,
    }


def build_safe_check_plan(package_scripts: dict[str, str]) -> dict[str, Any]:
    checks = [
        {
            "name": name,
            "command": f"npm run {name}",
            "source": "package.json scripts",
        }
        for name in CHECK_ORDER
        if name in package_scripts
    ]
    return {
        "checks": checks,
        "reason": "planned detected package scripts only" if checks else "no detected package scripts for safe checks",
    }


def is_dependency_file(path: str) -> bool:
    normalized = path.replace("\\", "/")
    name = Path(normalized).name
    return any(fnmatch.fnmatch(name, pattern) for pattern in DEPENDENCY_FILE_PATTERNS)


def _blocked_review(reason: str, budget: dict[str, int], check_plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "changedFiles": [],
        "changedFileCount": 0,
        "diffStat": "",
        "addedLines": 0,
        "deletedLines": 0,
        "diffLines": 0,
        "protectedFilesChanged": [],
        "dependencyFilesChanged": [],
        "riskBudget": budget,
        "budgetExceeded": True,
        "requiresUserReview": True,
        "checksMayProceed": False,
        "reasons": [reason],
        "checkPlan": check_plan,
    }


def _git(root: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(["git", *args], cwd=root, shell=False, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _paths_from_status(output: str) -> tuple[list[str], list[str]]:
    paths: list[str] = []
    untracked: list[str] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        status = line[:2]
        path = line[3:].strip() if len(line) > 3 else ""
        if " -> " in path:
            paths.extend(part.strip('"') for part in path.split(" -> ", maxsplit=1))
        elif path:
            normalized = path.strip('"')
            paths.append(normalized)
            if status == "??":
                untracked.append(normalized)
    return paths, untracked


def _lines(output: str) -> list[str]:
    return [line.strip() for line in output.splitlines() if line.strip()]


def _parse_numstat(output: str) -> tuple[int, int]:
    added = 0
    deleted = 0
    for line in _lines(output):
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            added += int(parts[0])
            deleted += int(parts[1])
        except ValueError:
            continue
    return added, deleted


def _count_untracked_added_lines(root: Path, paths: list[str]) -> int:
    total = 0
    for path in paths:
        if is_protected_path(path):
            continue
        candidate = (root / path).resolve()
        try:
            if not candidate.is_relative_to(root) or not candidate.is_file():
                continue
            with candidate.open("rb") as handle:
                line_count = 0
                last_byte = b""
                for chunk in iter(lambda: handle.read(8192), b""):
                    line_count += chunk.count(b"\n")
                    last_byte = chunk[-1:]
                if last_byte and last_byte != b"\n":
                    line_count += 1
                total += line_count
        except OSError:
            continue
    return total
