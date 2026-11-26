from __future__ import annotations

import csv

from prompt_lab.history import FIELDS, record_history
from prompt_lab.practice import build_practice


def test_history_contains_only_aggregate_fields(tmp_path) -> None:
    path = tmp_path / "history.csv"
    record_history(
        {
            "lesson": "01",
            "model": "local-model",
            "prompt_file": "attempt_01.txt",
            "temperature": 0,
            "visible_passed": 1,
            "visible_total": 2,
            "exact_match_rate": "0.5000",
            "source_input": "must not be recorded",
            "model_output": "must not be recorded",
        },
        path,
    )
    with path.open(newline="", encoding="utf-8") as history_file:
        rows = list(csv.DictReader(history_file))
    assert list(rows[0]) == FIELDS
    assert rows[0]["lesson"] == "01"
    assert "must not be recorded" not in path.read_text(encoding="utf-8")


def test_practice_selection_is_deterministic() -> None:
    assert build_practice(42) == build_practice(42)
    parts = build_practice(42)
    assert len(parts) == 4
    assert sum(part.minutes for part in parts) == 55
    assert parts[2].lesson == "09"

