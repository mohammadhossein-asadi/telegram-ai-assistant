from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from core.logging import get_logger
from database.models import User, UserSettings

log = get_logger(__name__)


class UserRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        async with self.db.session() as session:
            return await session.scalar(select(User).where(User.telegram_id == telegram_id))

    async def get_or_create(
        self,
        telegram_id: int,
        *,
        username: str | None = None,
        first_name: str | None = None,
        language: str = "fa",
    ) -> tuple[User, bool]:
        async with self.db.session() as session:
            user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
            created = False
            if user is None:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    language=language,
                )
                session.add(user)
                await session.flush()
                session.add(UserSettings(user_id=user.id))
                created = True
            else:
                if username is not None:
                    user.username = username
                if first_name is not None:
                    user.first_name = first_name
            user.last_seen_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(user)
            user = await session.scalar(select(User).where(User.id == user.id))
            return user, created

    async def get(self, user_id: int) -> User | None:
        async with self.db.session() as session:
            return await session.get(User, user_id)

    async def update_language(self, user_id: int, language: str) -> None:
        async with self.db.session() as session:
            user = await session.get(User, user_id)
            if user:
                user.language = language
                await session.commit()

    async def set_blocked(self, user_id: int, blocked: bool) -> None:
        async with self.db.session() as session:
            user = await session.get(User, user_id)
            if user:
                user.is_blocked = blocked
                await session.commit()

    async def all_ids(self) -> list[int]:
        async with self.db.session() as session:
            rows = await session.scalars(select(User.telegram_id).where(User.is_blocked.is_(False)))
            return list(rows)

    async def count(self) -> int:
        from sqlalchemy import func

        async with self.db.session() as session:
            return int(await session.scalar(select(func.count(User.id))) or 0)

    async def count_blocked(self) -> int:
        from sqlalchemy import func

        async with self.db.session() as session:
            return int(
                await session.scalar(select(func.count(User.id)).where(User.is_blocked.is_(True)))
                or 0
            )

    async def count_active_since(self, hours: int = 24) -> int:
        from sqlalchemy import func

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        async with self.db.session() as session:
            return int(
                await session.scalar(
                    select(func.count(User.id)).where(User.last_seen_at >= cutoff)
                )
                or 0
            )


class SettingsRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def get(self, user_id: int) -> UserSettings | None:
        async with self.db.session() as session:
            return await session.scalar(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )

    async def get_or_create(self, user_id: int) -> UserSettings:
        async with self.db.session() as session:
            settings = await session.scalar(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            if settings is None:
                settings = UserSettings(user_id=user_id)
                session.add(settings)
                await session.commit()
                await session.refresh(settings)
            return settings

    async def update(self, user_id: int, **fields) -> UserSettings:
        async with self.db.session() as session:
            settings = await session.scalar(
                select(UserSettings).where(UserSettings.user_id == user_id)
            )
            if settings is None:
                settings = UserSettings(user_id=user_id)
                session.add(settings)
            for key, value in fields.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            await session.commit()
            await session.refresh(settings)
            return settings

    async def reset(self, user_id: int) -> UserSettings:
        defaults = {
            "personality": "friendly",
            "style": "balanced",
            "tone": "casual",
            "creativity": "balanced",
            "memory_enabled": True,
            "response_language": "auto",
            "emoji_enabled": True,
            "custom_instructions": None,
            "model": None,
            "provider": None,
        }
        return await self.update(user_id, **defaults)
