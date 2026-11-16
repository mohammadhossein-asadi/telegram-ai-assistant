# 13 — Migration implementation

**Phase:** implementation · **Use when:** shipping a schema change.

## Role
Engineer performing an additive migration in `src/database/migrations.py`.

## Inputs
- `docs/database/migrations-strategy.md`
- `src/database/migrations.py`
- `tests/test_migrations.py`

## Task
1. Confirm the change is additive; otherwise stop and escalate to an ADR.
2. Increment `SCHEMA_VERSION` and add the `_ADDED_COLUMNS` entry with a DDL fragment that
   works on SQLite (`BOOLEAN DEFAULT 0 NOT NULL`, `INTEGER`, `VARCHAR(n)`, `TEXT`).
3. Add a test that builds the previous schema, runs migrations, and asserts the new
   column exists with defaults.
4. Update `artifacts/database/schema.sql` and the data dictionary.
5. Write the upgrade note for self-hosters (backup → pull → restart → verify logs).

## Constraints
- No `DROP`, `RENAME`, type change, or backfill.
- NOT NULL additions require a DEFAULT.
- The runner must remain idempotent and inspector-checked.
- Do not create a second schema authority (no Alembic without an ADR).

## Output
Diff + test + upgrade note.

## Verification
```bash
pytest -q tests/test_migrations.py tests/test_database.py
```
State the version numbers before and after.
