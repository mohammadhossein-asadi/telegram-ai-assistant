# Telegram AI Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![GitHub stars](https://img.shields.io/github/stars/mohammadhossein-asadi/MhaAiAssistantBot?style=social)](https://github.com/mohammadhossein-asadi/MhaAiAssistantBot)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-2CA5E0.svg)](https://telegram.org)

## 🤖 Overview

A fully functional, production-oriented **bilingual (Persian/English) Telegram AI Assistant** with interactive menus, AI chat, personality customization, multi-conversation management, GitHub profile integration, AI text tools, and admin controls — all modular, testable, and deployable via Docker.

---

## 🌐 Bilingual Support

This project supports **both Persian (Farsi) and English** with identical key sets enforced by tests.

| Language | Flag | Direction |
|----------|------|-----------|
| **Persian** | 🇮🇷 | RTL |
| **English** | 🇬🇧 | LTR |

All UI strings are localized in `src/localization/en.json` and `src/localization/fa.json` with **zero missing keys**.

---

## ✨ Features

### Core Features

- **AI Chat** with context, typing indicator, and safe Markdown→HTML conversion
- **Multiple independent conversations** per user with titles, summaries, pin/archive/delete
- **Persona system**: 10 presets, 6 styles, 5 tones, 3 creativity levels, custom instructions
- **AI model/provider abstraction** with capabilities, health checks, and auto-routing
- **AI tools**: summarize (4), translate (auto/fa/en), coding (5 modes: explain/debug/generate/review/improve), explain (3), custom prompt
- **Prompt Studio**: create/save/edit/delete prompts with categories, export/import
- **Developer GitHub profile integration** with repo listing, pagination, and detail view
- **Admin panel**: stats (including token usage), health checks, provider management, user block/unblock, broadcast

### Quality Attributes

- **Versioned, additive migrations** with an in-repo runner (`src/database/migrations.py`): v1 creates the schema, v2 adds personas, prompts and token columns
- **Rate limiting** and **daily caps** with in-memory sliding 60s window
- **Structured logging**
- **Behavioural tests** for localization parity, routing, repositories, prompts and migrations (no handler-level tests yet)
- **All 32 tests pass** locally (`pytest -q`), offline — no network or token required

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Runtime** | Python 3.12+ |
| **Framework** | aiogram 3.x |
| **ORM** | SQLAlchemy 2.x |
| **Migrations** | In-repo additive runner (`SCHEMA_VERSION = 2`) |
| **Async** | asyncio with `asyncio_mode=auto` |
| **Localization** | Identical key sets in `en.json` and `fa.json` |
| **Config** | pydantic `BaseSettings` (env + `.env`) with a module-level `container` singleton |
| **Deployment** | Docker + Docker Compose |
| **Testing** | pytest, pytest-asyncio |

---

## 📦 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/mohammadhossein-asadi/MhaAiAssistantBot.git
cd MhaAiAssistantBot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your values:
#   BOT_TOKEN=your_telegram_bot_token
#   AI_API_KEY=your_ai_api_key
#   ADMIN_IDS=your_telegram_user_id
#   GITHUB_TOKEN=optional_github_token

# 4. Run the bot
python run.py
```

---

## 📁 Project Structure

```
MhaAiAssistantBot/
├── src/                    # Source code
│   ├── core/               # Config, logging, service container
│   ├── database/           # SQLAlchemy models, migrations, repositories
│   ├── services/           # AI, chat engine, tools, memory, GitHub
│   ├── bot/                # Handlers, keyboards, views, middlewares, ui
│   ├── localization/       # en.json and fa.json
│   └── utils/              # Text, states and time helpers
├── data/                   # SQLite database output (git-ignored)
├── tests/                   # 32 passing tests
├── docs/                    # Full engineering documentation (start at docs/index.md)
├── artifacts/               # schema.sql, seed.sql, telegram-interface.json, diagrams
├── prompts/ skills/ templates/ manifest/   # Reusable agent assets
├── AGENTS.md               # Canonical instructions for AI coding agents
├── Dockerfile              # Production Docker image
├── docker-compose.yml      # Single-service Compose setup
├── README.md               # This file
└── HANDOFF.md              # Continuation notes and current status
```

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest -q

# Run specific test files
python -m pytest tests/test_routing.py -q     # Routing classification
python -m pytest tests/test_localization.py -q  # Localization parity
python -m pytest tests/test_personas_prompts.py -q  # Persona/prompt CRUD
python -m pytest tests/test_migrations.py -q     # Migration tests
python -m pytest tests/test_text.py -q          # Text utilities
```

**Result**: `32 passed, 0 failed`

---

## 🌐 Localization

Both Persian and English locales are maintained with **identical key sets**. The test `test_localization.py` validates that both files have zero missing keys against each other.

- `src/localization/en.json` - English strings
- `src/localization/fa.json` - Persian strings (RTL-friendly)

---

## 📚 Documentation

The complete engineering documentation lives in [`docs/`](docs/index.md): product and
requirements, research, architecture with 8 ADRs, database, bot-interface contract,
security, chat-UX design, testing, DevOps and project status.

| Start here | For |
| --- | --- |
| [docs/index.md](docs/index.md) | Map of every document |
| [AGENTS.md](AGENTS.md) | Instructions for AI coding agents (canonical) |
| [HANDOFF.md](HANDOFF.md) | Current status, gaps and next steps |
| [docs/architecture/system-architecture.md](docs/architecture/system-architecture.md) | How the system is structured |
| [docs/project/project-status.md](docs/project/project-status.md) | What is done and what is verified |
| [manifest/requirements-traceability.csv](manifest/requirements-traceability.csv) | Requirement → test traceability |

Reusable assets: [`prompts/`](prompts/README.md) (23 prompts),
[`skills/`](skills/) (4 procedures), [`templates/`](templates/) (ADR and doc templates),
[`artifacts/`](artifacts/) (generated schema, seed, interface contract, diagrams).

---

## 📊 Admin Panel

Accessible via `/admin` command includes:

- **Stats**: User count, message count, token usage totals
- **Health checks**: Iterating provider.health_check()
- **Provider management**: Add/configure AI providers
- **User block/unblock**: Manage user access
- **Broadcast**: Send messages to all users with rate limiting

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Handoff

For continuing development, see [HANDOFF.md](HANDOFF.md) - the source of truth for project continuation.

---

## 📞 Contact

**Developer**: Mohammadhossein Asadi  
**GitHub**: [@mohammadhossein-asadi](https://github.com/mohammadhossein-asadi)  
**Project**: [MhaAiAssistantBot](https://github.com/mohammadhossein-asadi/MhaAiAssistantBot)