# Lesson 06 — Reasoning scaffolds / decision checklists

## Concept
Give the model a private decision checklist while requesting only the final answer.

## Why it works
The checklist encourages consistent evidence checks without making hidden reasoning part of the interface.

## When to use it
Use a scaffold when classifications depend on several small questions.

## When not to use it
Do not request, store, display, or score hidden chain-of-thought.

## Common failure modes
The model may print its analysis, treat possibility as commitment, or infer a deadline.

## Exercise
Classify a statement as `COMMITMENT`, `POSSIBILITY`, `REQUEST`, or `FACT`.

## What to observe
The output should contain only the label even though the prompt supplies an internal checklist. This is the practical relationship to older “chain-of-thought prompting” terminology.

