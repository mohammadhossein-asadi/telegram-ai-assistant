# HANDOFF

> Source of truth for continuing development. Update after each milestone.

## Project overview

Bilingual (Persian/English) text-only AI assistant for Telegram. Interactive
inline menus, customizable personality/tone/style, multiple conversations with
persistent history, per-user memory, AI text tools, model selection, and an
admin panel.

**Developer:** Mohammadhossein Asadi — <https://github.com/mohammadhossein-asadi>

## Technology stack

- Python 3.12 (async-first)
- aiogram 3.x (routers, FSM `MemoryStorage`, inline keyboards)
- SQLAlchemy 2.x async + aiosqlite (SQLite)
- pydantic / pydantic-settings for config + validation
- httpx for OpenAI-compatible chat-completions calls
- pytest / pytest-asyncio for tests
- Docker + Docker Compose

## Implemented features

- [x] Full FA/EN localization (identical key sets, enforced by a test)
- [x] Onboarding language chooser + live language switching (updates UI **and** AI reply language)
- [x] Main menu with all 10 sections, Edit-in-place navigation, Back/Home
- [x] AI chat: context history, typing indicator, long-message splitting,
      safe Markdown→HTML, `/retry` regeneration, per-user concurrency lock
- [x] Multiple conversations: create/switch/rename/archive/delete (confirm), pagination
- [x] Personality: 10 presets, 6 styles, 5 tones, 3 creativity levels, custom instructions
- [x] Model selection from the provider registry
- [x] Memory: toggle, context window, per-user store, clear chat / clear all
- [x] Tools: summarize (4), translate (auto/fa/en), writing (6), explain (3), custom
- [x] Settings incl. response language, emoji, reset with confirmation, privacy screen
- [x] Admin: stats, broadcast, provider add/delete, limits, `/block` `/unblock`
- [x] Usage logging, sliding-window rate limit, daily request cap
- [x] Developer branding section (configurable, non-intrusive)
- [x] Versioned migrations, structured logging, Docker, README, tests

## Current project structure

See [README.md](README.md#project-layout) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Database status

Schema is created at startup by `database/migrations.py` (versioned, currently v1).
Tables: `users`, `user_settings`, `conversations`, `messages`, `user_memory`,
`ai_providers`, `usage_logs`, `schema_version`.
Cascade deletes remove a user's conversations/messages/memory.

## AI provider integration status

- Provider abstraction implemented and unit-tested with a fake provider.
- OpenAI-compatible HTTP client implemented (auth, timeouts, 401/429/error mapping).
- **Live calls are unverified** — the workspace has no API key, and no request
  may be faked. Set `AI_API_KEY` (and optionally `AI_BASE_URL` / `AI_MODEL`) and
  send one message to confirm end-to-end.

## Current development phase

MVP complete and locally tested. Awaiting credentials for live verification.

## Completed tasks

1. Config + logging + service container
2. Localization catalogs + loader
3. ORM models, migrations, repositories
4. Provider abstraction, registry, OpenAI-compatible client
5. Prompt builder + chat engine + tools + memory services
6. Keyboards, views, UI helpers, user middleware
7. All ten handler routers + admin panel
8. Entrypoint, tests, Docker, docs

## Remaining tasks

- [ ] Live smoke test with a real Telegram token and AI key
- [ ] Persist FSM state (Redis) so multi-step flows survive restarts
- [ ] Move rate-limit buckets to a shared store for multi-process deployments
- [ ] Encrypt provider API keys at rest
- [ ] Optional: Alembic baseline for schema evolution
- [ ] Optional: pagination for archived conversations view

## Known issues

- Provider API keys added via the admin panel are stored in plaintext in SQLite.
- Rate limiting is per-process and resets on restart.
- Pending FSM flows are lost on restart (`MemoryStorage`).
- `ChatEngine` writes the user turn **after** a successful provider call; a failed
  request leaves no partial history (intentional, but means no retry payload is stored).

## Important architectural decisions

- Handlers depend on a module-level `container` singleton rather than aiogram DI
  data, keeping handler signatures small while construction stays in one place.
- Conversation access always takes `user_id`; repositories return `None` on
  ownership mismatch to guarantee data isolation.
- Responses are converted from Markdown to **escaped** Telegram HTML, so model
  output cannot inject markup.
- Tools are separate one-shot completions, never mixed into conversation history.
- Branding strings come from config only (`DEVELOPER_*`, `BOT_BRANDING_ENABLED`).

## Next actionable steps

1. Create `.env` from `.env.example`, set `BOT_TOKEN`, `AI_API_KEY`, `ADMIN_IDS`.
2. `python run.py`; send `/start`, pick a language, send a message.
3. Open `/admin` → providers and add a second model to test switching.

## Required environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `BOT_TOKEN` | yes | Telegram bot token |
| `AI_API_KEY` | yes | OpenAI-compatible key |
| `AI_BASE_URL` | no | default `https://api.openai.com/v1` |
| `AI_MODEL` | no | default `gpt-4o-mini` |
| `AI_PROVIDER` | no | provider label (default `openai`) |
| `ADMIN_IDS` | no | comma-separated Telegram IDs |
| `DEFAULT_LANGUAGE` | no | `fa` or `en` |
| `DATABASE_URL` | no | default SQLite file under `./data` |
| `MAX_CONTEXT_MESSAGES` | no | context window (default 20) |
| `USER_RATE_LIMIT` | no | requests per minute |
| `MAX_DAILY_REQUESTS` | no | daily cap per user |
| `DEVELOPER_NAME` / `DEVELOPER_GITHUB` / `DEVELOPER_ROLE` | no | branding |
| `BOT_BRANDING_ENABLED` | no | show developer attribution |
| `LOG_LEVEL` / `BOT_VERSION` | no | ops metadata |
