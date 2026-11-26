# Task

Extract one row with fields in this exact order: `speaker|district|request|deadline`.

- Use one pipe between fields and no spaces around pipes.
- Do not output a header, Markdown, code fence, explanation, or terminal newline.
- Use an empty field for missing district, request, or deadline values.
- The `request` field contains the requested action without leading phrases such as “I request,” “please,” or “could you.”
- Copy an explicit deadline without a leading temporal connector such as `by` or `on`; never infer one.

