from __future__ import annotations

import csv
from io import StringIO
import json

from .lessons import Case


def diagnose(actual: str, case: Case) -> list[str]:
    expected = case.expected
    findings: list[str] = []
    if "```" in actual:
        findings.append("markdown_fence")
    if actual[:1].isspace() and not expected[:1].isspace():
        findings.append("leading_whitespace")
    if actual[-1:].isspace() and not expected[-1:].isspace():
        findings.append("trailing_whitespace")
    if "\n\n" in actual and "\n\n" not in expected:
        findings.append("unexpected_blank_line")

    actual_rows = actual.splitlines()
    expected_rows = expected.splitlines()
    candidate_rows = [row for row in actual_rows if row.strip() and not row.strip().startswith("```")]
    if case.format != "markdown" and case.columns and any(
        _looks_like_header(row, case) for row in candidate_rows[:2]
    ):
        findings.append("extra_header")
    if len(actual_rows) > len(expected_rows):
        findings.append("extra_rows")
    elif len(actual_rows) < len(expected_rows):
        findings.append("missing_rows")

    if case.format == "json":
        try:
            parsed_actual = json.loads(actual)
            parsed_expected = json.loads(expected)
            if parsed_actual == parsed_expected:
                findings.append("json_format_mismatch")
        except json.JSONDecodeError:
            findings.append("json_format_mismatch")
    elif case.format in {"csv", "tsv", "pipe", "markdown"}:
        findings.extend(_delimited_findings(actual, case))

    if not findings:
        findings.append("likely_value_mismatch")
    return list(dict.fromkeys(findings))


def field_counts(text: str, format_name: str) -> list[int]:
    if not text:
        return []
    if format_name == "csv":
        return [len(row) for row in csv.reader(StringIO(text))]
    delimiter = {"tsv": "\t", "pipe": "|"}.get(format_name)
    if delimiter:
        return [len(row.split(delimiter)) for row in text.splitlines()]
    if format_name == "markdown":
        return [len(_markdown_cells(row)) for row in text.splitlines() if "|" in row]
    return []


def _delimited_findings(actual: str, case: Case) -> list[str]:
    findings: list[str] = []
    required = len(case.columns)
    counts = field_counts(actual, case.format)
    if required and any(count != required for count in counts):
        findings.append("wrong_field_count")
    expected_delimiter = {"csv": ",", "tsv": "\t", "pipe": "|", "markdown": "|"}[case.format]
    if actual and expected_delimiter not in actual:
        findings.append("wrong_delimiter")
    if case.format == "markdown" and not _valid_markdown_table(actual, required):
        findings.append("wrong_delimiter")
    if case.format == "pipe" and any(
        " |" in row or "| " in row for row in actual.splitlines()
    ):
        findings.append("wrong_delimiter")
    return findings


def _looks_like_header(row: str, case: Case) -> bool:
    if case.format == "csv":
        cells = next(csv.reader([row]), [])
    elif case.format == "tsv":
        cells = row.split("\t")
    elif case.format in {"pipe", "markdown"}:
        cells = _markdown_cells(row) if case.format == "markdown" else row.split("|")
    else:
        return False
    return [cell.strip().lower() for cell in cells] == [column.lower() for column in case.columns]


def _markdown_cells(row: str) -> list[str]:
    stripped = row.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def _valid_markdown_table(text: str, required: int) -> bool:
    rows = [row for row in text.splitlines() if row.strip()]
    if len(rows) < 2 or not all("|" in row for row in rows):
        return False
    separator = _markdown_cells(rows[1])
    return (
        (not required or all(len(_markdown_cells(row)) == required for row in rows))
        and all(cell.strip().strip(":").replace("-", "") == "" and "-" in cell for cell in separator)
    )

