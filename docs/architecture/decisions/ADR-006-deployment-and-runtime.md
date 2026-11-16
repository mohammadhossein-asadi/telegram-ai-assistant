# ADR-006 — Single container, long polling, SQLite volume

- **Status:** Accepted (implemented)
- **Date:** 2026-11-16
- **Related:** [deployment](../../devops/deployment.md), [operations runbook](../../devops/operations-runbook.md)

## Context

The product targets self-hosting by one person, possibly on a small VPS, a home
server, or a PaaS. There is no team SRE, no domain name, no TLS requirement from the
product itself. Telegram supports both long polling (outbound only) and webhooks
(inbound HTTPS required).

## Problem

What runtime/deployment shape minimises operational surface while keeping the bot
always-on and the data durable?

## Considered alternatives

| Option | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| A. One container, long polling, SQLite on a volume | no inbound port, no TLS, no domain; one file to back up | single instance; ~polling latency; no horizontal scale | **Chosen** |
| B. Webhook mode behind a reverse proxy | lower latency, push delivery | needs public HTTPS + secret path + cert renewal | Deferred (TASK-305) |
| C. Serverless (Cloudflare Workers-style) | cheap idle | SQLite/file state unavailable; would force D1/KV rewrite | Rejected |
| D. Kubernetes/Compose with multiple replicas | scale | SQLite single-writer; in-memory FSM/limits; no shared store | Rejected |
| E. Managed PaaS with buildpacks | no Docker knowledge needed | less control; still one instance | Allowed as an alternative host, not as architecture |

## Decision

1. **Packaging:** `python:3.12-slim` image, dependencies installed from
   `requirements.txt` before source copy (layer cache), `PYTHONPATH=/app/src`,
   `CMD ["python", "run.py"]`.
2. **Supervision:** Docker Compose with `restart: unless-stopped`; `.env` via
   `env_file`; `./data:/app/data` volume; `DATABASE_URL` overridden to the volume
   path in Compose.
3. **Transport:** long polling (`dp.start_polling` with resolved update types). No
   inbound HTTP listener, no public port.
4. **State:** all durable state in one SQLite file under the volume; FSM, rate
   buckets and the GitHub cache are intentionally ephemeral.
5. **Shutdown:** `finally` closes the bot session and disposes the engine.

## Consequences

**Positive**

- Deployment is: copy `.env`, `docker compose up -d`. Nothing else.
- No certificate, domain, reverse proxy or firewall rule is required.
- Backup = copy one file (or `sqlite3 .backup`).

**Negative / accepted costs**

- Exactly one replica. Restarting means downtime of seconds to a minute.
- Polling adds a small latency and consumes a long-lived connection.
- Ephemeral FSM: a restart in the middle of rename/broadcast/provider-add loses the
  flow (documented in `HANDOFF.md`, TASK-201).
- Container runs as root with no healthcheck (hardening gap).

## Risks

| Risk | Mitigation |
| --- | --- |
| Two containers started by mistake → SQLite write conflicts | document "scale must remain 1"; alert on duplicate polling conflicts |
| Host disk full → DB write failures | monitor disk; retention policy for `messages` |
| Container killed mid-write | SQLite transactional safety; restore from backup if corrupt |
| Platform restarts during a broadcast | re-send after restart; failures counted, not retried automatically |

## Verification / current state

- `Dockerfile` and `docker-compose.yml` exist and match this description.
- `python run.py` boots from a clean checkout; `docs/devops/development-environment.md`
  contains the exact commands.
- **Not verified:** a deployment on a real host with a real token — no credentials are
  available in this workspace. Do not claim a live deployment exists.
