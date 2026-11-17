# Competitor & Comparable-Product Analysis

**Research date:** 2026-11-16. **Method:** public web/GitHub metadata via search
and repository pages; no private product accounts were used. Star counts are
third-party snapshots and change constantly — treat them as order-of-magnitude.
Anything marked **[unverified]** was not confirmed from a primary source and must
not be used as a fact in marketing copy.

---

## 1. Research methodology

1. Identify the category the product actually sits in: *self-hosted, BYO-key
   Telegram bot front-ends to a chat LLM*, not "AI assistants" generally.
2. Select comparables by (a) same channel (Telegram), (b) same deployment model
   (self-hosted/BYO key), (c) same language ecosystem (Python) where possible.
3. Extract only verifiable attributes: language, licence, deployment target,
   documented feature list, maintenance signals.
4. Compare against *implemented* features of this repository — never against its
   roadmap.
5. Record gaps that this product genuinely fills, and gaps against itself.

**Explicitly out of scope:** commercial SaaS assistants (TeleClaw-style hosted
products), general chat apps (ChatGPT/Claude apps), and Telegram Mini App
products. They compete for attention but not for the same deployment decision.

---

## 2. Comparables

### C1 — `n3d1117/chatgpt-telegram-bot`

| Attribute | Value |
| --- | --- |
| Channel | Telegram bot |
| Language | Python |
| Licence | **GPL-2.0** |
| Deployment | Docker / docker-compose / local |
| Scope | OpenAI official APIs: ChatGPT, DALL·E, Whisper |
| Breadth | Group topics, inline queries, voice, images, plugins, translations file |
| Maintenance | Last release 0.4.2 (Dec 2024); third-party trackers report no commits since mid-2025 → **stale** |
| Stars | ~3.4k (third-party snapshot) **[unverified]** |
| Source | <https://github.com/n3d1117/chatgpt-telegram-bot> · <https://github.com/n3d1117/chatgpt-telegram-bot/releases> |

**Relevant to us:** it is the closest analogue by ecosystem and scope, and it is
the reason "chat + tools + Docker" is table stakes. Its GPL licence is a real
differentiator constraint for downstream commercial reuse.

### C2 — `tbxark/ChatGPT-Telegram-Workers`

| Attribute | Value |
| --- | --- |
| Channel | Telegram bot |
| Language | TypeScript |
| Licence | **MIT** |
| Deployment | Cloudflare Workers (primary), Vercel, Docker, local server |
| Scope | Multi-provider (chat-completions, Anthropic Messages, OpenAI Responses, Workers AI), image providers, plugin system, admin panel + Mini App |
| Maintenance | Active — repository showed commits within the last week at research time |
| Stars | ~3.8k (third-party snapshot) **[unverified]** |
| Source | <https://github.com/tbxark/ChatGPT-Telegram-Workers> · <https://github.com/tbxark/ChatGPT-Telegram-Workers/blob/master/doc/en/CONFIG.md> |

**Relevant to us:** the strongest product feature set in the category (multi-provider
protocols, plugins, image generation, per-topic support). Its model is
configuration-in-a-database + a web Mini App admin surface — heavier than this
project's single-container SQLite design.

### C3 — `father-bot/chatgpt_telegram_bot`

| Attribute | Value |
| --- | --- |
| Channel | Telegram bot |
| Language | Python |
| Licence | MIT |
| Deployment | Docker / local |
| Scope | OpenAI + Claude via OpenRouter, vision, voice, 15 chat modes, allowed-user list **[unverified beyond third-party summary]** |
| Maintenance | Active (v1.6, June 2026 per third-party summary) **[unverified]** |
| Source | Third-party round-up: <https://avelina.ai/blog/best-personal-ai-agents-telegram-2026> |

**Relevant to us:** comparable tool-mode breadth in Python; different
architecture (heavier modes, no documented persona/memory model).

### C4 — Hosted Telegram AI products (category pressure, not a deploy decision)

