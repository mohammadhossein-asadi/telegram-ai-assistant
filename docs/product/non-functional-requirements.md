# Non-Functional Requirements

> **Reading rule:** every number below is either (a) a value that exists in code
> and is therefore a *fact*, or (b) an explicitly labelled **proposed target**
> that has not been measured. Nothing here is a measured benchmark result.

## 1. Performance

| ID | Requirement | Type | Evidence / measurement |
| --- | --- | --- | --- |
| NFR-PERF-001 | Handler overhead (non-AI) must be ≤ 100 ms p95 on the reference host | Proposed target | Measured indirectly via `usage_logs.latency_ms` for AI only; handler timing is not instrumented |
| NFR-PERF-002 | Context sent per request must be bounded | Fact | `MAX_CONTEXT_MESSAGES` default 20, hard range 2–200 (`Field(ge=2, le=200)`) |
| NFR-PERF-003 | A single reply must be delivered in ≤ 4 s p50 with `gpt-4o-mini`-class models | Proposed target | `usage_logs.latency_ms` (exists, unmeasured) |
| NFR-PERF-004 | Tool calls must not add an extra classification request | Fact | `classify_task()` is pure regex; no provider call |
| NFR-PERF-005 | GitHub reads must be cached to avoid rate-limit burn | Fact | TTL cache, default 900 s, `GITHUB_CACHE_TTL` 60–86 400 |
| NFR-PERF-006 | Memory per process must stay small enough for a 512 MB container | Proposed target | No profiling performed; single SQLite engine + in-memory FSM/limits |

## 2. Scalability

| ID | Requirement | Type | Notes |
| --- | --- | --- | --- |
| NFR-SCALE-001 | The system must support one bot process per deployment | Fact | SQLite single-writer; polling model |
| NFR-SCALE-002 | Concurrent in-flight AI requests must be limited per user to 1 | Fact | `asyncio.Lock` per user in `chat.py` |
| NFR-SCALE-003 | Broadcasts must be paced to respect Telegram limits | Fact | Sequential sends with failure counting |
| NFR-SCALE-004 | Horizontal scale-out would require a shared rate-limit store | Known limitation | Documented in `docs/ARCHITECTURE.md`, roadmap P2 |

## 3. Security

| ID | Requirement | Type | Evidence |
| --- | --- | --- | --- |
| NFR-SEC-001 | No credential may exist in version control | Fact | `.env` git-ignored; `.env.example` contains empty placeholders |
| NFR-SEC-002 | All user-scoped queries must be ownership-scoped | Fact | `user_id` parameter pattern in repositories; test T-09 |
| NFR-SEC-003 | User-supplied/model-supplied text must never be interpreted as Telegram HTML | Fact | `escape_html()` runs before any formatting |
| NFR-SEC-004 | Admin actions must require an id in `ADMIN_IDS` | Fact | `Settings.is_admin`, `admin.py` guard |
| NFR-SEC-005 | Blocked users must be unable to invoke any handler | Fact | Middleware returns `None` |
| NFR-SEC-006 | Provider keys added at runtime should be encrypted at rest | Proposed target (open) | Currently plaintext in SQLite — see [threat model](../security/threat-model.md) |

## 4. Privacy

| ID | Requirement | Type | Notes |
| --- | --- | --- | --- |
| NFR-PRIV-001 | Message content must be stored only for the owning user | Fact | `conversations.user_id`, `messages.conversation_id` |
| NFR-PRIV-002 | Users must be able to delete their content | Fact (partial) | Per-conversation delete, `/reset` clears conversations, memory clear; **no full account purge** — `[UNKNOWN — USER INPUT REQUIRED]` |
| NFR-PRIV-003 | No third-party analytics or telemetry may be embedded | Fact | Only outbound calls: Telegram API, AI endpoint, api.github.com |
| NFR-PRIV-004 | A privacy screen must explain storage in plain language | Fact | Settings → Privacy (`set:privacy`) |

## 5. Reliability & availability

| ID | Requirement | Type | Notes |
| --- | --- | --- | --- |
| NFR-REL-001 | Upstream AI failure must produce a localized error, never a crash | Fact | `except Exception` around `provider.chat`, logged |
| NFR-REL-002 | GitHub failure must produce a fallback message | Fact | `_get()` returns `None` on 4xx/5xx/timeouts |
| NFR-REL-003 | Restart must not corrupt the database | Fact | SQLite WAL-less default with transactional writes; docker volume persists `./data` |
| NFR-REL-004 | The process must restart automatically in Docker | Fact | `restart: unless-stopped` |
| NFR-REL-005 | Multi-step flows may be lost on restart | Accepted limitation | `MemoryStorage`; roadmap P2 |
| NFR-REL-006 | Availability target of 99 % monthly | Proposed target | Not measured; depends on host |

## 6. Maintainability

| ID | Requirement | Type | Evidence |
| --- | --- | --- | --- |
| NFR-MAINT-001 | Layer boundaries must be respected: handlers → services → repositories | Convention | `docs/ARCHITECTURE.md`, ADR-001 |
| NFR-MAINT-002 | No SQL in handlers | Convention | Repositories own sessions |
| NFR-MAINT-003 | New user-visible strings require both catalogs | Enforced | `tests/test_localization.py` |
| NFR-MAINT-004 | Formatting/lint gate | **Not implemented** | No ruff/black config in repo; proposed P2 |
| NFR-MAINT-005 | Type hints on public functions | Convention | `from __future__ import annotations` everywhere |
| NFR-MAINT-006 | Dependency count must stay minimal | Fact | 6 runtime deps + 2 dev deps |

