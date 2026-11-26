from __future__ import annotations

from prompt_lab.cli import _print_evaluation
from prompt_lab.evaluator import Evaluation
from prompt_lab.lessons import Case
from prompt_lab.provider import ChatResult


def failed_evaluation() -> Evaluation:
    case = Case("holdout_01", "source", "secret expected", "text")
    return Evaluation(case, ChatResult("actual"), False, ("likely_value_mismatch",))


def test_holdout_expected_is_hidden_by_default(capsys) -> None:
    _print_evaluation(failed_evaluation(), reveal=False)
    output = capsys.readouterr().out
    assert "secret expected" not in output
    assert "--reveal" in output


def test_reveal_shows_expected(capsys) -> None:
    _print_evaluation(failed_evaluation(), reveal=True)
    assert "secret expected" in capsys.readouterr().out

