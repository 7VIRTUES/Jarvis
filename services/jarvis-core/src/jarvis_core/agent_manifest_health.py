from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote


AGENT_ID = "agent_manifest_health_agent"
AGENT_NAME = "Agent Manifest Health Center"
MODE = "local_manifest_metadata_only"
REQUIRED_COMMON_FIELDS = {"id", "name", "implemented", "defaultEnabled"}
REQUIRED_AGENT_FIELDS = REQUIRED_COMMON_FIELDS | {"mode", "purpose", "capabilities"}
REQUIRED_PLACEHOLDER_FIELDS = {"id", "implemented", "defaultEnabled"}
SAFETY_BOOLEAN_FIELDS = [
    "uploads",
    "externalServices",
    "commandExecution",
    "gitWrites",
    "fileDeletion",
    "protectedSecretReads",
]
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


class AgentManifestHealthService:
    def __init__(self, connector_root: Path):
        self.connector_root = connector_root
        self.agent_root = connector_root / "agents"
        self.placeholder_root = connector_root / "placeholders"

    def manifest_health(self) -> dict[str, Any]:
        manifests = self._load_manifests()
        warning_count = sum(len(item["warnings"]) for item in manifests)
        implemented_local_agents = [
            item
            for item in manifests
            if item["manifestType"] == "agent" and item["implemented"] is True and item["localOnly"] is True
        ]
        disabled_placeholders = [
            item
            for item in manifests
            if item["manifestType"] == "placeholder" and item["implemented"] is False and item["defaultEnabled"] is False
        ]
        flagged = [item for item in manifests if item["warnings"]]
        return {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "mode": MODE,
            "totalManifests": len(manifests),
            "implementedLocalAgents": len(implemented_local_agents),
            "disabledPlaceholders": len(disabled_placeholders),
            "warningCount": warning_count,
            "manifests": manifests,
            "flaggedManifests": flagged[:10],
            "localOnly": True,
            "arbitraryFilesystemBrowsing": False,
            "manifestMutation": False,
            "connectorMutation": False,
            "commandExecution": False,
            "externalServices": False,
            "uploads": False,
        }

    def dashboard_summary(self) -> dict[str, Any]:
        health = self.manifest_health()
        return {
            "agentId": AGENT_ID,
            "agentName": AGENT_NAME,
            "status": "implemented_local_only",
            "mode": MODE,
            "totalManifests": health["totalManifests"],
            "implementedLocalAgents": health["implementedLocalAgents"],
            "disabledPlaceholders": health["disabledPlaceholders"],
            "warningCount": health["warningCount"],
            "recentOrFlaggedManifests": (health["flaggedManifests"] or health["manifests"])[:10],
            "endpoints": {
                "index": "/agents/manifest-health",
                "detailPattern": "/agents/manifest-health/{manifest_id}",
            },
            "localOnly": True,
            "manifestMutation": False,
            "connectorMutation": False,
            "commandExecution": False,
            "externalServices": False,
            "uploads": False,
        }

    def manifest_detail(self, manifest_id: str) -> dict[str, Any]:
        safe_id = self._validate_manifest_id(manifest_id)
        for manifest in self._load_manifests():
            if manifest["manifestId"] == safe_id:
                return manifest
        raise FileNotFoundError("manifest not found")

    def _load_manifests(self) -> list[dict[str, Any]]:
        manifests: list[dict[str, Any]] = []
        for manifest_type, root in [("agent", self.agent_root), ("placeholder", self.placeholder_root)]:
            if not root.exists() or not root.is_dir():
                continue
            root_resolved = root.resolve()
            for path in sorted(root.glob("*.json"), key=lambda item: item.name.lower()):
                manifests.append(self._manifest_metadata(path, root_resolved, manifest_type))
        return manifests

    def _manifest_metadata(self, path: Path, root: Path, manifest_type: str) -> dict[str, Any]:
        resolved = path.resolve()
        if not resolved.is_file() or not resolved.is_relative_to(root):
            return self._blocked_metadata(path.name, manifest_type, "manifest path escaped allowed directory")
        try:
            data = json.loads(resolved.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return self._blocked_metadata(path.name, manifest_type, "unknown JSON shape")
        if not isinstance(data, dict):
            return self._blocked_metadata(path.name, manifest_type, "unknown JSON shape")
        return self._safe_metadata(path.name, manifest_type, data)

    def _safe_metadata(self, filename: str, manifest_type: str, data: dict[str, Any]) -> dict[str, Any]:
        warnings: list[str] = []
        required = REQUIRED_AGENT_FIELDS if manifest_type == "agent" else REQUIRED_PLACEHOLDER_FIELDS
        missing = sorted(field for field in required if field not in data)
        if missing:
            warnings.append(f"missing required fields: {', '.join(missing)}")
        implemented = data.get("implemented")
        default_enabled = data.get("defaultEnabled")
        if manifest_type == "placeholder" and (implemented is not False or default_enabled is not False):
            warnings.append("future connector placeholder must remain implemented=false and defaultEnabled=false")
        if manifest_type == "agent" and implemented is True:
            unsafe = [field for field in SAFETY_BOOLEAN_FIELDS if data.get(field) is not False]
            if unsafe:
                warnings.append(f"implemented local agent missing false safety booleans: {', '.join(unsafe)}")
        if not data.get("safetyNotes") and not data.get("notes"):
            warnings.append("missing safety notes")
        safe_id = self._redact_text(str(data.get("id") or Path(filename).stem))
        summary = {
            "id": safe_id,
            "name": self._redact_text(str(data.get("name") or data.get("provider") or safe_id)),
            "purpose": self._redact_text(str(data.get("purpose") or data.get("notes") or ""))[:500],
            "readinessLevel": self._redact_text(str(data.get("readinessLevel") or "")),
        }
        return {
            "manifestId": filename,
            "filename": filename,
            "manifestType": manifest_type,
            "id": safe_id,
            "name": summary["name"],
            "implemented": implemented,
            "defaultEnabled": default_enabled,
            "mode": self._redact_text(str(data.get("mode") or "")),
            "readinessLevel": summary["readinessLevel"],
            "localOnly": manifest_type == "agent" and implemented is True and str(data.get("mode", "")).lower() in {"local_only", "local"},
            "capabilityCount": len(data.get("capabilities", [])) if isinstance(data.get("capabilities"), list) else None,
            "safetyBooleanStatus": {field: data.get(field) for field in SAFETY_BOOLEAN_FIELDS if field in data},
            "summary": summary,
            "warnings": warnings,
            "warningCount": len(warnings),
            "redacted": True,
        }

    def _blocked_metadata(self, filename: str, manifest_type: str, warning: str) -> dict[str, Any]:
        return {
            "manifestId": filename,
            "filename": filename,
            "manifestType": manifest_type,
            "id": Path(filename).stem,
            "name": Path(filename).stem,
            "implemented": None,
            "defaultEnabled": None,
            "mode": "",
            "readinessLevel": "",
            "localOnly": False,
            "capabilityCount": None,
            "safetyBooleanStatus": {},
            "summary": {},
            "warnings": [warning],
            "warningCount": 1,
            "redacted": True,
        }

    def _validate_manifest_id(self, manifest_id: str) -> str:
        decoded = unquote(manifest_id).strip()
        relative = Path(decoded.replace("\\", "/"))
        if (
            not decoded
            or decoded != manifest_id
            or relative.is_absolute()
            or len(relative.parts) != 1
            or ".." in relative.parts
            or relative.suffix.lower() != ".json"
        ):
            raise PermissionError("manifest id must be a single JSON manifest filename")
        return relative.name

    def _redact_text(self, text: str) -> str:
        redacted = ASSIGNMENT_VALUE_RE.sub(lambda match: f"{match.group('key')}{match.group('quote')}<redacted>", text)
        for pattern, replacement in TOKEN_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        return " ".join(redacted.replace("\x00", "").split())
