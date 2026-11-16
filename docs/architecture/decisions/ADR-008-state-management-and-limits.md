# ADR-008 — In-memory FSM, in-process rate buckets, per-user serialisation

- **Status:** Accepted with known limitations (revisit: TASK-201/202)
- **Date:** 2026-11-16
- **Related:** [rate limiting](../../api/rate-limiting.md), [operations runbook](../../devops/operations-runbook.md)

## Context

Multi-step interactions (rename, broadcast text, add provider, custom persona import,
prompt body, tool input) need per-chat state. AI requests must be limited per user to
protect a shared key, and two overlapping requests from one user would produce
confusing ordering and duplicated cost.

The deployment is single-process (ADR-006) and must not require Redis.

## Problem

Where should interaction state and throttling counters live, given a one-container
deployment that may later need to survive restarts or run multiple processes?

## Considered alternatives

| Concern | Options | Verdict |
| --- | --- | --- |
| FSM | `MemoryStorage` / Redis storage / custom SQL `Storage` | **`MemoryStorage` now**; Redis or SQL later |
| Rate limit | in-memory sliding window / DB rows per request / Redis | **in-memory window + DB daily counter** |
| Concurrency | no lock / per-user `asyncio.Lock` / global semaphore | **per-user lock** |
| Daily cap source of truth | separate counter table / `usage_logs` count | **`usage_logs` count** (one source, auditable) |

## Decision

1. **FSM:** `Dispatcher(storage=MemoryStorage())`; state groups declared in
   `src/utils/states.py` (8 groups). `/cancel` clears state. Restart resets flows.
2. **Per-minute limit:** `UsageRepository.check_rate()` keeps a deque of monotonic
   timestamps per Telegram id, prunes older than 60 s, and compares with
   `USER_RATE_LIMIT`.
3. **Daily cap:** `daily_allowed()` counts today's `usage_logs` rows for the user and
   compares with `MAX_DAILY_REQUESTS`. The same table is the audit log, so there is no
   second counter to drift.
4. **Serialisation:** one `asyncio.Lock` per user id guards the chat handler body, so
   a second message waits instead of racing.
5. **Limit enforcement point:** the handler guard runs before any provider call; it
   applies to chat *and* tools.
6. **Documented limits:** counters reset on restart and are per process. This is
   stated in `docs/ARCHITECTURE.md`, the threat model and the roadmap — not treated as
   a hidden property.

## Consequences

**Positive**

- No extra infrastructure; limits work in the default deployment.
- Daily usage is auditable from a single table.
- Locking prevents the most common double-charge pattern (impatient double-send).

**Negative / accepted costs**

- After a restart a user can exceed the per-minute limit once (buckets empty).
- Two processes would each allow the full quota.
- A retried message after a provider failure costs another unit (the failed attempt
  is also logged).

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Restart resets buckets | quota overshoot | acceptable at one-user-per-minute scale; TASK-202 for shared store |
| Lock held during a slow provider call | user appears unresponsive | typing indicator; bounded provider timeout |
| Memory growth of buckets for many users | RAM | pruned deques; ids removed when the window empties (implementation detail to verify under load) |
| FSM lost mid-broadcast | broadcast not sent | admin sees no confirmation; retry manually |

## Verification

- `tests/test_database.py` covers usage-dependent repository behaviour indirectly.
- **Gap:** no test asserts that the limit blocks a handler call. Recommended test:
  set `USER_RATE_LIMIT=1`, call twice, assert the second returns the localized error
  (see [test-cases T-22](../../testing/test-cases.md)).
