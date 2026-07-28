from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .file_data_agent import RUNTIME_SKIP_DIRS
from .knowledge import (
    MEDIA_TYPES,
    SENSITIVITY_VALUES,
    KnowledgeConflictError,
    KnowledgeNotFoundError,
    KnowledgeService,
    KnowledgeValidationError,
    deterministic_chunks,
    knowledge_content_hash,
    normalize_knowledge_content,
)
from .project_registry import ProjectRegistry
from .workspace_boundary import WorkspaceBoundaryValidator

MAX_REGISTERED_FILE_BYTES = 500_000
MAX_RELATIVE_PATH_LENGTH = 500
MAX_PREVIEW_CONTENT = 4_000
MAX_PREVIEW_CHUNKS = 5
_ALLOWED_EXTENSIONS = {".md": "text/markdown", ".txt": "text/plain", ".csv": "text/csv"}
_URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


class KnowledgeIngestionService:
    def __init__(
        self,
        knowledge: KnowledgeService,
        projects: ProjectRegistry,
        workspace_root: Path,
    ):
        self.knowledge = knowledge
        self.projects = projects
        self.workspace_root = workspace_root.resolve()

    def preview_paste(
        self, *, title: str, content: str, scope_type: str,
        scope_value: str | None, sensitivity: str, media_type: str,
        tags: list[str], private_session: bool,
    ) -> dict[str, Any]:
        normalized_title = self.knowledge.validate_title(title)
        normalized_scope_type, normalized_scope_value = self.knowledge.validate_scope(scope_type, scope_value)
        normalized_sensitivity = _choice("sensitivity", sensitivity, SENSITIVITY_VALUES)
        normalized_media_type = _choice("media type", media_type, MEDIA_TYPES)
        normalized_tags = self.knowledge.validate_tags(tags)
        normalized_content = normalize_knowledge_content(content, max_length=250_000)
        chunks = deterministic_chunks(normalized_content)
        return {
            "sourceType": "pasted_text",
            "title": normalized_title,
            "scopeType": normalized_scope_type,
            "scopeValue": normalized_scope_value,
            "sensitivity": normalized_sensitivity,
            "mediaType": normalized_media_type,
            "tags": normalized_tags,
            "contentHash": knowledge_content_hash(normalized_content),
            "characterCount": len(normalized_content),
            "chunkCount": len(chunks),
            "contentPreview": normalized_content[:MAX_PREVIEW_CONTENT],
            "contentPreviewTruncated": len(normalized_content) > MAX_PREVIEW_CONTENT,
            "chunkPreviews": _chunk_previews(chunks),
            "privateSession": bool(private_session),
            "importAllowed": not private_session,
            "persisted": False,
            "limitations": [
                "Preview is ephemeral and nothing was saved.",
                "Preview does not write SQLite, emit events, create an index, or invoke an agent.",
                "Import requires the exact preview hash and typed IMPORT confirmation.",
                "Private session allows pasted preview but blocks import.",
            ],
        }

    def import_paste(
        self, *, title: str, content: str, scope_type: str,
        scope_value: str | None, sensitivity: str, media_type: str,
        tags: list[str], expected_content_hash: str, confirmation: str,
        private_session: bool, actor: str = "local_user",
    ) -> dict[str, Any]:
        if private_session:
            raise KnowledgeConflictError("private session blocks persistent knowledge import")
        if confirmation != "IMPORT":
            raise KnowledgeValidationError("typed confirmation must be IMPORT")
        preview = self.preview_paste(
            title=title, content=content, scope_type=scope_type, scope_value=scope_value,
            sensitivity=sensitivity, media_type=media_type, tags=tags, private_session=False,
        )
        if preview["contentHash"] != expected_content_hash:
            raise KnowledgeConflictError("stale pasted-text preview; preview again before import")
        return self.knowledge.create_source(
            title=preview["title"], source_type="pasted_text",
            scope_type=preview["scopeType"], scope_value=preview["scopeValue"],
            sensitivity=preview["sensitivity"], media_type=preview["mediaType"],
            content=content, tags=preview["tags"], actor=actor,
        )

    def preview_project_file(
        self, *, project_name: str, relative_path: str,
        sensitivity: str, tags: list[str], private_session: bool,
    ) -> dict[str, Any]:
        if private_session:
            raise KnowledgeConflictError("private session blocks registered-project file reading")
        normalized_sensitivity = _choice("sensitivity", sensitivity, SENSITIVITY_VALUES)
        normalized_tags = self.knowledge.validate_tags(tags)
        file_data = self._read_registered_file(project_name, relative_path)
        return self._file_preview(file_data, normalized_sensitivity, normalized_tags)

    def import_project_file(
        self, *, project_name: str, relative_path: str,
        sensitivity: str, tags: list[str], expected_content_hash: str,
        expected_size_bytes: int, expected_modified_at: str,
        confirmation: str, private_session: bool, actor: str = "local_user",
    ) -> dict[str, Any]:
        if private_session:
            raise KnowledgeConflictError("private session blocks persistent knowledge import")
        if confirmation != "IMPORT":
            raise KnowledgeValidationError("typed confirmation must be IMPORT")
        normalized_sensitivity = _choice("sensitivity", sensitivity, SENSITIVITY_VALUES)
        normalized_tags = self.knowledge.validate_tags(tags)
        file_data = self._read_registered_file(project_name, relative_path)
        self._require_file_preview_match(
            file_data, expected_content_hash, expected_size_bytes, expected_modified_at,
            action="import",
        )
        return self.knowledge.create_source(
            title=file_data["filename"], source_type="registered_project_file",
            scope_type="project", scope_value=file_data["projectName"],
            sensitivity=normalized_sensitivity, media_type=file_data["mediaType"],
            content=file_data["content"], tags=normalized_tags,
            project_name=file_data["projectName"], relative_path=file_data["relativePath"],
            source_size_bytes=file_data["sizeBytes"],
            source_modified_at=file_data["sourceModifiedAt"], actor=actor,
        )

    def refresh_preview(self, source_id: str) -> dict[str, Any]:
        source = self.knowledge.get_source(source_id)
        if source["sourceType"] != "registered_project_file":
            raise KnowledgeValidationError("only registered-project files support refresh")
        file_data = self._read_registered_file(source["projectName"], source["relativePath"])
        preview = self._file_preview(file_data, source["sensitivity"], source["tags"])
        preview.update({
            "sourceId": source["sourceId"],
            "storedContentHash": source["contentHash"],
            "changeStatus": "unchanged" if file_data["contentHash"] == source["contentHash"] else "changed",
            "refreshAllowed": True,
        })
        return preview

    def refresh(
        self, source_id: str, *, expected_content_hash: str,
        expected_size_bytes: int, expected_modified_at: str,
        confirmation: str, actor: str = "local_user",
    ) -> dict[str, Any]:
        if confirmation != "REFRESH":
            raise KnowledgeValidationError("typed confirmation must be REFRESH")
        source = self.knowledge.get_source(source_id)
        if source["sourceType"] != "registered_project_file":
            raise KnowledgeValidationError("only registered-project files support refresh")
        file_data = self._read_registered_file(source["projectName"], source["relativePath"])
        self._require_file_preview_match(
            file_data, expected_content_hash, expected_size_bytes, expected_modified_at,
            action="refresh",
        )
        return self.knowledge.refresh_registered_source(
            source_id, content=file_data["content"],
            source_size_bytes=file_data["sizeBytes"],
            source_modified_at=file_data["sourceModifiedAt"], actor=actor,
        )

    def _read_registered_file(self, project_name: str, relative_path: str) -> dict[str, Any]:
        normalized_project = _required_text(project_name, 200, "project name")
        project = self.projects.get_project(normalized_project)
        if not project:
            raise KnowledgeNotFoundError("registered project not found")
        normalized_relative = _normalize_relative_path(relative_path)
        project_root = Path(str(project["path"])).expanduser().resolve()
        validator = WorkspaceBoundaryValidator(
            project_root, self.workspace_root, skip_dirs=RUNTIME_SKIP_DIRS
        )
        root_decision = validator.validate_root()
        if not root_decision.allowed:
            raise KnowledgeValidationError(root_decision.reason)
        parts = normalized_relative.split("/")
        traversed = project_root
        for part in parts:
            traversed = traversed / part
            try:
                if traversed.is_symlink():
                    raise KnowledgeValidationError("symlinked paths are not allowed")
            except OSError as exc:
                raise KnowledgeValidationError("file path could not be inspected safely") from exc
        candidate = project_root.joinpath(*parts)
        decision = validator.check_path(candidate)
        if not decision.allowed:
            raise KnowledgeValidationError(decision.reason)
        if not candidate.exists():
            raise KnowledgeNotFoundError("registered-project file not found")
        if candidate.is_dir() or not candidate.is_file():
            raise KnowledgeValidationError("relative path must identify exactly one file")
        extension = candidate.suffix.lower()
        media_type = _ALLOWED_EXTENSIONS.get(extension)
        if not media_type:
            raise KnowledgeValidationError("only .md, .txt, and .csv files are supported")
        try:
            stat_before = candidate.stat()
        except OSError as exc:
            raise KnowledgeValidationError("file metadata could not be read safely") from exc
        if stat_before.st_size > MAX_REGISTERED_FILE_BYTES:
            raise KnowledgeValidationError("registered-project file exceeds the 500000 byte limit")
        try:
            raw = candidate.read_bytes()
            stat_after = candidate.stat()
        except OSError as exc:
            raise KnowledgeValidationError("registered-project file could not be read safely") from exc
        if (
            stat_before.st_size != stat_after.st_size
            or stat_before.st_mtime_ns != stat_after.st_mtime_ns
        ):
            raise KnowledgeConflictError("registered-project file changed while it was being read; preview again")
        if len(raw) > MAX_REGISTERED_FILE_BYTES:
            raise KnowledgeValidationError("registered-project file exceeds the 500000 byte limit")
        if b"\x00" in raw:
            raise KnowledgeValidationError("binary files are not supported")
        try:
            decoded = raw.decode("utf-8-sig", errors="strict")
        except UnicodeDecodeError as exc:
            raise KnowledgeValidationError("registered-project file must be valid UTF-8") from exc
        controls = sum(1 for character in decoded if ord(character) < 32 and character not in "\t\n\r")
        if controls and controls / max(1, len(decoded)) > 0.01:
            raise KnowledgeValidationError("binary files are not supported")
        content = normalize_knowledge_content(decoded, max_length=500_000)
        chunks = deterministic_chunks(content)
        modified = datetime.fromtimestamp(stat_after.st_mtime, timezone.utc).isoformat()
        return {
            "projectName": normalized_project,
            "relativePath": normalized_relative,
            "filename": candidate.name,
            "mediaType": media_type,
            "sizeBytes": len(raw),
            "sourceModifiedAt": modified,
            "content": content,
            "contentHash": knowledge_content_hash(content),
            "characterCount": len(content),
            "chunks": chunks,
        }

    def _file_preview(
        self, file_data: dict[str, Any], sensitivity: str, tags: list[str]
    ) -> dict[str, Any]:
        content = file_data["content"]
        return {
            "sourceType": "registered_project_file",
            "title": file_data["filename"],
            "projectName": file_data["projectName"],
            "relativePath": file_data["relativePath"],
            "filename": file_data["filename"],
            "scopeType": "project",
            "scopeValue": file_data["projectName"],
            "sensitivity": sensitivity,
            "tags": tags,
            "mediaType": file_data["mediaType"],
            "sizeBytes": file_data["sizeBytes"],
            "sourceModifiedAt": file_data["sourceModifiedAt"],
            "contentHash": file_data["contentHash"],
            "characterCount": file_data["characterCount"],
            "chunkCount": len(file_data["chunks"]),
            "contentPreview": content[:MAX_PREVIEW_CONTENT],
            "contentPreviewTruncated": len(content) > MAX_PREVIEW_CONTENT,
            "chunkPreviews": _chunk_previews(file_data["chunks"]),
            "privateSession": False,
            "importAllowed": True,
            "persisted": False,
            "limitations": [
                "Preview is ephemeral and nothing was saved.",
                "Only this exact registered-project file was read; no directory enumeration or scan occurred.",
                "No absolute project path is returned or stored as source provenance.",
                "Import requires matching hash, byte size, modified timestamp, and typed IMPORT confirmation.",
            ],
        }

    def _require_file_preview_match(
        self, file_data: dict[str, Any], expected_content_hash: str,
        expected_size_bytes: int, expected_modified_at: str, *, action: str,
    ) -> None:
        if (
            file_data["contentHash"] != expected_content_hash
            or file_data["sizeBytes"] != expected_size_bytes
            or file_data["sourceModifiedAt"] != expected_modified_at
        ):
            raise KnowledgeConflictError(
                f"stale registered-project file preview; preview again before {action}"
            )


