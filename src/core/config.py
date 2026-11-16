from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

SUPPORTED_LANGUAGES = ("fa", "en")


class Settings(BaseSettings):
    """Application configuration loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Telegram
    bot_token: str = ""
    default_language: str = "fa"

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/bot.db"

    # Admins
    admin_ids: str = ""

    # AI
    ai_provider: str = "openai"
    ai_model: str = "gpt-4o-mini"
    ai_api_key: str = ""
    ai_base_url: str = "https://api.openai.com/v1"

    # Limits
    max_context_messages: int = Field(default=20, ge=2, le=200)
    user_rate_limit: int = Field(default=20, ge=1, le=10_000)
    max_daily_requests: int = Field(default=200, ge=1, le=1_000_000)

    # Product identity
    bot_name_fa: str = "دستیار هوشمند"
    bot_name_en: str = "AI Assistant"

    # GitHub integration
    github_username: str = "mohammadhossein-asadi"
    github_token: str = ""
    github_cache_ttl: int = Field(default=900, ge=60, le=86_400)

    # Developer branding
    developer_name: str = "Mohammadhossein Asadi"
    developer_github: str = "https://github.com/mohammadhossein-asadi"
    developer_role: str = "Frontend Developer"
    bot_branding_enabled: bool = True
    auto_routing_default: bool = False

    # Misc
    log_level: str = "INFO"
    bot_version: str = "1.0.0"

    @property
    def admin_id_list(self) -> list[int]:
        ids: list[int] = []
        for raw in self.admin_ids.replace(";", ",").split(","):
            raw = raw.strip()
            if raw.lstrip("-").isdigit():
                ids.append(int(raw))
        return ids

    def is_admin(self, telegram_id: int) -> bool:
        return telegram_id in self.admin_id_list

    def validate_runtime(self) -> list[str]:
        """Return human readable configuration problems (empty list == OK)."""
        problems: list[str] = []
        if not self.bot_token or self.bot_token.upper() == "TOKEN":
            problems.append("BOT_TOKEN is missing or still a placeholder.")
        if self.default_language not in SUPPORTED_LANGUAGES:
            problems.append(
                f"DEFAULT_LANGUAGE must be one of {SUPPORTED_LANGUAGES}, got {self.default_language!r}."
            )
        if not self.ai_api_key:
            problems.append(
                "AI_API_KEY is empty — the bot will start, but AI features will "
                "return a configuration error until a key is provided."
            )
        if not self.ai_base_url.startswith("http"):
            problems.append("AI_BASE_URL must be an http(s) URL.")
        if self.github_token and not self.github_username:
            problems.append("GITHUB_TOKEN is set but GITHUB_USERNAME is empty.")
        return problems


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()