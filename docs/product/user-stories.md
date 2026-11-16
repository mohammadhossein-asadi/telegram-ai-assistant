# User Stories

Format: `US-xxx` — *As a … I want … so that …*. Each story lists acceptance
criteria (AC) and the requirements it implements.

Personas: **Sara** (P1), **Amir** (P2), **Nika** (P3), **Operator** (P4), **Deployer** (P5).

---

## Onboarding & localization

### US-001 — First contact
*As Sara I want the bot to greet me in Persian and let me choose my language, so that I never see a language I cannot read.*

- **AC1** `/start` replies with `start.welcome` in `DEFAULT_LANGUAGE`.
- **AC2** Both locale buttons are visible in one row.
- **AC3** Choosing a language updates `users.language` and the next render is fully translated.
- **AC4** Choosing a language also changes the AI reply language (default `response_language='auto'`).
- **Implements:** FR-ONB-001, FR-I18N-001 · **Tests:** T-01, T-02

### US-002 — Switch language later
*As Nika I want to change the UI language from Settings without restarting, so that I can hand the phone to an English-speaking colleague.*

- **AC1** Settings → Language lists both languages with the active one marked.
- **AC2** Every subsequent screen (menus, keyboards, errors) is in the new language.
- **AC3** No restart required.
- **Implements:** FR-I18N-002

### US-003 — Missing translations must fail CI
*As the maintainer I want a test that fails when a key exists in one catalog only, so that parity cannot silently rot.*

- **AC1** `pytest tests/test_localization.py` fails with the missing key names.
- **AC2** Placeholder formatting (`{name}`) is exercised for both locales.
- **AC3** Unknown language falls back to the default locale instead of raising.
- **Implements:** FR-I18N-003 · **Tests:** T-14, T-15

---

## Chat

### US-004 — Ask anything and get context
*As Sara I want the assistant to remember my previous messages in this conversation, so that follow-up questions work.*

- **AC1** The last `MAX_CONTEXT_MESSAGES` turns are sent with each request.
- **AC2** A new conversation starts empty.
- **AC3** Both the user turn and assistant turn are stored after a successful call.
- **AC4** A failed provider call stores nothing *(documented trade-off)*.
- **Implements:** FR-CHAT-001, FR-CHAT-002 · **Tests:** T-03, T-04

### US-005 — Regenerate an answer
*As Amir I want to re-ask the last question with one tap, so that I can compare two answers.*

- **AC1** `/retry` (or the chat keyboard) removes the last assistant message and re-runs the same user text.
- **AC2** History ends with exactly one assistant reply afterwards.
- **Implements:** FR-CHAT-004 · **Tests:** T-05

### US-006 — Readable formatting
*As Sara I want bold text, code blocks and links rendered properly, so that answers are readable on mobile.*

- **AC1** Markdown subset (`**b**`, `*i*`, `~~s~~`, `` `code` ``, fenced blocks, `[label](url)`) becomes Telegram HTML.
- **AC2** Raw HTML in model output is escaped, never interpreted.
- **AC3** Answers longer than 3500 chars are split at paragraph → line → word boundaries.
- **Implements:** FR-CHAT-003, FR-CHAT-005 · **Tests:** T-16, T-17

### US-007 — Stop runaway requests
*As the Operator I want per-user caps so a single user cannot exhaust my API quota.*

- **AC1** A sliding 60-second window enforces `USER_RATE_LIMIT`.
- **AC2** `MAX_DAILY_REQUESTS` is counted from `usage_logs` for the current day.
- **AC3** Exceeding either limit returns a localized message and performs no provider call.
- **Implements:** FR-LIM-001, FR-LIM-002

---

## Tools

### US-008 — Summarise text
*As Sara I want four summary modes so I can choose between two sentences and key takeaways.*

- **AC1** Modes: short, detailed, bullets, takeaways.
- **AC2** Output language follows the UI language of the user.
- **AC3** No conversation rows are written.
- **Implements:** FR-TOOL-001 · **Tests:** T-06

### US-009 — Translate both directions
*As Nika I want translation to pick the direction automatically, so I do not have to think about it.*

- **AC1** `auto` translates Persian→English and English→Persian using `detect_language()`.
- **AC2** `fa` and `en` force the target.
- **AC3** Formatting is preserved; only the translation is returned.
- **Implements:** FR-TOOL-002 · **Tests:** T-07

### US-010 — Improve writing
*As Nika I want grammar-only and email modes, so I can polish without changing my voice.*

- **AC1** Modes: improve, rewrite, tone, grammar, ideas, email.
- **AC2** `grammar` preserves wording apart from corrections.
- **Implements:** FR-TOOL-003

### US-011 — Debug code
*As Amir I want a debugging mode that explains the cause first, so that I learn rather than get a blind rewrite.*

- **AC1** Modes: explain, debug, generate, review, improve.
- **AC2** `debug` must state the cause before the corrected code.
- **Implements:** FR-TOOL-004

---

## Personality & memory

### US-012 — Consistent voice
*As Nika I want personality, style, tone and creativity stored per account, so the assistant sounds the same tomorrow.*

- **AC1** 10 personalities, 6 styles, 5 tones, 3 creativity levels are selectable by tapping.
- **AC2** The composition order is personality → style → tone → language → emoji → memories.
- **AC3** Creativity maps to temperature 0.2 / 0.7 / 1.1.
- **Implements:** FR-PERS-001, FR-PERS-002

