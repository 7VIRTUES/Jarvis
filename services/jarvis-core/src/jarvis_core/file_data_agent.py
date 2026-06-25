from __future__ import annotations

from pathlib import Path
from typing import Any

from .project_registry import ProjectRegistry
from .workspace_boundary import DEFAULT_RUNTIME_SKIP_DIRS, PROTECTED_FILE_PATTERNS, WorkspaceBoundaryValidator


AGENT_ID = "file_data_agent"
STATUS = "local_only"
MODE = "registered_project_metadata_only"
MAX_SCANNED_FILES = 5000
MAX_DOC_PREVIEW_BYTES = 32_000
DOC_PREVIEW_CHARS = 400
EXTRA_RUNTIME_SKIP_DIRS = [".jarvis", ".next", ".expo", "coverage"]
RUNTIME_SKIP_DIRS = sorted(set(DEFAULT_RUNTIME_SKIP_DIRS + EXTRA_RUNTIME_SKIP_DIRS))


class FileDataAgentService:
    def __init__(self, projects: ProjectRegistry, workspace_root: Path):
        self.projects = projects
        self.workspace_root = workspace_root.resolve()

    def local_summary(self, project_name: str) -> dict[str, Any]:
        project_name = project_name.strip()
        if not project_name:
            raise ValueError("projectName is required")
        project = self.projects.get_project(project_name)
        if not project:
            raise KeyError(f"registered project not found: {project_name}")

        project_root = Path(str(project["path"])).expanduser().resolve()
        validator = WorkspaceBoundaryValidator(project_root, self.workspace_root, skip_dirs=RUNTIME_SKIP_DIRS)
        root_decision = validator.validate_root()
        if not root_decision.allowed:
            raise PermissionError(root_decision.reason)

        scan = _scan_project(project_root, validator)
        docs = _safe_docs_metadata(project_root, validator)
        warnings = _warnings(scan)
        return {
            "agentId": AGENT_ID,
            "status": STATUS,
            "mode": MODE,
            "projectName": str(project["name"]),
            "projectRoot": str(project_root),
            "scannedFiles": scan["scannedFiles"],
            "skippedFiles": scan["skippedFiles"],
            "skippedDirs": scan["skippedDirs"],
            "skippedDirList": scan["skippedDirList"],
            "protectedSkippedFiles": scan["protectedSkippedFiles"],
            "runtimeSkippedDirs": scan["runtimeSkippedDirs"],
            "fileTypeCounts": scan["fileTypeCounts"],
            "docsDetected": docs,
            "protectedPatternsActive": True,
            "protectedPatterns": list(PROTECTED_FILE_PATTERNS),
            "runtimeSkipDirs": list(RUNTIME_SKIP_DIRS),
            "warnings": warnings,
            "limitations": [
                "Registered projects only; raw arbitrary paths are not accepted.",
                "Metadata scan is bounded and skips runtime, dependency, cache, and protected paths.",
                "Only README.md and direct docs/*.md previews may be read, and only when safe and small.",
                "No full file contents, secret contents, external uploads, shell execution, or file mutation are performed.",
            ],
            "safety": file_data_safety(),
        }

    def dashboard_summary(self) -> dict[str, Any]:
        return file_data_dashboard_summary()


def file_data_dashboard_summary() -> dict[str, Any]:
    return {
        "agentId": AGENT_ID,
        "name": "File/Data Agent",
        "status": "implemented_local_only",
        "mode": MODE,
        "endpoint": "/agents/files/local-summary",
        "registeredProjectsOnly": True,
        "rawPathInputAccepted": False,
        "protectedPatternsActive": True,
        "runtimeSkipDirs": list(RUNTIME_SKIP_DIRS),
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "shellExecution": False,
        "fileMutation": False,
        "uploads": False,
        "accountAccess": False,
        "limitations": ["safe local metadata only", "bounded README/direct docs previews only"],
    }


def file_data_safety() -> dict[str, bool]:
    return {
        "localOnly": True,
        "registeredProjectsOnly": True,
        "rawPathInputAccepted": False,
        "externalServices": False,
        "paidApis": False,
        "webBrowsing": False,
        "connectorExecution": False,
        "shellExecution": False,
        "fileMutation": False,
        "uploads": False,
        "oauth": False,
        "accountAccess": False,
    }


