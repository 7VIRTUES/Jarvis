from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .permissions import is_protected_path


def load_json_config(path: Path, required_fields: set[str] | None = None) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    if is_protected_path(resolved):
        raise PermissionError("protected config paths cannot be read")
    if not resolved.exists() or not resolved.is_file():
        raise FileNotFoundError(str(resolved))
    with resolved.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("config root must be a JSON object")
    missing = (required_fields or set()) - set(data)
    if missing:
        raise ValueError(f"missing required fields: {', '.join(sorted(missing))}")
    return data

