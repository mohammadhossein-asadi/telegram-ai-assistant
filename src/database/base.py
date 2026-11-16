from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from core.logging import get_logger

log = get_logger(__name__)


class Base(DeclarativeBase):
    pass


class Database:
    """Thin async SQLAlchemy wrapper owning the engine and session factory."""

    def __init__(self, url: str) -> None:
        self.url = url
        self._ensure_sqlite_dir(url)
        self.engine = create_async_engine(url, echo=False, future=True)
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    @staticmethod
    def _ensure_sqlite_dir(url: str) -> None:
        if not url.startswith("sqlite"):
            return
        _, _, path = url.partition("///")
        if path and path != ":memory:":
            Path(path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

    async def create_all(self) -> None:
        from database import models

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("Database schema ready")

    def session(self) -> AsyncSession:
        return self.session_factory()

    async def dispose(self) -> None:
        await self.engine.dispose()