# User Personas

Personas are derived from the product's real constraints (Persian-first,
mobile Telegram, BYO key) — not invented market research. No persona below is a
real customer; they are design targets.

---

## P1 — Sara, Persian student (primary)

| Attribute | Detail |
| --- | --- |
| Context | Uses Telegram on an Android phone, 4G, sometimes on a laptop with the desktop client |
| Language | Persian UI, Persian replies; reads some English |
| Technical comfort | Low: will not type `/commands`, will not read documentation |
| Goal | Understand lecture notes and English articles quickly; keep a running study thread |
| Frustrations | Menus in machine-translated Persian; losing the thread when the bot forgets; long answers cut off mid-sentence |
| Success signal | Taps **Summarize** on a pasted article and gets 5 Persian bullets that fit in one message |

**Jobs to be done**

1. "When I paste an article, summarise it in Persian so I can decide whether to read it."
2. "When I come back tomorrow, continue the same conversation without re-explaining."
3. "When I don't understand a term, explain it simply."

**Design implications**: Persian-first copy (`src/localization/fa.json`), RTL-safe
formatting, `split_message()` chunking, conversation switching in ≤ 3 taps,
`response_language = auto` default so Persian input gets Persian output.

---

## P2 — Amir, developer (secondary)

| Attribute | Detail |
| --- | --- |
| Context | Desktop Telegram, terminal on a second monitor |
| Language | English UI, mixed FA/EN questions |
| Technical comfort | High; runs his own bot with a Docker command and his own API key |
| Goal | Debug tracebacks and review snippets without leaving the chat; keep separate threads per project |
| Frustrations | One flat chat; no way to pin a "code reviewer" personality; model forced to the cheapest one |
| Success signal | Creates a `reviewer` persona, assigns it to the "billing-api" conversation, switches model, and gets a diff-aware review |

**Jobs to be done**

1. "When I paste a traceback, tell me the cause, not a rewrite of my file."
2. "Keep a separate conversation per project, and pin the important ones."
3. "Let me point the bot at a different OpenAI-compatible endpoint."

**Design implications**: coding tool modes (`explain/debug/generate/review/improve`),
per-conversation model and persona overrides, pinned conversations, admin-added
providers, `/retry`, Markdown→HTML code blocks.

---

## P3 — Nika, bilingual professional (secondary)

| Attribute | Detail |
| --- | --- |
| Context | iPhone, between meetings |
| Language | Persian UI, needs English↔Persian output depending on the recipient |
| Technical comfort | Medium; uses the menu, ignores commands |
| Goal | Draft and polish work messages with a consistent professional voice |
| Frustrations | Tone drifts between sessions; emojis in formal email drafts; re-pasting the same instruction |
| Success signal | Applies the "professional" personality + "formal" tone with emoji off, saves the instruction in Prompt Studio, and reuses it next week |

**Jobs to be done**

1. "Rewrite this in a formal tone for a client."
2. "Translate this email into English but keep the structure."
3. "Remember that I prefer no emojis."

**Design implications**: personality/style/tone/creativity as stored settings,
`emoji_enabled` toggle, translate tool with `auto` direction detection, saved
prompts with categories.

---

## P4 — Operator / admin (internal)

| Attribute | Detail |
| --- | --- |
| Context | VPS shell + Telegram on desktop; also the repository maintainer |
| Goal | Know the bot is healthy and affordable; protect the shared AI quota |
| Frustrations | No visibility into failures; one abusive user burning the key |
| Success signal | `/admin` shows user/message/token totals and provider health; a blocked user receives `start.blocked` |

**Jobs to be done**

1. "Show me today's volume, failures and token spend."
2. "Add a fallback provider without redeploying."
3. "Block this user and tell everyone about scheduled maintenance."

**Design implications**: `ADMIN_IDS` allow-list, `adm:*` callbacks, provider CRUD,
`/block` `/unblock`, broadcast with pacing, `usage_logs` aggregates.

---

## P5 — Deployer / self-hoster (secondary)

| Attribute | Detail |
| --- | --- |
| Context | Wants their own private assistant; comfortable with Docker |
| Goal | Working bot in under 10 minutes with two secrets set |
| Frustrations | Hidden required env vars; undocumented startup order; migrations that need a separate command |
| Success signal | `cp .env.example .env`, fill `BOT_TOKEN` + `AI_API_KEY`, `docker compose up -d`, `/start` works |

**Design implications**: `.env.example` completeness, automatic schema creation at
boot (`run_migrations`), single container, no external services, clear boot
errors (`SystemExit` when `BOT_TOKEN` is missing).

---

## Persona → feature coverage

| Persona | Primary features | Documented in |
| --- | --- | --- |
| P1 Sara | Chat, summarize, translate, explain, conversations | [user-journeys](user-journeys.md) J1, J2, J5 |
| P2 Amir | Coding tools, personas, model selection, pinning | J3, J4, J6 |
| P3 Nika | Personality/tone, prompt studio, response language | J4, J7 |
| P4 Operator | Admin panel, broadcast, blocking | J8 |
| P5 Deployer | Setup, Docker, migrations | J0 |
