# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project
uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Full engineering documentation package: product, research, architecture (with 8
  ADRs), database, bot-interface contract, security, design, testing, DevOps, project
  status; machine-readable artifacts (`schema.sql`, `seed.sql`,
  `telegram-interface.json`); prompts, skills, templates and manifest with
  requirements traceability.
- Agent instruction layer: `AGENTS.md` plus adapters (`CLAUDE.md`, `GEMINI.md`,
  `.cursor/rules/`, `.github/copilot-instructions.md`).
- Repository community files: `LICENSE` (MIT), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`, `.editorconfig`.
- CI and security workflows (`.github/workflows/ci.yml`, `security.yml`) and issue /
  PR templates. **Not yet executed in this repository.**

### Fixed
- Removed a duplicated `@router.callback_query` decorator in
  `src/bot/handlers/conversations.py` (the `conv:unarch:` handler was registered
  twice).

### Documented
- Known inaccuracies in `README.md` (Alembic migrations, pydantic-settings container)
  are corrected by the documentation set; `README.md` itself is unchanged.

## [1.0.0]

Initial public state of the bot as it exists on `main`:

### Features
- Telegram chat with per-conversation context (bounded by `MAX_CONTEXT_MESSAGES`).
- Conversation management: list, create, rename, pin, archive, search, summary,
  export, delete.
- Personalities (10), styles (6), tones (5), creativity levels, custom instructions.
- Custom personas: create, import, edit, assign, export, delete.
- Long-term memory (key/value, capped injection) with on/off toggle.
- Model selection, provider registry, capability-based auto-routing.
- Tools: summarize, translate, write, explain, coding, custom prompt.
- Prompt Studio: saved prompts with categories, run/edit/delete/export.
- Settings: language, reply language, emoji, memory, auto-routing, privacy, reset.
- Developer profile screen backed by GitHub REST with TTL cache.
- Admin: stats, limits, provider health, add/delete providers, broadcast,
  block/unblock.
- Persian and English localization with parity test.
- SQLite persistence with an additive migration runner (`schema_version = 2`).
- Docker and Compose deployment.

### Known issues
- Failed AI calls leave no stored user turn (by design, documented in `HANDOFF.md`).
- In-memory FSM and rate buckets reset on restart.
- Provider keys added at runtime are stored in plaintext.
- No account deletion; no encryption at rest.
- No lint/type-check gate; no handler-level tests.

[Unreleased]: https://github.com/mohammadhossein-asadi/telegram-ai-assistant/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mohammadhossein-asadi/telegram-ai-assistant/releases/tag/v1.0.0
