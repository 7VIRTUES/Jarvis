from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .permissions import is_protected_path


AGENT_ID = "docs_runbook_center_agent"
AGENT_NAME = "Docs/Runbook Center"
MODE = "local_docs_metadata_only"
INDEX_CHAR_LIMIT = 16 * 1024
DETAIL_CHAR_LIMIT = 64 * 1024
SUMMARY_CHAR_LIMIT = 500
SECRET_KEYWORDS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "api_key",
    "secret_key",
    "access_token",
    "refresh_token",
    "private_key",
    "client_secret",
    "password",
    "passwd",
    "token",
]
ASSIGNMENT_VALUE_RE = re.compile(
    r"(?P<key>\b(?:" + "|".join(re.escape(k) for k in SECRET_KEYWORDS) + r")\b\s*(?:=|:)\s*)(?P<quote>['\"]?)(?P<value>[^'\"\s,#;]+)",
    re.IGNORECASE,
)
TOKEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{12,}\b", re.IGNORECASE), "Bearer <redacted>"),
    (re.compile(r"\bghp_[A-Za-z0-9_]{12,}\b"), "<redacted-token>"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{12,}\b"), "<redacted-token>"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"), "<redacted-token>"),
    (re.compile(r"\b(?=[A-Za-z0-9_]{32,}\b)(?=[A-Za-z0-9_]*\d)[A-Za-z0-9_]{32,}\b"), "<redacted-token>"),
]
PRIVATE_PATH_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"C:\\Users\\[^\\\s\"')]+(?:\\[^\\\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    (re.compile("C:" + r"/Users/[^/\s\"')]+(?:/[^/\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    (re.compile(r"OneDrive\s+-\s+[^\\/\"\r\n]+", re.IGNORECASE), "<redacted-org-path>"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\b"), "<redacted-email>"),
    (re.compile(r"/home/[^/\s\"')]+(?:/[^\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
    (re.compile(r"/Users/[^/\s\"')]+(?:/[^\s\"')]+)*", re.IGNORECASE), "<redacted-user-path>"),
]


class DocsCenterService:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.docs_root = workspace_root / "docs"

    def index_docs(self) -> dict[str, Any]:
        docs = [metadata for path in self._candidate_paths() if (metadata := self._metadata_for_path(path))]
        counts: dict[str, int] = {}
        for doc in docs:
            counts[doc["category"]] = counts.get(doc["category"], 0) + 1
        recent = sorted(docs, key=lambda doc: str(doc["modifiedAt"]), reverse=True)[:10]
        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "mode": MODE,
            "totalDocs": len(docs),
            "countsByCategory": dict(sorted(counts.items())),
            "recentDocs": recent,
            "docs": docs,
            "localOnly": True,
            "arbitraryFilesystemBrowsing": False,
            "docMutation": False,
            "externalServices": False,
            "uploads": False,
            "certification": False,
        }

    def dashboard_summary(self) -> dict[str, Any]:
        index = self.index_docs()
        return {
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "status": "implemented_local_only",
            "mode": MODE,
            "totalDocs": index["totalDocs"],
            "countsByCategory": index["countsByCategory"],
            "recentDocs": index["recentDocs"],
            "endpoints": {
                "index": "/docs/index",
                "detailPattern": "/docs/{doc_id}",
                "metadataPattern": "/docs/{doc_id}/metadata",
            },
            "localOnly": True,
            "docMutation": False,
            "externalServices": False,
            "uploads": False,
            "certification": False,
        }

    def get_doc_metadata(self, doc_id: str) -> dict[str, Any]:
        path = self._validated_doc_path(doc_id)
        metadata = self._metadata_for_path(path)
        if not metadata:
            raise FileNotFoundError("doc not found")
        return metadata

    def get_doc_detail(self, doc_id: str) -> dict[str, Any]:
        metadata = self.get_doc_metadata(doc_id)
        if not metadata["readable"]:
            return {
                "docId": metadata["docId"],
                "filename": metadata["filename"],
                "readable": False,
                "blockedReason": metadata["blockedReason"],
                "metadata": metadata,
            }
        path = self._validated_doc_path(doc_id)
        return {
            "docId": metadata["docId"],
            "filename": metadata["filename"],
            "contentType": "text/markdown",
            "readable": True,
            "redacted": True,
            "content": self._redact_text(self._read_text_prefix(path, DETAIL_CHAR_LIMIT)),
            "metadata": metadata,
        }

    def _candidate_paths(self) -> list[Path]:
        candidates = [self.workspace_root / "README.md"]
        if self.docs_root.exists() and self.docs_root.is_dir():
            candidates.extend(sorted(self.docs_root.glob("*.md"), key=lambda path: path.name.lower()))
        return candidates

    def _metadata_for_path(self, path: Path) -> dict[str, Any] | None:
        allowed_root = self.workspace_root.resolve() if path.name == "README.md" else self.docs_root.resolve()
        if not self._candidate_allowed(path, allowed_root):
            return None
        resolved = path.resolve(strict=True)
        stat = resolved.stat()
        doc_id = resolved.name
        category = self._category_for(resolved.name)
        metadata: dict[str, Any] = {
            "docId": doc_id,
            "filename": resolved.name,
            "title": resolved.stem,
            "category": category,
            "sizeBytes": stat.st_size,
            "modifiedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            "summary": "",
            "detailEndpoint": f"/docs/{doc_id}",
            "metadataEndpoint": f"/docs/{doc_id}/metadata",
            "readable": True,
            "blockedReason": None,
            "redacted": True,
        }
        if stat.st_size > DETAIL_CHAR_LIMIT:
            metadata["readable"] = False
            metadata["blockedReason"] = "size_limit"
            return metadata
        text = self._read_text_prefix(resolved, INDEX_CHAR_LIMIT)
        metadata["title"] = self._extract_title(text) or metadata["title"]
        metadata["summary"] = self._summary_from_text(text)
        return metadata

    def _candidate_allowed(self, path: Path, allowed_root: Path) -> bool:
        name = path.name
        if name.startswith(".") or name.endswith(("~", ".bak", ".tmp", ".temp")) or path.suffix.lower() != ".md":
            return False
        try:
            resolved = path.resolve(strict=True)
        except OSError:
            return False
        if not resolved.is_file() or not resolved.is_relative_to(allowed_root) or is_protected_path(resolved):
            return False
        if allowed_root == self.docs_root.resolve() and resolved.parent != allowed_root:
            return False
        return True

    def _validated_doc_path(self, doc_id: str) -> Path:
        decoded = unquote(doc_id).strip()
        relative = Path(decoded.replace("\\", "/"))
        if (
            not decoded
            or decoded != doc_id
            or relative.is_absolute()
            or len(relative.parts) != 1
            or ".." in relative.parts
            or relative.suffix.lower() != ".md"
        ):
            raise PermissionError("doc id must be a single Markdown filename")
        candidates = [self.workspace_root / "README.md", self.docs_root / relative.name]
        for candidate in candidates:
            if candidate.name != relative.name:
                continue
            allowed_root = self.workspace_root.resolve() if candidate.name == "README.md" else self.docs_root.resolve()
            try:
                resolved = candidate.resolve(strict=True)
            except OSError:
                continue
            if not resolved.is_relative_to(allowed_root):
                raise PermissionError("doc path is outside the approved docs directory")
            if resolved.is_file() and not is_protected_path(resolved):
                if allowed_root == self.docs_root.resolve() and resolved.parent != allowed_root:
                    raise PermissionError("doc path is outside the approved docs directory")
                return resolved
        raise FileNotFoundError("doc not found")

    def _read_text_prefix(self, path: Path, limit: int) -> str:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)

    def _extract_title(self, text: str) -> str | None:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return self._redact_text(stripped.lstrip("#").strip())
        return None

    def _summary_from_text(self, text: str) -> str:
        lines: list[str] = []
        in_code_block = False
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if line.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block or not line or line.startswith("#"):
                continue
            lines.append(line)
            if len(" ".join(lines)) >= SUMMARY_CHAR_LIMIT:
                break
        return self._redact_text(" ".join(lines))[:SUMMARY_CHAR_LIMIT]

    def _category_for(self, filename: str) -> str:
        lowered = filename.lower()
        if lowered == "readme.md":
            return "README"
        category_keywords = [
            ("safety", ["safety", "security", "public-repo"]),
            ("workflow", ["workflow", "coding-agent", "codex", "task"]),
            ("validation", ["validation", "test-plan", "vm-"]),
            ("diagnostics", ["diagnostics", "redacted"]),
            ("evidence", ["evidence"]),
            ("manifest", ["manifest"]),
            ("project profile", ["project-profile", "profile"]),
            ("packaging/readiness", ["packaging", "readiness", "private-alpha", "first-run"]),
            ("architecture", ["architecture", "scope", "roadmap"]),
        ]
        for category, keywords in category_keywords:
            if any(keyword in lowered for keyword in keywords):
                return category
        return "other"

    def _redact_text(self, text: str) -> str:
        redacted = ASSIGNMENT_VALUE_RE.sub(lambda match: f"{match.group('key')}{match.group('quote')}<redacted>", text)
        for pattern, replacement in TOKEN_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        for pattern, replacement in PRIVATE_PATH_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return " ".join(redacted.replace("\x00", "").split())
