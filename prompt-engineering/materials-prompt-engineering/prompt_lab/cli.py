from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .config import ConfigError, Settings, load_settings
from .evaluator import Evaluation, evaluate_case
from .history import record_history
from .lessons import LessonError, find_case, load_cases, load_prompt, normalize_lesson
from .ollama import OllamaClient
from .practice import build_practice
from .provider import ProviderError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Practice prompt engineering with local Ollama")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="Check local Ollama and the configured model")
    _add_provider_options(doctor)

    run = subparsers.add_parser("run", help="Run one lesson case")
    _add_lesson_options(run)
    run.add_argument("--case", required=True, dest="case_id")
    run.add_argument("--reveal", action="store_true")

    evaluate = subparsers.add_parser("evaluate", help="Evaluate a complete case split")
    _add_lesson_options(evaluate)
    evaluate.add_argument("--split", choices=("visible", "holdout"), default="visible")
    evaluate.add_argument("--reveal", action="store_true")

    practice = subparsers.add_parser("practice", help="Create a deterministic practice session")
    practice.add_argument("--seed", type=int, default=12345)
    return parser


def _add_provider_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--ollama-url")


def _add_lesson_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--lesson", required=True)
    parser.add_argument("--prompt")
    _add_provider_options(parser)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "practice":
            return _practice(args.seed)
        settings = _settings_for(args)
        if args.command == "doctor":
            return _doctor(settings)
        if args.command == "run":
            return _run(args, settings)
        return _evaluate(args, settings)
    except (ConfigError, LessonError, ProviderError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _settings_for(args: argparse.Namespace) -> Settings:
    return load_settings().with_overrides(
        url=args.ollama_url,
        model=args.model,
        temperature=args.temperature,
    )


def _doctor(settings: Settings) -> int:
    client = OllamaClient(settings)
    try:
        models = client.installed_models()
        print(f"Ollama reachable: {settings.url}")
        print(f"Active model: {settings.model}")
        if settings.model not in models:
            print(f"Model is not installed. Run: ollama pull {settings.model}")
            return 1
        result = client.chat([{"role": "user", "content": "Reply with exactly OK."}])
        if not result.content:
            print("Generation failed: Ollama returned empty content")
            return 1
        print("Generation succeeds: yes")
        print("Localhost-only configuration: yes")
        return 0
    finally:
        client.close()


def _run(args: argparse.Namespace, settings: Settings) -> int:
    lesson = normalize_lesson(args.lesson)
    split, case = find_case(lesson, args.case_id)
    prompt = load_prompt(lesson, args.prompt)
    client = OllamaClient(settings)
    try:
        evaluation = evaluate_case(client, prompt, case)
    finally:
        client.close()
    _print_evaluation(evaluation, reveal=args.reveal or split == "visible")
    _write_history(lesson, settings, prompt.path, split, [evaluation])
    return 0 if evaluation.passed else 1


def _evaluate(args: argparse.Namespace, settings: Settings) -> int:
    lesson = normalize_lesson(args.lesson)
    cases = load_cases(lesson, args.split)
    prompt = load_prompt(lesson, args.prompt)
    client = OllamaClient(settings)
    evaluations: list[Evaluation] = []
    try:
        for case in cases:
            evaluation = evaluate_case(client, prompt, case)
            evaluations.append(evaluation)
            _print_evaluation(
                evaluation,
                reveal=args.reveal or args.split == "visible",
                include_output=False,
            )
    finally:
        client.close()
    passed = sum(evaluation.passed for evaluation in evaluations)
    print(f"Exact matches: {passed}/{len(evaluations)} ({passed / len(evaluations):.1%})")
    _write_history(lesson, settings, prompt.path, args.split, evaluations)
    return 0 if passed == len(evaluations) else 1


def _print_evaluation(
    evaluation: Evaluation,
    *,
    reveal: bool,
    include_output: bool = True,
) -> None:
    status = "PASS" if evaluation.passed else "FAIL"
    print(f"[{status}] {evaluation.case.id}")
    if include_output:
        print("--- model output ---")
        sys.stdout.write(evaluation.result.content)
        if not evaluation.result.content.endswith("\n"):
            print()
    if evaluation.diagnostics:
        print(f"diagnostics: {', '.join(evaluation.diagnostics)}")
    if not evaluation.passed and reveal:
        print("--- expected ---")
        sys.stdout.write(evaluation.case.expected)
        if not evaluation.case.expected.endswith("\n"):
            print()
    elif not evaluation.passed:
        print("expected answer hidden; rerun with --reveal to inspect it")


def _write_history(
    lesson: str,
    settings: Settings,
    prompt_path: Path,
    split: str,
    evaluations: list[Evaluation],
) -> None:
    passed = sum(evaluation.passed for evaluation in evaluations)
    total = len(evaluations)
    metrics = [evaluation.result for evaluation in evaluations]
    record_history(
        {
            "lesson": lesson,
            "model": settings.model,
            "prompt_file": prompt_path.name,
            "temperature": settings.temperature,
            "visible_passed": passed if split == "visible" else "",
            "visible_total": total if split == "visible" else "",
            "holdout_passed": passed if split == "holdout" else "",
            "holdout_total": total if split == "holdout" else "",
            "exact_match_rate": f"{passed / total:.4f}",
            "latency_ms": _sum_metric(metrics, "latency_ms"),
            "prompt_tokens": _sum_metric(metrics, "prompt_tokens"),
            "completion_tokens": _sum_metric(metrics, "completion_tokens"),
        }
    )


def _sum_metric(results: list[object], field: str) -> object:
    values = [getattr(result, field) for result in results]
    return sum(values) if values and all(value is not None for value in values) else ""


def _practice(seed: int) -> int:
    print(f"Prompt Engineering Practice Session (seed {seed}, about 55 minutes)")
    for number, part in enumerate(build_practice(seed), start=1):
        print(f"\nPart {number} — {part.minutes} minutes")
        print(part.goal)
        print(f"python -m prompt_lab run --lesson {part.lesson} --case {part.case_id}")
    return 0

