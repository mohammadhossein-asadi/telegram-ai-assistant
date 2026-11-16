# Regression Testing

Purpose: prevent the failures this project has actually experienced or is structurally
prone to. Each row maps a past/near-miss defect to a cheap check.

## 1. Historically observed failure modes

| # | What happened / nearly happened | Root cause | Regression check |
| --- | --- | --- | --- |
| R1 | Duplicate `@router.callback_query` decorator on `conv:unarch:` | copy-paste during a refactor | run `tests/test_routing.py`-style import check; grep for duplicated decorators on the same `F.data` |
| R2 | Persian catalog characters corrupted (ZWNJ/ZWJ) | editor or scripted rewrite | byte-level diff when regenerating catalogs; `wc -c` + hash comparison |
| R3 | A callback namespace collided between routers | no central registry | grep each `F.data.startswith("ns:")` and confirm a single owner |
| R4 | README claimed Alembic migrations and a pydantic-settings container | documentation drift | this package's docs are code-verified; review README claims vs `src/database/migrations.py` and `src/core/container.py` |
| R5 | Remote repo had stray `src/__init__.py` / `src/core/__init__.py` | manual file creation | `git ls-files` review after mirroring |
| R6 | A v1 database would lose new columns | migration runner change | `test_additive_migration_on_legacy_schema` |

## 2. Always-run regression suite

```bash
pytest -q                      # 32 tests, ~1s
python -m compileall -q src    # syntax sanity
```

Both must pass before any commit that touches `src/`.

## 3. Targeted regression checks by change type

| Change | Additional check |
| --- | --- |
| New handler / callback | unique prefix (grep), added to `artifacts/api/telegram-interface.json` |
| New locale string | both catalogs updated; parity test passes |
| Model change | migration test + data dictionary update |
| Prompt composition change | `test_persona_instructions_reach_system_prompt`, plus a manual persona chat |
| Provider/registry change | `test_routing.py` + registry refresh logs |
| Text/formatting change | `test_text.py` + a manual message with a code block |
| Settings field | `validate_runtime()` output + `.env.example` |
| Dependency bump | full suite + `pip-audit` |

## 4. Manual regression walkthrough (10 minutes, real bot)

| Step | Pass condition |
| --- | --- |
| `/start` on an existing account | no duplicate user row; menu appears |
| Send a message | reply arrives; two rows added |
| `/retry` | last assistant message replaced |
| `/new`, rename, pin, archive, delete | list matches at each step |
| Persona → switch → chat | persona name visible on the persona screen |
| `/lang` → EN → all menus | no missing key strings (`errors.` or raw dotted keys visible = fail) |
| Tools → Summarize | result returned; conversation message count unchanged |
| `/admin` as admin / non-admin | panel / nothing |
| Restart container | bot reconnects; history intact |

## 5. Test data hygiene

- Regression runs use `./data/bot.db` copies, never production.
- `tests/` never touches `./data`.
- Any manual test that creates users must record their ids for cleanup.

## 6. Automation gap

The suite is bottom-heavy: there is **no handler-level regression test**, so R1, R3
and R5-style issues are caught by review and grep, not by CI. Closing this is
TASK-101 and is the top testing priority.

A cheap intermediate step (no aiogram harness needed):

```python
# proposed: tests/test_handler_contract.py
import importlib
from bot.handlers import ROUTERS

def test_router_names_unique():
    names = [r.name for r in ROUTERS]
    assert len(names) == len(set(names))
```

This catches duplicate router registration, not duplicate decorators, but it is
ten lines and prevents a whole class of startup bug.

## 7. Release regression record

Keep a short table in the release notes:

| Version | Date | Suite | Manual walkthrough | Notes |
| --- | --- | --- | --- | --- |
| v1.0.0 | `[UNKNOWN — USER INPUT REQUIRED]` | 32 pass | `[UNKNOWN]` | — |
