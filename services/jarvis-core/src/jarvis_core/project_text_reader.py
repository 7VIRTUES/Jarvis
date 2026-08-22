from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

from .permissions import is_protected_path
from .post_execution_review import is_dependency_file
from .project_registry import ProjectRegistry
from .workspace_boundary import (
    DEFAULT_RUNTIME_SKIP_DIRS,
    SAFE_TEXT_SUFFIXES,
    WorkspaceBoundaryValidator,
)


MAX_FILES_PER_READ = 5
MAX_BYTES_PER_FILE = 128_000
MAX_TOTAL_BYTES = 256_000
MAX_RETURNED_CHARS = 250_000
MAX_CATALOG_CANDIDATES = 1000

CATEGORY_MAP: dict[str, str] = {
    ".py": "Python Source",
    ".ts": "TypeScript Source",
    ".tsx": "TypeScript React",
    ".js": "JavaScript Source",
    ".jsx": "JavaScript React",
    ".json": "JSON Data / Config",
    ".md": "Markdown Document",
    ".txt": "Plain Text",
    ".yaml": "YAML Config",
    ".yml": "YAML Config",
    ".toml": "TOML Config",
    ".ini": "INI Config",
    ".cfg": "Configuration",
    ".css": "CSS Stylesheet",
    ".html": "HTML Document",
    ".ps1": "PowerShell Script",
    ".sh": "Shell Script",
}


def is_reparse_point(path: Path) -> bool:
    try:
        if hasattr(os.path, "isreparsepoint"):
            return bool(os.path.isreparsepoint(str(path)))
        return False
    except Exception:
        return False


