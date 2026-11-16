# Performance Testing

## 1. Honest starting point

**No benchmark has been run against this codebase.** There is no load-test script, no
latency baseline, and no profiling result committed. Everything below is either
(a) a structural fact about the code or (b) a **proposed target**, clearly labelled.

Any claim such as "handles 100 concurrent users" would be fabricated. Do not add one.

## 2. Where latency comes from

```mermaid
flowchart LR
    A[Telegram polling] --> B[Middleware: 1 SELECT]
    B --> C[Handler: 1-2 SELECTs]
    C --> D[Provider call<br/>hundreds of ms to tens of seconds]
    D --> E[2 INSERTs + 1 usage INSERT]
    E --> F[Telegram sendMessage]
```

| Stage | Expected magnitude | Dominates? |
| --- | --- | --- |
| Middleware user lookup | ~1 ms (indexed) | no |
| Context load (20 messages) | ~1–3 ms | no |
| **Provider call** | **0.5–30 s** | **yes** |
| Persistence (3 inserts) | ~2–5 ms | no |
| Telegram send | ~100–300 ms | no |

**Conclusion:** application-level optimisations (query tuning, caching) are irrelevant
next to provider latency. Effort belongs in UX (typing indicator, timeouts) and cost
(context bounds), not micro-optimisation.

## 3. Structural limits

| Resource | Limit | Source |
| --- | --- | --- |
| Concurrent provider calls | unbounded per process | no semaphore |
| Concurrent DB writes | 1 (SQLite writer) | engine |
| Messages per context | 20 (configurable 2–200) | `MAX_CONTEXT_MESSAGES` |
| Input size | 4096 chars | Telegram |
| Output chunk | 3500 chars | `split_message` |
| Memory facts injected | 20 | prompt builder |
| Users per broadcast | all users, sequential | admin handler |

## 4. Proposed targets (not measured)

| Metric | Proposed target | Rationale |
| --- | --- | --- |
| Middleware + handler CPU time (no provider) | < 20 ms p95 | keeps bot overhead negligible |
| Context load for 20 messages | < 10 ms | indexed query |
| Persistence of one turn | < 15 ms | three inserts |
| End-to-end reply (excluding provider) | < 400 ms p95 | dominated by Telegram send |
| Memory footprint idle | < 150 MB | Python + aiogram + SQLAlchemy |
| DB size per 10k messages | < 20 MB | text-dominated |

These are engineering targets for a future benchmark, not results.

## 5. How to measure (procedure to run)

### 5.1 Application overhead without an AI provider

A pytest benchmark with the fake provider isolates everything except the network:

```python
# proposed: benchmarks/test_overhead.py (does not exist yet)
async def test_chat_overhead(benchmark, env):
    engine, user, conv = env          # in-memory DB, fake provider
    benchmark(lambda: asyncio.run(engine.respond(user, conv, "hello")))
```

Acceptance: p95 under the targets in §4.

### 5.2 Database query plans

```sql
EXPLAIN QUERY PLAN
SELECT * FROM messages WHERE conversation_id = 1 ORDER BY id DESC LIMIT 20;
-- expect: SEARCH messages USING INDEX ix_messages_conversation_id
```

Run for: conversation list, message recent, usage count today, user lookup.

### 5.3 End-to-end with a real provider

| Step | Tool |
| --- | --- |
| Send N messages from one account | manual or a Telethon script (not included) |
| Measure reply latency | `usage_logs.latency_ms` (already recorded!) |
| Aggregate | `SELECT action, AVG(latency_ms), COUNT(*) FROM usage_logs GROUP BY action` |

`usage_logs.latency_ms` is the cheapest real telemetry the project has. It measures the
provider call only.

## 6. Known performance risks

| Risk | Trigger | Symptom | Mitigation |
| --- | --- | --- | --- |
| SQLite write lock | burst of messages across users | `database is locked` | WAL pragma (TR-01), retry |
| Context size | long conversations with large models | slower, costlier calls | lower `MAX_CONTEXT_MESSAGES` |
| `all_for_conversation` in export/summary | very long chats | memory spike | paginate the query |
| Per-request `httpx.AsyncClient` | high throughput | connection churn | shared client |
| Unbounded concurrency | many users at once | provider 429s | semaphore (TASK-105) |
| Broadcast to all users | large user base | Telegram flood limits | batching with delays |

## 7. What would falsify the "provider dominates" assumption

- A DB with millions of messages (then the unindexed `ORDER BY id DESC` scans matter).
- A local model with <100 ms responses.
- A host with slow disk (container on network storage).

If any of those appear, re-measure before optimising.
