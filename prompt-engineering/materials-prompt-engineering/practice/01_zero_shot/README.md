# Lesson 01 — Zero-shot prompting

## Concept
Give a complete task and output contract without demonstrations.

## Why it works
Clear transformations, placeholders, and preservation rules reduce the model's room to improvise.

## When to use it
Use zero-shot prompts for simple tasks whose rules can be stated directly.

## When not to use it
Add examples when labels are ambiguous or edge cases are easier to show than describe.

## Common failure modes
Vague prompts may rewrite dialogue, remove speaker labels, alter punctuation, or use inconsistent replacement text.

## Exercise
Replace email addresses with `[EMAIL]` and phone numbers with `[PHONE]` while preserving every other character.

## What to observe
Compare the vague starter with your explicit attempt. Check whether even a harmless extra newline fails exact matching.