def _scan_project(project_root: Path, validator: WorkspaceBoundaryValidator) -> dict[str, Any]:
    scanned_files = 0
    skipped_files = 0
    skipped_dirs = 0
    protected_skipped_files = 0
    runtime_skipped_dirs = 0
    skipped_dir_list: list[str] = []
    file_type_counts: dict[str, int] = {}
    stack = [project_root]
    scan_limit_hit = False

    while stack:
        directory = stack.pop()
        try:
            entries = sorted(directory.iterdir(), key=lambda path: path.name.lower())
        except OSError:
            skipped_dirs += 1
            relative = _relative_or_root(project_root, directory)
            skipped_dir_list.append(relative)
            continue

        for entry in entries:
            if entry.is_symlink():
                if _looks_like_dir(entry):
                    skipped_dirs += 1
                    skipped_dir_list.append(_relative_or_root(project_root, entry))
                else:
                    skipped_files += 1
                continue

            decision = validator.check_path(entry)
            if not decision.allowed:
                if entry.is_dir():
                    skipped_dirs += 1
                    if decision.skipped:
                        runtime_skipped_dirs += 1
                    if decision.relative_path:
                        skipped_dir_list.append(decision.relative_path)
                else:
                    skipped_files += 1
                    if decision.protected:
                        protected_skipped_files += 1
                continue

            if entry.is_dir():
                stack.append(entry)
                continue
            if not entry.is_file():
                skipped_files += 1
                continue

            scanned_files += 1
            extension = entry.suffix.lower() or "[no_extension]"
            file_type_counts[extension] = file_type_counts.get(extension, 0) + 1
            if scanned_files >= MAX_SCANNED_FILES:
                scan_limit_hit = True
                stack.clear()
                break

    return {
        "scannedFiles": scanned_files,
        "skippedFiles": skipped_files,
        "skippedDirs": skipped_dirs,
        "skippedDirList": sorted(set(skipped_dir_list))[:50],
        "protectedSkippedFiles": protected_skipped_files,
        "runtimeSkippedDirs": runtime_skipped_dirs,
        "fileTypeCounts": dict(sorted(file_type_counts.items())),
        "scanLimitHit": scan_limit_hit,
    }


def _safe_docs_metadata(project_root: Path, validator: WorkspaceBoundaryValidator) -> list[dict[str, Any]]:
    candidates = [project_root / "README.md"]
    docs_root = project_root / "docs"
    if docs_root.exists() and docs_root.is_dir():
        try:
            candidates.extend(path for path in sorted(docs_root.glob("*.md"), key=lambda item: item.name.lower()) if path.is_file())
        except OSError:
            pass

    docs: list[dict[str, Any]] = []
    for path in candidates:
        decision = validator.check_path(path)
        if not decision.allowed or not path.exists() or not path.is_file():
            continue
        try:
            size_bytes = path.stat().st_size
        except OSError:
            continue
        metadata: dict[str, Any] = {
            "relativePath": decision.relative_path,
            "filename": path.name,
            "sizeBytes": size_bytes,
            "previewAvailable": False,
        }
        if size_bytes <= MAX_DOC_PREVIEW_BYTES:
            preview = _read_bounded_preview(path)
            if preview:
                metadata["title"] = _extract_title(preview, path.stem)
                metadata["preview"] = preview[:DOC_PREVIEW_CHARS]
                metadata["previewAvailable"] = True
        else:
            metadata["warning"] = "file too large for bounded preview"
        docs.append(metadata)
    return docs[:25]


def _read_bounded_preview(path: Path) -> str:
    try:
        raw = path.read_bytes()[:MAX_DOC_PREVIEW_BYTES]
    except OSError:
        return ""
    if b"\x00" in raw:
        return ""
    return raw.decode("utf-8", errors="replace").strip()


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned.startswith("#"):
            return cleaned.lstrip("#").strip() or fallback
    return fallback


def _warnings(scan: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if scan["protectedSkippedFiles"]:
        warnings.append("Protected file patterns were detected and skipped.")
    if scan["runtimeSkippedDirs"]:
        warnings.append("Runtime, dependency, cache, or build directories were skipped.")
    if scan["scanLimitHit"]:
        warnings.append("Metadata scan stopped at the configured file count limit.")
    return warnings


def _looks_like_dir(path: Path) -> bool:
    try:
        return path.is_dir()
    except OSError:
        return False


def _relative_or_root(project_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(project_root)).replace("\\", "/") or "."
    except ValueError:
        return "."
