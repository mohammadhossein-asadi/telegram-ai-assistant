# ADR-007 — JSON catalogs, per-user language, parity enforced by test

- **Status:** Accepted (implemented)
- **Date:** 2026-11-16
- **Related:** [design system](../../design/design-system.md), [FR-I18N-*](../../product/functional-requirements.md)

## Context

The product is Persian-first but must be fully usable in English. Two audiences read
the same screens; Persian is RTL and uses ZWNJ/ZWJ characters that are easy to break
during edits. The repository has no build step and no translation service. The
codebase is maintained by one developer plus AI assistants, which raises the risk of
"translate the new string in one file only".

## Problem

How do we keep two complete locales in sync with zero tooling, while allowing a user
to switch UI language at runtime and independently control the language of AI replies?

## Considered alternatives

| Option | Pros | Cons | Verdict |
| --- | --- | --- | --- |
| A. Nested JSON + custom loader + parity test | no build step; readable diffs; test-enforced completeness | no pluralization/ICU; keys must be maintained by hand | **Chosen** |
| B. GNU gettext (`.po`/`.mo`) | translator tooling, plurals | compile step, binary-ish workflow, worse in-code review | Rejected |
| C. Fluent (`.ftl`) | plurals, gender, attributes | new runtime dependency and syntax to learn | Rejected |
| D. Inline `fa if lang=="fa" else en` | fastest to write | unmaintainable, untestable, spreads text through handlers | Rejected |
| E. Third-party TMS | translator workflow | external service, overkill for 2 locales | Rejected |

## Decision

1. **Storage:** `src/localization/en.json` and `fa.json`, nested by feature namespace
   (`common`, `start`, `menu`, `chat`, `convs`, `settings`, `admin`, …), 21 top-level
   namespaces.
2. **Loader:** `src/localization/__init__.py` reads both files once, resolves dotted
   keys, applies `str.format(**kwargs)`, and falls back to `DEFAULT_LANGUAGE` for an
   unknown language and to the key string for an unknown key.
3. **Selection:** `users.language` (persisted); middleware injects `lang` into every
   handler; keyboards/views always take `lang` as a parameter.
4. **AI language:** separate setting `response_language` ∈ {`auto`,`fa`,`en`}; `auto`
   uses `detect_language()` on the user's message, falling back to the UI language.
5. **Parity enforcement:** `tests/test_localization.py` compares recursive key sets;
   any missing/extra key fails CI.
6. **Text quality:** Persian strings are hand-authored (not machine-translated) with
   correct ZWNJ; a regression that replaces a character fails review, and the catalogs
   are verified byte-for-byte during mirroring operations.

## Consequences

**Positive**

- Reviewable diffs; no tooling to learn; parity cannot silently rot.
- UI language and reply language are independently controllable — a real user need.
- Adding a third locale = add `<lang>.json`, extend `SUPPORTED_LANGUAGES`, extend the
  language keyboard.

**Negative / accepted costs**

- No plural rules: strings must be written to avoid count-dependent grammar, or
  phrased neutrally.
- No context for translators (no comments in JSON).
- Placeholder names are not validated across locales at runtime; a mismatched
  placeholder raises `KeyError` in `str.format` (test coverage is partial).

## Risks

| Risk | Mitigation |
| --- | --- |
| Persian text corrupted (ZWNJ/ZWJ/VS16) | byte-level verification when files are regenerated; diff review |
| New key added to one file only | parity test fails CI |
| Key referenced in code but absent in catalogs | loader returns the key string; visible in UI during review |
| Placeholder mismatch between locales | extend the parity test to compare placeholder sets (recommended, not implemented) |

## Verification

- `tests/test_localization.py` — both catalogs load, identical keys, formatting,
  unknown-language fallback.
- `README.md` documents the two files and the parity guarantee.
