from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from .permissions import is_protected_path

AGENT_ID = "evidence_report_center_agent"
AGENT_NAME = "Evidence Report Center"
MODE = "local_report_metadata_only"
ALLOWED_EXTENSIONS = {".md", ".json"}
MARKDOWN_INDEX_CHAR_LIMIT = 16 * 1024
MARKDOWN_DETAIL_CHAR_LIMIT = 64 * 1024
JSON_CHAR_LIMIT = 256 * 1024
SUMMARY_CHAR_LIMIT = 500
SECRET_KEYWORDS = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "api_key", "secret_key", "access_token", "refresh_token", "private_key", "client_secret", "password", "passwd", "token"]
ASSIGNMENT_VALUE_RE = re.compile(r"(?P<key>\b(?:" + "|".join(re.escape(k) for k in SECRET_KEYWORDS) + r")\b\s*(?:=|:)\s*)(?P<quote>['\"]?)(?P<value>[^'\"\s,#;]+)", re.IGNORECASE)
SENSITIVE_MARKDOWN_HEADINGS = {
    "evidence",
    "findings",
    "logs",
    "notes",
    "raw evidence",
    "raw findings",
    "raw logs",
    "raw notes",
}
SENSITIVE_LINE_KEYS = {
    "evidence",
    "finding",
    "findings",
    "log",
    "logs",
    "note",
    "notes",
    "raw",
    "raw evidence",
    "raw log",
    "raw notes",
}
TOKEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{12,}\b", re.IGNORECASE), "Bearer <redacted>"),
    (re.compile(r"\bghp_[A-Za-z0-9_]{12,}\b"), "<redacted-token>"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{12,}\b"), "<redacted-token>"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"), "<redacted-token>"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL), "<redacted-private-key>"),
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