Free-tier + paid-credit products that provision a bot for the user. They win on
setup effort; they lose on data ownership, key ownership and Persian UX control.
Their existence is why the "self-host with your own key" story must be crisp.
Source: <https://darkfactory.education/guides/MhaAiAssistantBot> (third-party
survey, Sept 2026).

---

## 3. Feature comparison matrix

Legend: ✅ implemented · 🟡 partial/different approach · ❌ absent (per public docs)
`n/v` = not verified from a primary source.

| Capability | This project | C1 n3d1117 | C2 TBXark | C3 father-bot |
| --- | --- | --- | --- | --- |
| Persian + English UI with parity test | ✅ | 🟡 (`translations.json` exists; parity not enforced by test per repo contents) | 🟡 (i18n incl. Chinese; Persian `n/v`) | `n/v` |
| Inline-menu navigation for all features | ✅ | 🟡 (commands-first, some keyboards) | ✅ (admin keyboard) | 🟡 |
| Multi-conversation with titles/pin/archive | ✅ | 🟡 (per-chat/thread context) | 🟡 (topic mode) | ✅ (per-user threads) |
| User-authored personas assignable per conversation | ✅ | ❌ | 🟡 (system prompt per provider) | 🟡 (chat modes) |
| Saved prompt library with categories | ✅ | ❌ | 🟡 (plugins as templates) | ❌ |
| Per-user memory injected into prompt | ✅ | ❌ | 🟡 (user config) | ❌ |
| Tool modes (summarize/translate/write/explain/coding) | ✅ | 🟡 (some prompts) | ✅ (plugins/commands) | ✅ (15 modes) |
| Model selection from UI | ✅ | 🟡 (env) | ✅ | ✅ |
| Provider-agnostic (any OpenAI-compatible base URL) | ✅ | ❌ (OpenAI SDK) | ✅ (4 protocols) | ✅ (OpenRouter) |
| Capability-based auto-routing without extra call | ✅ | ❌ | ❌ | ❌ |
| Voice / vision | ❌ | ✅ | ✅ (image input) | ✅ |
| Image generation | ❌ | ✅ (DALL·E) | ✅ | `n/v` |
| Group/topic support | ❌ | ✅ | ✅ | `n/v` |
| Admin panel in chat | ✅ | 🟡 | ✅ (+ Mini App) | 🟡 |
| Broadcast | ✅ | ❌ | ✅ | `n/v` |
| Per-user rate limit + daily cap | ✅ | 🟡 (allowed users/tokens) | ✅ | 🟡 |
| Token accounting | ✅ | ❌ | ✅ | `n/v` |
| Licence | MIT | **GPL-2.0** | MIT | MIT |
| Language | Python | Python | TypeScript | Python |
| Single-container SQLite deploy | ✅ | ✅ | 🟡 (Workers/D1 or server) | ✅ |

---

## 4. Technical observations

1. **Two architectural camps.** *Stateless bridge* (C1: one OpenAI SDK call per
   message, state in memory) versus *configuration platform* (C2: providers,
   plugins and prompts stored in a DB, admin surface in a Mini App). This project
   sits between: DB-backed preferences and history, but a single process and no
   web surface.
2. **Licence economics.** GPL-2.0 (C1) deters proprietary reuse; MIT (C2, C3,
   this project) does not. For a portfolio/self-host project, MIT removes adoption
   friction but offers no protection.
3. **Python bots converge on aiogram/python-telegram-bot.** This project's choice of
   aiogram 3 with routers + FSM is the mainstream modern pattern; it is not a
   differentiator by itself.
4. **Breadth is expensive.** C2's multi-protocol + image + plugin surface implies
   substantial provider-specific code. This project deliberately narrows to a single
   OpenAI-compatible request shape — cheap to extend one provider class at a time.
5. **Persian RTL is largely unaddressed** by the public docs of C1–C3. That is the
   clearest unclaimed position.

---

## 5. Strengths & weaknesses (this project)

**Strengths**

