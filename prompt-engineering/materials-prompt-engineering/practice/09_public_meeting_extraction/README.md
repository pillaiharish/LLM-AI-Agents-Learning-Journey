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
Extract eight TSV fields from fictional civic-meeting transcripts. Visible and holdout cases cover introductions, metadata ownership, requests, promises, uncertainty, quotations, repeated speakers, changed positions, missing data, side discussion, and instruction-looking text.

## What to observe
Exact matching exposes both semantic and formatting errors. A plausible-looking row still fails if it infers a district or changes a literal delimiter.

### Commitment semantics

A commitment is a concrete future action explicitly undertaken by the current speaker. “May,” “might,” “hope,” “consider,” and “look into it” are not commitments. A deadline is populated only when the same commitment has an explicit time.