class ProjectTextReader:
    """Safe, bounded text and source file reader for registered Jarvis projects."""

    def __init__(self, projects: ProjectRegistry, workspace_root: Path) -> None:
        self.projects = projects
        self.workspace_root = Path(workspace_root).resolve()

    def list_safe_files(self, project_name: str) -> list[dict[str, Any]]:
        clean_project = str(project_name or "").strip()
        if not clean_project:
            raise ValueError("projectName is required.")

        proj = self.projects.get_project(clean_project)
        if not proj:
            raise KeyError(f"Registered project not found: {clean_project}")

        project_root = Path(proj["path"]).expanduser().resolve()
        validator = WorkspaceBoundaryValidator(project_root, self.workspace_root)
        root_decision = validator.validate_root()
        if not root_decision.allowed:
            raise PermissionError(root_decision.reason)

        candidates: list[dict[str, Any]] = []

        try:
            for root_dir, dirs, files in os.walk(project_root, followlinks=False):
                # Filter directories in-place to avoid descending into skipped paths
                dirs[:] = [
                    d for d in dirs
                    if not validator.is_skipped_dir(Path(root_dir) / d)
                    and not validator.is_protected_path(Path(root_dir) / d)
                    and not (Path(root_dir) / d).is_symlink()
                    and not is_reparse_point(Path(root_dir) / d)
                ]

                for filename in files:
                    file_path = Path(root_dir) / filename
                    if file_path.is_symlink() or is_reparse_point(file_path):
                        continue

                    decision = validator.check_path(file_path)
                    if not decision.allowed or decision.protected or decision.skipped:
                        continue

                    suffix = file_path.suffix.lower()
                    if suffix not in SAFE_TEXT_SUFFIXES:
                        continue

                    try:
                        stat = file_path.stat()
                        size = stat.st_size
                    except Exception:
                        continue

                    if size > MAX_BYTES_PER_FILE or size == 0:
                        continue

                    # Quick binary check on first 512 bytes
                    try:
                        with open(file_path, "rb") as f:
                            header = f.read(512)
                            if b"\x00" in header:
                                continue
                    except Exception:
                        continue

                    rel_path = file_path.relative_to(project_root).as_posix()
                    category = CATEGORY_MAP.get(suffix, "Source / Text")

                    candidates.append({
                        "relativePath": rel_path,
                        "filename": filename,
                        "extension": suffix,
                        "sizeBytes": size,
                        "readable": True,
                        "category": category,
                    })

                    if len(candidates) >= MAX_CATALOG_CANDIDATES:
                        break
                if len(candidates) >= MAX_CATALOG_CANDIDATES:
                    break
        except Exception as exc:
            raise RuntimeError(f"Error scanning project files: {exc}") from exc

        candidates.sort(key=lambda c: c["relativePath"])
        return candidates

    def validate_safe_paths(
        self,
        project_name: str,
        relative_paths: list[str],
        *,
        max_files: int = 10,
        reject_dependency_files: bool = False,
        enforce_total_bytes_limit: bool = False,
        max_total_bytes: int = MAX_TOTAL_BYTES,
    ) -> list[dict[str, Any]]:
        """Validates relative paths strictly against registered project and security boundaries without returning full file content to untrusted callers."""
        clean_project = str(project_name or "").strip()
        if not clean_project:
            raise ValueError("projectName is required.")

        if not isinstance(relative_paths, list) or len(relative_paths) < 1:
            raise ValueError("At least 1 relative file path must be specified.")

        if len(relative_paths) > max_files:
            raise ValueError(f"Cannot select more than {max_files} files per execution.")

        proj = self.projects.get_project(clean_project)
        if not proj:
            raise KeyError(f"Registered project '{clean_project}' no longer found in registry.")

        project_root = Path(proj["path"]).expanduser().resolve()
        validator = WorkspaceBoundaryValidator(project_root, self.workspace_root)
        root_decision = validator.validate_root()
        if not root_decision.allowed:
            raise PermissionError(root_decision.reason)

        validated: list[dict[str, Any]] = []
        seen_paths: set[str] = set()
        total_bytes = 0

        for raw_path in relative_paths:
            if not isinstance(raw_path, str) or not raw_path.strip():
                raise ValueError("Empty or invalid relative path specified.")

            trimmed = raw_path.strip()

            # Reject absolute / UNC / drive-qualified forms before normalization
            if trimmed.startswith("/") or trimmed.startswith("\\"):
                raise PermissionError(f"Absolute or root-relative paths are not permitted: {raw_path}")
            if trimmed.startswith("//") or trimmed.startswith("\\\\"):
                raise PermissionError(f"UNC network paths are not permitted: {raw_path}")
            if bool(re.match(r"^[a-zA-Z]:", trimmed)):
                raise PermissionError(f"Drive-qualified paths are not permitted: {raw_path}")
            if Path(trimmed).is_absolute():
                raise PermissionError(f"Absolute paths are not permitted: {raw_path}")

            norm_rel = trimmed.replace("\\", "/")
            if ".." in norm_rel.split("/"):
                raise PermissionError(f"Directory traversal '..' not permitted: {raw_path}")

            if any(char in norm_rel for char in ("*", "?", "[", "]", ":")):
                raise ValueError(f"Glob patterns or invalid characters not permitted in paths: {raw_path}")

            if norm_rel in seen_paths:
                raise ValueError(f"Duplicate file path selected: '{norm_rel}'")
            seen_paths.add(norm_rel)

            target_path = (project_root / norm_rel).resolve()

            if not target_path.is_relative_to(project_root):
                raise PermissionError(f"File path escapes project root: {raw_path}")

            if not target_path.exists():
                raise FileNotFoundError(f"Selected file does not exist: {norm_rel}")

            if not target_path.is_file():
                raise ValueError(f"Selected path is not a regular file: {norm_rel}")

            if target_path.is_symlink():
                raise PermissionError(f"Symlinked files cannot be accessed: {norm_rel}")

            if is_reparse_point(target_path):
                raise PermissionError(f"Reparse/junction paths cannot be accessed: {norm_rel}")

            decision = validator.check_path(target_path)
            if not decision.allowed:
                raise PermissionError(f"Path not allowed by boundary policy: {norm_rel} ({decision.reason})")
            if decision.protected:
                raise PermissionError(f"Access to protected file is blocked: {norm_rel}")
            if decision.skipped:
                raise PermissionError(f"Access to runtime/cache directory is blocked: {norm_rel}")

            if reject_dependency_files and is_dependency_file(norm_rel):
                raise PermissionError(f"Dependency and package files cannot be modified in conservative mode: {norm_rel}")

            suffix = target_path.suffix.lower()
            if suffix not in SAFE_TEXT_SUFFIXES:
                raise PermissionError(f"File extension '{suffix}' is not permitted for safe text access: {norm_rel}")

            stat = target_path.stat()
            file_size = stat.st_size

            if file_size > MAX_BYTES_PER_FILE:
                raise ValueError(
                    f"File '{norm_rel}' exceeds size limit of {MAX_BYTES_PER_FILE} bytes ({file_size} bytes)."
                )

            raw = target_path.read_bytes()
            if b"\x00" in raw:
                raise ValueError(f"Binary file containing NUL bytes rejected: {norm_rel}")

            total_bytes += file_size
            if enforce_total_bytes_limit and total_bytes > max_total_bytes:
                raise ValueError(
                    f"Combined size of selected files ({total_bytes} bytes) exceeds limit of {max_total_bytes} bytes."
                )

            sha256 = hashlib.sha256(raw).hexdigest()
            category = CATEGORY_MAP.get(suffix, "Source / Text")

            validated.append({
                "relativePath": norm_rel,
                "filename": target_path.name,
                "extension": suffix,
                "sizeBytes": file_size,
                "sha256": sha256,
                "category": category,
                "_target_path": target_path,
                "_raw_bytes": raw,
            })

        return validated

    def read_text_files(
        self,
        project_name: str,
        relative_paths: list[str],
    ) -> dict[str, Any]:
        clean_project = str(project_name or "").strip()
        validated_files = self.validate_safe_paths(
            project_name=clean_project,
            relative_paths=relative_paths,
            max_files=MAX_FILES_PER_READ,
            reject_dependency_files=False,
            enforce_total_bytes_limit=True,
            max_total_bytes=MAX_TOTAL_BYTES,
        )

        read_files: list[dict[str, Any]] = []
        warnings: list[str] = []
        total_chars = 0

        # Read contents safely
        for item in validated_files:
            norm_rel = item["relativePath"]
            raw = item["_raw_bytes"]
            try:
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                content = raw.decode("utf-8", errors="replace")
                warnings.append(f"File '{norm_rel}' contained non-UTF-8 bytes replaced during decoding.")

            total_chars += len(content)
            if total_chars > MAX_RETURNED_CHARS:
                raise ValueError(
                    f"Combined character count exceeds maximum limit of {MAX_RETURNED_CHARS} characters."
                )

            line_count = len(content.splitlines())

            read_files.append({
                "relativePath": norm_rel,
                "sizeBytes": item["sizeBytes"],
                "lineCount": line_count,
                "sha256": item["sha256"],
                "content": content,
            })

        return {
            "executed": True,
            "actionType": "read_project_text_files",
            "toolId": "filesystem_tool",
            "projectName": clean_project,
            "totalFiles": len(read_files),
            "totalBytes": sum(f["sizeBytes"] for f in read_files),
            "files": read_files,
            "warnings": warnings,
            "limitations": [
                "Read-only bounded source reading from registered projects only.",
                "Protected files, runtime caches, dependencies, and binary files are blocked.",
                "Maximum 5 files and 256 KB total read limit per execution.",
                "Contents are ephemeral in session memory and not persisted into audit logs or databases.",
            ],
        }
