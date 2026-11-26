# Lesson 09 — Public meeting information extraction

## Concept
Combine instruction boundaries, evidence rules, decision checklists, and an exact TSV schema on realistic synthetic transcripts.

## Why it works
The prompt defines who owns each fact, distinguishes requests from commitments, and constrains serialization.

## When to use it
Use this pattern for grounded extraction from meetings, hearings, consultations, and other speaker-labeled records.

## When not to use it
Do not treat model extraction as authoritative without review, especially when a source is ambiguous or affects people.

## Common failure modes
Project addresses become speaker addresses, quotations become commitments, moderator summaries become direct statements, uncertain language becomes a promise, or formatting gains a header or extra newline.

## Exercise
Extract eight TSV fields from fictional civic-meeting transcripts. Level 1 contains 10 visible and 10 holdout controlled-language cases for learning the schema. Level 2 adds five visible natural-language cases, seven medium holdouts, and three long/noisy holdouts.

## What to observe
Exact matching exposes both semantic and formatting errors. A plausible-looking row still fails if it infers a district or changes a literal delimiter.

### Commitment semantics

A commitment is a concrete future action explicitly undertaken by the current speaker. “May,” “might,” “hope,” “consider,” and “look into it” are not commitments. A deadline is populated only when the same commitment has an explicit time.

### Natural transcript tier

The `visible_natural_*`, `holdout_natural_*`, and `holdout_long_*` cases avoid repeated extraction cues. They use interruptions, indirect requests, cross-turn context, quoted speech, moderator corrections, irrelevant procedure, and commitments expressed in varied language. Long cases contain 10–20 speaker turns but only 4–7 qualifying rows.

The exact normalization rules are part of `task.md`. Read them before writing a prompt; the solution prompt implements the contract but does not define additional requirements.

