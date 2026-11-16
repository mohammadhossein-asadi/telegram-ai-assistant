# 20 — Security review

**Phase:** review · **Use when:** a change touches auth, rendering, SQL, secrets, or external input.

## Role
Security reviewer using the project's STRIDE model.

## Inputs
- `docs/security/threat-model.md` (T1–T18)
- `docs/security/authentication-authorization.md`
- The diff

## Task
1. Map the change to affected threats (or state "none" and justify).
2. Check authorization: can another user reach this data or action?
3. Check input: is anything user-controlled reaching SQL, HTML, a URL, or the filesystem?
4. Check output: is model/user text escaped before HTML conversion?
5. Check secrets: any new value logged, stored, or echoed?
6. Check resource use: can this be abused for cost or disk?
7. Assign severity and recommend a concrete mitigation.

## Constraints
- Do not report theoretical issues without an exploit path; label them as hardening.
- Do not weaken escaping or ownership checks to satisfy a feature.
- Never print or request real credentials.

## Output
Threat mapping table, findings with severity + exploit sketch + fix, verdict.

## Verification
- Each finding names the file/line and the mitigation.
- Hardening items are separated from vulnerabilities.
