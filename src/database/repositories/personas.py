from __future__ import annotations

from sqlalchemy import delete, select, update

from database.models import Persona


class PersonaRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def list_for_user(self, user_id: int) -> list[Persona]:
        async with self.db.session() as session:
            return list(
                await session.scalars(
                    select(Persona)
                    .where(Persona.user_id == user_id)
                    .order_by(Persona.is_default.desc(), Persona.name)
                )
            )

    async def get(self, persona_id: int, user_id: int) -> Persona | None:
        async with self.db.session() as session:
            persona = await session.get(Persona, persona_id)
            if persona and persona.user_id == user_id:
                return persona
            return None

    async def count(self, user_id: int) -> int:
        async with self.db.session() as session:
            rows = await session.scalars(
                select(Persona.id).where(Persona.user_id == user_id)
            )
            return len(list(rows))

    async def create(
        self, user_id: int, name: str, instructions: str, emoji: str = "🎭"
    ) -> Persona:
        async with self.db.session() as session:
            existing = await session.scalar(
                select(Persona).where(
                    Persona.user_id == user_id, Persona.name == name[:80]
                )
            )
            if existing:
                existing.instructions = instructions
                existing.emoji = emoji
                await session.commit()
                await session.refresh(existing)
                return existing
            persona = Persona(
                user_id=user_id, name=name[:80], instructions=instructions, emoji=emoji
            )
            session.add(persona)
            await session.commit()
            await session.refresh(persona)
            return persona

    async def update_instructions(
        self, persona_id: int, user_id: int, instructions: str
    ) -> bool:
        async with self.db.session() as session:
            persona = await session.get(Persona, persona_id)
            if not persona or persona.user_id != user_id:
                return False
            persona.instructions = instructions
            await session.commit()
            return True

    async def set_default(self, persona_id: int, user_id: int) -> bool:
        async with self.db.session() as session:
            persona = await session.get(Persona, persona_id)
            if not persona or persona.user_id != user_id:
                return False
            await session.execute(
                update(Persona).where(Persona.user_id == user_id).values(is_default=False)
            )
            persona.is_default = True
            await session.commit()
            return True

    async def delete(self, persona_id: int, user_id: int) -> bool:
        async with self.db.session() as session:
            persona = await session.get(Persona, persona_id)
            if not persona or persona.user_id != user_id:
                return False
            await session.delete(persona)
            await session.commit()
            return True

    async def clear_default(self, user_id: int) -> None:
        async with self.db.session() as session:
            await session.execute(
                update(Persona).where(Persona.user_id == user_id).values(is_default=False)
            )
            await session.commit()
