# Design Principles

The product has **no web UI**. Its surface is a Telegram chat: text messages, inline
keyboards and short flows. "Design" here means information hierarchy in a message,
button taxonomy, copy tone, and behaviour under Telegram's constraints.

## 1. Product character

| Dimension | Choice | Consequence |
| --- | --- | --- |
| Tone | Calm, competent, lightly warm | no hype, no emoji spam, no exclamation marks |
| Density | Low per screen | ≤ 8 buttons visible; lists paginate at 5 |
| Navigation | Always reversible | every screen has `home`; every destructive action is two-step |
| Language | Persian-first, English parity | RTL layout, ZWNJ correctness, mirrored arrow glyphs |
| Identity | Minimal | the bot is a tool, not a character |

## 2. Principles

### P1 — One decision per screen
Every message either *shows state* or *asks for one thing*. A screen with a menu and a
question is two screens.

**Applied:** `conv:list` shows a list; `conv:rn:<id>` asks only for the new title.

### P2 — The keyboard is the API
Users should never have to remember a command. Every capability is reachable by
tapping; commands exist as shortcuts for power users.

**Applied:** all 10 commands have an equivalent button path (`/new` ⇄ `conv:new`).

### P3 — Never lose the user's place
After a flow completes, return to the screen that started it, not to `/start`.

**Applied:** rename/edit flows re-render the detail view.

### P4 — Say what happened, then what's next
Confirmations are one line of fact plus the available next step.

**Applied:** `✅ Saved` + `[Back] [Menu]`.

### P5 — Destructive actions take two taps
Delete conversation and reset settings need an explicit confirm step with the object
named (`conv:del:<id>` → `conv:delok:<id>`; `set:reset` → `set:resetok`).

**Applied:** in `conversations.py` and `settings.py`.

### P6 — Degrade, never break
Long output is chunked; failed HTML falls back to plain text; a missing translation
shows the key instead of crashing.

**Applied:** `utils/text.split_message`, `ui.safe_edit`, localization fallback.

### P7 — Respect the reader's language
UI language and AI reply language are separate settings, because a Persian speaker may
want English answers or vice versa. Dates, numbers and arrows follow the UI language.

**Applied:** `users.language` vs `user_settings.response_language`; `detect_language`.

### P8 — Quiet by default
No unsolicited messages, no notifications, no "did you know" tips, no streaks.

**Applied:** no scheduled sending exists; broadcast is admin-only and manual.

### P9 — Errors are instructions
Every error states what to do next, in the user's language, without jargon.

**Applied:** `errors.*` keys phrased as actions.

### P10 — The chat is the record
History reflects what actually happened; no fake typing, no optimistic rows that later
vanish.

**Applied:** persist-after-success (ADR-004) means history never contains an
unanswered user turn.

## 3. Anti-patterns (explicitly avoided)

| Anti-pattern | Why avoided |
| --- | --- |
| Wall-of-text menus | Telegram clients truncate and users scroll; buttons win |
| Emoji as the only signal | screen readers and non-emoji fonts; always pair with text |
| Nested submenus beyond 2 levels | users lose the path; flatten instead |
| Command-only features | discoverability collapses |
| "Typing…" simulation without a real request | dishonest and confusing |
| Auto-deleting messages | breaks the chat record and user trust |
| Mixed RTL/LTR without isolation | punctuation jumps; mitigated by Persian-first copy |
| Modals/alerts for non-errors | `show_alert` is reserved for real problems |

## 4. Voice and copy rules

| Rule | Example |
| --- | --- |
| Sentence case | `New chat`, not `New Chat` |
| Second person, no honorifics | `Your chats` |
| No gendered Persian verbs where avoidable | `ذخیره شد` instead of `ذخیره کردی` |
| Numbers as digits in both locales | `۲۰` in FA copy, `20` in EN |
| Max one emoji per message, at the end | `✅ Saved` |
| Buttons ≤ 20 characters | `🗑 Delete` |
| No technical terms in errors | "AI service didn't respond", not "HTTP 502" |

## 5. Constraint-driven design

| Constraint | Design response |
| --- | --- |
| 4096-char message limit | chunk at 3500; AI replies split on paragraph boundaries where possible |
| Callback data ≤ 64 bytes | short prefixes + integer ids |
| No hover, no tooltips | every action is labelled; no icon-only buttons without text |
| No custom fonts or colours | hierarchy comes from bold, spacing, emoji and order |
| Clients render differently | never rely on precise alignment or tables |
| RTL in FA | avoid leading arrows in mixed text; use `→` after the label |

## 6. Success criteria for a screen (review checklist)

1. Can a first-time user tell what this screen is for in 3 seconds?
2. Is there exactly one primary action?
3. Is there a way back that does not require typing?
4. Does it work in both languages without truncation?
5. Does it survive a 4096-char paste?
6. If the AI call fails, is the failure visible and recoverable?

See [design system](design-system.md) and [components](components.md) for the concrete
patterns.
