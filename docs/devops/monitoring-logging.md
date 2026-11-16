# Monitoring & Logging

## 1. What exists

| Signal | Where | Retention |
| --- | --- | --- |
| Application logs | stdout → Docker json-file | host default (often unlimited) |
| AI usage rows | `usage_logs` table | forever |
| Admin stats screen | `/admin` → `adm:stats` | live query |
| Provider health | `adm:health` | live query |
| Process status | `docker compose ps` | — |

**Not present:** metrics endpoint, APM, tracing, alerting, error tracking, uptime
checks, dashboards. Any claim of observability beyond the above would be false.

## 2. Logging

`core/logging.py` configures stdlib logging once with `force=True`:

```
%(asctime)s | %(levelname)-8s | %(name)s | %(message)s
```

| Level | Used for |
| --- | --- |
| INFO | startup, migration summary, provider refresh, broadcast result |
| WARNING | config problems (`CONFIG: …`), GitHub failure, invalid preset value |
| ERROR | provider failures, DB errors, handler exceptions |
| DEBUG | request metadata (opt-in) |

### Log review commands

```bash
docker compose logs --tail=200 bot
docker compose logs -f bot | grep -Ei "error|exception|traceback"
docker compose logs bot | grep -c "CONFIG:"
```

### What must never appear in logs

Bot token, API keys, full prompts, message bodies, provider response bodies.
Error text is truncated to 300 characters.

## 3. Database-based telemetry

`usage_logs` is the most useful operations dataset:

```sql
-- requests and latency per action (last 24h)
SELECT action, COUNT(*) n, AVG(latency_ms) avg_ms,
       SUM(prompt_tokens + completion_tokens) tokens
FROM usage_logs
WHERE created_at >= datetime('now','-1 day')
GROUP BY action ORDER BY n DESC;

-- failure rate per provider
SELECT provider,
       SUM(CASE WHEN success THEN 0 ELSE 1 END) failed,
       COUNT(*) total
FROM usage_logs GROUP BY provider;

-- heaviest users today
SELECT user_id, COUNT(*) n FROM usage_logs
WHERE date(created_at) = date('now')
GROUP BY user_id ORDER BY n DESC LIMIT 10;
```

## 4. Health signals and thresholds (proposed)

| Signal | Healthy | Investigate | Act |
| --- | --- | --- | --- |
| Failure rate (per provider, 1h) | < 2% | 2–10% | > 10% — check key/quota/status page |
| Median chat latency | provider-dependent | 2× baseline | check provider status |
| `CONFIG:` warnings at boot | 0–1 | — | fix `.env` |
| DB size growth | linear | sudden jump | check for loops/duplicates |
| Process restarts | 0 | 1–2/day | investigate crash loop |
| Duplicate polling conflict | none | any | stop the extra instance |

Thresholds are **proposals**, not tuned values.

## 5. Minimal monitoring setup (recommended)

| Layer | Tool | Effort |
| --- | --- | --- |
| Process alive | Docker `restart: unless-stopped` | already |
| Log retention | Docker `logging: options: max-size/max-file` | 3 lines |
| External uptime | any ping service hitting the Telegram `getMe` via a cron script | small |
| Error visibility | a `dp.errors` handler + log | TASK-102 |
| Metrics | Prometheus exporter | TASK-302 (not scheduled) |

Note: because there is no HTTP endpoint, external uptime checks cannot hit the bot
directly; they must check the process (e.g. Docker healthcheck) or Telegram's API
reachability.

## 6. Alerting (target, not implemented)

| Alert | Condition | Channel |
| --- | --- | --- |
| Bot down | container not running > 2 min | operator's choice |
| Provider failing | failure rate > 10% over 15 min | operator |
| Disk low | < 1 GB free | operator |
| Daily quota exhausted for many users | > 50% users capped | operator |

## 7. Incident evidence collection

```bash
docker compose ps
docker compose logs --since=2h bot > /tmp/bot-logs.txt
sqlite3 data/bot.db ".backup '/tmp/bot-db-snapshot.db'"
sqlite3 data/bot.db "SELECT * FROM usage_logs ORDER BY id DESC LIMIT 50;"
```

Redact logs before sharing; they may contain user ids.

## 8. Retention guidance

| Data | Suggested retention | Mechanism |
| --- | --- | --- |
| Docker logs | 7–14 days | log rotation |
| `usage_logs` | 90 days for analytics, keep aggregates | periodic prune (not implemented) |
| `messages` | user-controlled | clear per conversation |
| Backups | 7 daily + 4 weekly | operator script |

No automated pruning exists; these are recommendations.
