# Task

Classify one support message and return exactly one lowercase label: `billing`, `technical`, `account`, or `other`.

- Charges, invoices, and refunds are `billing`.
- Sign-in, password, and credential problems are `account`.
- A product malfunction after successful sign-in is `technical`.
- Use `other` when the message does not contain enough information.
- Return only the label, with no explanation, punctuation, code fence, or terminal newline.

