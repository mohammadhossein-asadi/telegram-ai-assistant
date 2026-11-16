# Prompt library

Reusable, project-specific prompts for humans and AI agents working on this
repository. Each file is self-contained: role, inputs, task, constraints, output shape,
and a verification step.

## Phases

| Phase | Prompts |
| --- | --- |
| Discovery | 01 product discovery · 02 persona definition · 03 scope & non-goals · 04 success metrics |
| Research | 05 competitor analysis · 06 technical feasibility · 07 dependency evaluation |
| Architecture | 08 system architecture · 09 data model · 10 ADR authoring · 11 interface contract |
| Implementation | 12 feature · 13 migration · 14 localization · 15 bug fix |
| Testing | 16 test plan · 17 test case generation · 18 regression review |
| Review | 19 code review · 20 security review · 21 documentation review |
| Handoff | 22 release handoff · 23 agent handoff |

## How to use

1. Pick the phase that matches the task, not the job title.
2. Fill the **Inputs** section with the actual files/ids for your change.
3. Keep the **Constraints** — they encode decisions recorded in the ADRs.
4. Produce the **Output** shape so the result is reviewable.
5. Run the **Verification** step before reporting success.

## Conventions

- Prompts never grant permission to invent facts; unknown values are written as
  `[UNKNOWN — USER INPUT REQUIRED]`.
- Prompts that produce code expect `pytest -q` and `python -m compileall -q src`.
- Prompts that produce docs expect code-grounded claims and a link check.

See [`AGENTS.md`](../AGENTS.md) for the invariants these prompts assume.
