# Environment Reference (generated from `Settings`)

Source: `src/core/config.py`. Prefix-free, case-insensitive. `.env` in the working
directory is loaded automatically. `get_settings()` is cached per process.

```dotenv
# ---- Telegram -------------------------------------------------------------
# Required. Missing or "TOKEN" => SystemExit at boot.
BOT_TOKEN=
# fa | en  (validated)
DEFAULT_LANGUAGE=fa

# ---- Database -------------------------------------------------------------
# Any SQLAlchemy async URL. SQLite path's parent directory is created on boot.
DATABASE_URL=sqlite+aiosqlite:///./data/bot.db

# ---- Admins ---------------------------------------------------------------
# Comma or semicolon separated Telegram numeric ids. Invalid tokens ignored.
ADMIN_IDS=

# ---- AI provider (OpenAI-compatible) --------------------------------------
AI_PROVIDER=openai
AI_MODEL=gpt-4o-mini
# Empty => bot starts, AI calls return a configuration error.
AI_API_KEY=
# Must start with http. "/chat/completions" is appended.
AI_BASE_URL=https://api.openai.com/v1
# Initial value of the per-user auto-routing flag.
AUTO_ROUTING_DEFAULT=false

# ---- Limits ---------------------------------------------------------------
MAX_CONTEXT_MESSAGES=20      # 2..200
USER_RATE_LIMIT=20           # 1..10000  per user per minute
MAX_DAILY_REQUESTS=200       # 1..1000000 per user per day (attempts, incl. failures)

# ---- Product identity -----------------------------------------------------
BOT_NAME_FA=دستیار هوشمند
BOT_NAME_EN=AI Assistant
BOT_VERSION=1.0.0
BOT_BRANDING_ENABLED=true

# ---- Developer branding ---------------------------------------------------
DEVELOPER_NAME=Mohammadhossein Asadi
DEVELOPER_GITHUB=https://github.com/mohammadhossein-asadi
DEVELOPER_ROLE=Frontend Developer

# ---- GitHub integration ---------------------------------------------------
GITHUB_USERNAME=mohammadhossein-asadi
# Optional: raises the unauthenticated rate limit. Read-only public data.
GITHUB_TOKEN=
GITHUB_CACHE_TTL=900         # 60..86400 seconds

# ---- Observability --------------------------------------------------------
LOG_LEVEL=INFO               # DEBUG | INFO | WARNING | ERROR
```

## Precedence

```
process environment > .env file > declared defaults
```

## Validation matrix

| Field | Rule | On violation |
| --- | --- | --- |
| `bot_token` | non-empty, not `TOKEN` | fatal (`SystemExit`) |
| `default_language` | in `("fa","en")` | warning; lookup falls back |
| `ai_api_key` | non-empty | warning; AI calls fail at runtime |
| `ai_base_url` | starts with `http` | warning |
| `max_context_messages` | 2–200 | **fatal** (`ValidationError`) |
| `user_rate_limit` | 1–10 000 | **fatal** |
| `max_daily_requests` | 1–1 000 000 | **fatal** |
| `github_cache_ttl` | 60–86 400 | **fatal** |
| `github_token` without `github_username` | — | warning |

## Notes

- Booleans accept `true/false`, `1/0`, `yes/no` (pydantic parsing).
- Unknown variables are ignored (`extra="ignore"`).
- No variable is read via `os.environ` anywhere in `src/`.
