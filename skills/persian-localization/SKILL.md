---
name: persian-localization
description: Add or fix bilingual FA/EN copy in this bot — key parity, ZWNJ, Persian digits and punctuation, tone, and label-length limits.
---

# Skill: Persian/English localization

Use for any user-visible string.

## Files

- `src/localization/fa.json` — Persian (default language)
- `src/localization/en.json` — English
- Lookup: `t(lang, key, **kwargs)` from `bot.ui` → `localization.t`. A missing key falls
  back to the key string itself (e.g. the UI shows `convs.empty`), so a typo is silent at
  runtime; `tests/test_localization.py` is what actually protects you.

## Steps

1. Find the namespace: `convs.*`, `persona.*`, `set.*`, `tools.*`, `prom.*`, `mem.*`,
   `models.*`, `adm.*`, `dev.*`, `errors.*`, `menu.*`, `common.*`.
2. Add the same key to both files at the same position.
3. Keep placeholders identical: `{count}` in FA must be `{count}`, not `{تعداد}`.
4. Write Persian with correct ZWNJ (`میشود`, `دستش`) and Persian punctuation `،` `؟`;
   use Persian digits in copy that shows numbers to users.
5. Match the tone in `docs/design/design-system.md` §Voice: second person, direct,
   no honorific padding, no exclamation marks.
6. Keep buttons short: EN ≤ 20 chars, FA ≤ 22 chars.
7. Run the parity test.

## Examples

| Key | FA | EN |
| --- | --- | --- |
| `convs.empty` | هنوز هیچ گفتگویی ندارید. | You have no conversations yet. |
| `convs.confirm_delete` | «{title}» حذف شود؟ این کار قابل بازگشت نیست. | Delete "{title}"? This cannot be undone. |
| `errors.rate_limited` | ⏳ درخواست‌ها بیش از حد است. کمی صبر کنید. | ⏳ Too many requests. Please wait a moment. |
| `errors.daily_limited` | 🚫 به محدودیت درخواست امروز رسیدید ({limit}). | 🚫 You reached today's request limit ({limit}). |
| `common.empty` | هنوز چیزی اینجا نیست. | Nothing here yet. |

These are copies of real entries; keep new copy consistent with them.

## Anti-patterns

| Bad | Why |
| --- | --- |
| `درخواستها` written without the ZWNJ | renders as one malformed word; write `درخواست‌ها` |
| `لطفا کلیک کنید` | transliterated UI verb; existing copy uses natural Persian |
| English text inside `fa.json` | parity test passes, UX fails |
| `{name}` → `{نام}` | `KeyError`/`ValueError` at format time |
| Emoji in every string | noise; the project uses emoji sparingly and per-setting |

## Verification

```bash
pytest -q tests/test_localization.py
python - <<'PY'
import json
fa = json.load(open("src/localization/fa.json", encoding="utf-8"))
en = json.load(open("src/localization/en.json", encoding="utf-8"))
print(len(fa), len(en), set(fa) ^ set(en))
PY
```

The symmetric difference must be empty. Then check the string in Telegram manually —
rendering of long Persian labels in inline keyboards is not covered by tests.
