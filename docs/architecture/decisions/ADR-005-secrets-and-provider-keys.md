# ADR-005 — Secrets live in the environment; admin-added provider keys are a documented exception

- **Status:** Accepted with a known open risk (revisit: TASK-104)
- **Date:** 2026-11-16
- **Related:** [secrets management](../../security/secrets-management.md), [threat model](../../security/threat-model.md)

## Context

The bot needs a Telegram token, an AI key, and optionally a GitHub token. Admins can
also add extra OpenAI-compatible providers at runtime, which requires storing *their*
keys somewhere. The repository is public. The deployment is a single container with
a `.env` file and a SQLite volume.

## Problem

Where do credentials live so that (a) nothing secret is ever committed, (b) a
self-hoster can rotate a key without touching code, and (c) runtime-added providers
still work — without pretending the residual risk does not exist?

## Considered alternatives

| Option | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| A. Env/`.env` only | no secret in DB; standard practice; easy rotation | cannot add a provider without a redeploy | **Chosen for primary credentials** |
| B. Env for primary + plaintext in DB for admin providers | runtime provider management works | plaintext at rest in SQLite; a DB leak exposes keys | **Chosen as interim, documented** |
| C. Env + encrypted DB column (app-managed key) | no plaintext at rest | key must live somewhere (env), rotation story, crypto code to maintain | **Recommended next (TASK-104)** |
| D. External secret manager (Vault, SSM) | strongest | new dependency and ops burden for one operator | Rejected at this scale |
| E. No runtime providers (env only) | simplest, safest | admins must redeploy for each provider; contradicts a shipped feature | Rejected |

## Decision

1. **Primary credentials** (`BOT_TOKEN`, `AI_API_KEY`, `AI_BASE_URL`, optional
   `GITHUB_TOKEN`) come only from `Settings`/`.env`. They are never written to the
   database and never returned to users.
2. **Runtime providers** are stored in `ai_providers` **as entered**, including the
   key, because the feature's value is "add a provider without a redeploy". This is
   recorded as an accepted risk in the threat model, not hidden.
3. **No secret is logged.** Error surfaces use `str(exc)[:300]`; provider keys are
   never formatted into messages or log lines.
4. **`.env` is git-ignored**, `.env.example` ships empty placeholders, and the
   `Settings` defaults for all secrets are empty strings.
5. **Rotation:** replace the value in `.env` and restart; or delete/re-add the
   provider row for DB-stored keys.
6. **Encryption of DB keys is the agreed next step** once the key-derivation
   question is answered (see open question Q-03).

## Consequences

**Positive**

- A public repository can never leak the operator's primary key through a commit.
- Rotation is a one-line `.env` edit.
- The risk of the runtime feature is explicit and auditable.

**Negative / accepted costs**

- `ai_providers.api_key` is plaintext at rest; anyone with the SQLite file — or a
  backup of it — reads every runtime provider key.
- No key versioning or audit trail of who added which provider.

## Risks and mitigations

| Risk | Severity | Mitigation now | Mitigation planned |
| --- | --- | --- | --- |
| DB file leaked (backup, volume snapshot) | High | file permissions on host; backups treated as secrets | TASK-104 encryption |
| Key accidentally printed in an error path | Medium | truncation, no key echo | add a redaction helper + test |
| `.env` committed by mistake | High | `.gitignore` entry exists | CI secret scanning (`security.yml`) |
| Admin account compromise → key exfiltration | High | `ADMIN_IDS` allow-list; no key display in UI | audit log for provider changes |

## Verification / current state

- `.gitignore` contains `.env`; `.env.example` has empty values only.
- `grep -ri "api_key" src/bot` shows no message that renders a key.
- No automated secret scan has run in this repository yet — the workflow is provided
  but not yet executed. Do not claim scanning is active.
