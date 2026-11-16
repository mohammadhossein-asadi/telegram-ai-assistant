# 03 — Scope and non-goals

**Phase:** discovery · **Use when:** a feature request is vague, large, or risks scope creep.

## Role
Maintainer applying the project's stated boundaries.

## Inputs
- `docs/product/product-dna.md` §boundaries
- `docs/product/functional-requirements.md` (out-of-scope table)
- `docs/product/product-roadmap.md`

## Task
1. Write the request as a one-line user outcome.
2. Split it into: **must**, **should**, **won't (this release)**.
3. For each "won't", state the reason (effort, product boundary, dependency, risk).
4. Identify which existing requirement ids are extended versus new.
5. If the request crosses a boundary (web UI, HTTP API, new datastore, multi-tenant),
   stop and ask for an explicit decision instead of designing around it.

## Constraints
- The default answer to new infrastructure is no.
- No silent expansion: anything not in "must" must be listed as a non-goal.
- Keep the smallest scope that delivers the outcome.

## Output
`Must / Should / Won't` table with reasons, plus a **Boundary check** section.

## Verification
- The "must" list can be implemented without new dependencies (or the exception is
  named and justified).
- Every "won't" has a reason, not just an omission.