def _normalize_relative_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise KnowledgeValidationError("relative path is required")
    if len(value) > MAX_RELATIVE_PATH_LENGTH:
        raise KnowledgeValidationError("relative path exceeds the 500 character limit")
    if "\x00" in value:
        raise KnowledgeValidationError("relative path contains a NUL character")
    if value.startswith(("/", "\\")) or value.startswith("//") or value.startswith("\\\\"):
        raise KnowledgeValidationError("absolute and UNC paths are not allowed")
    if re.match(r"^[A-Za-z]:", value) or _URL_SCHEME.match(value):
        raise KnowledgeValidationError("drive-qualified paths and URL schemes are not allowed")
    if value.endswith(("/", "\\")):
        raise KnowledgeValidationError("relative path must not end with a directory separator")
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise KnowledgeValidationError("relative path contains an invalid path component")
    return "/".join(parts)


def _chunk_previews(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "chunkIndex": chunk["chunkIndex"],
            "contentHash": chunk["contentHash"],
            "charStart": chunk["charStart"],
            "charEnd": chunk["charEnd"],
            "content": chunk["content"],
        }
        for chunk in chunks[:MAX_PREVIEW_CHUNKS]
    ]


def _choice(label: str, value: Any, allowed: frozenset[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise KnowledgeValidationError(f"unsupported {label}")
    return value


def _required_text(value: Any, maximum: int, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeValidationError(f"{label} is required")
    normalized = value.strip()
    if len(normalized) > maximum:
        raise KnowledgeValidationError(f"{label} exceeds the {maximum} character limit")
    return normalized
