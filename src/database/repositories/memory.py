from __future__ import annotations

from sqlalchemy import delete, select

from database.models import UserMemory


class MemoryRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def list_for_user(self, user_id: int) -> list[UserMemory]:
        async with self.db.session() as session:
            return list(
                await session.scalars(select(UserMemory).where(UserMemory.user_id == user_id))
            )

    async def upsert(self, user_id: int, key: str, value: str) -> None:
        async with self.db.session() as session:
            existing = await session.scalar(
                select(UserMemory).where(
                    UserMemory.user_id == user_id, UserMemory.key == key
                )
            )
            if existing:
                existing.value = value
            else:
                session.add(UserMemory(user_id=user_id, key=key[:120], value=value))
            await session.commit()

    async def count(self, user_id: int) -> int:
        async with self.db.session() as session:
            rows = await session.scalars(
                select(UserMemory.id).where(UserMemory.user_id == user_id)
            )
            return len(list(rows))

    async def clear(self, user_id: int) -> None:
        async with self.db.session() as session:
            await session.execute(delete(UserMemory).where(UserMemory.user_id == user_id))
            await session.commit()
