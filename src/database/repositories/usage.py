from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from database.models import UsageLog


class UsageRepository:
    def __init__(self, db, max_daily_requests: int = 200, rate_limit: int = 20) -> None:
        self.db = db
        self.max_daily_requests = max_daily_requests
        self.rate_limit = rate_limit
        self._recent: dict[int, deque[float]] = {}

    async def log(
        self,
        user_id: int | None,
        *,
        action: str = "chat",
        provider: str | None = None,
        model: str | None = None,
        success: bool = True,
        error: str | None = None,
        latency_ms: int | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> None:
        async with self.db.session() as session:
            session.add(
                UsageLog(
                    user_id=user_id,
                    action=action,
                    provider=provider,
                    model=model,
                    success=success,
                    error=(error or "")[:2000] or None,
                    latency_ms=latency_ms,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                )
            )
            await session.commit()

    async def count_today(self, user_id: int) -> int:
        start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        async with self.db.session() as session:
            return int(
                await session.scalar(
                    select(func.count(UsageLog.id)).where(
                        UsageLog.user_id == user_id, UsageLog.created_at >= start
                    )
                )
                or 0
            )

    async def count_total(self) -> int:
        async with self.db.session() as session:
            return int(await session.scalar(select(func.count(UsageLog.id))) or 0)

    async def token_totals(self) -> tuple[int, int]:
        async with self.db.session() as session:
            row = (
                await session.execute(
                    select(
                        func.coalesce(func.sum(UsageLog.prompt_tokens), 0),
                        func.coalesce(func.sum(UsageLog.completion_tokens), 0),
                    )
                )
            ).one()
            return int(row[0] or 0), int(row[1] or 0)

    def check_rate(self, user_id: int, now: float | None = None) -> bool:
        """Sliding 60-second window; returns True when the user is within limit."""
        import time

        now = now if now is not None else time.monotonic()
        bucket = self._recent.setdefault(user_id, deque())
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= self.rate_limit:
            return False
        bucket.append(now)
        return True

    async def daily_allowed(self, user_id: int) -> bool:
        if self.max_daily_requests <= 0:
            return True
        return await self.count_today(user_id) < self.max_daily_requests
