from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.network import RouteHistory


class RouteHistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        source: str,
        destination: str,
        total_latency: float,
        path: list[str],
    ) -> RouteHistory:
        record = RouteHistory(
            source=source,
            destination=destination,
            total_latency=total_latency,
            path=path,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_history(
        self,
        source: Optional[str] = None,
        destination: Optional[str] = None,
        limit: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[RouteHistory]:
        query = select(RouteHistory).order_by(RouteHistory.created_at.desc())

        # Apply filters only when provided
        if source:
            query = query.where(RouteHistory.source == source)
        if destination:
            query = query.where(RouteHistory.destination == destination)
        if date_from:
            query = query.where(RouteHistory.created_at >= date_from)
        if date_to:
            query = query.where(RouteHistory.created_at <= date_to)
        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())
