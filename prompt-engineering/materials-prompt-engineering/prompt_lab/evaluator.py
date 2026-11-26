from __future__ import annotations

from dataclasses import dataclass

from .diagnostics import diagnose
from .lessons import Case, PromptTemplate
from .provider import ChatProvider, ChatResult


@dataclass(frozen=True)
class Evaluation:
    case: Case
    result: ChatResult
    passed: bool
    diagnostics: tuple[str, ...]


def exact_match(actual: str, expected: str) -> bool:
    return actual == expected


def evaluate_case(
    provider: ChatProvider,
    prompt: PromptTemplate,
    case: Case,
) -> Evaluation:
    result = provider.chat(prompt.render(case.input))
    passed = exact_match(result.content, case.expected)
    findings = () if passed else tuple(diagnose(result.content, case))
    return Evaluation(case=case, result=result, passed=passed, diagnostics=findings)

