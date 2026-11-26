# Lesson 07 — Structured output

## Concept
An exact output contract specifies serialization, field order, missing values, whitespace, headers, and forbidden extras.

## Why it works
“Return a table” leaves many valid-looking choices. A complete contract gives the model one acceptable representation.

## When to use it
Use explicit formats when software or an exact-match evaluator consumes the response.

## When not to use it
Do not pretend prompting alone guarantees valid production data; applications must still validate untrusted model output.

## Common failure modes
Headers, prose, fences, spaces instead of tabs, spaces around pipes, wrong field order or case, invented missing values, leading/trailing whitespace, extra newlines, and extra rows all fail.

## Exercise
Handle five independent contracts: JSON, CSV, TSV, pipe-delimited text, and Markdown tables.

## What to observe
Markdown is deliberately separate: unlike raw delimiters, it requires a header and separator row.

