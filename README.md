# Telegram AI Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![GitHub stars](https://img.shields.io/github/stars/mohammadhossein-asadi/telegram-ai-assistant?style=social)](https://github.com/mohammadhossein-asadi/telegram-ai-assistant)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-2CA5E0.svg)](https://telegram.org)

## Overview

A fully functional, production-oriented bilingual (Persian/English) Telegram AI Assistant with interactive menus, AI chat, personality customization, multi-conversation management, GitHub profile integration, AI text tools, and admin controls.

## Bilingual Support

This project supports both Persian (Farsi) and English with identical key sets enforced by tests.

## Features

- AI Chat with context, typing indicator, and safe Markdown to HTML conversion
- Multiple independent conversations per user
- Persona system: 10 presets, 6 styles, 5 tones, 3 creativity levels
- AI tools: summarize, translate, coding (5 modes), explain, custom prompt
- Prompt Studio: create/save/edit/delete prompts with categories
- Developer GitHub profile integration
- Admin panel: stats, health checks, provider management, user block/unblock, broadcast

## Quick Start

```bash
git clone https://github.com/mohammadhossein-asadi/telegram-ai-assistant.git
cd telegram-ai-assistant
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Running Tests

```bash
python -m pytest -q
```

Result: 31 passed, 0 failed

## License

MIT License

## Contact

**Developer**: Mohammadhossein Asadi
**GitHub**: [@mohammadhossein-asadi](https://github.com/mohammadhossein-asadi)