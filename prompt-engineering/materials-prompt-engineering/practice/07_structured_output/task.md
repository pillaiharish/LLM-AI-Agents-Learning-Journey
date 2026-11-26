# Task

Each input supplies a `FORMAT` and records with fields `id`, `item`, and `status`. Serialize only those records according to the selected contract.

## Common rules

- Preserve record order, field order, value spelling, and case.
- Missing values are empty strings or empty fields; never invent a value.
- Do not output explanatory prose, Markdown fences, leading/trailing whitespace, extra rows, or a terminal newline.

## Format contracts

- **JSON:** Return one compact JSON array. Each object uses keys in the exact order `id`, `item`, `status`. Missing values are `""`.
- **CSV:** Return `id,item,status` fields with standard CSV quoting. Do not output a header. Use one record per line.
- **TSV:** Return `id`, `item`, and `status` separated by one literal TAB character. Do not output a header. Use one record per line.
- **PIPE:** Return `id|item|status`, with no spaces around pipes and no header. Use one record per line.
- **MARKDOWN:** Return `| id | item | status |`, then `|---|---|---|`, then one row per record with one space around each cell value.

