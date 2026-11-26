from __future__ import annotations

import ast
import json
from pathlib import Path
import re

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


def test_public_meeting_natural_tier_shape() -> None:
    visible = load_cases("09", "visible")
    holdout = load_cases("09", "holdout")
    visible_natural = [case for case in visible if case.id.startswith("visible_natural_")]
    holdout_natural = [case for case in holdout if case.id.startswith("holdout_natural_")]
    holdout_long = [case for case in holdout if case.id.startswith("holdout_long_")]
    assert len(visible_natural) == 5
    assert len(holdout_natural) == 7
    assert len(holdout_long) == 3

    for case in [*visible_natural, *holdout_natural, *holdout_long]:
        assert "My issue is" not in case.input
        assert "I request" not in case.input

    for case in visible_natural + holdout_natural:
        assert 150 <= len(case.input.split()) <= 400

    for case in holdout_long:
        assert 1_000 <= len(case.input.split()) <= 2_500
        assert 10 <= len(re.findall(r"(?m)^[A-Z][A-Z ]*:", case.input)) <= 20
        assert 4 <= len(case.expected.splitlines()) <= 7


def test_public_meeting_normalization_examples() -> None:
    cases = {case.id: case for split in ("visible", "holdout") for case in load_cases("09", split)}
    assert "\trequest a pedestrian signal\t" in cases["visible_01"].expected
    assert "\tconsider a weekend bus lane\t\t" in cases["visible_06"].expected
    assert "\t\tinspect the site\tFriday" in cases["visible_07"].expected
    for case in cases.values():
        for row in case.expected.splitlines():
            if not row:
                continue
            fields = row.split("\t")
            assert not fields[5].lower().startswith(("i ", "we "))
            assert not fields[6].lower().startswith(("i ", "we ", "will ", "shall "))
            assert not fields[7].lower().startswith(("by ", "on ", "before "))


def test_task_files_define_requirements_without_deferring_to_solution() -> None:
    for lesson in LESSON_DIRS:
        task = (lesson_path(lesson) / "task.md").read_text(encoding="utf-8")
        assert "solution prompt" not in task.lower()

    structured = (lesson_path("07") / "task.md").read_text(encoding="utf-8")
    for requirement in ("JSON", "CSV", "TSV", "PIPE", "MARKDOWN", "terminal newline"):
        assert requirement in structured

    meeting = (lesson_path("09") / "task.md").read_text(encoding="utf-8")
    for requirement in ("literal TAB", "exactly eight fields", "no header", "terminal newline", "position_or_request", "commitment", "deadline"):
        assert requirement in meeting


def test_no_active_branding_or_absolute_local_paths() -> None:
    forbidden = ["Acc" + "enture", "/" + "Users/", "Hacker" + "Rank"]
    suffixes = {".py", ".md", ".toml", ".txt", ".json"}
    for path in PROJECT_ROOT.rglob("*"):
        if path.is_file() and path.suffix in suffixes and ".pytest_cache" not in path.parts:
            content = path.read_text(encoding="utf-8")
            for value in forbidden:
                assert value not in content, f"{value!r} found in {path}"

    notes = PROJECT_ROOT.parent / "PROMPT_ENGINEERING_NOTES.md"
    assert notes.is_file()
    assert not (PROJECT_ROOT.parent / "questions.md").exists()
    notes_text = notes.read_text(encoding="utf-8")
    for value in forbidden:
        assert value not in notes_text


def test_github_actions_runs_offline_suite() -> None:
    workflow = PROJECT_ROOT.parents[1] / ".github" / "workflows" / "prompt-engineering-lab.yml"
    content = workflow.read_text(encoding="utf-8")
    assert "actions/checkout@v7" in content
    assert "actions/setup-python@v7" in content
    assert "python-version: \"3.12\"" in content
    assert "pytest -q" in content
    assert "ollama" not in content.lower()


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

