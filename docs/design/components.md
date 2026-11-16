# Components

Catalogue of reusable UI units. "Component" = a keyboard builder in
`src/bot/keyboards/common.py` plus a renderer in `src/bot/views.py`, both pure
functions of `(lang, data)`.

## 1. Component inventory

| Component | Builder | Renderer | States |
| --- | --- | --- | --- |
| Main menu | `main_menu` | `views.main_menu_text` | root |
| Back/Menu row | `back_to_menu` | — | every screen |
| Conversation list | `conversation_list` | `views.conversation_list_text` | empty, list, paginated |
| Conversation detail | `conversation_detail` | `views.conversation_detail_text` | active, archived, pinned |
| Language picker | `language_keyboard` | `views.language_text` | current marked |
| Settings screen | `settings_menu` | `views.settings_text` | toggles on/off |
| Persona menu | `persona_menu` | `views.persona_text` | preset selected |
| Preset grid | `persona_presets` / `style_grid` / `tone_grid` / `creativity_grid` | `views.*` | current marked |
| Custom persona list | `custom_persona_list` | `views.*` | empty, list |
| Memory screen | `memory_menu` | `views.memory_text` | enabled/disabled, empty |
| Model picker | `model_menu` | `views.model_text` | provider groups, auto on/off |
| Tools menu | `tools_menu` | `views.tools_text` | — |
| Tool input prompts | `tool_targets` etc. | `views.*` | FSM step |
| Prompt list | `prompt_list` | `views.prompt_list_text` | empty, paginated, filtered |
| Prompt detail | `prompt_detail` | `views.prompt_detail_text` | — |
| Developer profile | `developer_menu` | `views.developer_text` | loaded, unavailable |
| Repo list | `repo_list` | `views.repo_list_text` | paginated |
| About | `about_menu` | `views.about_text` | — |
| Admin panel | `admin_menu` | `views.admin_text` | — |
| Admin stats/limits/health | `admin_*` | `views.admin_*_text` | — |
| Provider list | `provider_list` | `views.provider_list_text` | empty, list |
| Confirm dialog | inline pairs | `views.confirm_text` | — |
| Error message | — | `ui.error_text` | key-based |

## 2. Component contracts

### 2.1 Main menu

```
Input:  lang, is_admin
Output: text (bold title + one-line hint), keyboard rows:
        [💬 Chat] [🗂 Chats]
        [🎭 Persona] [🤖 Model]
        [🛠 Tools] [🧠 Memory]
        [📚 Prompts] [⚙️ Settings]
        [👤 Profile] [ℹ️ About]
        ([🛡 Admin] only for admins)
Rules:  10 buttons max; every label localized; admin row omitted (not disabled)
```

### 2.2 Conversation list

```
Input:  lang, conversations[], page, total
Output: numbered text list (≤5 per page), one button per item labelled "{n}. {title}",
        navigation row [◀][▶] (rendered only when needed),
        action row [+ New] [🔍 Search] [Menu]
States: empty → text "No chats yet" + [+ New] as the only action
Order:  pinned first, then updated_at desc (repository decides)
```

### 2.3 Conversation detail

```
Input:  lang, conversation, message_count
Output: title, message count, model, persona, summary presence,
        actions: [Open] [Rename] [Pin/Unpin] [Archive/Unarchive]
                 [Summary] [Export] [Delete] [Back]
Rules:  Delete → confirm screen (two-step)
        Pin label reflects current state (button = toggle)
```

### 2.4 Settings

```
Input:  lang, settings
Output: rows for reply language, emoji, memory, auto-routing, privacy,
        and a destructive "Reset settings" (two-step)
Rules:  toggles show current state in the label ("Emoji: on")
```

### 2.5 Error message

```
Input:  lang, key, optional detail
Output: "⚠️ {localized message}" + next-step hint + [Retry][Menu] when applicable
Rules:  never include provider names, status codes, stack traces, or ids
```

### 2.6 Confirm dialog

```
Input:  lang, action_label, object_label, confirm_callback, cancel_callback
Output: "<b>{action}?</b>\n\n{object}\n⚠️ {irreversible hint}\n[✅ Confirm][Cancel]"
Rules:  confirm callback distinct from the initiating callback (prevents double-tap)
```

## 3. Composition rules

1. **Pure builders:** keyboards take data and return markup; no DB calls, no I/O.
2. **Renderers take `lang`:** never read `container` for translation.
3. **One callback per row item**, integer id only.
4. **Back target is explicit:** detail screens return to their list, not to home.
5. **Pagination is stateless:** the page number is in the callback
   (`conv:list:2`), never in FSM.

## 4. Density limits

| Surface | Max items |
| --- | --- |
| Main menu buttons | 10 (+1 admin) |
| List page | 5 |
| Preset grid | 6 per row × 2 rows |
| Model list | 8 providers visible, then scroll via pagination |
| Message length | 3500 chars per chunk |

## 5. Missing components (deliberate)

| Not built | Reason |
| --- | --- |
| Search results pager with query state | search enters FSM, results are one page |
| Rich media cards | no images/files in the product |
| Inline query results | no use case |
| Mini App | no web UI |
| Toast-only confirmations | destructive actions need a real screen |

## 6. Adding a component

1. Builder in `keyboards/common.py` (or its domain module).
2. Renderer in `views.py` (pure).
3. Both catalogs updated (parity test enforces).
4. Callback prefix added to `artifacts/api/telegram-interface.json`.
5. Screenshot-free review using the six success criteria in
   [design principles](design-principles.md#6-success-criteria-for-a-screen-review-checklist).
