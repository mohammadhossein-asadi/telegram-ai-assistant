# Contributing

Thanks for considering a contribution. This project is small on purpose; the fastest
way to get a change merged is to keep it small too.

## 1. Before you start

| Change | Do this first |
| --- | --- |
| Bug fix | open an issue with reproduction steps (or reference an existing one) |
| New feature | open an issue describing the user problem — features are scoped against the [product DNA](docs/product/product-dna.md) |
| Docs | PR directly, no issue needed |
| Dependency/tooling addition | justify it in the issue; the default answer is no |
| Security issue | **do not open an issue** — see [SECURITY.md](SECURITY.md) |

## 2. Setup

```bash
git clone https://github.com/mohammadhossein-asadi/MhaAiAssistantBot.git
cd MhaAiAssistantBot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env      # only needed to run the bot, not for tests
pytest -q                 # 31 tests, offline
```

Full guide: [development environment](docs/devops/development-environment.md).

## 3. Architecture rules you must respect

1. Handlers orchestrate; services own logic; repositories own SQL.
2. No `aiogram` imports in `services/` or `database/`.
3. Every user-scoped query filters on `user_id`.
4. The chat router is registered **last**.
5. Locale keys must exist in both `fa.json` and `en.json`.
6. Schema changes are additive: bump `SCHEMA_VERSION`, add the column entry, update
   `artifacts/database/schema.sql` and `docs/database/data-dictionary.md`.
7. Callback payloads follow `namespace:action[:id]` and have exactly one owner.

Details: [ADR-001](docs/architecture/decisions/ADR-001-architecture-pattern.md).

## 4. Coding standards

- Python 3.12, `from __future__ import annotations`, type hints, double quotes.
- Match the surrounding file; do not reformat unrelated code.
- No new dependency without a demonstrated need.
- No secret in code, tests, fixtures, logs, or docs.
- No `print`; use the module logger.

## 5. Tests

- New behaviour ⇒ a test at the lowest level that can observe it.
- Bug fix ⇒ a test that fails before and passes after.
- Tests must be offline, deterministic, and isolated (in-memory DB, fake provider).
- Do not delete or weaken a test to make a change pass — explain a genuine behaviour
  change in the PR instead.

## 6. Commit and PR

**Commit messages**

```
<area>: <imperative summary>

Why this change is needed. What was wrong or missing.
```

Examples:

```
chat: persist usage for failed provider calls
i18n: fix ZWNJ in conversation delete confirmation
db: add latency_ms to usage_logs
```

**PR checklist**

```markdown
- [ ] `pytest -q` passes
- [ ] `python -m compileall -q src` passes
- [ ] both locale files updated (if strings changed)
- [ ] migration + docs updated (if schema changed)
- [ ] no unrelated reformatting
- [ ] PR description explains the user-visible effect
```

Keep PRs focused; split refactors from behaviour changes.

## 7. Documentation

Docs live in [`docs/`](docs/index.md) and are organised by concern. If your change
alters a contract (command, callback, env var, schema, limit), update the matching
document and, for requirement changes, the traceability CSV in `manifest/`.

## 8. Localization contributions

Persian copy needs correct ZWNJ (`میشود`, not `میشود`), Persian digits in copy, and
`،`/`؟` punctuation. Do not machine-translate: match the existing tone (see
[design principles](docs/design/design-principles.md)). A native review is expected
for substantial Persian changes.

## 9. Review expectations

| Aspect | Looked at |
| --- | --- |
| Correctness | does it do what the issue asked |
| Scope | nothing unrelated changed |
| Layering | imports respect the architecture |
| Data safety | migrations, ownership filters |
| Tests | meaningful, not just green |
| Docs | updated where behaviour is contractual |

## 10. Code of conduct

Participation is governed by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
