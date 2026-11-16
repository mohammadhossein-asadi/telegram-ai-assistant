# Secrets Management

Decision record: [ADR-005](../architecture/decisions/ADR-005-secrets-and-provider-keys.md).

## 1. Secret inventory

| Name | Required | Used by | Failure if absent | Blast radius if leaked |
| --- | --- | --- | --- | --- |
| `BOT_TOKEN` | **yes** | aiogram `Bot` | process exits (`SystemExit`) | full bot takeover, message access |
| `AI_API_KEY` | effectively yes | provider | `errors.ai` on every request | billing abuse on the operator's account |
| `AI_BASE_URL` | no (default set) | provider | — | — |
| `AI_MODEL` | no (default set) | provider | — | — |
| `GITHUB_TOKEN` | no | GitHub client | unauthenticated rate limit (60/h) | read-only public data; low |
| `ADMIN_IDS` | no (empty) | admin gate | nobody is admin | privilege escalation if wrong |
| `DATABASE_URL` | no (default `sqlite+aiosqlite:///./data/bot.db`) | DB | — | path disclosure only |
| runtime provider keys | optional | `ai_providers.api_key` | — | **high** — plaintext at rest |

## 2. Storage rules

1. **Only `.env`** (never committed) or the host's secret mechanism (Compose
   `secrets`, systemd `EnvironmentFile` with `600`).
2. `.env.example` contains keys with **empty values** and comments — it is the
   documented inventory and must never contain a real value.
3. No secret is written into a JSON/YAML config, a test fixture, a Dockerfile `ENV`,
   or a documentation example.
4. Runtime provider keys go into SQLite by design; the operator must accept the
   at-rest risk or use env-only providers.

## 3. Verification that no secret is committed

```bash
git ls-files | grep -E '(^|/)\.env$' && echo "FAIL: .env tracked" || echo "OK"
grep -rInE '(sk-[A-Za-z0-9]{16,}|[0-9]{8,10}:AA[A-Za-z0-9_-]{30,})' --exclude-dir=.git . || echo "OK: no key-shaped strings"
```

The provided `.github/workflows/security.yml` runs a secret scan on push/PR. **It has
not been executed in this repository yet** — do not claim scanning is active until a
run appears in the Actions tab.

## 4. Rotation

| Secret | Procedure | Downtime |
| --- | --- | --- |
| `BOT_TOKEN` | BotFather → Revoke current token → paste into `.env` → restart container | ~5 s (no updates lost; Telegram retries) |
| `AI_API_KEY` | issue a new key at the provider → replace in `.env` → restart → revoke old key | ~5 s |
| `GITHUB_TOKEN` | revoke on GitHub → create new → `.env` → restart | none (cached) |
| runtime provider key | admin UI: delete provider, re-add with the new key | none |
| `ADMIN_IDS` | edit `.env` → restart | none |

Rotate immediately if: a laptop with `.env` is lost, a backup leaks, a CI secret
appears in logs, or the repository accidentally publishes a value.

## 5. Incident: suspected key leak

1. Revoke at the source (BotFather / provider dashboard) — **before** investigating.
2. Replace in `.env`, restart, confirm the bot answers.
3. Check provider usage for unexpected spend; check Telegram for unexpected messages.
4. If `bot.db` was exposed, treat **all** runtime provider keys as compromised.
5. Purge the value from git history if it was committed (`git filter-repo`); force-push
   only with the owner's explicit approval.

## 6. Admin-added provider keys (the known exception)

| Aspect | Reality |
| --- | --- |
| Storage | `ai_providers.api_key`, `TEXT`, plaintext |
| Why | enables adding a provider without a redeploy |
| Who can add | admins only |
| Displayed anywhere? | No — the admin list shows name/base URL/model, never the key |
| Logged? | No |
| Deletion | `adm:delprov:<id>` removes the row |
| Planned fix | TASK-104: encrypt with an app key from env, or restrict runtime providers to env-only mode |

**Backup implication:** a `bot.db` backup contains those keys. Store backups with the
same care as `.env`.

## 7. What is explicitly forbidden

- Printing a secret in a chat message, log line, or documentation example.
- Storing a secret in `localization/*.json`, tests, or `artifacts/`.
- Sending a secret through the bot (e.g. an admin "show my key" feature).
- Committing `.env`, `data/`, or backups.

## 8. Developer workflow

```bash
cp .env.example .env
# fill BOT_TOKEN and AI_API_KEY locally; never paste into chat issues/PRs
```

Reviewer checklist for any PR touching configuration: does it add a secret name,
echo a value, or broaden the silent-logging surface?
