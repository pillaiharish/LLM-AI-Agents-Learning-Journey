# Practice mode

`python -m prompt_lab practice` creates a deterministic 45–60 minute local session for self-study, prompt-engineering assessments, LLM engineering practice, or automated prompt-evaluation practice.

The four parts are:

1. Write a zero-shot or few-shot prompt.
2. Combine input boundaries with an exact output contract.
3. Extract supported facts from a synthetic public-meeting transcript.
4. Review exact-match failures, improve the prompt, and rerun it.

Use `--seed` to reproduce the same selection:

```bash
python -m prompt_lab practice --seed 12345
```

The command prints case commands without revealing expected answers. It does not call Ollama until you run those commands.

