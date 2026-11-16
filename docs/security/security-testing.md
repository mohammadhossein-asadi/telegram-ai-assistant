# Security Testing

## 1. Current state (measured, not aspirational)

| Check | Exists? | Runs today? |
| --- | --- | --- |
| Unit tests for text escaping | ✔ `tests/test_text.py` | ✔ locally |
| Localization parity | ✔ `tests/test_localization.py` | ✔ |
| Migration idempotency | ✔ `tests/test_migrations.py` | ✔ |
| Ownership regression tests | ✘ | — |
| Authorization tests | ✘ | — |
| Dependency audit (`pip-audit`) | ✔ workflow provided | ✘ never executed |
| Secret scanning (gitleaks) | ✔ workflow provided | ✘ never executed |
| Static analysis (bandit/ruff) | ✘ | — |
| Dynamic/penetration testing | ✘ | — |

**Statement of fact:** the repository's security testing is currently *unit tests on
utility functions plus two provided CI jobs that have not run*. Anything stronger is a
recommendation.

## 2. Test cases to add (ordered by value)

### 2.1 Access control (highest priority)

| ID | Case | Setup | Expected |
| --- | --- | --- | --- |
| ST-01 | Foreign conversation open | user B calls `conversations.get(a_conv.id, b.id)` | `None` |
| ST-02 | Foreign conversation delete | same with delete | raises/returns not found, row intact |
| ST-03 | Foreign persona update | id + wrong `user_id` | `None`, unchanged |
| ST-04 | Foreign prompt delete | id + wrong `user_id` | no deletion |
| ST-05 | Memory isolation | `list(a)` vs `list(b)` | disjoint |
| ST-06 | Admin gate | `Settings(admin_ids="1").is_admin(2)` | `False` |
| ST-07 | Admin gate parsing | `"1, 2 ,3"`, `" 4 "` | correct ids |

These are cheap repository-level tests and close the biggest gap.

### 2.2 Injection / rendering

| ID | Case | Input | Expected |
| --- | --- | --- | --- |
| ST-10 | HTML in AI output | `<b>x</b>` | escaped as `&lt;b&gt;` |
| ST-11 | Script-ish text | `<script>alert(1)</script>` | escaped, no tags |
| ST-12 | Markdown code fence | ```` ```py\nprint(1)\n``` ```` | `<pre>` block, content escaped |
| ST-13 | Nested/malformed markdown | `**unclosed` | plain text, no exception |
| ST-14 | Link with quotes | `[x](https://a.b/?q=")` | escaped href |
| ST-15 | Very long message | 4000 chars | chunked ≤ 3500, no split inside a code fence (documented limitation) |
| ST-16 | RTL + ZWNJ text | Persian string | preserved byte-for-byte |

Several of ST-10…ST-13 are already covered by `tests/test_text.py`; extend rather
than duplicate.

### 2.3 Data handling

| ID | Case | Expected |
| --- | --- | --- |
| ST-20 | `bot.db` contains no env secret | grep for the configured key returns nothing |
| ST-21 | `.env` untracked | `git ls-files` has no `.env` |
| ST-22 | Export contains only the caller's conversation | ids match |
| ST-23 | Clear history only affects one conversation | others intact |

### 2.4 Rate limiting

| ID | Case | Expected |
| --- | --- | --- |
| ST-30 | 21st request within a minute | `errors.rate_limited`, no provider call |
| ST-31 | Daily cap reached | `errors.daily_limited`, no provider call |
| ST-32 | Admin bypass | admin not limited |
| ST-33 | Failed call consumes quota | documented behaviour, assert it |

## 3. Manual security checklist (pre-release)

```markdown
[ ] `.env` not in git history (`git log --all -- .env`)
[ ] No key-shaped strings (`git grep -nE 'sk-[A-Za-z0-9]{16,}'`)
[ ] Non-admin cannot reach /admin or adm:* (manual test with a second account)
[ ] Foreign `conv:open:<id>` returns "not found"
[ ] Blocked user receives nothing
[ ] Prompt containing `<b>x</b>` renders literally in the chat
[ ] `data/` permissions are 700/600 on the host
[ ] Backups are encrypted or stored offline
[ ] `pip-audit -r requirements.txt` clean (or findings triaged)
[ ] Docker image runs as non-root (currently fails — known gap)
```

## 4. Tooling recommendations

| Tool | Purpose | Cost | Recommendation |
| --- | --- | --- | --- |
| `pip-audit` | known CVEs in deps | free | enable in CI (workflow provided) |
| `gitleaks`/`trufflehog` | secret scanning | free | enable (workflow provided) |
| `bandit` | Python SAST | free | add to CI; likely few findings in this codebase |
| `ruff` (S rules) | fast lint incl. security | free | TASK-103 |
| `semgrep` | custom rules (e.g. "no f-string SQL") | free tier | optional |

## 5. Reporting a vulnerability

See [`SECURITY.md`](../../SECURITY.md). Do **not** open a public issue containing an
exploit; report privately to the maintainer listed there.
