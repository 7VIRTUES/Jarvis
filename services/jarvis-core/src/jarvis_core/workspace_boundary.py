from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path


PROTECTED_FILE_PATTERNS = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
    "service-account*.json",
    "firebase-adminsdk*",
    "supabase-service-role*",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.log",
]

DEFAULT_RUNTIME_SKIP_DIRS = [
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "tmp",
    ".jarvis/logs",
    ".jarvis/runtime",
]

SAFE_METADATA_FILES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "README.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
}

SAFE_TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

MAX_SAFE_TEXT_BYTES = 1_000_000


@dataclass(frozen=True)
class BoundaryDecision:
    allowed: bool
    status: str
    reason: str
    path: str
    relative_path: str | None = None
    protected: bool = False
    skipped: bool = False


class WorkspaceBoundaryValidator:
    def __init__(self, project_root: Path | str, allowed_root: Path | str | None = None, skip_dirs: list[str] | None = None):
        self.allowed_root = Path(allowed_root).expanduser().resolve() if allowed_root is not None else None
        self.project_root = Path(project_root).expanduser().resolve()
        self.skip_dirs = [self._normalize_relative(skip_dir) for skip_dir in (skip_dirs or DEFAULT_RUNTIME_SKIP_DIRS)]

    def validate_root(self) -> BoundaryDecision:
        if not self.project_root.exists() or not self.project_root.is_dir():
            return self._decision(False, "blocked", "project root is missing or is not a directory", self.project_root)
        if self.allowed_root is not None and not self.project_root.is_relative_to(self.allowed_root):
            return self._decision(False, "blocked", "project root must stay inside the allowed workspace root", self.project_root)
        if self.is_protected_path(self.project_root):
            return self._decision(False, "blocked", "protected paths cannot be used as project roots", self.project_root, protected=True)
        return self._decision(True, "allowed", "project root is inside the allowed boundary", self.project_root, "")

    def check_path(self, candidate: Path | str, allow_protected: bool = False) -> BoundaryDecision:
        raw = Path(candidate)
        path = (self.project_root / raw).resolve() if not raw.is_absolute() else raw.expanduser().resolve()
        if not path.is_relative_to(self.project_root):
            return self._decision(False, "blocked", "path escapes the project root after resolution", path)
        relative = self.relative_path(path)
        if self.is_runtime_or_cache_path(path):
            return self._decision(False, "skipped", "path is in a runtime/cache/dependency directory", path, relative, skipped=True)
        protected = self.is_protected_path(path)
        if protected and not allow_protected:
            return self._decision(False, "blocked", "protected file contents must not be read", path, relative, protected=True)
        return self._decision(True, "allowed", "path is inside the project boundary", path, relative, protected=protected)

    def safe_to_read_metadata(self, candidate: Path | str) -> BoundaryDecision:
        decision = self.check_path(candidate)
        if not decision.allowed:
            return decision
        name = Path(decision.relative_path or "").name
        relative = (decision.relative_path or "").replace("\\", "/")
        if name in SAFE_METADATA_FILES or relative in {
            "docs/public-repo-readiness.md",
            "docs/public-safety-boundaries.md",
        }:
            return decision
        return self._decision(False, "skipped", "path is not an approved metadata file", Path(decision.path), decision.relative_path)

    def safe_to_scan_text(self, candidate: Path | str) -> BoundaryDecision:
        decision = self.check_path(candidate)
        if not decision.allowed:
            return decision
        path = Path(decision.path)
        if path.suffix.lower() not in SAFE_TEXT_SUFFIXES:
            return self._decision(False, "skipped", "file extension is not part of the safe text scan set", path, decision.relative_path, skipped=True)
        try:
            if path.stat().st_size > MAX_SAFE_TEXT_BYTES:
                return self._decision(False, "skipped", "file is too large for normal text scanning", path, decision.relative_path, skipped=True)
            sample = path.read_bytes()[:4096]
        except OSError:
            return self._decision(False, "skipped", "file could not be sampled safely", path, decision.relative_path, skipped=True)
        if b"\x00" in sample:
            return self._decision(False, "skipped", "file appears to be binary", path, decision.relative_path, skipped=True)
        return decision

    def is_runtime_or_cache_path(self, candidate: Path | str) -> bool:
        path = Path(candidate).expanduser().resolve()
        if not path.is_relative_to(self.project_root):
            return False
        relative = self._normalize_relative(self.relative_path(path))
        parts = relative.split("/") if relative else []
        for skip_dir in self.skip_dirs:
            skip_parts = skip_dir.split("/")
            if parts[: len(skip_parts)] == skip_parts:
                return True
        return False

    def is_protected_path(self, candidate: Path | str) -> bool:
        path = Path(candidate)
        normalized = str(path).replace("\\", "/").lower()
        name = path.name.lower()
        return any(fnmatch.fnmatch(name, pattern.lower()) or fnmatch.fnmatch(normalized, pattern.lower()) for pattern in PROTECTED_FILE_PATTERNS)

    def relative_path(self, candidate: Path | str) -> str:
        return str(Path(candidate).resolve().relative_to(self.project_root)).replace("\\", "/")

    def _decision(
        self,
        allowed: bool,
        status: str,
        reason: str,
        path: Path,
        relative_path: str | None = None,
        protected: bool = False,
        skipped: bool = False,
    ) -> BoundaryDecision:
        return BoundaryDecision(
            allowed=allowed,
            status=status,
            reason=reason,
            path=str(path),
            relative_path=relative_path,
            protected=protected,
            skipped=skipped,
        )

    def _normalize_relative(self, path: str | Path) -> str:
        return str(path).replace("\\", "/").strip("/")
