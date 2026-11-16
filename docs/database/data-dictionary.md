# Data Dictionary

Every column of every table, with type, nullability, default, constraints, source in
code and notes. Types are the SQLAlchemy declaration (SQLite storage differs slightly,
e.g. `BOOLEAN` is `0/1`).

Legend: **PK** primary key · **FK** foreign key · **UK** unique · **NN** not null.

## 1. `users`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | autoincrement | PK | surrogate |
| `telegram_id` | BigInteger | ✔ | — | UK | Telegram user id; the natural key |
| `username` | String(64) | ✘ | NULL | — | may change or be absent |
| `first_name` | String(128) | ✘ | NULL | — | display only |
| `language` | String(5) | ✔ | `fa` (settings default) | — | `fa` \| `en` |
| `is_blocked` | Boolean | ✔ | `false` | — | checked by middleware |
| `last_seen_at` | DateTime(tz) | ✘ | NULL | — | **not currently updated** |
| `created_at` | DateTime(tz) | ✔ | `now()` | — | |
| `updated_at` | DateTime(tz) | ✔ | `now()` + `onupdate` | — | |

Source: `models/__init__.py::User`. Repository: `repositories/users.py`.

## 2. `user_settings`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | autoincrement | PK | |
| `user_id` | Integer | ✔ | — | FK→users.id, UK | one settings row per user |
| `personality` | String(32) | ✔ | `helpful` | — | 10 presets in `prompts.py` |
| `style` | String(32) | ✔ | `friendly` | — | 6 presets |
| `tone` | String(32) | ✔ | `neutral` | — | 5 presets |
| `creativity` | String(16) | ✔ | `balanced` | — | `low` 0.2 / `balanced` 0.7 / `high` 1.1 |
| `memory_enabled` | Boolean | ✔ | `true` | — | gates memory injection |
| `response_language` | String(8) | ✔ | `auto` | — | `auto` \| `fa` \| `en` |
| `emoji_enabled` | Boolean | ✔ | `true` | — | prompt hint only |
| `custom_instructions` | Text | ✘ | NULL | — | user appendix to system prompt |
| `model` | String(128) | ✘ | NULL | — | preferred model |
| `provider` | String(64) | ✘ | NULL | — | preferred provider name |
| `current_conversation_id` | Integer | ✘ | NULL | loose id | active conversation |
| `default_persona_id` | Integer | ✘ | NULL | loose id | applied to new conversations |
| `auto_routing` | Boolean | ✔ | `false` | — | enables `ModelRouter` |
| `created_at` / `updated_at` | DateTime(tz) | ✔ | now / onupdate | — | |

## 3. `personas`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | autoincrement | PK | |
| `user_id` | Integer | ✔ | — | FK→users.id | CASCADE |
| `name` | String(80) | ✔ | — | UK(user_id,name) | truncated to 80 chars; `create()` upserts by name |
| `instructions` | Text | ✔ | — | — | system-level instruction block |
| `emoji` | String(8) | ✔ | `🎭` | — | label in UI |
| `is_default` | Boolean | ✔ | `false` | — | one logical default |
| timestamps | DateTime(tz) | ✔ | — | — | |

Limits: name 1–80 (repository validates length/emptiness); instructions non-empty.

## 4. `conversations`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | autoincrement | PK | |
| `user_id` | Integer | ✔ | — | FK→users.id | CASCADE |
| `title` | String(120) | ✔ | `New chat` | — | user-renamable |
| `is_archived` | Boolean | ✔ | `false` | — | hidden from default list |
| `is_pinned` | Boolean | ✔ | `false` | — | sorted first |
| `summary` | Text | ✘ | NULL | — | injected into system prompt |
| `persona_id` | Integer | ✘ | NULL | *no FK* | dangling ids ignored |
| `model` | String(128) | ✘ | NULL | — | per-conversation override |
| timestamps | DateTime(tz) | ✔ | — | — | `updated_at` touched per turn |

## 5. `messages`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | autoincrement | PK | ordering proxy |
| `conversation_id` | Integer | ✔ | — | FK→conversations.id | CASCADE |
| `role` | String(16) | ✔ | — | — | `system`/`user`/`assistant` |
| `content` | Text | ✔ | — | — | raw text as sent/received |
| timestamps | DateTime(tz) | ✔ | — | — | |

Writes: `add_user`, `add_assistant`, `delete_last_assistant`; reads:
`recent(limit)`, `last`, `count`, `all_for_conversation`.

