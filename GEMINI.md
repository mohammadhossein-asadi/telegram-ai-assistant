# GEMINI.md

Canonical instructions: [AGENTS.md](AGENTS.md). This file adds only Gemini-specific
notes.

## Context

- Telegram bot, Python 3.12, aiogram 3, SQLAlchemy 2 async, SQLite.
- No HTTP server, no frontend, no build step.
- Tests: `pytest -q` (31 tests, offline).

## Rules of engagement

1. Inspect before editing; state assumptions when the request is ambiguous.
2. Keep diffs minimal and scoped to the request.
3. Never add dependencies, frameworks, or tooling that was not requested.
4. Maintain locale parity between `src/localization/fa.json` and `en.json`.
5. Maintain schema discipline: model change ⇒ `SCHEMA_VERSION` bump + additive
   migration entry + docs.
6. Run `pytest -q` and `python -m compileall -q src` after touching `src/`.

## Repo quirks

| Quirk | Note |
| --- | --- |
| Imports are `src`-rooted | run via `python run.py` or pytest, not by file path |
| Router order matters | chat router last |
| Persona create upserts | by `(user_id, name)` |
| Failed AI calls write nothing to history | intentional |
| No linter configured | don't impose one |

## Output expectations

- Summarise what changed and which files.
- List the exact commands run and their results.
- If something could not be verified (e.g. real Telegram behaviour), say so plainly.

Docs map: [docs/index.md](docs/index.md). Current status: [HANDOFF.md](HANDOFF.md).
