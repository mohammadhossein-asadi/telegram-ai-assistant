# 14 — Localization update

**Phase:** implementation · **Use when:** any user-visible string is added or changed.

## Role
Bilingual maintainer (Persian-native quality bar).

## Inputs
- `src/localization/en.json`, `src/localization/fa.json`
- `docs/design/design-system.md` §localization tokens
- `tests/test_localization.py`

## Task
1. Add the key under the correct namespace in **both** files, same order.
2. Keep placeholders identical (`{count}`, `{name}`) in both languages.
3. Persian: correct ZWNJ, Persian digits, `،`/`؟`, natural verb order, no machine-translated
   phrasing; match the existing tone.
4. Keep button labels ≤ 20 characters (EN) / 22 (FA).
5. Run the parity test; report the result.

## Constraints
- No key removal without grepping for its usage.
- No fallback-only additions (English text inside fa.json).
- Do not reorder or reformat unrelated keys.

## Output
Key list added/changed + parity test result + note on truncation risk.

## Verification
```bash
pytest -q tests/test_localization.py
python -c "import json;print(len(json.load(open('src/localization/fa.json'))))"
```