## 6. `prompts`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | autoincrement | PK | |
| `user_id` | Integer | ✔ | — | FK→users.id | CASCADE |
| `title` | String(100) | ✔ | — | — | |
| `body` | Text | ✔ | — | — | may contain `{placeholder}` |
| `category` | String(50) | ✔ | `general` | — | free-form label |
| timestamps | DateTime(tz) | ✔ | — | — | |

## 7. `user_memory`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | | PK | |
| `user_id` | Integer | ✔ | | FK→users.id | CASCADE |
| `key` | String(120) | ✔ | | UK(user_id,key) | reserved word → quoted in DDL |
| `value` | Text | ✔ | | — | |
| timestamps | DateTime(tz) | ✔ | | — | |

Upsert: `set()` updates value when the key exists. Injection cap: 20 facts.

## 8. `ai_providers`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | | PK | |
| `name` | String(64) | ✔ | | UK | used by `resolve`/`find_by_model` |
| `base_url` | String(255) | ✔ | | — | no trailing-slash normalisation documented |
| `model` | String(128) | ✔ | | — | default model for this provider |
| `api_key` | Text | ✔ | | — | **plaintext** (ADR-005) |
| `is_active` | Boolean | ✔ | `true` | — | inactive rows skipped |
| `capabilities` | String(255) | ✔ | `general` | — | csv of task classes |
| timestamps | DateTime(tz) | ✔ | | — | |

## 9. `usage_logs`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `id` | Integer | ✔ | | PK | |
| `user_id` | Integer | ✘ | NULL | FK→users.id, SET NULL | NULL for system-level calls |
| `action` | String(32) | ✔ | `chat` | — | `chat`,`summarize`,`translate`,`write`,`explain`,`coding`,`custom`,`test` |
| `provider` | String(64) | ✘ | NULL | — | provider name |
| `model` | String(128) | ✘ | NULL | — | model used |
| `success` | Boolean | ✔ | `true` | — | false for failed attempts |
| `error` | Text | ✘ | NULL | — | truncated message |
| `latency_ms` | Integer | ✘ | NULL | — | wall time of the call |
| `prompt_tokens` | Integer | ✔ | `0` | — | 0 when provider omits usage |
| `completion_tokens` | Integer | ✔ | `0` | — | idem |
| timestamps | DateTime(tz) | ✔ | | — | `created_at` is the quota window |

Queries: `log`, `count_today`, `count_total`, `token_totals`, `check_rate`,
`daily_allowed`.

## 10. `schema_version`

| Column | Type | NN | Default | Keys | Notes |
| --- | --- | --- | --- | --- | --- |
| `version` | Integer | ✔ | — | PK | 1, 2 |
| `description` | Text | ✘ | NULL | — | human label |
| `applied_at` | Timestamp | ✘ | `CURRENT_TIMESTAMP` | — | |

## 11. Value domains (application-level)

| Domain | Allowed values | Where defined | Invalid value behaviour |
| --- | --- | --- | --- |
| `users.language` | `fa`, `en` | `config.SUPPORTED_LANGUAGES` | falls back to `DEFAULT_LANGUAGE` |
| `user_settings.personality` | `helpful`, `professional`, `friendly`, `creative`, `teacher`, `coach`, `analyst`, `philosopher`, `hacker`, `poet` | `chat/prompts.py` | unknown → `helpful` |
| `user_settings.style` | `concise`, `friendly`, `detailed`, `bullet`, `story`, `academic` | same | unknown → `friendly` |
| `user_settings.tone` | `neutral`, `formal`, `casual`, `humorous`, `empathetic` | same | unknown → `neutral` |
| `user_settings.creativity` | `low`, `balanced`, `high` | same | unknown → 0.7 |
| `user_settings.response_language` | `auto`, `fa`, `en` | `config` | unknown → `auto` |
| `messages.role` | `system`, `user`, `assistant` | convention | not validated |
| `ai_providers.capabilities` | subset of `general, coding, reasoning, creative, translation, summarization` | `ai/registry.py` | unknown entries ignored |
| `usage_logs.action` | free string ≤ 32 | callers | not validated |

## 12. Migration-relevant columns (v2 additions)

`personas`, `prompts`, `user_settings.auto_routing`, `conversations.is_pinned`,
`conversations.summary`, `conversations.persona_id`, `conversations.model`,
`usage_logs.prompt_tokens`, `usage_logs.completion_tokens`, `usage_logs.latency_ms`
— see [migrations-strategy](migrations-strategy.md).