class EvidenceReportCenterService:
    def __init__(self, reports_root: Path):
        self.reports_root = reports_root

    def index_reports(self) -> dict[str, Any]:
        root = self.reports_root.resolve()
        reports: list[dict[str, Any]] = []
        warnings: list[str] = []
        if self.reports_root.exists() and self.reports_root.is_dir():
            for path in sorted(self.reports_root.iterdir(), key=lambda item: item.name.lower()):
                metadata = self._metadata_for_candidate(path, root)
                if not metadata:
                    continue
                reports.append(metadata)
                if metadata["reportType"] in {"markdown_report", "json_report"}:
                    warnings.append(f"Unknown report type inferred for {metadata['filename']}.")
                if metadata.get("blockedReason"):
                    warnings.append(f"{metadata['filename']} is not readable: {metadata['blockedReason']}.")
        counts: dict[str, int] = {}
        for report in reports:
            counts[str(report["reportType"])] = counts.get(str(report["reportType"]), 0) + 1
        return {"generatedAt": self._now(), "reportsRoot": "jarvis_reports_directory", "totalReports": len(reports), "reportCountsByType": dict(sorted(counts.items())), "reports": reports, "warnings": warnings, "limitations": self._limitations(), "localOnly": True, "uploads": False, "externalServices": False, "commandExecution": False, "fileDeletion": False, "certification": False}

    def dashboard_summary(self) -> dict[str, Any]:
        index = self.index_reports()
        return {"agentId": AGENT_ID, "agentName": AGENT_NAME, "status": "implemented_local_only", "mode": MODE, "totalReports": index["totalReports"], "reportCountsByType": index["reportCountsByType"], "recentReports": index["reports"][:10], "warningCount": len(index["warnings"]), "endpoints": {"index": "/evidence/reports", "detailPattern": "/evidence/reports/{report_id}", "metadataPattern": "/evidence/reports/{report_id}/metadata"}, "localOnly": True, "uploads": False, "externalServices": False, "commandExecution": False, "fileDeletion": False, "arbitraryFilesystemBrowsing": False, "protectedSecretReads": False, "certification": False}

    def get_report_metadata(self, report_id: str) -> dict[str, Any]:
        path = self._validated_report_path(report_id)
        metadata = self._metadata_for_candidate(path, self.reports_root.resolve())
        if not metadata:
            raise FileNotFoundError("report not found")
        return metadata

    def get_report_detail(self, report_id: str) -> dict[str, Any]:
        metadata = self.get_report_metadata(report_id)
        if not metadata["readable"]:
            return {"reportId": metadata["reportId"], "filename": metadata["filename"], "reportType": metadata["reportType"], "contentType": None, "readable": False, "blockedReason": metadata["blockedReason"], "metadata": metadata}
        path = self._validated_report_path(report_id)
        if path.suffix.lower() == ".json":
            return {"reportId": metadata["reportId"], "filename": metadata["filename"], "reportType": metadata["reportType"], "contentType": "application/json", "readable": True, "metadataOnly": True, "metadata": metadata}
        return {"reportId": metadata["reportId"], "filename": metadata["filename"], "reportType": metadata["reportType"], "contentType": "text/markdown", "readable": True, "redacted": True, "content": self._safe_markdown_detail(metadata), "metadata": metadata}

    def _metadata_for_candidate(self, path: Path, root: Path) -> dict[str, Any] | None:
        if not self._candidate_allowed(path, root):
            return None
        resolved = path.resolve()
        stat = resolved.stat()
        metadata: dict[str, Any] = {"reportId": resolved.name, "filename": resolved.name, "reportType": self._report_type(resolved.name), "title": resolved.stem, "createdOrModifiedAt": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(), "sizeBytes": stat.st_size, "extension": resolved.suffix.lower(), "safeDetailEndpoint": f"/evidence/reports/{resolved.name}", "summary": "", "warningCount": None, "findingCount": None, "verdict": None, "status": None, "redacted": "unknown", "readable": True, "blockedReason": None}
        if resolved.suffix.lower() == ".md":
            self._apply_markdown_metadata(resolved, metadata)
        else:
            self._apply_json_metadata(resolved, metadata)
        return metadata

    def _candidate_allowed(self, path: Path, root: Path) -> bool:
        name = path.name
        if name.startswith(".") or name.endswith(("~", ".bak", ".tmp", ".temp", ".log", ".db", ".sqlite", ".sqlite3")):
            return False
        try:
            resolved = path.resolve(strict=True)
        except OSError:
            return False
        if not resolved.is_file() or not resolved.is_relative_to(root) or is_protected_path(resolved):
            return False
        return resolved.suffix.lower() in ALLOWED_EXTENSIONS

    def _validated_report_path(self, report_id: str) -> Path:
        decoded = unquote(report_id).strip()
        relative = Path(decoded.replace("\\", "/"))
        if not decoded or decoded != report_id or relative.is_absolute() or len(relative.parts) != 1 or ".." in relative.parts or relative.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise PermissionError("report id must be a single Markdown or JSON report filename")
        root = self.reports_root.resolve()
        candidate = (root / relative.name).resolve()
        if not candidate.is_relative_to(root) or is_protected_path(candidate):
            raise PermissionError("report path is outside the approved reports directory")
        if not candidate.exists() or not candidate.is_file():
            raise FileNotFoundError("report not found")
        return candidate

    def _apply_markdown_metadata(self, path: Path, metadata: dict[str, Any]) -> None:
        if path.stat().st_size > MARKDOWN_DETAIL_CHAR_LIMIT:
            metadata["readable"] = False
            metadata["blockedReason"] = "size_limit"
            return
        text = self._read_text_prefix(path, MARKDOWN_INDEX_CHAR_LIMIT)
        metadata["title"] = self._extract_heading(text) or metadata["title"]
        fields = self._extract_markdown_fields(text)
        metadata["summary"] = self._summary_from_text(text)
        metadata["warningCount"] = self._count_heading_items(text, "warnings")
        metadata["findingCount"] = self._markdown_finding_count(text)
        metadata["verdict"] = fields.get("verdict") or fields.get("overall verdict")
        metadata["status"] = fields.get("status") or fields.get("verdict/status")
        metadata["redacted"] = self._redacted_status(text)

    def _apply_json_metadata(self, path: Path, metadata: dict[str, Any]) -> None:
        if path.stat().st_size > JSON_CHAR_LIMIT:
            metadata["readable"] = False
            metadata["blockedReason"] = "size_limit"
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            metadata["readable"] = False
            metadata["blockedReason"] = "invalid_json"
            return
        if not isinstance(data, dict):
            metadata["readable"] = False
            metadata["blockedReason"] = "unsupported_json_shape"
            return
        summary = self._safe_json_summary(data)
        metadata["title"] = str(summary.get("title") or summary.get("agentId") or summary.get("bundleId") or metadata["title"])
        metadata["summary"] = self._redact_text(json.dumps(summary, sort_keys=True))
        metadata["warningCount"] = summary.get("warningCount")
        metadata["findingCount"] = summary.get("findingCount")
        metadata["verdict"] = summary.get("verdict") or summary.get("overallVerdict")
        metadata["status"] = summary.get("status")
        metadata["redacted"] = self._json_redacted_status(data)

    def _safe_markdown_detail(self, metadata: dict[str, Any]) -> str:
        lines = [
            f"# {metadata['title']}",
            "",
            f"- Report ID: {metadata['reportId']}",
            f"- Report type: {metadata['reportType']}",
            f"- File extension: {metadata['extension']}",
            f"- Size bytes: {metadata['sizeBytes']}",
            f"- Modified at: {metadata['createdOrModifiedAt']}",
            f"- Readable: {metadata['readable']}",
            f"- Redacted: {metadata['redacted']}",
        ]
        for key, label in [("status", "Status"), ("verdict", "Verdict"), ("warningCount", "Warning count"), ("findingCount", "Finding count")]:
            value = metadata.get(key)
            if value is not None:
                lines.append(f"- {label}: {self._redact_text(str(value))}")
        lines.extend(
            [
                "",
                "## Safe Summary",
                metadata.get("summary") or "No safe summary available.",
                "",
                "## Detail Boundary",
                "Raw findings, notes, evidence, logs, protected contents, and secret-like values are omitted from this detail view.",
            ]
        )
        return "\n".join(lines)
    def _read_text_prefix(self, path: Path, limit: int) -> str:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)

    def _report_type(self, filename: str) -> str:
        lowered = filename.lower()
        if lowered.startswith("security-safety-") and lowered.endswith(".md"):
            return "security_safety_review"
        if (lowered.startswith("validation-") or lowered.startswith("validation-run-")) and lowered.endswith(".md"):
            return "validation_report"
        if lowered.startswith("private-alpha-readiness-") and lowered.endswith(".md"):
            return "private_alpha_readiness_snapshot"
        if lowered.startswith("diagnostics-bundle-") and lowered.endswith((".md", ".json")):
            return "redacted_diagnostics_bundle"
        return "markdown_report" if lowered.endswith(".md") else "json_report"

    def _extract_heading(self, text: str) -> str | None:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return self._redact_text(stripped.lstrip("#").strip())
        return None

    def _extract_markdown_fields(self, text: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        lines = text.splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip().strip("-").strip()
            key = value = None
            if ":" in stripped:
                left, right = stripped.split(":", 1)
                key = left.strip().lower()
                value = right.strip()
            elif stripped.startswith("## "):
                key = stripped[3:].strip().lower()
                value = lines[index + 1].strip() if index + 1 < len(lines) else ""
            if key in {"verdict", "status", "generated at", "agent", "report id", "overall verdict", "verdict/status"} and value:
                fields[key] = self._redact_text(value)
        return fields

    def _summary_from_text(self, text: str) -> str:
        lines: list[str] = []
        in_sensitive_section = False
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("```"):
                continue
            if line.startswith("#"):
                in_sensitive_section = self._heading_name(line) in SENSITIVE_MARKDOWN_HEADINGS
                if in_sensitive_section:
                    continue
            if in_sensitive_section or self._line_is_sensitive_report_content(line):
                continue
            lines.append(line)
            if len(" ".join(lines)) >= SUMMARY_CHAR_LIMIT:
                break
        return self._redact_text(" ".join(lines))[:SUMMARY_CHAR_LIMIT]

    def _heading_name(self, line: str) -> str:
        return line.lstrip("#").strip().lower()

    def _line_is_sensitive_report_content(self, line: str) -> bool:
        normalized = line.lstrip("-*0123456789. ").strip()
        if ":" not in normalized:
            return False
        key = normalized.split(":", 1)[0].strip().lower()
        return key in SENSITIVE_LINE_KEYS
    def _count_heading_items(self, text: str, heading: str) -> int | None:
        lines = text.splitlines()
        in_section = False
        count = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## "):
                in_section = stripped[3:].strip().lower() == heading.lower()
                continue
            if in_section and stripped.startswith("- ") and "none recorded" not in stripped.lower():
                count += 1
        return count if count else None

    def _markdown_finding_count(self, text: str) -> int | None:
        match = re.search(r'"matchedCount"\s*:\s*(\d+)|"findingCount"\s*:\s*(\d+)', text)
        return int(next(value for value in match.groups() if value is not None)) if match else None

    def _safe_json_summary(self, data: dict[str, Any]) -> dict[str, Any]:
        warnings = data.get("warnings") if isinstance(data.get("warnings"), list) else None
        findings = data.get("findings") if isinstance(data.get("findings"), list) else None
        summary: dict[str, Any] = {}
        for key in ["agentId", "agentName", "verdict", "overallVerdict", "status", "bundleId", "snapshotId", "runId", "generatedAt", "reportId"]:
            if key in data and not isinstance(data[key], (dict, list)):
                summary[key] = self._redact_value(data[key])
        if isinstance(data.get("summary"), dict):
            for key in ["localOnly", "uploaded", "commandExecution", "externalServices", "certification", "warningCount"]:
                if key in data["summary"] and not isinstance(data["summary"][key], (dict, list)):
                    summary[key] = self._redact_value(data["summary"][key])
        if warnings is not None:
            summary["warningCount"] = len(warnings)
        if findings is not None:
            summary["findingCount"] = len(findings)
        return summary

    def _redacted_status(self, text: str) -> bool | str:
        if "redacted" in text.lower():
            return True
        return True if self._redact_text(text) != " ".join(text.replace("\x00", "").split()) else "unknown"

    def _json_redacted_status(self, data: dict[str, Any]) -> bool | str:
        redaction = data.get("redactionSummary")
        return True if isinstance(redaction, dict) and redaction.get("rawSecretValuesIncluded") is False else "unknown"

    def _redact_value(self, value: Any) -> Any:
        return self._redact_text(value) if isinstance(value, str) else value

    def _redact_text(self, text: str) -> str:
        redacted = ASSIGNMENT_VALUE_RE.sub(lambda match: f"{match.group('key')}{match.group('quote')}<redacted>", text)
        for pattern, replacement in TOKEN_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        for pattern, replacement in PRIVATE_PATH_PATTERNS:
            redacted = pattern.sub(replacement, redacted)
        if ".env" in redacted.lower() and ("=" in redacted or ":" in redacted):
            redacted = re.sub(r"(?im)^.*\.env.*(?:=|:).*$", "<redacted-env-like-line>", redacted)
        return " ".join(redacted.replace("\x00", "").split())

    def _limitations(self) -> list[str]:
        return [
            "Indexes only allowed Markdown and JSON report files directly under the Jarvis reports directory.",
            "Reads bounded snippets for metadata and redacted Markdown detail only.",
            "JSON detail returns safe metadata only, not the raw full report body.",
            "Does not upload, send, share, edit, delete, rewrite, certify, or scan arbitrary folders.",
        ]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


