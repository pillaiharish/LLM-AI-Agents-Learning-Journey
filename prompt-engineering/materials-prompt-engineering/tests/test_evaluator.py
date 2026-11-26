from __future__ import annotations

from prompt_lab.diagnostics import diagnose, field_counts
from prompt_lab.evaluator import evaluate_case, exact_match
from prompt_lab.lessons import Case, PromptTemplate
from prompt_lab.provider import ChatResult


class FakeProvider:
    def __init__(self, content: str) -> None:
        self.content = content

    def chat(self, messages: list[dict[str, str]]) -> ChatResult:
        assert messages[0]["content"] == "Input: source"
        return ChatResult(self.content)


def case(expected: str, format_name: str = "text") -> Case:
    return Case(
        id="visible_01",
        input="source",
        expected=expected,
        format=format_name,
        columns=("name", "status") if format_name != "text" else (),
    )


def test_exact_match_does_not_strip_or_normalize() -> None:
    assert exact_match("value", "value")
    assert not exact_match("value\n", "value")
    assert not exact_match(" value", "value")


def test_evaluates_untouched_provider_content() -> None:
    prompt = PromptTemplate(path=None, messages=({"role": "user", "content": "Input: {{INPUT}}"},))  # type: ignore[arg-type]
    evaluation = evaluate_case(FakeProvider("expected\n"), prompt, case("expected"))
    assert not evaluation.passed
    assert "trailing_whitespace" in evaluation.diagnostics


def test_reports_fence_header_and_whitespace() -> None:
    structured = case("Ada\topen", "tsv")
    actual = "```\nname\tstatus\nAda\topen\n```\n"
    findings = diagnose(actual, structured)
    assert "markdown_fence" in findings
    assert "extra_header" in findings
    assert "trailing_whitespace" in findings
    assert "extra_rows" in findings


def test_reports_wrong_tsv_fields_and_delimiter() -> None:
    structured = case("Ada\topen", "tsv")
    findings = diagnose("Ada open", structured)
    assert "wrong_field_count" in findings
    assert "wrong_delimiter" in findings


def test_reports_json_format_mismatch_for_equivalent_values() -> None:
    structured = case('{"name":"Ada","status":"open"}', "json")
    findings = diagnose('{\n  "name": "Ada",\n  "status": "open"\n}', structured)
    assert "json_format_mismatch" in findings


def test_delimited_field_counts() -> None:
    assert field_counts('1,"a,b",open', "csv") == [3]
    assert field_counts("1\ta\topen\n2\tb\t", "tsv") == [3, 3]
    assert field_counts("1|a|open", "pipe") == [3]
    assert field_counts("| a | b |\n|---|---|", "markdown") == [2, 2]


def test_csv_pipe_and_markdown_validation() -> None:
    csv_case = case("Ada,open", "csv")
    assert "wrong_field_count" in diagnose("Ada", csv_case)

    pipe_case = case("Ada|open", "pipe")
    assert "wrong_delimiter" in diagnose("Ada | open", pipe_case)

    markdown_case = case("| name | status |\n|---|---|\n| Ada | open |", "markdown")
    findings = diagnose("| name | status |\n| Ada | open |", markdown_case)
    assert "wrong_delimiter" in findings
    assert "extra_header" not in findings

