from __future__ import annotations

import ast
import json
from pathlib import Path

from prompt_lab.config import PROJECT_ROOT
from prompt_lab.lessons import LESSON_DIRS, load_cases, lesson_path, load_prompt


def test_every_lesson_has_common_files() -> None:
    required = {
        "README.md",
        "task.md",
        "starter_prompt.txt",
        "solution_prompt.txt",
        "cases/visible.json",
        "cases/holdout.json",
        "prompts/attempt_01.txt",
    }
    for lesson in LESSON_DIRS:
        root = lesson_path(lesson)
        assert all((root / relative).is_file() for relative in required)
        load_prompt(lesson)


def test_lesson_seven_covers_all_formats() -> None:
    for split in ("visible", "holdout"):
        assert {case.format for case in load_cases("07", split)} == {
            "json",
            "csv",
            "tsv",
            "pipe",
            "markdown",
        }


def test_public_meeting_expected_rows_have_eight_tsv_fields() -> None:
    for split in ("visible", "holdout"):
        for case in load_cases("09", split):
            for row in case.expected.splitlines():
                assert len(row.split("\t")) == 8, case.id


def test_no_active_branding_or_absolute_local_paths() -> None:
    forbidden = ["Acc" + "enture", "/" + "Users/", "Hacker" + "Rank"]
    suffixes = {".py", ".md", ".toml", ".txt", ".json"}
    for path in PROJECT_ROOT.rglob("*"):
        if path.is_file() and path.suffix in suffixes and ".pytest_cache" not in path.parts:
            content = path.read_text(encoding="utf-8")
            for value in forbidden:
                assert value not in content, f"{value!r} found in {path}"


def test_active_python_avoids_dangerous_calls_and_cloud_clients() -> None:
    for root_name in ("prompt_lab", "scripts"):
        for path in (PROJECT_ROOT / root_name).rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            assert "api.openai.com" not in source
            assert "import openai" not in source.lower()
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    assert node.func.id not in {"eval", "exec"}
                for keyword in getattr(node, "keywords", []):
                    assert not (keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True)


def test_fixture_json_has_unique_ids_and_no_real_contact_patterns() -> None:
    for lesson in LESSON_DIRS:
        for split in ("visible", "holdout"):
            path = lesson_path(lesson) / "cases" / f"{split}.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            ids = [case["id"] for case in data["cases"]]
            assert len(ids) == len(set(ids))
            text = path.read_text(encoding="utf-8")
            if "@" in text:
                assert "@example.com" in text

