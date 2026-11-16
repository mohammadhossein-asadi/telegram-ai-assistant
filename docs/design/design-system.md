# Design System

Tokens available inside Telegram: **text formatting, emoji, whitespace, button order
and message segmentation.** There are no colours, fonts, shadows or spacing variables
to control — choosing to design *with* the platform's typography is the system.

## 1. Typography

| Role | Rendering | Example |
| --- | --- | --- |
| Screen title | bold, first line | **Chats** |
| Section label | bold + emoji prefix | **🧠 Memory** |
| Body | plain text | `You have 12 chats.` |
| Emphasis | bold | `**pinned**` |
| Inline code | `<code>` | `/new` |
| Block code | `<pre>` | fenced code from a model reply |
| Muted/secondary | no italics (unreliable across clients) — use parentheses | `(auto)` |
| Divider | blank line, or `—` only when needed | — |

**Rules**

- One bold line per message maximum (the title).
- No ALL CAPS (breaks Persian shaping and reads as shouting).
- Italic is avoided as a semantic device; some clients render Persian italic poorly.

## 2. Spacing and segmentation

Telegram collapses repeated spaces and has no margins, so spacing is created by
**message segmentation**:

| Pattern | Use |
| --- | --- |
| Title / blank / body | detail screens |
| Body / blank / hint | confirmations with a next step |
| List items separated by `\n` | lists of ≤ 8 items |
| Separate message | progress or a long AI answer |

Hard rule: never emit more than 3 consecutive messages for one user action.

## 3. Colour and status (semantic emoji only)

| Meaning | Token | Where |
| --- | --- | --- |
| Success | ✅ | confirmations |
| Warning / recoverable | ⚠️ | `errors.*` |
| Failure | ❌ | destructive result |
| In progress | ⏳ | long operations (rare) |
| Feature badge | 🧠 memory, 🎭 persona, 🛠 tools, 📚 prompts, ⚙️ settings, 👤 profile, 🤖 model, 💬 chat | menus |
| Pin / archive | 📌 / 🗂 | conversation rows |
| Admin | 🛡 | admin panel |

Emoji carry **secondary** meaning only; the text always states the meaning. This keeps
the UI usable with emoji disabled (`emoji_enabled=false` removes decorative emoji from
AI prompts, not from UI labels).

## 4. Layout grammar

**Detail screen**

```
<b>{Title}</b>

{body line 1}
{body line 2}

{hint}
[primary action] [secondary]
[Back] [Menu]
```

**List screen (paginated)**

```
<b>{Title}</b>

1. {item} {badges}
2. {item}
…

[1] {first item}
[2] {second item}
…
[◀ Prev] [Next ▶]
[+ New] [Menu]
```

**Confirmation**

```
<b>{Action}?</b>

{object name}
{warning if destructive}

[✅ Confirm] [Cancel]
```

**Error**

```
⚠️ {what failed, one line}

{what to do}

[Retry] [Menu]
```

## 5. Buttons

| Property | Rule |
| --- | --- |
| Label length | ≤ 20 characters, ≤ 3 words |
| Order | primary left/top, cancel right/bottom |
| Row width | 2 buttons for actions, 1 for destructive confirm |
| Persistent row | `[Back] [Menu]` on every non-root screen |
| Callback data | `namespace:action[:id]`, ≤ 64 bytes |
| Icon-only | never |
| Disabled state | not available in Telegram — omit the button instead |

### Button taxonomy

| Kind | Example | Behaviour |
| --- | --- | --- |
| Navigate | `menu:settings` | edits the current message |
| Select | `ps:teacher` | edits in place, shows the new value |
| Toggle | `mem:toggle` | edits in place, label reflects new state |
| Act | `conv:new` | may send a new message or enter FSM |
| Confirm | `conv:delok:12` | performs the destructive action |
| External | `gh:refresh` | may take seconds; show a toast first |

## 6. Content patterns

| Content | Pattern |
| --- | --- |
| Conversation list item | `📌 {title} · {n} msgs` |
| Persona item | `{emoji} {name}{ · default}` |
| Prompt item | `{title} · {category}` |
| Provider row | `{name} · {model}{ · inactive}` |
| Usage line | `{action} · {tokens} tok · {latency} ms` |
| Model line | `{provider} / {model}{ (auto)}` |

## 7. Localization tokens

| Concern | FA | EN |
| --- | --- | --- |
| Direction | RTL | LTR |
| Digits | Persian digits in copy (`۲۰`) | Latin (`20`) |
| Punctuation | `،` and `؟` | `,` and `?` |
| ZWNJ | required in `میشود`, `چتها` | n/a |
| Arrow placement | after the label to avoid bidi jumps | `→` prefix allowed |
| Truncation | allow +15% width vs EN | baseline |

Catalog structure: 21 namespaces (`common`, `start`, `menu`, `chat`, `convs`,
`personas`, `cps`, `memory`, `model`, `tools`, `prompts`, `settings`, `admin`,
`developer`, `about`, `errors`, `usage`, `limits`, `privacy`, `lang`, `emoji`).
Parity enforced by test (ADR-007).

## 8. Motion

There is no animation control. The only "motion" tokens are:

| Token | Implementation |
| --- | --- |
| Typing indicator | `ChatActionSender`/`typing` while a provider call runs |
| Progress feedback | toast via `answerCallbackQuery` for slow callbacks |
| No spinners | a bot cannot render them; never promise progress percentages |

## 9. Accessibility hooks

Bold titles, labelled buttons, no icon-only controls, semantic emoji with text
fallbacks. Full treatment: [accessibility](accessibility.md).

## 10. What this system deliberately lacks

No component library, no theme switcher, no dark mode, no custom emoji pack, no
inline-mode results, no Mini App. Each would require a web surface the product does
not have.
