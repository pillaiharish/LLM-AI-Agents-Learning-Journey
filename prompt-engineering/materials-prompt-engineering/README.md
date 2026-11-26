# Prompt Engineering Practice Lab

A hands-on progression for learning prompt engineering through progressively harder exercises using local language models.

Many prompt tutorials stop when an answer looks good. This lab treats a prompt as a testable specification and checks correctness, formatting, ambiguity, missing values, adversarial input, unseen cases, and model variation.

```text
Input contract
    ↓
Prompt instructions
    ↓
Local LLM
    ↓
Output contract
    ↓
Exact-match tests
```

Everything runs through local Ollama by default. Core lessons use fictional, committed fixtures and require no network access.

## Setup

Install [Ollama](https://ollama.com/), then confirm the default model is available:

```bash
ollama list
ollama pull qwen3.5:9b  # only if it is missing
```

Create the Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m prompt_lab doctor
```

The lab never pulls a model automatically. Edit `prompt_lab.toml` or use `--model` to select another model already installed in Ollama.

## Learning path

| Lesson | Skill |
|---|---|
| 01 | Zero-shot instructions |
| 02 | Few-shot examples |
| 03 | Input delimiters |
| 04 | Stepwise task specification |
| 05 | Useful role prompts |
| 06 | Reasoning scaffolds |
| 07 | Exact structured output |
| 08 | Labeled conversations |
| 09 | Real-world information extraction with controlled and natural transcript tiers |
| 10 | Robustness and holdout evaluation |

Start with Lesson 01:

```bash
cd practice/01_zero_shot
less README.md
cd ../..
python -m prompt_lab run --lesson 01 --case visible_01
python -m prompt_lab evaluate --lesson 01 --split visible
```

Edit `practice/01_zero_shot/prompts/attempt_01.txt`, rerun the cases, and compare your prompt with `solution_prompt.txt` only after experimenting.

## Commands

```bash
python -m prompt_lab doctor
python -m prompt_lab run --lesson 07 --case visible_01
python -m prompt_lab evaluate --lesson 09 --split visible
python -m prompt_lab evaluate --lesson 09 --split holdout
python -m prompt_lab evaluate --lesson 09 --split holdout --reveal
python -m prompt_lab practice --seed 12345
```

Use `--prompt attempt_02.txt` to evaluate another prompt revision. Use `--model`, `--temperature`, or `--ollama-url` for one-run overrides. The URL must remain on the local machine.

Lesson 09 progresses from short controlled-language cases to natural multi-speaker transcripts. Its visible split contains 10 controlled and five natural cases; its holdout split contains 10 controlled, seven medium natural, and three long/noisy cases.

Visible cases show expected answers after a failure. Holdout answers stay hidden unless you deliberately pass `--reveal`. They are local educational fixtures, not encrypted secrets.

## Exact output means exact output

The evaluator first compares the untouched response with the expected string using `actual == expected`. It does not strip whitespace, repair JSON, reorder fields, or normalize delimiters. After a failure, diagnostics can explain likely formatting problems without changing the score.

Run summaries go to ignored `runs/history.csv`. The history contains aggregate scores and model metrics, never prompts, source transcripts, expected answers, model output, environment variables, or reasoning.

## Optional public transcripts

The complete curriculum uses synthetic data. For optional practice with public civic data, see `scripts/fetch_public_transcript.py` and `data/external/README.md`. Downloads are explicit, ignored by Git, and never converted into fixtures automatically.

## Tests

Ordinary tests use a mocked provider and need neither Ollama nor internet access:

```bash
pytest -q
```

To run the optional local integration check:

```bash
RUN_OLLAMA_INTEGRATION=1 pytest -m integration
```

## Credits and inspiration

Some introductory concepts and the original seed exercises were inspired by Real Python's [“Practical Prompt Engineering”](https://realpython.com/practical-prompt-engineering/) tutorial.

This repository expands those ideas into an original local-LLM curriculum with structured-output evaluation, adversarial cases, transcript extraction, and exact-match testing. See [CREDITS.md](CREDITS.md) and [NOTICE.md](NOTICE.md).

