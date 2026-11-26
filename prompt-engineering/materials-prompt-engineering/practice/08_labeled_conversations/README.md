# Lesson 08 — Labeled conversations

## Concept
Model APIs distinguish `system`, `user`, and `assistant` messages. These roles can separate operating rules, input, and demonstrations.

## Why it works
Message boundaries make the purpose of each piece clearer than one giant user message.

## When to use it
Use labeled messages for standing rules and multi-turn few-shot demonstrations.

## When not to use it
Do not add messages that have no distinct role or rely on a role to override application security.

## Common failure modes
Putting source data in the system message, using invalid roles, or placing the input marker more than once makes the prompt ambiguous.

## Exercise
Return `ALLOW` only when the current request explicitly includes an approval token; otherwise return `DENY`.

## What to observe
Run the default single-message attempt, then compare it with `solution_messages.json`.

