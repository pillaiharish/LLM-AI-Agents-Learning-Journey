#!/usr/bin/env python3
"""Dev Tools — Unified CLI"""
import json
import sys

import click
from tabulate import tabulate


# ── Helpers ──────────────────────────────────────────────────────────────────

def _format_cost(cost):
    if cost is None:
        return "-"
    if cost < 0.000001:
        return "$0.00"
    return f"${cost:.6f}"


def _format_tokens(tokens):
    if tokens is None:
        return "N/A"
    return f"{tokens:,}"


def _format_context(ctx):
    if ctx >= 1_000_000:
        return f"{ctx / 1_000_000:.1f}M"
    return f"{ctx // 1000}K"


def _print_token_results(data):
    click.echo()
    if data.get("filename"):
        click.echo(f"  File: {data['filename']} ({data.get('file_type', 'text')})")
    if data.get("word_count") is not None:
        click.echo(f"  Words: {data['word_count']:,}  |  Characters: {data['char_count']:,}")
    click.echo()

    headers = ["Model", "Provider", "Context", "Tokens", "Method", "Input Cost", "Cached Cost", "Output Cost"]
    rows = []
    for r in data["results"]:
        rows.append([
            r["model"], r["provider"], _format_context(r["context_window"]),
            _format_tokens(r["tokens"]), r["method"],
            _format_cost(r["input_cost"]), _format_cost(r["cached_input_cost"]), _format_cost(r["output_cost"]),
        ])
    click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
    click.echo()


# ── CLI Group ────────────────────────────────────────────────────────────────

@click.group()
def cli():
    """Dev Tools — local developer utilities."""
    pass


# ── Token Calculator ─────────────────────────────────────────────────────────

@cli.command()
@click.option("--text", "-t", help="Text to calculate tokens for")
@click.option("--file", "-f", "files", multiple=True, type=click.Path(exists=True), help="File(s) to calculate tokens for")
@click.option("--model", "-m", help="Filter models (case-insensitive substring match)")
@click.option("--output", "-o", type=click.Path(), help="Save JSON results to file")
def tokens(text, files, model, output):
    """Estimate token counts and API costs for various LLMs."""
    from app.token_calculator.calculator import TokenCalculator

    if not text and not files:
        click.echo("Error: Provide --text or --file. Use --help for usage.", err=True)
        sys.exit(1)

    all_results = []
    if text:
        result = TokenCalculator.calculate_from_text(text, model)
        all_results.append(result)
        if not output:
            _print_token_results(result)

    for file_path in files:
        result = TokenCalculator.calculate_from_file(file_path, model)
        all_results.append(result)
        if not output:
            _print_token_results(result)

    if output:
        out = all_results[0] if len(all_results) == 1 else all_results
        with open(output, "w") as f:
            json.dump(out, f, indent=2)
        click.echo(f"Results saved to {output}")


# ── JSON Formatter ───────────────────────────────────────────────────────────

@cli.command("json-format")
@click.argument("file", type=click.Path(exists=True))
@click.option("--indent", "-i", default=2, help="Indentation level (default: 2)")
def json_format(file, indent):
    """Pretty-print a JSON file."""
    with open(file, "r", encoding="utf-8") as f:
        text = f.read()
    try:
        parsed = json.loads(text)
        click.echo(json.dumps(parsed, indent=indent, ensure_ascii=False))
    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON: {e}", err=True)
        sys.exit(1)


# ── Excel to CSV ─────────────────────────────────────────────────────────────

@cli.command("excel-to-csv")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output CSV path")
@click.option("--sheet", "-s", help="Sheet name (default: first sheet)")
def excel_to_csv(file, output, sheet):
    """Convert an Excel file to CSV."""
    from app.excel_reader.reader import ExcelReader
    from app.excel_reader.converter import ExcelConverter
    import os

    sheets = ExcelReader.read_sheets(file)
    if not sheets:
        click.echo("No sheets found.", err=True)
        sys.exit(1)

    csvs = ExcelConverter.sheets_to_csv(sheets, sheet_name=sheet)
    if not csvs:
        available = ", ".join(sheets.keys())
        click.echo(f"Sheet not found. Available: {available}", err=True)
        sys.exit(1)

    for name, csv_text in csvs.items():
        if output and len(csvs) == 1:
            out_path = output
        else:
            base = os.path.splitext(output or file)[0]
            suffix = f"_{name}" if len(csvs) > 1 else ""
            out_path = f"{base}{suffix}.csv"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(csv_text)
        click.echo(f"Saved: {out_path}")


if __name__ == "__main__":
    cli()
