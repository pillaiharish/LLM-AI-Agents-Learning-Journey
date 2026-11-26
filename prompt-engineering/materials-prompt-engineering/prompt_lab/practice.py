from __future__ import annotations

from dataclasses import dataclass
import random

from .lessons import load_cases


@dataclass(frozen=True)
class PracticePart:
    minutes: int
    lesson: str
    case_id: str
    goal: str


def build_practice(seed: int) -> list[PracticePart]:
    rng = random.Random(seed)
    first_lesson = rng.choice(["01", "02"])
    second_lesson = rng.choice(["03", "07"])
    first_case = rng.choice(load_cases(first_lesson, "visible")).id
    second_case = rng.choice(load_cases(second_lesson, "visible")).id
    meeting_cases = [
        case for case in load_cases("09", "visible")
        if case.id.startswith("visible_natural_")
    ]
    meeting_case = rng.choice(meeting_cases).id
    return [
        PracticePart(10, first_lesson, first_case, "Write a clear zero-shot or few-shot prompt"),
        PracticePart(15, second_lesson, second_case, "Enforce input boundaries and an exact output contract"),
        PracticePart(20, "09", meeting_case, "Extract supported public-meeting facts as exact TSV"),
        PracticePart(10, "09", meeting_case, "Review failures, revise the prompt, and rerun"),
    ]

