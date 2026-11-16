# 07 — Dependency evaluation

**Phase:** research · **Use when:** someone proposes adding or replacing a package.

## Role
Maintainer protecting a six-dependency runtime.

## Inputs
- `requirements.txt`, `requirements-dev.txt`
- `docs/research/opensource-research.md`

## Task
1. Name the exact problem the dependency solves.
2. Show that the standard library or an existing dependency cannot solve it.
3. Report: licence, maintenance signal (last release, activity), install size, transitive
   dependency count, async support, Python 3.12 support.
4. Estimate integration cost (files touched, tests needed) and removal cost.
5. Give a verdict: adopt / defer / reject — with the trigger that would change it.

## Constraints
- No dependency for something under ~50 lines of local code.
- No vendor SDK when a protocol client suffices (see ADR-003).
- MIT/BSD preferred; copyleft requires an explicit licence decision.

## Output
One-page evaluation + verdict + revisit trigger.

## Verification
- Every version/licence claim has a source.
- The "could we not?" question is answered explicitly.
