from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.network import Edge


class EdgeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_duplicate(self, source: str, destination: str) -> Edge | None:
        result = await self.db.execute(
            select(Edge).where(
                and_(Edge.source == source, Edge.destination == destination)
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Edge]:
        result = await self.db.execute(select(Edge))
        return list(result.scalars().all())

    async def create(self, source: str, destination: str, latency: float) -> Edge:
        edge = Edge(source=source, destination=destination, latency=latency)
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        return edge

    async def delete(self, edge: Edge) -> None:
        await self.db.delete(edge)
        await self.db.commit()

    async def get_by_id(self, edge_id: int) -> Edge | None:
        result = await self.db.execute(select(Edge).where(Edge.id == edge_id))
        return result.scalar_one_or_none()

    async def delete_by_node_name(self, node_name: str) -> None:
        # Delete all edges where this node is either the source or destination
        # Must run before deleting the node itself to avoid FK constraint errors
        result = await self.db.execute(
            select(Edge).where(
                (Edge.source == node_name) | (Edge.destination == node_name)
            )
        )
        edges = result.scalars().all()
        for edge in edges:
            await self.db.delete(edge)
        await self.db.commit()
