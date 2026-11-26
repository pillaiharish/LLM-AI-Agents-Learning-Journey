from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from .config import PROJECT_ROOT


FIELDS = [
    "timestamp_utc",
    "lesson",
    "model",
    "prompt_file",
    "temperature",
    "visible_passed",
    "visible_total",
    "holdout_passed",
    "holdout_total",
    "exact_match_rate",
    "latency_ms",
    "prompt_tokens",
    "completion_tokens",
]


def record_history(row: dict[str, object], path: Path | None = None) -> None:
    history_path = path or PROJECT_ROOT / "runs" / "history.csv"
    history_path.parent.mkdir(parents=True, exist_ok=True)
    exists = history_path.exists()
    safe_row = {field: row.get(field, "") for field in FIELDS}
    safe_row["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    with history_path.open("a", encoding="utf-8", newline="") as history_file:
        writer = csv.DictWriter(history_file, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow(safe_row)

