from __future__ import annotations

import json

import pytest

from prompt_lab import lessons
from prompt_lab.lessons import LessonError, load_cases, load_prompt, normalize_lesson


def test_all_lesson_cases_load() -> None:
    expected_counts = {
        "01": (2, 2),
        "02": (2, 2),
        "03": (2, 2),
        "04": (2, 2),
        "05": (2, 2),
        "06": (2, 2),
        "07": (5, 5),
        "08": (2, 2),
        "09": (15, 20),
        "10": (5, 5),
    }
    for lesson, counts in expected_counts.items():
        assert len(load_cases(lesson, "visible")) == counts[0]
        assert len(load_cases(lesson, "holdout")) == counts[1]


def test_normalizes_lesson_number() -> None:
    assert normalize_lesson("1") == "01"
    assert normalize_lesson("10") == "10"
    with pytest.raises(LessonError):
        normalize_lesson("11")


def test_loads_labeled_message_prompt() -> None:
    prompt = load_prompt("08", "solution_messages.json")
    rendered = prompt.render("Operation: test\nAPPROVED: T-1")
    assert [message["role"] for message in rendered] == [
        "system",
        "user",
        "assistant",
        "user",
        "assistant",
        "user",
    ]
    assert "{{INPUT}}" not in json.dumps(rendered)
    assert "APPROVED: T-1" in rendered[-1]["content"]


def test_prompt_requires_exactly_one_marker(tmp_path, monkeypatch) -> None:
    root = tmp_path / "practice" / "01_zero_shot"
    (root / "prompts").mkdir(parents=True)
    (root / "prompts" / "attempt_01.txt").write_text("No marker", encoding="utf-8")
    monkeypatch.setattr(lessons, "PROJECT_ROOT", tmp_path)
    with pytest.raises(LessonError, match="exactly one"):
        load_prompt("01")


def test_message_prompt_rejects_invalid_role(tmp_path, monkeypatch) -> None:
    root = tmp_path / "practice" / "08_labeled_conversations"
    root.mkdir(parents=True)
    path = root / "bad.json"
    path.write_text('[{"role":"tool","content":"{{INPUT}}"}]', encoding="utf-8")
    monkeypatch.setattr(lessons, "PROJECT_ROOT", tmp_path)
    with pytest.raises(LessonError, match="Invalid role"):
        load_prompt("08", str(path))

