# 10 — ADR authoring

**Phase:** architecture · **Use when:** a decision is costly to reverse, crosses layers, or will be questioned later.

## Role
Decision recorder. An ADR explains **why**, not how.

## Inputs
- `templates/adr/ADR-template.md`
- Existing `docs/architecture/decisions/ADR-001..008`
- The change being decided

## Task
1. Assign the next ADR number; never renumber existing ones.
2. Write Context (forces, constraints), Problem (one question), Considered alternatives
   (at least three, including "do nothing"), Decision, Consequences (positive and
   negative), Risks with mitigations, Verification.
3. Mark status: Proposed / Accepted / Superseded.
4. Add cross-links from the documents that depend on the decision.
5. If it supersedes an ADR, update that ADR's status line — do not delete it.

## Constraints
- Alternatives must include the one the project currently uses.
- Consequences must name costs, not only benefits.
- No decision without a verification method.
- Past-tense honesty: describe what exists, not what is planned, in "Decision".

## Output
One ADR file at `docs/architecture/decisions/ADR-00N-<slug>.md` + links.

## Verification
- Every claim about current code is checkable.
- Status and date present; supersession links both ways.
