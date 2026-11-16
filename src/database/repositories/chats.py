from __future__ import annotations

from sqlalchemy import delete, func, select

from database.models import Conversation, Message


class ConversationRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def create(self, user_id: int, title: str = "New chat") -> Conversation:
        async with self.db.session() as session:
            conv = Conversation(user_id=user_id, title=title)
            session.add(conv)
            await session.commit()
            await session.refresh(conv)
            return conv

    async def get(self, conversation_id: int, user_id: int | None = None) -> Conversation | None:
        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if conv and user_id is not None and conv.user_id != user_id:
                return None
            return conv

    async def list_for_user(
        self, user_id: int, *, include_archived: bool = False
    ) -> list[Conversation]:
        async with self.db.session() as session:
            stmt = select(Conversation).where(Conversation.user_id == user_id)
            if not include_archived:
                stmt = stmt.where(Conversation.is_archived.is_(False))
            stmt = stmt.order_by(
                Conversation.is_pinned.desc(), Conversation.updated_at.desc()
            )
            return list(await session.scalars(stmt))

    async def search(self, user_id: int, query: str, limit: int = 10) -> list[Conversation]:
        async with self.db.session() as session:
            pattern = f"%{query.strip()}%"
            stmt = (
                select(Conversation)
                .where(
                    Conversation.user_id == user_id,
                    Conversation.title.ilike(pattern),
                )
                .order_by(Conversation.updated_at.desc())
                .limit(limit)
            )
            return list(await session.scalars(stmt))

    async def set_pinned(self, conversation_id: int, user_id: int, pinned: bool) -> bool:
        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if not conv or conv.user_id != user_id:
                return False
            conv.is_pinned = pinned
            await session.commit()
            return True

    async def set_summary(
        self, conversation_id: int, user_id: int, summary: str
    ) -> bool:
        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if not conv or conv.user_id != user_id:
                return False
            conv.summary = summary
            await session.commit()
            return True

    async def set_persona(
        self, conversation_id: int, user_id: int, persona_id: int | None
    ) -> bool:
        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if not conv or conv.user_id != user_id:
                return False
            conv.persona_id = persona_id
            await session.commit()
            return True

    async def set_model(self, conversation_id: int, user_id: int, model: str | None) -> bool:
        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if not conv or conv.user_id != user_id:
                return False
            conv.model = model
            await session.commit()
            return True

    async def rename(self, conversation_id: int, user_id: int, title: str) -> bool:
        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if not conv or conv.user_id != user_id:
                return False
            conv.title = title[:120]
            await session.commit()
            return True

    async def set_archived(self, conversation_id: int, user_id: int, archived: bool) -> bool:
        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if not conv or conv.user_id != user_id:
                return False
            conv.is_archived = archived
            await session.commit()
            return True

    async def delete(self, conversation_id: int, user_id: int) -> bool:
        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if not conv or conv.user_id != user_id:
                return False
            await session.delete(conv)
            await session.commit()
            return True

    async def count(self, user_id: int | None = None) -> int:
        async with self.db.session() as session:
            stmt = select(func.count(Conversation.id))
            if user_id is not None:
                stmt = stmt.where(Conversation.user_id == user_id)
            return int(await session.scalar(stmt) or 0)

    async def touch(self, conversation_id: int) -> None:
        from database.models import utcnow

        async with self.db.session() as session:
            conv = await session.get(Conversation, conversation_id)
            if conv:
                conv.updated_at = utcnow()
                await session.commit()


class MessageRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def add(
        self, conversation_id: int, role: str, content: str
    ) -> Message:
        async with self.db.session() as session:
            msg = Message(conversation_id=conversation_id, role=role, content=content)
            session.add(msg)
            await session.commit()
            await session.refresh(msg)
            return msg

    async def recent(self, conversation_id: int, limit: int) -> list[Message]:
        async with self.db.session() as session:
            stmt = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.id.desc())
                .limit(limit)
            )
            rows = list(await session.scalars(stmt))
            return list(reversed(rows))

    async def last_assistant(self, conversation_id: int) -> Message | None:
        async with self.db.session() as session:
            stmt = (
                select(Message)
                .where(
                    Message.conversation_id == conversation_id,
                    Message.role == "assistant",
                )
                .order_by(Message.id.desc())
                .limit(1)
            )
            return await session.scalar(stmt)

    async def clear(self, conversation_id: int) -> None:
        async with self.db.session() as session:
            await session.execute(delete(Message).where(Message.conversation_id == conversation_id))
            await session.commit()

    async def delete_last_assistant(self, conversation_id: int) -> None:
        async with self.db.session() as session:
            last = await session.scalar(
                select(Message)
                .where(Message.conversation_id == conversation_id, Message.role == "assistant")
                .order_by(Message.id.desc())
                .limit(1)
            )
            if last:
                await session.delete(last)
                await session.commit()

    async def count(self) -> int:
        async with self.db.session() as session:
            return int(await session.scalar(select(func.count(Message.id))) or 0)

    async def all_for_conversation(self, conversation_id: int) -> list[Message]:
        async with self.db.session() as session:
            stmt = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.id)
            )
            return list(await session.scalars(stmt))
