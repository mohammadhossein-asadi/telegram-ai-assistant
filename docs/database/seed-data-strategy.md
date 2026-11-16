# Seed Data Strategy

## 1. Principle: the product ships with **no seeded rows**

A fresh deployment starts with an empty database. Nothing is inserted at boot except:

- `schema_version` rows (1, 2) written by the migration runner.
- The **env-configured AI provider**, which exists only in memory
  (`ProviderRegistry.refresh()` reads `Settings`, not the DB).
- A `users` row for someone who messages the bot, and their `user_settings` row lazily
  on first need.

This is deliberate: seeded demo users would pollute real usage statistics, admin
counts and the "total users" number.

## 2. Where "default content" actually lives

| Content | Location | Why not the database |
| --- | --- | --- |
| 10 personalities, 6 styles, 5 tones | `src/services/chat/prompts.py` constants | they are product text, versioned with code, translated in code |
| Tool prompts (summarize/write/explain/coding/translate) | `src/services/tools/service.py` | same |
| UI strings | `src/localization/*.json` | parity-tested |
| Keyboard layouts | `src/bot/keyboards/common.py` | derived from code |
| Model routing keywords | `src/services/ai/router.py` | behaviour, not data |

Consequence: "changing a preset" is a code change, reviewed and tested — not an admin
action. Custom personas/prompts are the user-facing extension mechanism.

## 3. Optional local development seed

[`artifacts/database/seed.sql`](../../artifacts/database/seed.sql) inserts a single
demo user with related settings, one persona, one prompt and two memory facts so a
developer can inspect the UI without chatting.

Rules for that file:

- **Never run against production.** Header says so.
- Idempotent (`INSERT OR IGNORE` on natural keys / explicit ids).
- Uses a reserved-range Telegram id (`900000001`) that will never collide with a real
  account.
- Contains **no API keys**, no tokens, no personal data.
- Not referenced by the application; nothing loads it automatically.

```bash
# local only
sqlite3 ./data/bot.db < artifacts/database/seed.sql
```

## 4. Test data

Tests do **not** use the seed file. `tests/conftest.py` creates a fresh in-memory
database per test and builds exactly the rows it needs:

| Fixture | Creates |
| --- | --- |
| database | `sqlite+aiosqlite:///:memory:` + `create_all` |
| user | one `User` with `telegram_id=1` |
| conversation | one conversation owned by that user |
| fake provider | in-memory `AIProvider` returning a fixed reply |

Benefits: no cross-test coupling, no cleanup, no ordering dependence.

## 5. Production-like data for demos or portfolio screenshots

If demo data is needed (e.g. for a screenshot), it must be generated in a **separate**
database file (`DEMO_DATABASE_URL`) and never merged into `data/bot.db`. Suggested
generator (not implemented): a small script that creates N users, M conversations and
K messages with synthetic Persian/English text.

## 6. Seed data rules (for any future addition)

1. Idempotent by construction.
2. No secrets, no real identifiers, no copyrighted text.
3. Never required for the app to function.
4. Documented in this file and in the implementation log.
5. Removable with a documented `DELETE` without breaking foreign keys.

## 7. Verification

- A fresh `python run.py` against an empty file creates 10 tables and no user rows.
- `artifacts/database/seed.sql` parses and applies cleanly to the schema from
  `artifacts/database/schema.sql` (checked with `sqlite3` during documentation
  generation).
