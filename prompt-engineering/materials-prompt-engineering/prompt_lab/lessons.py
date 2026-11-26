from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from .config import PROJECT_ROOT


INPUT_MARKER = "{{INPUT}}"
VALID_ROLES = {"system", "user", "assistant"}
VALID_FORMATS = {"text", "json", "csv", "tsv", "pipe", "markdown"}
LESSON_DIRS = {
    "01": "01_zero_shot",
    "02": "02_few_shot",
    "03": "03_delimiters",
    "04": "04_numbered_steps",
    "05": "05_role_prompts",
    "06": "06_reasoning_scaffolds",
    "07": "07_structured_output",
    "08": "08_labeled_conversations",
    "09": "09_public_meeting_extraction",
    "10": "10_adversarial_evaluation",
}


class LessonError(ValueError):
    """Raised when lesson content is missing or malformed."""


@dataclass(frozen=True)
class Case:
    id: str
    input: str
    expected: str
    format: str
    columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class PromptTemplate:
    path: Path
    messages: tuple[dict[str, str], ...]

    def render(self, case_input: str) -> list[dict[str, str]]:
        return [
            {"role": message["role"], "content": message["content"].replace(INPUT_MARKER, case_input)}
            for message in self.messages
        ]


def normalize_lesson(value: str) -> str:
    try:
        normalized = f"{int(value):02d}"
    except ValueError as exc:
        raise LessonError(f"Invalid lesson: {value}") from exc
    if normalized not in LESSON_DIRS:
        raise LessonError(f"Unknown lesson: {value}")
    return normalized


def lesson_path(lesson: str) -> Path:
    normalized = normalize_lesson(lesson)
    return PROJECT_ROOT / "practice" / LESSON_DIRS[normalized]


def load_cases(lesson: str, split: str) -> list[Case]:
    if split not in {"visible", "holdout"}:
        raise LessonError(f"Unknown split: {split}")
    path = lesson_path(lesson) / "cases" / f"{split}.json"
    try:
        raw_cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise LessonError(f"Cannot load cases from {path}: {exc}") from exc
    cases: list[Case] = []
    seen: set[str] = set()
    for raw in raw_cases:
        try:
            case = Case(
                id=str(raw["id"]),
                input=str(raw["input"]),
                expected=str(raw["expected"]),
                format=str(raw.get("format", "text")),
                columns=tuple(str(column) for column in raw.get("columns", [])),
            )
        except (TypeError, KeyError) as exc:
            raise LessonError(f"Malformed case in {path}: {exc}") from exc
        if case.id in seen or case.format not in VALID_FORMATS:
            raise LessonError(f"Invalid or duplicate case {case.id!r} in {path}")
        seen.add(case.id)
        cases.append(case)
    if not cases:
        raise LessonError(f"No cases found in {path}")
    return cases


def find_case(lesson: str, case_id: str) -> tuple[str, Case]:
    for split in ("visible", "holdout"):
        for case in load_cases(lesson, split):
            if case.id == case_id:
                return split, case
    raise LessonError(f"Case {case_id!r} does not exist in lesson {normalize_lesson(lesson)}")


def load_prompt(lesson: str, prompt: str | None = None) -> PromptTemplate:
    root = lesson_path(lesson)
    if prompt is None:
        path = root / "prompts" / "attempt_01.txt"
    else:
        candidate = Path(prompt).expanduser()
        if candidate.is_absolute() or candidate.exists():
            path = candidate
        elif (root / "prompts" / candidate).exists():
            path = root / "prompts" / candidate
        else:
            path = root / candidate
    try:
        if path.suffix == ".json":
            raw_messages = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw_messages, list):
                raise LessonError(f"Message prompt must be a JSON array: {path}")
            messages = tuple(_validate_message(message, path) for message in raw_messages)
        else:
            messages = ({"role": "user", "content": path.read_text(encoding="utf-8")},)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        if isinstance(exc, LessonError):
            raise
        raise LessonError(f"Cannot load prompt {path}: {exc}") from exc
    marker_count = sum(message["content"].count(INPUT_MARKER) for message in messages)
    if marker_count != 1:
        raise LessonError(f"Prompt must contain exactly one {INPUT_MARKER}; found {marker_count}")
    return PromptTemplate(path=path, messages=messages)


def _validate_message(message: object, path: Path) -> dict[str, str]:
    if not isinstance(message, dict):
        raise LessonError(f"Each message in {path} must be an object")
    role = message.get("role")
    content = message.get("content")
    if role not in VALID_ROLES or not isinstance(content, str):
        raise LessonError(f"Invalid role or content in {path}")
    return {"role": role, "content": content}

