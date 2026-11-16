# Backup & Recovery

The entire durable state is one SQLite file. Everything else (FSM, rate buckets,
GitHub cache) is disposable.

## 1. What to back up

| Item | Path | Criticality |
| --- | --- | --- |
| Database | `./data/bot.db` | **critical** |
| Configuration | `.env` | **critical** (contains secrets — store encrypted) |
| Compose overrides / systemd unit | host-specific | useful |
| Uploaded assets | none exist | — |

## 2. Backup methods

### 2.1 Live backup with the SQLite CLI (preferred)

```bash
docker compose exec bot sh -c \
  'sqlite3 /app/data/bot.db ".backup \"/app/data/backup-$(date +%F).db\""'
```

`.backup` is safe while the bot runs (it uses SQLite's online backup API).

### 2.2 Copy while stopped

```bash
docker compose stop bot
cp data/bot.db "backups/bot-$(date +%F-%H%M).db"
docker compose start bot
```

Never `cp` a live `bot.db` on a busy system — you can capture a torn file.

### 2.3 Dump to SQL (portable, diffable)

```bash
sqlite3 data/bot.db .dump > backups/bot-$(date +%F).sql
```

Larger and slower to restore, but survives schema-level tooling issues.

## 3. Schedule (recommended, not automated)

| Frequency | Retention | Method |
| --- | --- | --- |
| Daily 03:00 | 7 files | `.backup` via cron |
| Weekly | 4 files | copy off-host |
| Before every upgrade | 1 | rename `pre-upgrade.db` |
| Before any manual SQL | 1 | `.backup` |

```bash
# crontab -e (on the host)
0 3 * * * cd /opt/telegram-ai-assistant && \
  docker compose exec -T bot sh -c 'sqlite3 /app/data/bot.db ".backup \"/app/data/daily.db\""' && \
  cp data/daily.db /backups/bot-$(date +\%F).db
```

`-T` is required for cron (no TTY).

## 4. Restore

```bash
docker compose stop bot
cp backups/bot-2026-11-10.db data/bot.db
chown 1000:1000 data/bot.db        # if running as non-root
docker compose start bot
docker compose logs --tail=30 bot  # expect "migrations applied" and polling
```

Verify after restore:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM messages;
SELECT MAX(version) FROM schema_version;
```

If the restored file is from an older version, the additive migration runner upgrades
it on boot.

## 5. Manual erasure (user deletion requests)

There is no delete-account feature. The operator can run this **after a backup**:

```sql
PRAGMA foreign_keys = ON;
BEGIN;
DELETE FROM messages WHERE conversation_id IN
  (SELECT id FROM conversations WHERE user_id = :uid);
DELETE FROM conversations WHERE user_id = :uid;
DELETE FROM personas   WHERE user_id = :uid;
DELETE FROM prompts    WHERE user_id = :uid;
DELETE FROM user_memory WHERE user_id = :uid;
DELETE FROM user_settings WHERE user_id = :uid;
UPDATE usage_logs SET user_id = NULL WHERE user_id = :uid;   -- keep audit aggregate
DELETE FROM users WHERE id = :uid;
COMMIT;
```

Notes:

- `usage_logs` rows are retained with `user_id = NULL` so aggregate counts stay
  truthful. If the requester demands full removal, `DELETE FROM usage_logs WHERE
  user_id = :uid` instead — this changes historical statistics.
- Export the user's data first: they can run `conv:exp` per conversation, or the
  operator can query `messages` directly.
- This is an **operator procedure**, not a product feature (gap G3, TASK-204).

## 6. Recovery scenarios

| Scenario | Symptom | Action |
| --- | --- | --- |
| Corrupt DB | "database disk image is malformed" | `sqlite3 bot.db "PRAGMA integrity_check;"`; restore last good backup |
| Accidental migration | bot fails after upgrade | restore `pre-upgrade.db`, pin old image |
| Disk full | write errors | free space, restart, verify `PRAGMA quick_check` |
| Lost `.env` | cannot boot | re-issue `BOT_TOKEN` (BotFather), re-create keys |
| Lost volume | empty DB | bot recreates schema; history is gone unless backed up |

## 7. Integrity checks

```bash
sqlite3 data/bot.db "PRAGMA integrity_check;"     # expect "ok"
sqlite3 data/bot.db "PRAGMA quick_check;"
sqlite3 data/bot.db "SELECT COUNT(*) FROM messages WHERE conversation_id NOT IN (SELECT id FROM conversations);"
```

The last query should return `0` (no orphan messages).

## 8. Security of backups

Backups contain conversation text and (today) plaintext provider keys from
`ai_providers`. Therefore:

1. Encrypt off-host copies (`age`, `gpg`, or an encrypted bucket).
2. Restrict permissions (`600`).
3. Treat backup retention as a privacy decision — deleted data may still exist in old
   backups; rotate them out on a schedule.

## 9. What is not backed up

FSM state, rate-limit buckets, GitHub cache, logs. Losing them is harmless.
