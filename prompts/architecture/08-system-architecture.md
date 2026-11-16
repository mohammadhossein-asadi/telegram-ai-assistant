# 08 — System architecture

**Phase:** architecture · **Use when:** a change alters module boundaries, data flow, or external integrations.

## Role
Architect for a layered modular monolith (ADR-001).

## Inputs
- `docs/architecture/system-architecture.md`
- `docs/architecture/repository-structure.md`
- `src/bot/main.py::bootstrap`, `src/core/container.py`

## Task
1. Describe the current flow for the affected path (update → middleware → handler →
   service → repository → model → external).
2. Identify where the new behaviour belongs and why the other layers are wrong.
3. List the modules touched and the dependency direction between them.
4. Produce a Mermaid diagram for the changed flow (sequenceDiagram or flowchart).
5. Record the trade-off: what gets harder as a result of this placement.
6. If the change requires a new layer or service, stop and write an ADR instead.

## Constraints
- `services/` and `database/` never import `aiogram`.
- No SQL in handlers.
- One composition point (`bootstrap()`); do not scatter construction.
- Prefer extending an existing service over creating a new module.

## Output
Flow description + Mermaid diagram + file list + trade-off + ADR-needed verdict.

## Verification
- Mermaid renders (balanced subgraph/end, valid arrows).
- The described flow matches symbols that exist in `src/`.
