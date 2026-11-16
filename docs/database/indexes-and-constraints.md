# Indexes and Constraints

Actual state, as declared in `src/database/models/__init__.py`. No index in this
document is aspirational; proposed ones are marked **PROPOSED**.

## 1. Indexes

| # | Index | Table | Columns | Kind | Access pattern served |
| --- | --- | --- | --- | --- | --- |
| 1 | `ix_users_telegram_id` | users | `telegram_id` | UNIQUE btree | every update: `get_or_create` by Telegram id |
| 2 | `ix_user_settings_user_id` | user_settings | `user_id` | UNIQUE btree | 1:1 lookup by user |
| 3 | `ix_conversations_user_id` | conversations | `user_id` | btree | "my conversations" list, ownership checks |
| 4 | `ix_messages_conversation_id` | messages | `conversation_id` | btree | context load, listing, clear |
| 5 | `ix_personas_user_id` | personas | `user_id` | btree | persona list |
| 6 | `ix_prompts_user_id` | prompts | `user_id` | btree | prompt list |
| 7 | `ix_user_memory_user_id` | user_memory | `user_id` | btree | memory injection |
| 8 | `ix_usage_logs_user_id` | usage_logs | `user_id` | btree | daily count, per-user stats |
| 9 | *(implicit)* | all | `id` | PK | identity, ordering |

### Query-to-index mapping

| Query | Source | Index used |
| --- | --- | --- |
| `SELECT ... FROM users WHERE telegram_id = ?` | `UserRepository.get_by_telegram_id` | #1 |
| `SELECT ... FROM conversations WHERE user_id=? ORDER BY is_pinned DESC, updated_at DESC` | `ConversationRepository.list` | #3 (sort is in-memory/partial) |
| `SELECT ... FROM messages WHERE conversation_id=? ORDER BY id DESC LIMIT n` | `MessageRepository.recent` | #4 |
| `SELECT COUNT(*) FROM usage_logs WHERE user_id=? AND created_at >= ?` | `UsageRepository.count_today` | #8 (then filter) |
| `SELECT ... FROM ai_providers WHERE name = ?` | `ProviderRepository.get_by_name` | UK on `name` |
| `SELECT ... FROM personas WHERE user_id=? AND name=?` | uniqueness + lookup | `uq_persona_name` |
| `SELECT ... FROM user_memory WHERE user_id=?` | `MemoryRepository.list` | #7 |

### Missing indexes (measured relevance: hypothetical until load exists)

| Candidate | Why it would help | Cost | Status |
| --- | --- | --- | --- |
| `messages(conversation_id, id)` composite | avoids backward scan on `ORDER BY id DESC` | extra btree per row | **PROPOSED** (low value at current volume) |
| `usage_logs(user_id, created_at)` composite | daily count scans then filters | small | **PROPOSED** |
| `usage_logs(created_at)` | admin "today" aggregate across users | small | **PROPOSED** |
| `conversations(user_id, updated_at DESC)` | list ordering without sort | small | **PROPOSED** |

**Do not add these blindly.** SQLite with tens of thousands of rows handles the
current queries instantly; measure with `EXPLAIN QUERY PLAN` before adding write cost.

## 2. Constraints

### 2.1 Primary keys
All tables: surrogate `id INTEGER PRIMARY KEY` (SQLite rowid alias). `schema_version`
uses `version` as PK.

### 2.2 Unique constraints

| Name | Table | Columns | Enforced by | Violation behaviour |
| --- | --- | --- | --- | --- |
| `ix_users_telegram_id` | users | `telegram_id` | index | `get_or_create` re-selects; otherwise `IntegrityError` |
| `ix_user_settings_user_id` | user_settings | `user_id` | index | `get_or_create` returns existing |
| `uq_persona_name` | personas | `user_id`, `name` | table constraint | `PersonaRepository.create()` looks up by name first and updates the existing row (upsert) |
| `uq_user_memory_key` | user_memory | `user_id`, `key` | table constraint | `set()` performs upsert |
| *(unnamed)* | ai_providers | `name` | table constraint | admin handler reports "name exists" |

### 2.3 Foreign keys

| Child | Column | Parent | `ondelete` | ORM cascade |
| --- | --- | --- | --- | --- |
| user_settings | user_id | users.id | CASCADE | yes |
| personas | user_id | users.id | CASCADE | yes |
| conversations | user_id | users.id | CASCADE | yes |
| messages | conversation_id | conversations.id | CASCADE | yes |
| prompts | user_id | users.id | CASCADE | yes |
| user_memory | user_id | users.id | CASCADE | yes |
| usage_logs | user_id | users.id | SET NULL | no (audit rows preserved) |

**Critical nuance:** SQLite enforces `ON DELETE` **only when
`PRAGMA foreign_keys=ON`**, and this project does not set that pragma. Therefore the
*effective* cascade today is the ORM's `cascade="all, delete-orphan"` on the five
`User` relationships (settings, conversations, memories, personas, prompts). Those
cover every user-owned table **except** `usage_logs`, which has no relationship on
`User` at all.

Consequence: deleting a `User` row would remove five child sets but leave
`usage_logs` rows behind with a dangling `user_id` (no `SET NULL` without the pragma,
and no `delete_user` repository method exists today).

> **There is no supported account-deletion path.** A real purge must delete children
> explicitly (or enable `PRAGMA foreign_keys=ON`) and decide what happens to audit
> rows. Recorded as known issue K-4 in [`HANDOFF.md`](../../HANDOFF.md).

### 2.4 Not-null constraints
Every column is `NOT NULL` unless listed as nullable in the
[data dictionary](data-dictionary.md). Nullable by design: `username`, `first_name`,
`last_seen_at`, `custom_instructions`, `model`, `provider`,
`current_conversation_id`, `default_persona_id`, `summary`, `persona_id`, `error`,
`latency_ms`, `usage_logs.user_id`.

### 2.5 Check constraints
**None exist.** Enum-like columns are free strings validated by fallback maps in
`services/chat/prompts.py`. Rationale: adding a CHECK requires a table rebuild in
SQLite, and a bad value degrading to a default is preferable to a hard write failure
for a chat product. Trade-off accepted; documented in
[database-design](database-design.md#8-known-modelling-gaps).

### 2.6 Defaults

| Setting | Where | Notes |
| --- | --- | --- |
| `created_at`/`updated_at` | Python `default=now`, `onupdate=now` | DB default `CURRENT_TIMESTAMP` also in DDL |
| booleans | Python defaults (`False`/`True`) | see data dictionary |
| `user_settings.personality` etc. | Python defaults | applied on insert |
| `usage_logs.prompt_tokens`/`completion_tokens` | `0` | missing usage block |
| `messages.role` | caller supplies | no default |

## 3. Referential integrity rules worth testing

1. Deleting a conversation removes its messages (ORM cascade).
2. Deleting a user removes settings, personas, conversations (and messages), prompts,
   memory.
3. `usage_logs` rows survive (no cascade) — verify intended behaviour before any
   account-deletion feature is built.
4. Calling `create()` with an existing `(user_id, name)` persona updates instructions/emoji instead of inserting; a raw `INSERT` bypassing the repository would raise `IntegrityError`.
