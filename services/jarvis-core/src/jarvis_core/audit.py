from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonlLogger:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def append(self, log_name: str, event: dict[str, Any]) -> Path:
        if log_name not in {"actions", "commands", "security"}:
            raise ValueError(f"unsupported log: {log_name}")
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **event,
        }
        path = self.root / f"{log_name}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
        return path

