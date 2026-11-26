# Task

Classify the current speaker's statement as exactly one of `COMMITMENT`, `POSSIBILITY`, `REQUEST`, or `FACT`.

- A `COMMITMENT` is a concrete future action explicitly undertaken by the current speaker.
- `may`, `might`, `hope`, and similar uncertain language indicate `POSSIBILITY`, not commitment.
- A request asks another party to act; a fact describes a present or past condition.
- Apply any decision checklist internally. Return only the final label, never hidden reasoning, explanation, punctuation, or a terminal newline.

