# Prompt engineering notes

Prompt engineering is the practice of turning an intended model behavior into a clear, testable input contract. A useful prompt does more than describe a topic: it defines the task, separates instructions from source data, states what evidence may be used, and specifies the exact output expected by the next consumer.

The executable companion to these notes is the [Prompt Engineering Practice Lab](materials-prompt-engineering/README.md).

## Prompts as contracts

Think about a prompt as a software interface:

```text
input contract → instructions → model → output contract → tests
```

An answer can be factually reasonable and still fail if it violates the interface—for example, by adding a Markdown fence around JSON, emitting a header where none was requested, or replacing literal tabs with spaces.

## Core techniques

- **Zero-shot prompting:** State the task and constraints without examples. This is a good starting point for simple, well-defined transformations.
- **One-shot and few-shot prompting:** Add carefully selected demonstrations. Contrasting or edge-case examples usually teach more than several redundant easy examples.
- **Delimiters:** Mark where instructions end and source data begins. Text that looks like an instruction inside a delimited transcript remains source data.
- **Numbered procedures:** Break dependent decisions into an explicit order so the model is less likely to skip evidence checks or formatting steps.
- **Role prompts:** Define responsibility and boundaries, such as extracting only supported facts, rather than adding a theatrical persona.
- **Decision checklists:** Ask the model to apply checks internally and return only the final result. Hidden reasoning should not become part of the output contract.
- **Structured output:** Define serialization, field order, delimiters, headers, missing values, casing, whitespace, and whether a final newline is allowed.
- **Labeled conversations:** Use `system`, `user`, and `assistant` messages to separate standing behavior, source input, and demonstrations.

## Exact evaluation and holdouts

The lab compares the untouched model response with the expected value. It does not strip whitespace or repair output before scoring. Diagnostics explain likely causes only after a failure.

Visible cases support prompt development. Holdout cases check whether the prompt learned the rule rather than merely matching the examples. A useful suite includes missing fields, ambiguous language, quoted speech, instruction-looking source text, and cases whose surface wording differs from the demonstrations.

## A practical experiment loop

1. Read the task contract without opening the solution prompt.
2. Write the smallest prompt that appears to satisfy it.
3. Run visible cases and inspect exact-match diagnostics.
4. Revise the prompt, not the evaluator or expected output.
5. Run holdouts only after the visible behavior is stable.
6. Repeat with another locally installed model to identify model-specific overfitting.

## Local-first privacy

The practice lab uses local Ollama by default and committed synthetic fixtures. Local execution reduces accidental data sharing, but downloaded public transcripts still require provenance, privacy review, and anonymization before reuse.

## Further reading

Some introductory ideas and the original seed exercises were inspired by Real Python's [“Practical Prompt Engineering”](https://realpython.com/practical-prompt-engineering/). The active lab is an original local-model curriculum focused on prompt contracts, exact evaluation, and realistic extraction.
