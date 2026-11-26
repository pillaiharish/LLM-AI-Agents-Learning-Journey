# Lesson 10 — Adversarial and exact-match evaluation

## Concept
Visible examples help develop a prompt; holdout cases test whether it learned the rule rather than memorizing the examples.

## Why it works
Robustness tests expose unsupported inference, formatting drift, ambiguity, reordered fields, quoted speech, and instruction-like data.

## When to use it
Use holdouts whenever prompts feed automated workflows or will see inputs different from the examples.

## When not to use it
Do not mistake a small fixture suite for proof that a probabilistic system is safe in every setting.

## Common failure modes
The model overfits names and wording, follows source-text commands, invents missing evidence, adds prose, changes key order, or wraps JSON in a fence.

## Exercise
Classify whether the current speaker explicitly accepts, rejects, or leaves a proposal undecided. Return compact JSON with exact key order.

## What to observe
Improve against visible cases first, then use holdout failures to find assumptions your prompt did not state.

