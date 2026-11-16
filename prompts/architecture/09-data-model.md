# 09 — Data model change

**Phase:** architecture · **Use when:** persisting something new, or changing an existing table.

## Role
Engineer responsible for schema safety in a single-file SQLite database.

## Inputs
- `src/database/models/__init__.py`
- `src/database/migrations.py` (`SCHEMA_VERSION`, `_ADDED_COLUMNS`)
- `docs/database/*`, `artifacts/database/schema.sql`

## Task
1. Decide whether the data belongs in an existing table or a new one; state why.
2. Define columns with type, nullability, default, index, and FK behaviour.
3. Confirm the change is **additive**. If it is not, stop: a rebuild or Alembic decision
   is required first.
4. Bump `SCHEMA_VERSION`, add the `_ADDED_COLUMNS` entry with a default for NOT NULL.
5. Update `artifacts/database/schema.sql`, `docs/database/data-dictionary.md`,
   `docs/database/entity-relationship-diagram.md`, `docs/database/indexes-and-constraints.md`.
6. Add a migration test starting from the previous schema.

## Constraints
- No destructive DDL, no renames, no type changes.
- Every user-scoped table carries `user_id` and an ownership-filtered repository method.
- Cascades must be explicit (ORM cascade; note the missing `PRAGMA foreign_keys`).
- Validate the DDL by executing it against SQLite.

## Output
Model diff, migration entry, docs diff, test, and a rollback note (restore backup).

## Verification
```bash
pytest -q tests/test_migrations.py
python -c "import sqlite3;sqlite3.connect(':memory:').executescript(open('artifacts/database/schema.sql').read())"
```
