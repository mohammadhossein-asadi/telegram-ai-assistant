from __future__ import annotations

from sqlalchemy import select

from database.models import Prompt


class PromptRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def list_for_user(
        self, user_id: int, category: str | None = None
    ) -> list[Prompt]:
        async with self.db.session() as session:
            stmt = select(Prompt).where(Prompt.user_id == user_id)
            if category:
                stmt = stmt.where(Prompt.category == category)
            stmt = stmt.order_by(Prompt.updated_at.desc())
            return list(await session.scalars(stmt))

    async def get(self, prompt_id: int, user_id: int) -> Prompt | None:
        async with self.db.session() as session:
            prompt = await session.get(Prompt, prompt_id)
            if prompt and prompt.user_id == user_id:
                return prompt
            return None

    async def create(
        self, user_id: int, title: str, body: str, category: str = "general"
    ) -> Prompt:
        async with self.db.session() as session:
            prompt = Prompt(
                user_id=user_id,
                title=title[:100],
                body=body,
                category=(category or "general")[:50],
            )
            session.add(prompt)
            await session.commit()
            await session.refresh(prompt)
            return prompt

    async def update_body(self, prompt_id: int, user_id: int, body: str) -> bool:
        async with self.db.session() as session:
            prompt = await session.get(Prompt, prompt_id)
            if not prompt or prompt.user_id != user_id:
                return False
            prompt.body = body
            await session.commit()
            return True

    async def delete(self, prompt_id: int, user_id: int) -> bool:
        async with self.db.session() as session:
            prompt = await session.get(Prompt, prompt_id)
            if not prompt or prompt.user_id != user_id:
                return False
            await session.delete(prompt)
            await session.commit()
            return True

    async def categories(self, user_id: int) -> list[str]:
        async with self.db.session() as session:
            rows = await session.scalars(
                select(Prompt.category).where(Prompt.user_id == user_id).distinct()
            )
            return sorted({row for row in rows if row})
