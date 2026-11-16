## What and why

<!-- One or two sentences: what changed and the problem it solves. -->

Closes #

## Type

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor (no behaviour change)
- [ ] Documentation
- [ ] Chore / tooling
- [ ] Security fix (describe the impact without exploit details)

## Verification

<!-- Paste the commands you ran. Do not tick boxes you did not actually run. -->

```bash
pytest -q
python -m compileall -q src
```

- Tests run: <!-- e.g. "31 passed" -->
- Manual check: <!-- what you did in Telegram, or "not performed (no token)" -->

## Checklist

- [ ] Scoped to one concern; no unrelated reformatting
- [ ] New/updated behaviour has a test
- [ ] Both `src/localization/fa.json` and `en.json` updated (if strings changed)
- [ ] Schema change ⇒ `SCHEMA_VERSION` bumped + additive migration + `schema.sql` +
      data dictionary updated
- [ ] Callback prefix documented in `artifacts/api/telegram-interface.json`
      (if a button/payload was added)
- [ ] No secret, token, or private chat content in the diff
- [ ] Docs updated where a contract changed (command, callback, env var, limit)

## Risk

<!-- What could break? Who is affected? Any migration or data implications? -->

## Screenshots / logs

<!-- Optional. Redact user ids, tokens and chat content. -->
