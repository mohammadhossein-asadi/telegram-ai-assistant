# Implementation Log

Reverse-chronological. Each entry records what changed, what was verified, and what
remains unverified.

## 2026-11-16 — Documentation package

**Scope:** a complete, code-grounded engineering documentation set for the repository,
written directly to disk (no archive).

**Added**

- `docs/product/` (8 files), `docs/research/` (3), `docs/architecture/` (3 + 8 ADRs),
  `docs/database/` (6), `docs/api/` (4), `docs/security/` (6), `docs/design/` (5),
  `docs/testing/` (6), `docs/devops/` (7), `docs/ai/` (1), `docs/project/` (4),
  `docs/index.md`.
- `artifacts/database/{schema.sql,seed.sql}`, `artifacts/api/telegram-interface.json`,
  `artifacts/configurations/env-reference.md`, `artifacts/diagrams/*.mmd`.
- `prompts/` (23 prompts + index), `skills/` (4 `SKILL.md`), `templates/{adr,documentation}`.
- `AGENTS.md` (canonical), `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/*`,
  `.github/copilot-instructions.md`.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `LICENSE` (MIT),
  `.editorconfig`, `CHANGELOG.md`.
- `.github/` issue forms, PR template, `labeler.yml`, `workflows/{ci,security}.yml`.
- `manifest/{documentation-index.json,requirements-traceability.csv,generation-status.json}`.

**Changed**

- `src/bot/handlers/conversations.py`: removed a duplicated
  `@router.callback_query(F.data.startswith("conv:unarch:"))` decorator on
  `cb_unarchive`. aiogram would otherwise register the same handler twice. This is the
  only source change; it is **uncommitted** in this workspace.

**Verified**

| Check | Command | Result |
| --- | --- | --- |
| Tests | `pytest -q` | 32 passed |
| Syntax | `python -m compileall -q src` | clean |
| DDL | execute `schema.sql` in SQLite | 10 tables; `schema_version` rows 1–2 |
| Seed idempotency | apply `seed.sql` twice | counts unchanged |
| Interface JSON | `python -m json.tool` | valid |
| Doc links | internal-link script | see `manifest/generation-status.json` |

**Not verified**

- Live bot run (no `BOT_TOKEN`), live provider call (no `AI_API_KEY`), container build,
  CI execution, Telegram rendering of the documented screens.

**Corrections made while documenting** (documentation followed the code, not the
README):

- `README.md` claims Alembic migrations; the project uses a hand-rolled additive runner.
- `README.md` lists `pydantic-settings` under "Container"; `Settings` is
  `BaseSettings` from pydantic, not the separate package.
- Persona creation upserts by `(user_id, name)` rather than always inserting.
- `MAX_DAILY_REQUESTS` rejects `0` (`ge=1`), so the repository's "unlimited" path is
  unreachable through env config.
- Only `BOT_TOKEN` is fatal at boot; a missing `AI_API_KEY` warns and fails later.
- `.env.example` omits six variables that `Settings` reads.

## Pre-2026-11-16 — Application (as found)

The v1.0 feature set described in [`CHANGELOG.md`](../../CHANGELOG.md) and
[product status](project-status.md). No dated per-commit log exists for this period;
the Git history is the record.

## Entry format for future changes

```markdown
## YYYY-MM-DD — <short title>

**Scope:** one line.
**Changed:** files, one line each.
**Verified:** command → result (paste real output).
**Not verified:** what you could not run, and why.
**Follow-ups:** task ids or none.
```
