# Business Rules

Rules the system enforces regardless of interface. Each rule names the code that
implements it; a rule without an implementation is marked **policy** (human
process) rather than pretending to be enforced.

## 1. Identity & access

| ID | Rule | Enforced by | Type |
| --- | --- | --- | --- |
| BR-001 | A Telegram account maps to exactly one `users` row; `telegram_id` is unique | `UNIQUE(telegram_id)` + `get_or_create` | Enforced |
| BR-002 | A new user is created with the deployment's `DEFAULT_LANGUAGE` and an empty settings row on first `get_or_create` of settings | `UserRepository.get_or_create`, `SettingsRepository.get_or_create` | Enforced |
| BR-003 | A blocked user cannot invoke any handler | `UserMiddleware` early return | Enforced |
| BR-004 | Admin rights are derived only from `ADMIN_IDS`, never from the database or a chat command | `Settings.is_admin()` | Enforced |
| BR-005 | There are no roles other than "user" and "admin"; no per-user permissions exist | Model schema (no roles table) | Structural |

## 2. Conversation ownership

| ID | Rule | Enforced by |
| --- | --- | --- |
| BR-006 | Only the owner may read, rename, pin, archive, summarise, export or delete a conversation | every repository method takes `user_id` and filters on it |
| BR-007 | Deleting a conversation deletes its messages in the same transaction | ORM cascade + `ondelete="CASCADE"` |
| BR-008 | A user always has an active conversation when chatting; one is created if none exists | `helpers.ensure_conversation()` |
| BR-009 | Archiving the active conversation clears the active pointer | `cb_archive` / `cb_delete_confirm` update `current_conversation_id=None` |
| BR-010 | Conversation titles are at most 120 characters; the UI derives a title from the first message or the user supplies one | `String(120)`, `utils.text.derive_title` |

## 3. Chat execution

| ID | Rule | Enforced by |
| --- | --- | --- |
| BR-011 | History is written only after a successful provider response | `ChatEngine.respond()` order of operations |
| BR-012 | The provider receives at most `MAX_CONTEXT_MESSAGES` prior turns plus the new message | `messages.recent(conversation.id, limit)` |
| BR-013 | One user's requests are serialised | per-user `asyncio.Lock` in `chat.py` |
| BR-014 | `/retry` replaces the last assistant message rather than appending | `delete_last_assistant` then `respond` |
| BR-015 | A tool invocation never writes to `messages` | `run_tool()` path has no `messages.add` |
| BR-016 | Conversation `updated_at` is refreshed on each successful turn, driving list order | `conversations.touch()` |

## 4. Model resolution

| ID | Rule | Enforced by |
| --- | --- | --- |
| BR-017 | Precedence is conversation override → auto-routing (if enabled) → account setting → first provider | `_resolve_model()` |
| BR-018 | An unknown model string never raises; it falls back to the first configured provider | `ProviderRegistry.resolve()` |
| BR-019 | Auto-routing never calls a model to classify; classification is regex-based | `router.classify_task()` |
| BR-020 | The environment-configured provider always exists in the registry, even with zero DB rows | `ProviderRegistry.refresh()` |

## 5. Prompt composition

| ID | Rule | Enforced by |
| --- | --- | --- |
| BR-021 | A conversation's persona overrides the account's personality preset | `build_system_prompt(persona_instructions=...)` |
| BR-022 | When personality is `custom`, the preset is replaced by the custom text (not appended) | `prompts.py` branch |
| BR-023 | Reply language `auto` uses the detected input language, else the UI language | `detect_language()` + `build_system_prompt` |
| BR-024 | At most 20 memories are injected | `memories[:20]` |
| BR-025 | Temperatures are exactly 0.2 / 0.7 / 1.1 for low / balanced / high | `TEMPERATURES` map |

## 6. Limits & cost

| ID | Rule | Enforced by |
| --- | --- | --- |
| BR-026 | A user may send at most `USER_RATE_LIMIT` AI requests per rolling 60 s | `UsageRepository.check_rate` |
| BR-027 | A user may consume at most `MAX_DAILY_REQUESTS` AI requests per UTC day | `UsageRepository.daily_allowed` |
| BR-028 | Limits apply to chat and tool calls alike (both go through the guard in `chat.py`) | handler guard before dispatch |
| BR-029 | Usage rows are immutable audit records; a failed call is logged with `success=False` and the error text | `usage.log()` |
| BR-030 | Usage rows for a deleted user are retained with `user_id=NULL` | `ondelete="SET NULL"` |

## 7. Localization

| ID | Rule | Enforced by |
| --- | --- | --- |
| BR-031 | Every user-visible string comes from a catalog; no inline human text in handlers | convention + review; tests enforce parity, not absence of literals |
| BR-032 | Both catalogs must contain the same key set | `tests/test_localization.py` |
| BR-033 | An unknown language falls back to `DEFAULT_LANGUAGE` at load time | `localization/__init__.py` |
| BR-034 | Persian UI implies Persian AI replies by default (`response_language='auto'`) | settings default + prompts |

## 8. Formatting & delivery

| ID | Rule | Enforced by |
| --- | --- | --- |
| BR-035 | Model output is escaped before Markdown conversion; model HTML is never trusted | `markdown_to_telegram_html` |
| BR-036 | Delivery chunks are ≤ 3500 chars for AI output | `ui.send_ai/answer_ai` |
| BR-037 | A failed HTML send falls back to plain text rather than dropping the reply | `except TelegramBadRequest` fallback |
| BR-038 | "Message is not modified" errors on edit are ignored, not surfaced | `safe_edit` |

## 9. Data retention

| ID | Rule | Enforced by | Notes |
| --- | --- | --- | --- |
| BR-039 | Conversations and messages persist until the user deletes them or resets | `delete`, `/reset` | No TTL job |
| BR-040 | Memory persists until cleared | `MemoryRepository.clear` | |
| BR-041 | Usage logs are retained indefinitely | no delete path | Policy: rotate manually if needed |
| BR-042 | Account deletion is a manual operator action (SQL) | — | **Policy**, documented in the runbook |

## 10. Provider & secret handling

| ID | Rule | Enforced by | Notes |
| --- | --- | --- | --- |
| BR-043 | Environment keys are read from settings only; never written back to the DB | `ProviderRegistry` | |
| BR-044 | Admin-added provider keys are stored in the local database | `ai_providers.api_key` | Known risk; encryption planned (TASK-104) |
| BR-045 | Secrets must never be logged or echoed to users | review + `str(exc)[:300]` truncation | No automated test |

## 11. Broadcast

| ID | Rule | Enforced by |
| --- | --- | --- |
| BR-046 | A broadcast targets every known user id, including blocked users | `users.all_ids()` |
| BR-047 | A per-recipient failure does not abort the broadcast | per-send `try/except`, counters |
| BR-048 | Broadcast is available only to admins | `is_admin` guard |

## 12. Change-management rules (policy)

| ID | Rule |
| --- | --- |
| BR-049 | A schema change requires a new `SCHEMA_VERSION` step and an idempotent column check |
| BR-050 | A new user-visible string requires entries in both catalogs in the same commit |
| BR-051 | An architectural decision that changes layering requires an ADR before merge |
| BR-052 | `main` must be green; a failing suite blocks merge |
| BR-053 | No credential may be committed, including in tests, docs or fixtures |