## 7. Testability

| ID | Requirement | Type | Evidence |
| --- | --- | --- | --- |
| NFR-TEST-001 | The suite must run without network access | Fact | Fake provider in `tests/test_chat_engine.py`; in-memory SQLite in `tests/conftest.py` |
| NFR-TEST-002 | The suite must pass on a clean checkout | Fact | 32 tests, `pytest -q` |
| NFR-TEST-003 | Repositories must be testable without aiogram | Fact | Direct repository tests |
| NFR-TEST-004 | CI must run the suite on every push/PR | Proposed (workflow provided) | `.github/workflows/ci.yml` |

## 8. Accessibility & UX quality

| ID | Requirement | Type | Notes |
| --- | --- | --- | --- |
| NFR-A11Y-001 | Every screen must be operable by tapping only | Fact | Inline keyboards for all 10 sections |
| NFR-A11Y-002 | Copy must be RTL-safe (no bidi-breaking punctuation at line start) | Convention | See [accessibility](../design/accessibility.md) |
| NFR-A11Y-003 | Errors must state what to do next | Convention | e.g. `errors.ai` includes upstream detail |
| NFR-A11Y-004 | Text must remain readable in Telegram's smallest font on a 5" screen | Proposed target | Chunking + short menus |

## 9. Localization & internationalization

| ID | Requirement | Type | Evidence |
| --- | --- | --- | --- |
| NFR-I18N-001 | Two locales must always have identical key sets | Enforced | test T-14 |
| NFR-I18N-002 | Adding a locale must not require code changes beyond the catalog + `SUPPORTED_LANGUAGES` | Fact | `loc` loader reads JSON files |
| NFR-I18N-003 | Dates/numbers must not be hard-coded into strings | Convention | Timestamps rendered by Telegram, not the bot |
| NFR-I18N-004 | Persian text must use correct ZWNJ/ZWJ where required | Convention | Existing `fa.json` contains ZWNJ (U+200C) sequences |

## 10. Observability

| ID | Requirement | Type | Notes |
| --- | --- | --- | --- |
| NFR-OBS-001 | Structured single-line logs with timestamp/level/logger/message | Fact | `core/logging.py` format |
| NFR-OBS-002 | AI calls must be logged with latency and token counts | Fact | `usage_logs` |
| NFR-OBS-003 | Failed AI calls must log the provider error text | Fact | `usage_logs.error` (full text) + warning log |
| NFR-OBS-004 | No secret may appear in logs | Requirement | Provider keys never passed to `log.*` |
| NFR-OBS-005 | Error reporting to a third-party service | Not implemented | `[UNKNOWN — USER INPUT REQUIRED]` |

## 11. Data consistency & recovery

| ID | Requirement | Type | Notes |
| --- | --- | --- | --- |
| NFR-DATA-001 | Each repository method must commit atomically | Fact | `async with self.db.session()` + commit per operation |
| NFR-DATA-002 | Conversation delete must remove messages | Fact | ORM cascade + `ondelete="CASCADE"` |
| NFR-DATA-003 | Migration must be safe to re-run | Fact | version check + column existence check |
| NFR-DATA-004 | Backup must be possible by copying one file (or `sqlite3 .backup`) | Fact | Single-file DB |
| NFR-DATA-005 | RPO/RTO | Proposed: RPO 24 h (daily copy), RTO 15 min | Not implemented; see [backup-recovery](../devops/backup-recovery.md) |

## 12. Compliance

| ID | Requirement | Type | Notes |
| --- | --- | --- | --- |
| NFR-COMP-001 | No PII beyond Telegram profile fields (id, username, first name) | Fact | `users` table |
| NFR-COMP-002 | Data subject deletion request | Manual (SQL) today | Documented in [operations-runbook](../devops/operations-runbook.md) |
| NFR-COMP-003 | Telegram Bot Platform terms must be respected (no spam, no scraping) | Requirement | Broadcast pacing; public GitHub reads only |
| NFR-COMP-004 | AI provider terms — user content is sent to the configured endpoint | Requirement | Must be disclosed in the privacy screen |

## 13. Cost

| ID | Requirement | Type | Notes |
| --- | --- | --- | --- |
| NFR-COST-001 | Per-user daily cap must bound spend | Fact | `MAX_DAILY_REQUESTS` |
| NFR-COST-002 | Tool actions must be single completion calls | Fact | `run_tool()` |
| NFR-COST-003 | Prompt size must be bounded by history window + ≤ 20 memories | Fact | `build_system_prompt` |

## 14. Target reference environment

| Item | Value |
| --- | --- |
| CPU | 1–2 vCPU (proposed) |
| RAM | 256–512 MB (proposed) |
| Disk | 1 GB + database growth (proposed) |
| Python | 3.12 (Dockerfile) |
| Network | Outbound HTTPS to `api.telegram.org`, AI base URL, `api.github.com` |
| OS | Any host with Docker; no OS-specific code paths |
