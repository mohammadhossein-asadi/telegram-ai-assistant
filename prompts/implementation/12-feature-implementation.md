# 12 — Feature implementation

**Phase:** implementation · **Use when:** building an approved, scoped feature.

## Role
Implementer working inside the existing layers.

## Inputs
- The scoped requirement (`FR-*`, `US-*`) and its acceptance criteria
- `AGENTS.md` §invariants
- Relevant handler/service/repository files

## Task
1. List the files to touch and the layer each belongs to.
2. Implement bottom-up: model/repository → service → handler → keyboard/view →
   localization.
3. Add or update tests at the lowest observable level.
4. Update docs that state a contract (commands, callbacks, env vars, limits, schema).
5. Run `pytest -q` and `python -m compileall -q src`; report exact output.

## Constraints
- Smallest diff; no drive-by refactors or reformatting.
- Both locale catalogs updated; Persian needs correct ZWNJ.
- No new dependency, no schema change without the migration checklist.
- Errors render through `errors.*` keys; no stack traces to users.
- Never weaken an existing test.

## Output
Summary, file list with one line each, test commands and results, and anything not
verified (e.g. real Telegram rendering).

## Verification
- `pytest -q` passes.
- New tests fail without the change (state this if you checked it).
