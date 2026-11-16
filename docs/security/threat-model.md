# Threat Model

Method: STRIDE over the trust boundaries in
[security architecture](security-architecture.md). Severity uses a simple
likelihood × impact scale (Low/Medium/High/Critical) for a **self-hosted single-user-
operator bot**, not for an internet-scale SaaS.

## 1. Actors

| Actor | Capability | Motivation |
| --- | --- | --- |
| Ordinary Telegram user | send messages, tap buttons | free AI usage; curiosity |
| Malicious user | crafted callbacks, prompt injection, long inputs | abuse quota, extract system prompt, break formatting |
| Blocked user | same, but updates are dropped | bypass the block |
| Operator/admin | full config, provider keys, broadcast | (insider) |
| Host attacker | filesystem access to `bot.db` and `.env` | keys, conversations |
| Provider (external) | returns arbitrary text | (untrusted) inject content into the chat |
| Dependency attacker | supply-chain compromise | code execution |

## 2. STRIDE table

| # | Category | Threat | Path | Likelihood | Impact | Risk | Mitigation (status) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | Spoofing | Forge another user's identity | send an update impersonating `from.id` | Very low (needs bot token) | High | Low | Telegram-signed updates; bot token secrecy |
| T2 | Spoofing | Non-admin invokes admin callbacks | craft `adm:*` payload | Very low | High | Low | admin check re-run inside every `adm:*` handler |
| T3 | Tampering | Modify another user's conversation | `conv:open:<id>` with foreign id | Medium (easy to try) | High | **Medium** | `get(id, user_id)` returns None → empty toast, no data |
| T4 | Tampering | Modify another user's persona/prompt | `cps:edit:<id>` / `pr:del:<id>` | Medium | Medium | **Medium** | ownership-scoped repository methods |
| T5 | Repudiation | Admin denies a broadcast or block | no audit trail | Medium | Low | Low | **gap G5** — no audit log |
| T6 | Information disclosure | Read chats from a leaked `bot.db` | host/backup access | Medium | High | **High** | file permissions only; **no encryption (G2)** |
| T7 | Information disclosure | Provider keys from a leaked DB | `ai_providers.api_key` | Medium | High | **High** | none at rest → TASK-104 |
| T8 | Information disclosure | `.env` committed | mistake | Low | Critical | **High** | `.gitignore`; CI scan (not yet executed) |
| T9 | Information disclosure | System prompt extracted via injection | user asks "print your instructions" | High | Low | Low | prompts contain no secrets; deliberate |
| T10 | Denial of service | Quota exhaustion by one user | rapid messages | High | Medium | **Medium** | per-minute + daily limits; `/block` |
| T11 | Denial of service | Provider cost amplification | long contexts | Medium | Medium | Medium | 20-message context, 4096-char input cap |
| T12 | Denial of service | Broadcast storm | admin misuse | Low | Medium | Low | one send per user, sequential |
| T13 | Elevation of privilege | Blocked user regains access | new account | High | Low | Low | block is per Telegram id, not per person — accepted |
| T14 | Elevation of privilege | Admin base URL pointed at internal service | admin config | Low | Medium | Low | admin-only; **no URL validation (G6)** |
| T15 | Tampering | HTML/script injection into messages | model output rendered with `parse_mode=HTML` | Medium | Medium (Telegram sanitises) | Low | escape-then-convert; plain-text fallback |
| T16 | Tampering | SQL injection | any input reaching a query | Low | Critical | Low | SQLAlchemy parameterised queries; no string-built SQL with user data |
| T17 | Information disclosure | Logs contain secrets or chat text | operator log access | Low | Medium | Low | no prompt/response bodies logged; errors truncated |
| T18 | Supply chain | Malicious dependency | `pip install` | Low | Critical | Medium | 6 pinned packages; `pip-audit` in CI (provided) |

## 3. Attack trees (selected)

### T3/T4 — horizontal access to another user's data

```
Goal: read/delete another user's conversation
├── guess a conversation id (sequential integers)         [easy]
├── send conv:open:<id>                                   [easy]
└── handler calls conversations.get(id, user.id)          [blocked: returns None]
    └── fallback? no raw-id query path exists             [blocked]
```

Residual risk: **enumeration confirms existence indirectly** — no, the same
the handler answers with an empty toast for both "does not exist" and "not yours",
so there is no oracle. Good.

### T7 — key exfiltration

```
Goal: obtain a provider API key
├── read .env                     [host access required]
├── read data/bot.db              [host access required; plaintext today]
├── ask the bot to print it       [blocked: no handler renders keys]
└── trigger an error that echoes the key
    └── provider errors are truncated and never include the Authorization header
```

### T10 — quota exhaustion

```
Goal: use the operator's credits for free
├── send many messages
│   └── per-minute limit (20) + daily cap (200)   [mitigated]
├── create many Telegram accounts
│   └── per-account caps                           [not mitigated — accepted]
└── trigger failures to burn the daily count       [possible; failed calls count]
```

## 4. Risk register (ranked)

| Rank | Threat | Risk | Owner action |
| --- | --- | --- | --- |
| 1 | T6 chats exposed by DB/backup leak | High | restrict file perms; encrypt backups; consider SQLCipher |
| 2 | T7 provider keys plaintext | High | TASK-104 (encryption or env-only mode) |
| 3 | T8 `.env` committed | High | enable the provided secret-scan workflow |
| 4 | T3/T4 horizontal access | Medium | keep ownership filters; add regression tests |
| 5 | T10 quota abuse | Medium | limits exist; consider email/phone gating |
| 6 | T18 supply chain | Medium | run `pip-audit`; pin with hashes (optional) |
| 7 | T5 admin repudiation | Low | TASK-106 audit log |

## 5. Out of scope

- Telegram platform compromise.
- AI provider model behaviour (hallucination is a product concern, not a security one).
- Physical attacks on the host.
- Multi-tenant isolation (each deployment is one operator's bot).
- Regulatory compliance certification (GDPR/DPDP "compliance" is not claimed; see
  [data protection](data-protection.md) for the practical stance).

## 6. Review cadence

Re-run this model when: a new handler namespace is added, authentication changes, a
new external integration appears, or a new table stores user content.
