# Open Questions

Everything below genuinely needs an answer from the maintainer or the operator. Nothing
here is resolved by reading the code.

Status legend: **blocking** (stops a planned task) · **open** · **answered** (kept for
history).

## Product

| ID | Question | Why it matters | Status |
| --- | --- | --- | --- |
| Q-01 | What is the real monthly AI spend per active user? | decides whether per-user quotas are generous or tight | `[UNKNOWN — USER INPUT REQUIRED]` |
| Q-02 | Is the target audience primarily Iranian users behind network restrictions? | affects provider defaults (some providers are unreachable) | `[UNKNOWN — USER INPUT REQUIRED]` |
| Q-03 | Should the developer screen show a public GitHub profile, or is it branding only? | it currently fetches `GITHUB_USERNAME` | `[UNKNOWN — USER INPUT REQUIRED]` |
| Q-04 | Is group-chat support ever wanted? | the chat router assumes private chats | open (out of scope v1) |
| Q-05 | What is the acceptable reply-length limit for the Persian UI? | chunking is at 3500 chars | `[UNKNOWN — USER INPUT REQUIRED]` |

## Architecture & operations

| ID | Question | Why it matters | Status |
| --- | --- | --- | --- |
| Q-06 | Will the bot ever run more than one instance? | current FSM and rate limits are process-local | **blocking** TASK-201/202 |
| Q-07 | Is a webhook deployment (public URL) ever required? | changes hosting, TLS, and the runbook | open |
| Q-08 | Should provider keys be encrypted with a passphrase or an environment-held key? | no key-management decision exists | **blocking** TASK-104 |
| Q-09 | Which hosting platform is the reference deployment? | the runbook currently covers Docker Compose generically | `[UNKNOWN — USER INPUT REQUIRED]` |
| Q-10 | How long must `usage_logs` be retained? | retention drives pruning and backup size | open |
| Q-11 | Is there an existing backup destination (S3, NAS)? | backup doc offers methods, not a chosen one | `[UNKNOWN — USER INPUT REQUIRED]` |

## Privacy & compliance

| ID | Question | Why it matters | Status |
| --- | --- | --- | --- |
| Q-12 | What is the promised response time for a data-deletion request? | there is no deletion feature, only an operator procedure | `[UNKNOWN — USER INPUT REQUIRED]` |
| Q-13 | Is a privacy policy or terms page required for the bot? | Telegram bots handling personal data may need one | `[UNKNOWN — USER INPUT REQUIRED]` |
| Q-14 | Should memory facts be encrypted at rest? | memory holds user-provided personal facts | open |

## Documentation & quality

| ID | Question | Why it matters | Status |
| --- | --- | --- | --- |
| Q-15 | Is the Persian copy reviewed by a native speaker? | machine-written copy can read awkwardly | `[UNKNOWN — USER INPUT REQUIRED]` |
| Q-16 | Should `ruff` be adopted as the lint/format gate? | no style tool today; TASK-103 proposes it | open |
| Q-17 | Should the README be rewritten to match this documentation set? | it currently claims Alembic and a pydantic-settings container | open (not changed by this work) |
| Q-18 | Which licence year/owner should the `LICENSE` show? | written as 2026 / Mohammadhossein Asadi | answered: matches repository owner |

## Answered (history)

| ID | Question | Answer |
| --- | --- | --- |
| Q-19 | Should documentation be delivered as a ZIP? | No — written directly into the repository. |
| Q-20 | Should the docs describe a REST API? | No — the bot has no HTTP surface; the contract is Telegram commands/callbacks. |

## How to close a question

1. Answer it in this file with the date and the decision taken.
2. If it changed a boundary, write an ADR and link it.
3. Update the affected document (and the traceability CSV if a requirement changed).
