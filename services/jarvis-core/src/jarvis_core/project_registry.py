from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .permissions import is_protected_path


class ProjectRegistry:
    def __init__(self, conn: sqlite3.Connection, allowed_root: Path):
        self.conn = conn
        self.allowed_root = allowed_root.resolve()

    def _validate_path(self, path: Path | str) -> Path:
        resolved = Path(path).expanduser().resolve()
        if not resolved.exists() or not resolved.is_dir():
            raise ValueError("project path is missing or is not a directory")
        if not resolved.is_relative_to(self.allowed_root):
            raise ValueError("project path must stay inside the allowed workspace root")
        if is_protected_path(resolved):
            raise PermissionError("protected paths cannot be registered")
        return resolved

    def add_project(self, name: str, path: Path | str) -> dict[str, Any]:
        if not name.strip():
            raise ValueError("project name is required")
        resolved = self._validate_path(path)
        self.conn.execute(
            "insert into projects (name, path) values (?, ?) on conflict(name) do update set path=excluded.path",
            (name, str(resolved)),
        )
        self.conn.commit()
        return {"name": name, "path": str(resolved)}

    def list_projects(self) -> list[dict[str, Any]]:
        rows = self.conn.execute("select name, path, created_at from projects order by name").fetchall()
        return [{"name": row[0], "path": row[1], "createdAt": row[2]} for row in rows]

    def get_project(self, name: str) -> dict[str, Any] | None:
        row = self.conn.execute("select name, path, created_at from projects where name = ?", (name,)).fetchone()
        if not row:
            return None
        return {"name": row[0], "path": row[1], "createdAt": row[2]}
