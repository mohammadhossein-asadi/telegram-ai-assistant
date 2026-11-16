from __future__ import annotations

from sqlalchemy import delete, select

from database.models import AIProvider


class ProviderRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def list_active(self) -> list[AIProvider]:
        async with self.db.session() as session:
            return list(
                await session.scalars(
                    select(AIProvider).where(AIProvider.is_active.is_(True)).order_by(AIProvider.id)
                )
            )

    async def add(self, name: str, base_url: str, model: str, api_key: str) -> AIProvider:
        async with self.db.session() as session:
            existing = await session.scalar(select(AIProvider).where(AIProvider.name == name))
            if existing:
                existing.base_url = base_url
                existing.model = model
                existing.api_key = api_key
                existing.is_active = True
                await session.commit()
                await session.refresh(existing)
                return existing
            provider = AIProvider(name=name, base_url=base_url, model=model, api_key=api_key)
            session.add(provider)
            await session.commit()
            await session.refresh(provider)
            return provider

    async def set_capabilities(self, provider_id: int, capabilities: str) -> bool:
        async with self.db.session() as session:
            provider = await session.get(AIProvider, provider_id)
            if not provider:
                return False
            provider.capabilities = capabilities[:255]
            await session.commit()
            return True

    async def delete(self, provider_id: int) -> bool:
        async with self.db.session() as session:
            provider = await session.get(AIProvider, provider_id)
            if not provider:
                return False
            await session.delete(provider)
            await session.commit()
            return True
