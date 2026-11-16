# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| `main` (latest) | ✅ |
| older tags | ❌ — upgrade to the latest tag |

This is a single-maintainer project with no LTS branch.

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

Report privately through either channel:

1. GitHub → repository → **Security** → **Report a vulnerability** (private advisory).
2. A direct message to the maintainer,
   [@mohammadhossein-asadi](https://github.com/mohammadhossein-asadi), including a
   minimal reproduction.

Include:

- affected file/component and version or commit,
- steps to reproduce (or a proof of concept),
- impact you believe it has,
- whether the issue is already public.

## What to expect

| Stage | Target |
| --- | --- |
| Acknowledgement | within 72 hours (best effort) |
| Initial assessment | within 7 days |
| Fix or mitigation plan | depends on severity; critical issues prioritised |
| Public disclosure | coordinated with the reporter after a fix is available |

These are intentions, not a contractual SLA.

## In scope

- Authorization bypass (reading or modifying another user's data).
- Telegram HTML/markdown injection through model output.
- SQL injection.
- Secret leakage in code, logs, messages, or repository history.
- Denial of service caused by unbounded resource use (quota, memory, disk).
- Dependency vulnerabilities with a practical exploit path.

## Out of scope

- Vulnerabilities in Telegram, the AI provider, or the host OS.
- Prompt-injection *within a single user's own session* (a user may instruct the model
  however they like; it cannot reach another user's data).
- Model hallucinations or incorrect answers.
- Missing hardening from the known-gaps list (rate limiting per process, container
  running as root, no encryption at rest) — these are documented limitations. **Reports
  that add exploitation detail are still welcome.**
- Social engineering of the operator.

## Known security limitations (disclosed)

1. Admin-added provider keys are stored **plaintext** in SQLite
   ([ADR-005](docs/architecture/decisions/ADR-005-secrets-and-provider-keys.md)).
2. No encryption at rest for conversations or backups.
3. No account-deletion feature; erasure is a manual operator procedure.
4. Rate limits are in-process and reset on restart.
5. The container runs as root and has no healthcheck.

Full analysis: [threat model](docs/security/threat-model.md).

## Handling secrets

- Never commit `.env`, `data/`, or keys.
- If you suspect a leak, revoke first, then rotate
  ([secrets management §5](docs/security/secrets-management.md#5-incident-suspected-key-leak)).
- Do not paste production secrets into issues, PRs, or chat.

## Safe-harbour

Good-faith research that respects this policy, avoids privacy violations, avoids
service disruption, and reports privately will not be pursued legally by the
maintainer. Do not test against deployments you do not own.
