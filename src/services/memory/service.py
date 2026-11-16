from __future__ import annotations

from database.models import UserMemory
from database.repositories import MemoryRepository


class MemoryService:
    """Thin facade over persistent per-user memory."""

    def __init__(self, repo: MemoryRepository) -> None:
        self.repo = repo

    async def remember(self, user_id: int, key: str, value: str) -> None:
        await self.repo.upsert(user_id, key, value)

    async def list(self, user_id: int) -> list[UserMemory]:
        return await self.repo.list_for_user(user_id)

    async def count(self, user_id: int) -> int:
        return await self.repo.count(user_id)

    async def clear(self, user_id: int) -> None:
        await self.repo.clear(user_id)
