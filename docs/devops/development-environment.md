# Development Environment

Verified by running these commands in a Linux container with Python 3.12.

## 1. Prerequisites

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.12 (3.11 likely works, untested) | `X | None` syntax and `dict[str,...]` used throughout |
| pip | bundled with Python | no Poetry/uv/Pipenv in the repo |
| Git | any | |
| Docker | only for container testing | not needed for `pytest` |

**No Node.js, no database server, no Redis.** The project is pure Python + SQLite.

## 2. First-time setup

```bash
git clone https://github.com/mohammadhossein-asadi/telegram-ai-assistant.git
cd telegram-ai-assistant

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements-dev.txt
cp .env.example .env               # then fill BOT_TOKEN and AI_API_KEY
```

`requirements-dev.txt` includes `-r requirements.txt` plus pytest/pytest-asyncio.

## 3. Running the bot locally

```bash
python run.py
```

`run.py` inserts `src` on `sys.path` and calls `bot.main.main()`. Expected log lines:

```
INFO  database migrations applied (schema_version=2)
INFO  providers loaded: 1
INFO  bot started (long polling)
```

If `BOT_TOKEN` is empty the process exits with a clear message — that is
`validate_runtime()` doing its job, not a crash to debug.

### Without a Telegram token

You can still work on everything except live messaging:

```bash
pytest -q                 # 32 tests, no network, no token
```

## 4. Database during development

| Scenario | Command |
| --- | --- |
| Default file DB | `DATABASE_URL=sqlite+aiosqlite:///./data/bot.db` (from `.env`) |
| Fresh start | stop the bot, `rm -f data/bot.db`, start again |
| Inspect | `sqlite3 data/bot.db ".tables"` / `.schema users` |
| Demo rows | `sqlite3 data/bot.db < artifacts/database/seed.sql` (**dev only**) |

`Database._ensure_sqlite_dir()` creates `./data` if missing.

## 5. Common tasks

| Task | Command |
| --- | --- |
| Run all tests | `pytest -q` |
| Run one file | `pytest tests/test_text.py -v` |
| Run one test | `pytest tests/test_chat_engine.py::test_respond_persists_both_turns -v` |
| Syntax check | `python -m compileall -q src` |
| Format/lint | **no linter configured** (TASK-103); if you use ruff locally, do not reformat unrelated files |
| Check imports | `python -c "import sys;sys.path.insert(0,'src');import bot.main"` |

## 6. Project layout reminders

- Imports are **top-level** (`from core.config import ...`), because `run.py` and
  `PYTHONPATH=/app/src` put `src` on the path. Running `python src/run.py` will not work.
- Tests import `database`, `services`, etc. the same way; `pytest.ini` sets
  `testpaths = tests` and `asyncio_mode = auto`.
- No `pyproject.toml`, so there is no `pip install -e .`.

## 7. Environment variables for development

Minimum to boot: `BOT_TOKEN`.
Minimum to chat: `BOT_TOKEN` + `AI_API_KEY`.
Optional: `ADMIN_IDS` (your own Telegram id for admin screens), `LOG_LEVEL=DEBUG`.

Full table: [environment variables](environment-variables.md).

## 8. Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `SystemExit` with "BOT_TOKEN is missing" | empty token | fill `.env` |
| `AIError 401` in chat | wrong key/base URL | check `AI_API_KEY`, `AI_BASE_URL` |
| `database is locked` | two processes on one file | stop the second process |
| `ModuleNotFoundError: core` | ran a file directly instead of `run.py`/pytest | use `python run.py` |
| `KeyError` in a message | missing locale key | add to both JSON catalogs |
| Tests hang | a real network call leaked in | the suite should never hit the network; find the offending test |
| `pytest` collects 0 tests | ran outside the repo root | `cd` to the repo root |

## 9. Editor setup

| File | Purpose |
| --- | --- |
| `.editorconfig` | UTF-8, LF, 4 spaces (Python), trim trailing whitespace |
| `.cursor/rules/*.mdc` | rules for Cursor |
| `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` | tool-specific instruction adapters pointing at `AGENTS.md` |

## 10. What "done" means locally

1. `pytest -q` passes.
2. `python -m compileall -q src` passes.
3. The bot boots and answers `/start` (if you have a token).
4. Both locale files are updated for any new string.
