#!/usr/bin/env python3
import json
import sys
import os

import click
from tabulate import tabulate

sys.path.insert(0, os.path.dirname(__file__))
from core.calculator import TokenCalculator


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


def _print_results(data):
    click.echo()

    if data.get("filename"):
        click.echo(f"  File: {data['filename']} ({data.get('file_type', 'text')})")
    if data.get("word_count") is not None:
        click.echo(
            f"  Words: {data['word_count']:,}  |  Characters: {data['char_count']:,}"
        )
    click.echo()

    headers = [
        "Model",
        "Provider",
        "Context",
        "Tokens",
        "Method",
        "Input Cost",
        "Cached Cost",
        "Output Cost",
    ]
    rows = []
    for r in data["results"]:
        rows.append(
            [
                r["model"],
                r["provider"],
                _format_context(r["context_window"]),
                _format_tokens(r["tokens"]),
                r["method"],
                _format_cost(r["input_cost"]),
                _format_cost(r["cached_input_cost"]),
                _format_cost(r["output_cost"]),
            ]
        )

    click.echo(tabulate(rows, headers=headers, tablefmt="grid"))
    click.echo()


@click.command()
@click.option("--text", "-t", help="Text to calculate tokens for")
@click.option(
    "--file",
    "-f",
    "files",
    multiple=True,
    type=click.Path(exists=True),
    help="File(s) to calculate tokens for",
)
@click.option("--model", "-m", help="Filter models (case-insensitive substring match)")
@click.option("--output", "-o", type=click.Path(), help="Save JSON results to file")
def main(text, files, model, output):
    """Token Calculator - Estimate token counts and API costs for various LLMs."""
    if not text and not files:
        click.echo("Error: Provide --text or --file. Use --help for usage.", err=True)
        sys.exit(1)

    all_results = []

    if text:
        result = TokenCalculator.calculate_from_text(text, model)
        all_results.append(result)
        if not output:
            _print_results(result)

    for file_path in files:
        result = TokenCalculator.calculate_from_file(file_path, model)
        all_results.append(result)
        if not output:
            _print_results(result)

    if output:
        out = all_results[0] if len(all_results) == 1 else all_results
        with open(output, "w") as f:
            json.dump(out, f, indent=2)
        click.echo(f"Results saved to {output}")


if __name__ == "__main__":
    main()
