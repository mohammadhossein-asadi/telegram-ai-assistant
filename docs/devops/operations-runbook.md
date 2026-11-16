# Operations Runbook

Audience: the operator of a deployed instance. Each section is a symptom → diagnosis →
action sequence. No step requires reading source code.

## 1. Daily checks (2 minutes)

```bash
docker compose ps                              # container Up
docker compose logs --tail=20 bot              # no ERROR lines
sqlite3 data/bot.db "SELECT COUNT(*) FROM users;"
curl -s -o /dev/null -w "%{http_code}\n" https://api.telegram.org   # outbound reachability
```

## 2. "The bot doesn't answer"

| Step | Command | Finding → action |
| --- | --- | --- |
| 1 | `docker compose ps` | not running → §2.1 |
| 2 | `docker compose logs --tail=100 bot` | `SystemExit` → fix `.env` |
| 3 | Same | `Conflict: terminated by other getUpdates request` → §2.2 |
| 4 | Same | `Unauthorized` → token revoked → rotate token |
| 5 | `sqlite3 data/bot.db "PRAGMA integrity_check;"` | not `ok` → restore backup |
| 6 | Telegram `/start` | no reply but logs show updates → check block state of the account |

### 2.1 Container restart loop

```bash
docker compose logs --tail=200 bot | head -40
```

| Error | Cause | Fix |
| --- | --- | --- |
| `BOT_TOKEN is not configured` | empty `.env` | set `BOT_TOKEN` |
| `ValidationError` for an int field | e.g. `USER_RATE_LIMIT=abc` | fix the value |
| `unable to open database file` | volume/permission | `mkdir -p data && chown -R 1000:1000 data` |
| `database is locked` | second process | stop the duplicate |

### 2.2 Duplicate polling

**Cause:** two instances with the same token (old container + new, or a stray
`python run.py`). **Action:** keep exactly one; `docker compose down` then `up -d`.

## 3. "The bot replies with an AI error"

| Log line | Meaning | Action |
| --- | --- | --- |
| `AIError ... status=401` | key invalid/revoked | rotate `AI_API_KEY` |
| `status=429` | provider rate limit or quota | wait, reduce limits, check billing |
| `status=404` | wrong `AI_BASE_URL` or model | verify endpoint + model name |
| `AITimeoutError` | provider slow | retry; check provider status |
| `no AI_API_KEY` | key empty | set it, restart |

Quick check without Telegram:

```bash
curl -s https://api.openai.com/v1/models -H "Authorization: Bearer $AI_API_KEY" | head -c 200
```

(Substitute your provider's base URL.)

## 4. "Users report slow replies"

1. Check `usage_logs` latency:

```sql
SELECT action, AVG(latency_ms), MAX(latency_ms), COUNT(*)
FROM usage_logs WHERE created_at >= datetime('now','-1 hour') GROUP BY action;
```

2. If latency is high but the DB is fast, it is the provider — nothing to fix locally.
3. If the DB is the bottleneck (`database is locked`), see §6.

## 5. "Disk is full"

```bash
df -h .
du -sh data/ backups/
docker system df
```

Actions (in order): remove old backups, `docker image prune -f`,
`docker builder prune -f`, then rotate logs:

```yaml
# compose addition
logging:
  options: { max-size: "10m", max-file: "3" }
```

## 6. "database is locked" / write failures

| Cause | Fix |
| --- | --- |
| Two processes | run one |
| Long-running query | check for a huge export/summary; restart if stuck |
| Host disk stalls | check `iostat`; move to local SSD |

WAL mode is **not** enabled (TR-01). Enabling it is a one-line pragma change plus a
test; it is not part of the current release.

## 7. Broadcast

`/admin` → Broadcast → type the message → confirm.

| Observation | Meaning |
| --- | --- |
| "sent to N users, failed M" | expected; failures are usually users who blocked the bot |
| Nothing happens | FSM lost (restart) → retry |
| Very large user base | sends are sequential; allow time |

There is no scheduling and no retry for failed recipients.

## 8. Blocking a user

```bash
# via Telegram
/block 123456789
```

Effects: updates from that id are dropped in middleware. Unblock with `/unblock`.

## 9. Rotating secrets

Full procedure: [secrets management §4](../security/secrets-management.md#4-rotation).
Short version: change the value in `.env`, `docker compose up -d`, verify a chat.

## 10. Upgrading

[Deployment §8](deployment.md#8-upgrades). Always back up first; migrations run on
boot and are additive.

## 11. Restoring service after data loss

[Backup & recovery §4](backup-recovery.md#4-restore).

## 12. Escalation checklist (when nothing above applies)

Collect before asking for help — and redact before sharing:

```bash
docker compose ps > /tmp/report.txt
docker compose logs --since=6h bot >> /tmp/report.txt
docker compose exec -T bot python -c "import sys; print(sys.version)" >> /tmp/report.txt
grep -c "ERROR" /tmp/report.txt
```

Never include `.env` contents, the token, or API keys in a report.

## 13. Known operational limitations

| Limitation | Workaround |
| --- | --- |
| Restart loses in-progress FSM flows | retry the flow |
| Restart resets per-minute rate buckets | none needed |
| No healthcheck | `docker compose ps` |
| No alerting | daily manual check |
| No automatic pruning | manual SQL + log rotation |
| Single instance only | do not scale |
