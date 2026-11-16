# ADR templates

## Files

| File | Purpose |
| --- | --- |
| `ADR-template.md` | Copy for any new decision record |

Existing decisions live in [`docs/architecture/decisions/`](../../docs/architecture/decisions/)
(ADR-001 … ADR-008).

## When to write one

Write an ADR when the decision:

- changes a boundary (layers, modules, external service),
- is expensive to reverse (schema strategy, provider abstraction, deployment model),
- closes off an option someone will later ask about,
- or replaces a previous decision.

Do **not** write one for reversible implementation details; those belong in code
comments or the implementation log.

## Numbering and filenames

```
docs/architecture/decisions/ADR-009-<kebab-slug>.md
```

Numbers are never reused or reordered. A superseded ADR keeps its file and gets
`Status: Superseded by ADR-0NN` plus a link from the new one.

## Minimal process

1. Copy the template.
2. Fill Context and Problem before thinking about the answer.
3. List alternatives, including "do nothing" and the current approach.
4. Decide, and write the negative consequences honestly.
5. Add the verification method.
6. Link it from `docs/architecture/system-architecture.md` and, if it changes
   requirements, from `docs/project/decisions-log.md`.

## Review checklist

- [ ] Status and date present
- [ ] At least three alternatives, one being "do nothing"
- [ ] Consequences include costs
- [ ] Verification is executable
- [ ] Cross-links resolve
- [ ] No invented facts about the current system
