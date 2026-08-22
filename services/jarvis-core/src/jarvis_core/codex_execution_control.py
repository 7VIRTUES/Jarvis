from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .permissions import is_protected_path
from .post_execution_review import is_dependency_file
from .time_utils import utc_now


SCOPE_MANIFEST_BEGIN = "<!-- JARVIS_CODEX_SCOPE_V1_BEGIN -->"
SCOPE_MANIFEST_END = "<!-- JARVIS_CODEX_SCOPE_V1_END -->"

MAX_APPROVED_FILES = 10
MAX_DIFF_LINES = 700
MAX_CHANGED_FILES = 10


@dataclass
class ActiveExecutionState:
    execution_id: str
    plan_id: str
    task_id: str
    project_name: str
    phase: str
    started_at: str
    cancellation_requested: bool = False
    cancellable: bool = True
    process: subprocess.Popen[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "executionId": self.execution_id,
            "planId": self.plan_id,
            "taskId": self.task_id,
            "projectName": self.project_name,
            "phase": self.phase,
            "startedAt": self.started_at,
            "cancellationRequested": self.cancellation_requested,
            "cancellable": self.cancellable,
        }


class CodexActiveExecutionTracker:
    """Thread-safe in-memory tracker for active conservative Codex child processes."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current: ActiveExecutionState | None = None

    def get_active(self) -> dict[str, Any] | None:
        with self._lock:
            if self._current is None:
                return None
            return self._current.to_dict()

    def set_active(
        self,
        execution_id: str,
        plan_id: str,
        task_id: str,
        project_name: str,
        phase: str = "starting",
    ) -> ActiveExecutionState:
        with self._lock:
            if self._current is not None and self._current.phase not in {"completed", "failed", "blocked", "cancelled"}:
                raise RuntimeError(f"Another Codex execution '{self._current.execution_id}' is currently active.")
            self._current = ActiveExecutionState(
                execution_id=execution_id,
                plan_id=plan_id,
                task_id=task_id,
                project_name=project_name,
                phase=phase,
                started_at=utc_now(),
            )
            return self._current

    def update_phase(self, execution_id: str, phase: str, process: subprocess.Popen[str] | None = None) -> None:
        with self._lock:
            if self._current and self._current.execution_id == execution_id:
                self._current.phase = phase
                if process is not None:
                    self._current.process = process

    def clear(self, execution_id: str) -> None:
        with self._lock:
            if self._current and self._current.execution_id == execution_id:
                self._current = None

    def cancel_active(
        self,
        confirmation: str,
        expected_execution_id: str | None = None,
    ) -> tuple[bool, str, dict[str, Any] | None]:
        if confirmation.strip() != "STOP CODEX EXECUTION":
            return False, "Exact confirmation string 'STOP CODEX EXECUTION' is required.", None

        with self._lock:
            if self._current is None:
                return False, "No active Codex execution found to cancel.", None

            if expected_execution_id and self._current.execution_id != expected_execution_id.strip():
                return False, f"Active execution ID '{self._current.execution_id}' does not match expected '{expected_execution_id}'.", None

            if self._current.phase in {"completed", "failed", "blocked", "cancelled"}:
                return False, f"Execution is already in terminal phase: {self._current.phase}.", self._current.to_dict()

            self._current.cancellation_requested = True
            self._current.phase = "cancelling"
            proc = self._current.process
            current_info = self._current.to_dict()

        # Terminate exact owned process without holding the lock
        if proc is not None:
            try:
                proc.terminate()
                try:
                    proc.wait(timeout=3.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=2.0)
            except (OSError, ProcessLookupError):
                pass

        with self._lock:
            if self._current and self._current.execution_id == current_info["executionId"]:
                self._current.phase = "cancelled"
                self._current.cancellable = False
                final_info = self._current.to_dict()
            else:
                final_info = current_info

        return True, "Codex execution stopped. Any changes already written remain in the workspace and require review.", final_info


def generate_scope_manifest(
    project_path: Path,
    project_name: str,
    allowed_files: list[str],
) -> tuple[dict[str, Any], str]:
    """Generates a strictly validated scope manifest for a conservative Codex plan."""
    if not allowed_files:
        raise ValueError("At least 1 allowed file must be specified for conservative Codex execution.")

    if len(allowed_files) > MAX_APPROVED_FILES:
        raise ValueError(f"Cannot approve more than {MAX_APPROVED_FILES} files for conservative Codex execution.")

    root = project_path.resolve()
    validated_files: list[str] = []
    file_hashes: dict[str, str] = {}

    for raw_path in allowed_files:
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise ValueError("Empty file path in allowed_files.")

        norm_rel = raw_path.strip().replace("\\", "/").lstrip("/")
        if ".." in norm_rel.split("/"):
            raise ValueError(f"Directory traversal '..' is not allowed: {raw_path}")

        if any(char in norm_rel for char in ("*", "?", "[", "]", ":")):
            raise ValueError(f"Glob patterns or invalid characters not permitted in allowed files: {raw_path}")

        file_path = (root / norm_rel).resolve()
        if not file_path.is_relative_to(root):
            raise ValueError(f"File path escapes project root: {raw_path}")

        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"Approved file does not exist or is not a regular file: {norm_rel}")

        if file_path.is_symlink():
            raise ValueError(f"Symlinked files cannot be approved for Codex execution: {norm_rel}")

        if is_protected_path(norm_rel) or is_protected_path(file_path):
            raise PermissionError(f"Access to protected file is blocked: {norm_rel}")

        if is_dependency_file(norm_rel):
            raise PermissionError(f"Dependency and package files cannot be modified in conservative mode: {norm_rel}")

        raw_bytes = file_path.read_bytes()
        sha256 = hashlib.sha256(raw_bytes).hexdigest()

        validated_files.append(norm_rel)
        file_hashes[norm_rel] = sha256

    manifest: dict[str, Any] = {
        "schemaVersion": "v1",
        "projectName": project_name,
        "allowedFiles": validated_files,
        "allowedFileHashes": file_hashes,
        "existingFilesOnly": True,
        "maxChangedFiles": MAX_CHANGED_FILES,
        "maxDiffLines": MAX_DIFF_LINES,
        "maxCodexRuns": 1,
        "automaticChecks": False,
        "automaticRepairs": False,
        "requireCleanWorkingTree": True,
        "createdAt": utc_now(),
    }

    manifest_block = (
        f"{SCOPE_MANIFEST_BEGIN}\n"
        f"{json.dumps(manifest, indent=2)}\n"
        f"{SCOPE_MANIFEST_END}"
    )

    return manifest, manifest_block


def parse_scope_manifest(
    prompt_content: str,
    expected_project_name: str | None = None,
) -> tuple[str | None, dict[str, Any] | None]:
    """Parses and validates the embedded scope manifest from an approved prompt."""
    if not prompt_content or SCOPE_MANIFEST_BEGIN not in prompt_content:
        return "missing scope manifest in prompt content", None

    if prompt_content.count(SCOPE_MANIFEST_BEGIN) != 1 or prompt_content.count(SCOPE_MANIFEST_END) != 1:
        return "duplicate or ambiguous scope manifest blocks detected in prompt", None

    try:
        start_idx = prompt_content.index(SCOPE_MANIFEST_BEGIN) + len(SCOPE_MANIFEST_BEGIN)
        end_idx = prompt_content.index(SCOPE_MANIFEST_END)
        raw_json = prompt_content[start_idx:end_idx].strip()
    except Exception:
        return "malformed scope manifest block in prompt", None

    if len(raw_json) > 16384:
        return "scope manifest block exceeds maximum permitted size", None

    try:
        manifest = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        return f"invalid JSON in scope manifest: {exc}", None

    if not isinstance(manifest, dict):
        return "scope manifest must be a JSON object", None

    if manifest.get("schemaVersion") != "v1":
        return f"unsupported scope manifest schema version: '{manifest.get('schemaVersion')}'", None

    if expected_project_name and manifest.get("projectName") != expected_project_name:
        return f"manifest project '{manifest.get('projectName')}' does not match expected '{expected_project_name}'", None

    allowed_files = manifest.get("allowedFiles")
    if not isinstance(allowed_files, list) or len(allowed_files) < 1 or len(allowed_files) > MAX_APPROVED_FILES:
        return f"allowedFiles must be a list containing 1 to {MAX_APPROVED_FILES} files", None

    file_hashes = manifest.get("allowedFileHashes")
    if not isinstance(file_hashes, dict):
        return "allowedFileHashes must be a dictionary of relative paths to SHA-256 hashes", None

    for rel_path in allowed_files:
        if not isinstance(rel_path, str) or not rel_path.strip():
            return "empty file path in allowedFiles", None
        if ".." in rel_path.split("/") or rel_path.startswith("/") or "\\" in rel_path:
            return f"invalid path format in allowedFiles: '{rel_path}'", None
        if rel_path not in file_hashes or not isinstance(file_hashes[rel_path], str) or len(file_hashes[rel_path]) != 64:
            return f"missing or invalid SHA-256 hash for approved file '{rel_path}'", None
        if is_protected_path(rel_path):
            return f"protected file found in approved manifest: '{rel_path}'", None
        if is_dependency_file(rel_path):
            return f"dependency file found in approved manifest: '{rel_path}'", None

    if manifest.get("maxCodexRuns") != 1:
        return "maxCodexRuns must be exactly 1 for conservative execution", None

    if manifest.get("automaticChecks") is not False:
        return "automaticChecks must be False for conservative execution", None

    if manifest.get("automaticRepairs") is not False:
        return "automaticRepairs must be False for conservative execution", None

    if manifest.get("existingFilesOnly") is not True:
        return "existingFilesOnly must be True for conservative execution", None

    return None, manifest


def verify_stale_files(project_path: Path, manifest: dict[str, Any]) -> str | None:
    """Verifies that all approved files still exist and match their approval-time hashes."""
    root = project_path.resolve()
    file_hashes = manifest.get("allowedFileHashes", {})

    for rel_path, expected_hash in file_hashes.items():
        file_path = (root / rel_path).resolve()
        if not file_path.is_relative_to(root):
            return f"approved file path escapes project root: {rel_path}"

        if not file_path.exists() or not file_path.is_file():
            return f"approved source file is missing: '{rel_path}'; prepare a new plan"

        if file_path.is_symlink():
            return f"approved file '{rel_path}' is a symlink; prepare a new plan"

        try:
            current_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        except OSError as exc:
            return f"error reading approved file '{rel_path}': {exc}"

        if current_hash != expected_hash:
            return f"approved source changed since plan creation; prepare a new plan (file: '{rel_path}')"

    return None


def inspect_git_clean_baseline(project_path: Path) -> tuple[str | None, dict[str, Any]]:
    """Checks that the working tree is clean outside of .jarvis runtime paths."""
    root = project_path.resolve()
    if shutil.which("git") is None:
        return "git CLI is unavailable for baseline verification", {}

    try:
        status_proc = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=str(root),
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        head_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        branch_proc = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(root),
            shell=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"git baseline inspection failed: {exc}", {}

    if status_proc.returncode != 0:
        return "git status check failed (not a git repository or git error)", {}

    head_sha = head_proc.stdout.strip() if head_proc.returncode == 0 else "unknown"
    branch_name = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "unknown"

    dirty_files: list[str] = []
    for line in status_proc.stdout.splitlines():
        if not line.strip():
            continue
        rel = line[3:].strip() if len(line) > 3 else ""
        if " -> " in rel:
            rel = rel.split(" -> ", maxsplit=1)[1].strip()
        norm = rel.replace("\\", "/").strip('"')
        if norm.startswith(".jarvis/") or norm == ".jarvis":
            continue
        dirty_files.append(norm)

    if dirty_files:
        return (
            f"working tree is not clean outside .jarvis runtime paths ({len(dirty_files)} uncommitted changes detected: {', '.join(dirty_files[:3])}); clean workspace before executing approved plan",
            {"headSha": head_sha, "branch": branch_name, "dirtyFiles": dirty_files, "clean": False},
        )

    return None, {"headSha": head_sha, "branch": branch_name, "clean": True}


def review_conservative_git_diff(
    project_path: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Strictly reviews Git changes following a single conservative Codex execution."""
    root = project_path.resolve()
    allowed_files_set = set(manifest.get("allowedFiles", []))
    max_changed_files = manifest.get("maxChangedFiles", MAX_CHANGED_FILES)
    max_diff_lines = manifest.get("maxDiffLines", MAX_DIFF_LINES)

    if shutil.which("git") is None:
        return {
            "requiresUserReview": True,
            "reasons": ["git CLI is unavailable for post-execution diff review"],
            "changedFiles": [],
            "diffLines": 0,
        }

    try:
        status_proc = subprocess.run(["git", "status", "--porcelain=v1"], cwd=str(root), shell=False, capture_output=True, text=True, timeout=10)
        stat_proc = subprocess.run(["git", "diff", "--stat"], cwd=str(root), shell=False, capture_output=True, text=True, timeout=10)
        numstat_proc = subprocess.run(["git", "diff", "--numstat"], cwd=str(root), shell=False, capture_output=True, text=True, timeout=10)
        name_proc = subprocess.run(["git", "diff", "--name-only"], cwd=str(root), shell=False, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "requiresUserReview": True,
            "reasons": [f"git diff review command failed: {exc}"],
            "changedFiles": [],
            "diffLines": 0,
        }

    reasons: list[str] = []
    modified_files: list[str] = []
    added_files: list[str] = []
    deleted_files: list[str] = []
    renamed_files: list[str] = []
    untracked_files: list[str] = []

    for line in status_proc.stdout.splitlines():
        if not line.strip():
            continue
        status_code = line[:2]
        path_part = line[3:].strip() if len(line) > 3 else ""
        if " -> " in path_part:
            path_part = path_part.split(" -> ", maxsplit=1)[1].strip()
        norm_path = path_part.replace("\\", "/").strip('"')

        if norm_path.startswith(".jarvis/") or norm_path == ".jarvis":
            continue

        if status_code == "??":
            untracked_files.append(norm_path)
        elif "A" in status_code:
            added_files.append(norm_path)
        elif "D" in status_code:
            deleted_files.append(norm_path)
        elif "R" in status_code:
            renamed_files.append(norm_path)
        elif "M" in status_code:
            modified_files.append(norm_path)
        else:
            modified_files.append(norm_path)

    for line in name_proc.stdout.splitlines():
        norm = line.strip().replace("\\", "/").strip('"')
        if norm and not norm.startswith(".jarvis/") and norm not in modified_files and norm not in added_files:
            modified_files.append(norm)

    all_changed_files = sorted(set(modified_files + added_files + deleted_files + renamed_files + untracked_files))

    # Strict Scope Enforcement
    if added_files or untracked_files:
        new_items = sorted(set(added_files + untracked_files))
        reasons.append(f"new or untracked files created outside allowed scope: {', '.join(new_items[:5])}")

    if deleted_files:
        reasons.append(f"files deleted outside allowed scope: {', '.join(deleted_files[:5])}")

    if renamed_files:
        reasons.append(f"files renamed outside allowed scope: {', '.join(renamed_files[:5])}")

    unapproved_modified = [f for f in modified_files if f not in allowed_files_set]
    if unapproved_modified:
        reasons.append(f"files modified outside approved scope: {', '.join(unapproved_modified[:5])}")

    protected_changed = [f for f in all_changed_files if is_protected_path(f)]
    if protected_changed:
        reasons.append(f"protected file modifications detected: {', '.join(protected_changed[:5])}")

    dependency_changed = [f for f in all_changed_files if is_dependency_file(f)]
    if dependency_changed:
        reasons.append(f"dependency/package file modifications detected: {', '.join(dependency_changed[:5])}")

    # Calculate diff lines
    added_lines = 0
    deleted_lines = 0
    for line in numstat_proc.stdout.splitlines():
        parts = line.strip().split("\t")
        if len(parts) >= 3:
            file_name = parts[2].replace("\\", "/")
            if not file_name.startswith(".jarvis/"):
                try:
                    added_lines += int(parts[0])
                    deleted_lines += int(parts[1])
                except ValueError:
                    pass

    total_diff_lines = added_lines + deleted_lines

    if len(all_changed_files) > max_changed_files:
        reasons.append(f"changed file count ({len(all_changed_files)}) exceeds budget of {max_changed_files}")

    if total_diff_lines > max_diff_lines:
        reasons.append(f"total diff lines ({total_diff_lines}) exceeds budget of {max_diff_lines}")

    requires_review = bool(reasons)

    return {
        "requiresUserReview": requires_review,
        "reasons": reasons or ["Code change completed within approved file scope. Automated checks were skipped by extreme-budget policy."],
        "changedFiles": all_changed_files,
        "changedFileCount": len(all_changed_files),
        "modifiedFiles": modified_files,
        "addedFiles": added_files,
        "untrackedFiles": untracked_files,
        "deletedFiles": deleted_files,
        "renamedFiles": renamed_files,
        "protectedFilesChanged": protected_changed,
        "dependencyFilesChanged": dependency_changed,
        "diffStat": stat_proc.stdout.strip(),
        "addedLines": added_lines,
        "deletedLines": deleted_lines,
        "diffLines": total_diff_lines,
        "checksMayProceed": False,  # Extreme-budget mode skips automated checks
    }
