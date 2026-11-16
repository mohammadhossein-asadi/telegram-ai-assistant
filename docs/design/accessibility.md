# Accessibility

A Telegram bot inherits the client's accessibility features (screen readers, font
scaling, high contrast). What the bot controls is **text structure, label clarity,
language and keyboard-only reachability**. This document records what is done and what
cannot be done.

## 1. What the platform provides

| Feature | Provided by | Our dependency |
| --- | --- | --- |
| Screen reader | client (TalkBack/VoiceOver/NVDA) | text must be meaningful when read linearly |
| Font scaling | client | avoid layout that assumes a fixed width |
| High contrast | client | we cannot set colours; rely on structure |
| Keyboard navigation (desktop) | client | buttons must be reachable via tab/arrow keys |
| RTL support | client, driven by message content | correct Persian copy |

## 2. What the bot does

| Practice | Implementation | Why it matters |
| --- | --- | --- |
| Bold titles rather than ALL CAPS | renderers use `<b>` | screen readers may spell out caps |
| Every button has a text label | keyboard builders | icon-only buttons are unusable with a screen reader |
| Emoji are decorative and duplicated by text | labels like `🧠 Memory` | emoji names are read aloud ("brain") and add noise |
| Status words, not colour | `✅`, `⚠️` + words | no colour semantics exist |
| Linear reading order | title → body → hint → buttons | the client reads in this order |
| Short paragraphs | segmentation rules | long unbroken blocks are hard to scan |
| Consistent button order | `[Back] [Menu]` last row | predictable position for keyboard users |
| No timed interactions | no auto-dismiss, no countdown | users with motor impairments are not rushed |
| No required typing | every action has a button | commands remain as shortcuts |
| Plain-language errors | `errors.*` copy | avoids jargon and status codes |
| Language choice persisted | `users.language` | the reader's language is respected across sessions |
| Reply-language independent of UI | `response_language` | cognitive accessibility: read UI in one language, answers in another |

## 3. Known accessibility gaps

| # | Gap | Impact | Possible fix |
| --- | --- | --- | --- |
| A1 | Persian copy sometimes uses Arabic-presentation forms inconsistently | screen reader pronunciation varies | copy review with a native reader |
| A2 | Numbered lists are visual only (no `1.` semantics in text) | screen readers read "1 dot" | acceptable; could use words |
| A3 | Pagination labels `◀`/`▶` are symbols | read as "left triangle" | add `Prev`/`Next` text (recommended) |
| A4 | Emoji in the main menu (10 rows) can be noisy | verbosity | `emoji` setting affects AI replies only — UI emoji are fixed |
| A5 | No explicit "current selection" text in some grids (only a dot prefix) | depends on visual cue | add `(selected)` text |
| A6 | Very long AI answers are split without part numbers | users may lose order | add `(1/3)` only when >2 chunks |
| A7 | No image alt text | no images exist | n/a |
| A8 | No reduced-motion consideration | only a typing indicator | n/a |
| A9 | No high-contrast variant | platform-controlled | n/a |

A3 and A5 are cheap fixes and are listed in the roadmap as polish, not scheduled work.

## 4. Language and readability

| Metric | Target | Current |
| --- | --- | --- |
| Sentence length | ≤ 20 words | mostly met; admin text is longer |
| Jargon in user-facing copy | none | "provider", "model" appear on the model screen (acceptable domain terms) |
| Persian ZWNJ correctness | required | maintained; verified byte-level during mirroring |
| Mixed-script strings | avoid | some model names are Latin inside Persian text (unavoidable) |
| Directional marks | use sparingly | not currently used; RTL relies on client bidi |

## 5. Keyboard-only walkthrough (target flow)

1. `/start` → focus lands on the message; arrow keys move through buttons.
2. `[💬 Chat]` → Enter → chat screen.
3. Type a message → send → reply arrives as a new message.
4. `[Menu]` → back to root.

No step requires a mouse, a hover, or a long-press. No step requires typing a command.

## 6. Verification

| Check | Method | Status |
| --- | --- | --- |
| Labels are text, not icons | code review of `keyboards/common.py` | verified by inspection |
| Titles use bold not caps | code review of `views.py` | verified by inspection |
| Errors avoid status codes | review of `errors.*` copy | verified by inspection |
| Screen-reader pass (FA/EN) | manual with TalkBack/VoiceOver | **not performed** |
| Font scaling at 200% | manual | **not performed** |
| Keyboard-only pass on desktop | manual | **not performed** |

The last three require a Telegram client and are outstanding; this document does not
claim they were done.

## 7. Accessibility in contribution review

A PR that adds a screen must answer:

1. Does every control have a text label?
2. Does the screen read sensibly in order, without seeing the layout?
3. Does it work in Persian without ZWNJ errors and in English without truncation?
4. Is there a non-typing path to the same action?
5. Does it avoid timers and auto-dismiss?