- Enforced FA/EN parity (test), not a translation file of unknown completeness.
- Persona + memory + saved prompts as first-class, user-owned data.
- Ownership scoping baked into repository signatures and proven by a test.
- Zero external services: one container, one SQLite file, no Redis/queue.
- Documented trade-offs (plaintext provider keys, in-memory FSM/limits) rather than
  silent gaps.

**Weaknesses**

- No voice/vision/image generation — C1/C2 users get those.
- No group support — a large share of Telegram bot demand is group-oriented.
- Single-process ceiling; no horizontal scaling story.
- No live end-to-end verification in the repository (no key available).
- No lint/format gate in CI today.

---

## 6. Market / product gaps (defensible)

| Gap | Evidence it is unaddressed | How this product addresses it |
| --- | --- | --- |
| Persian-first UX with enforced parity | C1–C3 docs mention i18n but not Persian parity tests | `tests/test_localization.py`, hand-authored `fa.json` |
| Persistent persona identity across sessions | C1 stateless; C2 per-provider prompt | `personas` table + per-conversation assignment |
| "No extra call" routing | C1/C2/C3 route manually or not at all | regex `classify_task` |
| Menu-only operation for non-technical users | C1 command-centric | 10-section inline menu, all features tap-reachable |
| Cost visibility for a shared key | Token accounting uncommon | `usage_logs` with prompt/completion tokens |

---

## 7. Differentiation opportunities (ranked, honest)

1. **Own the Persian-first niche** — it is cheap to defend and already implemented.
2. **"One container, one file, no services"** — the lowest-ops self-host story in
   the comparison set.
3. **Persona + memory + prompt library** as a coherent "your assistant" bundle.
4. **Deterministic routing** — a genuine technical differentiator with a cost story.
5. **Documentation quality** — ADRs, threat model, traceability; rare in this niche.

Do **not** compete on breadth (voice/vision/groups). Those are C1/C2 territory and
would require media pipelines this product has explicitly excluded.

---

## 8. Product recommendations

| # | Recommendation | Effort | Rationale |
| --- | --- | --- | --- |
| R1 | Ship the live smoke test and state clearly in the README that live calls are operator-verified, not CI-verified | S | Honesty about verification is a trust asset |
| R2 | Add a short "Why not X" section linking this document | S | Pre-empts "why not C2" questions |
| R3 | Add a Persian screenshot/GIF to the README | S | The niche claim needs visual proof |
| R4 | Encrypt provider keys or remove admin-added keys from the MVP path | M | Only material security gap vs C2 |
| R5 | Defer voice/vision until a media storage decision exists | — | Avoid half-built breadth |

---

## 9. Sources

| # | Source | Used for | Date |
| --- | --- | --- | --- |
| S1 | <https://github.com/n3d1117/chatgpt-telegram-bot> | C1 language, licence, scope, deployment files | 2026-11-16 |
| S2 | <https://github.com/n3d1117/chatgpt-telegram-bot/releases> | C1 release cadence (0.4.2 latest) | 2026-11-16 |
| S3 | <https://github.com/tbxark/ChatGPT-Telegram-Workers> | C2 language, licence, deployment, scope | 2026-11-16 |
| S4 | <https://github.com/tbxark/ChatGPT-Telegram-Workers/blob/master/doc/en/CONFIG.md> | C2 provider protocols, admin panel scope | 2026-11-16 |
| S5 | <https://github.com/tbxark/ChatGPT-Telegram-Workers/blob/master/doc/en/CHANGELOG.md> | C2 feature timeline (plugins, providers) | 2026-11-16 |
| S6 | <https://avelina.ai/blog/best-personal-ai-agents-telegram-2026> | C3 summary, C1 staleness claim (third-party) | 2026-11-16 |
| S7 | <https://darkfactory.education/guides/MhaAiAssistantBot> | Hosted-product category context (third-party) | 2026-11-16 |

**Confidence:** licence, language and documented features for C1/C2 are
high-confidence (primary repository pages). C3 attributes and all star counts are
**medium/low** and come from third-party summaries; they are marked accordingly and
must not be repeated as hard facts.
