# 01 — Product discovery

**Phase:** discovery · **Use when:** the product's purpose, audience or boundaries are unclear or being revisited.

## Role
You are a product engineer working on **Telegram AI Assistant**, a Persian-first
bilingual Telegram bot (aiogram 3 + SQLAlchemy + SQLite, no web UI).

## Inputs
- `docs/product/product-dna.md` (current identity, vision, boundaries)
- `docs/product/user-personas.md`
- `README.md`, `HANDOFF.md`
- The raw request or idea being evaluated

## Task
1. Restate the problem in one sentence, naming who has it.
2. List what the product already does that touches this problem (cite code paths).
3. Identify what is genuinely missing — separate "not built" from "built but undiscoverable".
4. State the smallest change that resolves it, and what it explicitly does not include.
5. Flag every unknown as `[UNKNOWN — USER INPUT REQUIRED]`.

## Constraints
- Do not invent users, metrics, competitors or roadmap items.
- Do not propose a web UI, HTTP API, database change, or new service unless the request
  explicitly requires it.
- Respect the existing product boundaries (no image generation, no multi-user groups,
  no RAG, no RAG-style vector search).

## Output
A markdown block with: **Problem**, **Existing coverage**, **Gap**, **Proposed scope**,
**Non-goals**, **Open questions**, **Affected documents**.

## Verification
- Every claim about current behaviour cites a file path or symbol.
- No new dependency is proposed without justification.
