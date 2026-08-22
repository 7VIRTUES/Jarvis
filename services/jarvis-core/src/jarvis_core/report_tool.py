from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from .time_utils import utc_now


MAX_TITLE_CHARS = 160
MIN_TITLE_CHARS = 1
MAX_CONTENT_CHARS = 50_000
MIN_CONTENT_CHARS = 1

WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


class ReportTool:
    """Safe, non-destructive report generator writing exclusively new Markdown files to a fixed server-controlled root."""

    def __init__(self, reports_root: Path) -> None:
        self.reports_root = Path(reports_root).resolve()
        self.reports_root.mkdir(parents=True, exist_ok=True)

    def _sanitize_segment(self, text: str, max_len: int = 50) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(text or "").strip().lower())
        cleaned = re.sub(r"-+", "-", cleaned).strip("-._ ")
        if not cleaned:
            cleaned = "report"
        if cleaned.upper() in WINDOWS_RESERVED_NAMES:
            cleaned = f"rep-{cleaned}"
        return cleaned[:max_len].rstrip("-._ ")

    def _generate_filename(self, project_name: str, title: str) -> str:
        proj_part = self._sanitize_segment(project_name, 30) or "project"
        title_part = self._sanitize_segment(title, 50) or "report"
        unique_id = uuid4().hex[:8]
        return f"{proj_part}__{title_part}__{unique_id}.md"

    def create_markdown_report(
        self,
        *,
        project_name: str,
        title: str,
        content: str,
    ) -> dict[str, Any]:
        # 1. Validate title bounds
        clean_title = str(title or "").strip()
        if not (MIN_TITLE_CHARS <= len(clean_title) <= MAX_TITLE_CHARS):
            raise ValueError(f"Report title must be between {MIN_TITLE_CHARS} and {MAX_TITLE_CHARS} characters.")
        if "\x00" in clean_title:
            raise ValueError("Report title contains invalid NUL characters.")

        # 2. Validate content bounds
        if not isinstance(content, str) or not (MIN_CONTENT_CHARS <= len(content) <= MAX_CONTENT_CHARS):
            raise ValueError(f"Report content must be between {MIN_CONTENT_CHARS} and {MAX_CONTENT_CHARS} characters.")
        if "\x00" in content:
            raise ValueError("Report content contains invalid NUL characters.")

        clean_project = str(project_name or "").strip()
        if not clean_project:
            raise ValueError("project_name is required.")

        # 3. Generate sanitized unique filename
        filename = self._generate_filename(clean_project, clean_title)
        candidate_path = (self.reports_root / filename).resolve()

        # 4. Enforce fixed output root containment
        if not candidate_path.is_relative_to(self.reports_root) or candidate_path.parent != self.reports_root:
            raise PermissionError("Report path escapes fixed Jarvis reports directory.")

        # 5. Exclusive creation (no overwrite guarantee)
        written = False
        try:
            with open(candidate_path, mode="x", encoding="utf-8") as f:
                f.write(content)
            written = True
        except FileExistsError:
            # Fallback with fresh unique ID
            filename = self._generate_filename(clean_project, clean_title)
            candidate_path = (self.reports_root / filename).resolve()
            if not candidate_path.is_relative_to(self.reports_root) or candidate_path.parent != self.reports_root:
                raise PermissionError("Report path escapes fixed Jarvis reports directory.")
            with open(candidate_path, mode="x", encoding="utf-8") as f:
                f.write(content)
            written = True
        except Exception:
            if candidate_path.exists() and not written:
                try:
                    candidate_path.unlink()
                except Exception:
                    pass
            raise

        char_count = len(content)
        byte_count = len(content.encode("utf-8"))
        relative_path = str(Path("assistant") / filename)

        return {
            "filename": filename,
            "relativeReportPath": relative_path,
            "fullPath": str(candidate_path),
            "charCount": char_count,
            "byteCount": byte_count,
            "createdAt": utc_now(),
            "title": clean_title,
            "projectName": clean_project,
            "overwrite": False,
        }