### US-013 — Custom instructions
*As Amir I want to paste my own system instructions, so the bot follows my house style.*

- **AC1** `custom` personality stores free text from the next message.
- **AC2** A persona assigned to a conversation overrides global custom instructions.
- **Implements:** FR-PERS-003, FR-PERS-004 · **Tests:** T-08

### US-014 — Long-term memory
*As Sara I want the bot to remember a few facts about me, so I do not repeat them every session.*

- **AC1** `user_memory` is unique per `(user_id, key)`; re-storing a key updates it.
- **AC2** Up to 20 facts are injected when memory is enabled.
- **AC3** Disabling memory removes them from the prompt immediately.
- **AC4** Clearing memory deletes rows for that user only.
- **Implements:** FR-MEM-001, FR-MEM-002, FR-MEM-003 · **Tests:** T-18

---

## Conversations

### US-015 — Multiple threads
*As Amir I want one conversation per project, so contexts do not bleed.*

- **AC1** Create, open, rename, archive, delete are all available from the list.
- **AC2** Five conversations are shown per page with working pagination.
- **AC3** Pinning keeps important threads at the top.
- **AC4** Deleting a conversation deletes its messages.
- **Implements:** FR-CONV-001 … FR-CONV-006 · **Tests:** T-09, T-10

### US-016 — Summarise and export
*As Sara I want a summary and a text export of a long conversation.*

- **AC1** Summary is 3–5 sentences in the user's language and is persisted to `conversations.summary`.
- **AC2** Export produces a `.txt` file with `[role] content` lines.
- **AC3** Both are owner-scoped.
- **Implements:** FR-CONV-007, FR-CONV-008

### US-017 — Ownership cannot be guessed
*As Sara I want nobody to open my conversation by guessing an id.*

- **AC1** Every read/mutate takes `user_id`; mismatches return `None`/`False`.
- **AC2** A test proves user B cannot read user A's messages.
- **Implements:** FR-SEC-001 · **Tests:** T-09

---

## Models

### US-018 — Choose a model
*As Amir I want to pick the model per account and per conversation.*

- **AC1** Model list comes from the registry, not a hard-coded list.
- **AC2** A conversation-level `model` overrides the account setting.
- **AC3** Unknown stored model falls back to the first provider without error.
- **Implements:** FR-MODEL-001, FR-MODEL-002 · **Tests:** T-11

### US-019 — Capability routing
*As the Operator I want coding questions to hit a capable model when auto-routing is on, without paying for an extra classification call.*

- **AC1** Classification is regex-based over 6 task classes.
- **AC2** Routing only happens when `auto_routing` is enabled.
- **AC3** No provider supports the task → fall back to the default model.
- **Implements:** FR-MODEL-003 · **Tests:** T-12

---

## Prompts

### US-020 — Reusable prompts
*As Nika I want to save my best instructions with categories, so I do not retype them.*

- **AC1** Create, list (paginated), filter by category, edit body, run, delete.
- **AC2** Running a prompt is a one-shot call and does not modify conversation history.
- **Implements:** FR-PROMPT-001, FR-PROMPT-002 · **Tests:** T-13

---

## Operator

### US-021 — Health at a glance
*As the Operator I want user/message/token totals and provider health in one screen.*

- **AC1** Non-admins receive `admin.denied`.
- **AC2** Stats include total users, blocked users, active in 24 h, message count, requests today, token totals.
- **AC3** Health lists each provider with ok/failure detail.
- **Implements:** FR-ADMIN-001, FR-ADMIN-002

### US-022 — Add a provider without redeploying
*As the Operator I want to add an OpenAI-compatible endpoint at runtime.*

- **AC1** Name, base URL, model, key are stored in `ai_providers`.
- **AC2** The registry refreshes without restarting the process.
- **AC3** Deletion removes it from the keyboard.
- **Implements:** FR-ADMIN-003

### US-023 — Protect the quota
*As the Operator I want to block and unblock a user.*

- **AC1** Blocked users cannot trigger handlers or AI calls.
- **AC2** They receive a localized blocked notice.
- **Implements:** FR-ADMIN-004

### US-024 — Announce
*As the Operator I want to broadcast a message to all users with pacing and a result count.*

- **AC1** Every user id is attempted; per-send failures are counted, not fatal.
- **AC2** Sends are paced to respect Telegram flood limits.
- **Implements:** FR-ADMIN-005

---

## Deployer

### US-025 — Ten-minute setup
*As a self-hoster I want one container and two required secrets.*

- **AC1** `.env.example` documents every variable the code reads.
- **AC2** Schema is created automatically on first boot.
- **AC3** Missing `BOT_TOKEN` fails fast with an actionable message.
- **AC4** `/app/data` is a volume so the database survives restarts.
- **Implements:** FR-CFG-001, FR-CFG-002

### US-026 — Safe schema evolution
*As a self-hoster I want an upgrade to add columns without losing data.*

- **AC1** Migration v2 adds only missing columns and is idempotent.
- **AC2** `schema_version` records the applied version.
- **AC3** A legacy v1 database upgrades on boot.
- **Implements:** FR-DB-002 · **Tests:** T-19, T-20
