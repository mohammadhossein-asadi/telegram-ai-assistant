# CLAUDE.md

Canonical instructions live in [AGENTS.md](AGENTS.md). Read it first; this file only
adds Claude-specific working notes.

## Quick context

- Python 3.12 · aiogram 3 · SQLAlchemy 2 async · SQLite · no web layer.
- Entry: `run.py` → `src/bot/main.py`. Imports are rooted at `src/`.
- 31 tests: `pytest -q` (no network, no token needed).
- No linter/formatter/type-checker is configured — do not add one unasked.

## Working style for this repo

1. Read the file you intend to change, plus its neighbours in the same layer, before
   editing.
2. Prefer the smallest diff that satisfies the request. This codebase is deliberately
   small (79 source files); large refactors need explicit approval.
3. When touching handlers, check `src/bot/handlers/__init__.py` order — the chat
   router must stay last.
4. When touching user-visible strings, update **both** `src/localization/fa.json` and
   `en.json`. Persian strings need correct ZWNJ; copy existing style.
5. When touching models, update `migrations.py`, `artifacts/database/schema.sql`, and
   `docs/database/data-dictionary.md`.
6. Run `pytest -q` after changes that touch `src/`.

## Things that will surprise you

| Surprise | Explanation |
| --- | --- |
| `container` used without import wiring | module-level singleton set in `bootstrap()`; handlers assume it is populated |
| Persona "create" updates instead of duplicating | `PersonaRepository.create` upserts by `(user_id, name)` |
| Failed AI calls leave no message rows | persist-after-success by design (ADR-004) |
| `MAX_DAILY_REQUESTS=0` is rejected | `Settings` uses `ge=1`, though the repository supports ≤0 as unlimited |
| Callback `persona_id` has no FK | dangling ids are ignored at read time |
| No `pyproject.toml` | imports work only with `src` on the path (`run.py`/pytest) |

## Verification

```bash
pytest -q
python -m compileall -q src
```

Report exactly what you ran. Do not claim a Telegram-side check you could not perform.

## Documentation

[docs/index.md](docs/index.md) is the map; [HANDOFF.md](HANDOFF.md) carries the
current status and known issues.
