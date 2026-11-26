# Task

Extract qualifying public-meeting contributions as TSV rows with these fields:

1. `speaker_name`
2. `speaker_role`
3. `address_or_area`
4. `district`
5. `issue`
6. `position_or_request`
7. `commitment`
8. `deadline`

## Output contract

- Use one literal TAB between fields and exactly eight fields per row.
- Return no header, Markdown, code fence, explanation, leading/trailing whitespace, or terminal newline.
- Use an empty field for missing information and never infer a value.
- Preserve transcript order. Emit one row per contribution containing an issue, position, request, or commitment.
- Emit separate rows for multiple distinct issues or commitments in one contribution.
- If no contribution qualifies, return an empty response.

## Evidence ownership

- Moderator metadata belongs to a speaker only when the moderator explicitly associates it with that speaker.
- A project location is not the speaker's address or area.
- Quoted speech and moderator summaries are not direct statements by the quoted person.
- Later contributions by the same speaker remain separate rows and do not automatically inherit role, area, or district values.

## Field normalization

- `speaker_name`, `speaker_role`, `address_or_area`, `district`: copy only explicitly associated source wording.
- `issue`: copy the shortest source-supported noun phrase naming the concern. Remove only framing such as “my issue is,” “my concern is,” or “the problem is.” Do not invent a category or free-form paraphrase.
- `position_or_request`: remove a leading `I` or `we` and terminal punctuation, but preserve semantic stance/modal verbs including `request`, `support`, `oppose`, `consider`, `may`, and `might`. Normalize direct imperative or question requests without a stance verb to `request <base action>`.
- `commitment`: extract only a concrete future action explicitly undertaken by the current speaker. Remove a leading pronoun and `will`/`shall`, retain negation, and exclude the time phrase stored in `deadline`.
- `deadline`: copy the shortest explicit time phrase after removing a leading connector such as `by`, `on`, or `before`. Preserve meaningful wording such as `beginning next week`.
- `may`, `might`, `hope`, `consider`, and `look into` may describe a position but never a commitment.

Examples:

```text
I request a pedestrian signal.       → position_or_request: request a pedestrian signal
I oppose overnight work.             → position_or_request: oppose overnight work
We will consider a weekend bus lane. → position_or_request: consider a weekend bus lane
We will inspect the site by Friday.  → commitment: inspect the site; deadline: Friday
```

