# Lesson 04 — Numbered steps

## Concept
Break a task with dependent decisions into an explicit ordered procedure.

## Why it works
Numbered steps keep the model from skipping identification, support checks, missing-value handling, or serialization.

## When to use it
Use steps when later decisions depend on earlier extraction or classification.

## When not to use it
Avoid ceremony for a single obvious transformation.

## Common failure modes
Vague steps, conflicting order, and unspecified missing values still produce inconsistent output.

## Exercise
Extract speaker, district, request, and deadline as four pipe-delimited fields.

## What to observe
See whether the model leaves missing fields empty and avoids inferring a deadline.

