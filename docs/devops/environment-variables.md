# Environment Variables

Authoritative source: `src/core/config.py` (`Settings`). Every variable is read from
the environment or `.env`; nothing reads `os.environ` directly.

## 1. Required to operate

| Variable | Default | Validation | Purpose |
| --- | --- | --- | --- |
| `BOT_TOKEN` | `""` | non-empty, not `TOKEN` | Telegram bot token. Missing → `SystemExit` |
| `AI_API_KEY` | `""` | non-empty (warning only) | key for the OpenAI-compatible endpoint |

The bot **starts** without `AI_API_KEY` but every AI action returns a configuration
error. That is intentional so the operator can reach the admin panel to add a provider.

## 2. Telegram and identity

| Variable | Default | Validation | Purpose |
| --- | --- | --- | --- |
| `DEFAULT_LANGUAGE` | `fa` | must be `fa` or `en` | language for new users and fallback |
| `ADMIN_IDS` | `""` | comma or semicolon separated integers; spaces tolerated | admin allow-list |
| `BOT_NAME_FA` | `دستیار هوشمند` | — | brand name in Persian |
| `BOT_NAME_EN` | `AI Assistant` | — | brand name in English |
| `BOT_VERSION` | `1.0.0` | — | shown in About |
| `BOT_BRANDING_ENABLED` | `true` | bool | show developer branding |

`ADMIN_IDS` parsing: `"1, 2 ;3"` → `[1, 2, 3]`; non-numeric tokens are ignored.

## 3. Database

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/bot.db` | SQLAlchemy async URL; the parent directory is created automatically |

Compose overrides it to the volume path. A Postgres URL is *plausible* but untested.

## 4. AI provider

| Variable | Default | Validation | Purpose |
| --- | --- | --- | --- |
| `AI_PROVIDER` | `openai` | — | provider name used in logs/usage |
| `AI_MODEL` | `gpt-4o-mini` | — | default model |
| `AI_API_KEY` | `""` | — | bearer token |
| `AI_BASE_URL` | `https://api.openai.com/v1` | must start with `http` | endpoint root; `/chat/completions` is appended |
| `AUTO_ROUTING_DEFAULT` | `false` | bool | initial value of the per-user auto-routing flag |

Any OpenAI-compatible endpoint works: OpenRouter, Together, Groq, Ollama
(`http://host:11434/v1`), LM Studio, vLLM.

## 5. Limits

| Variable | Default | Range | Purpose |
| --- | --- | --- | --- |
| `MAX_CONTEXT_MESSAGES` | `20` | 2–200 | turns sent to the model |
| `USER_RATE_LIMIT` | `20` | 1–10 000 | requests per user per minute |
| `MAX_DAILY_REQUESTS` | `200` | 1–1 000 000 | requests per user per day (attempts, including failures) |

## 6. GitHub integration

| Variable | Default | Range | Purpose |
| --- | --- | --- | --- |
| `GITHUB_USERNAME` | `mohammadhossein-asadi` | — | profile shown on the Developer screen |
| `GITHUB_TOKEN` | `""` | — | optional; raises the API rate limit |
| `GITHUB_CACHE_TTL` | `900` | 60–86 400 | seconds to cache profile/repos |

## 7. Branding

| Variable | Default |
| --- | --- |
| `DEVELOPER_NAME` | `Mohammadhossein Asadi` |
| `DEVELOPER_GITHUB` | `https://github.com/mohammadhossein-asadi` |
| `DEVELOPER_ROLE` | `Frontend Developer` |

## 8. Observability

| Variable | Default | Values | Notes |
| --- | --- | --- | --- |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `DEBUG` may print more metadata; review before production |

## 9. `.env.example` completeness

`.env.example` in the repo currently documents most but **not all** settings.

| Setting | Present in `.env.example`? |
| --- | --- |
| `BOT_TOKEN`, `DEFAULT_LANGUAGE` | ✔ |
| `DATABASE_URL`, `ADMIN_IDS` | ✔ |
| `AI_PROVIDER`, `AI_MODEL`, `AI_API_KEY`, `AI_BASE_URL` | ✔ |
| `MAX_CONTEXT_MESSAGES`, `USER_RATE_LIMIT`, `MAX_DAILY_REQUESTS` | ✔ |
| `DEVELOPER_*`, `BOT_BRANDING_ENABLED`, `LOG_LEVEL`, `BOT_VERSION` | ✔ |
| `BOT_NAME_FA`, `BOT_NAME_EN` | ✘ (defaults are used) |
| `GITHUB_USERNAME`, `GITHUB_TOKEN`, `GITHUB_CACHE_TTL` | ✘ (defaults/empty are used) |
| `AUTO_ROUTING_DEFAULT` | ✘ (defaults to `false`) |

This is a documentation gap in the repo, not a runtime bug: all settings have safe
defaults. Adding the five missing lines to `.env.example` is a one-line-each change
(not applied by this documentation package, which does not modify code).

## 10. Precedence and loading

```
real environment variables  >  .env file  >  field defaults
```

`get_settings()` is `@lru_cache(maxsize=1)`; changes require a process restart (or
`get_settings.cache_clear()` in tests). `extra="ignore"` means platform-injected
variables (e.g. `PATH`, `HOSTNAME`) do not break startup.

`validate_runtime()` reports problems at boot:

| Problem | Severity |
| --- | --- |
| `BOT_TOKEN` missing/placeholder | **fatal** — `main()` raises `SystemExit` |
| `DEFAULT_LANGUAGE` invalid | warning (logged) — falls back to `DEFAULT_LANGUAGE` at lookup time |
| `AI_API_KEY` empty | warning |
| `AI_BASE_URL` not http(s) | warning |
| `GITHUB_TOKEN` set without `GITHUB_USERNAME` | warning |

Only the token check is fatal: `validate_runtime()` returns a list and `main()` logs
each entry as `CONFIG: …` at WARNING, then checks the token explicitly.

## 11. Secrets policy

Never commit `.env`. Never paste real values into issues, PRs or documentation.
See [secrets management](../security/secrets-management.md).
