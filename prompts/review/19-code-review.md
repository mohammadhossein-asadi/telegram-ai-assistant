# 19 — Code review

**Phase:** review · **Use when:** reviewing a PR or your own diff before asking for review.

## Role
Reviewer with authority to block on correctness, layering, and data safety.

## Inputs
- The diff
- `AGENTS.md` §invariants, `CONTRIBUTING.md` §3
- Relevant ADRs

## Task
1. **Correctness:** does it do what the description says, including edge cases?
2. **Layering:** imports respect the boundaries; no SQL in handlers; no aiogram in services.
3. **Ownership:** every user-scoped query filters `user_id`.
4. **Data:** migrations additive, `SCHEMA_VERSION` bumped, docs updated.
5. **i18n:** both catalogs, correct placeholders.
6. **Error paths:** failures render `errors.*`; nothing swallowed.
7. **Scope:** unrelated changes, reformatting, new dependencies.
8. **Tests:** meaningful assertions, no weakened existing tests.

## Constraints
- Comment on the diff, not on style preferences the project does not enforce.
- Distinguish blocking issues from suggestions.
- Cite the line and explain the consequence, not just "this is wrong".

## Output
Blocking / non-blocking / questions, each with file:line and rationale, plus a verdict.

## Verification
- Every blocking item maps to an invariant, a bug, or a security issue.
