from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    DuplicateEdgeError,
    NodeNotFoundError,
)
from app.models.network import Edge
from app.repositories.edge_repository import EdgeRepository
from app.repositories.node_repository import NodeRepository
from app.schemas.network import EdgeCreate


class EdgeService:
    def __init__(self, db: AsyncSession):
        self.repo = EdgeRepository(db)
        self.node_repo = NodeRepository(db)

    async def create_edge(self, payload: EdgeCreate) -> Edge:
        # Both nodes must exist before we can connect them
        source_node = await self.node_repo.get_by_name(payload.source)
        if not source_node:
            raise NodeNotFoundError(payload.source)

        dest_node = await self.node_repo.get_by_name(payload.destination)
        if not dest_node:
            raise NodeNotFoundError(payload.destination)

        # Prevent duplicate edges in the same direction
        duplicate = await self.repo.get_duplicate(payload.source, payload.destination)
        if duplicate:
            raise DuplicateEdgeError(payload.source, payload.destination)

        return await self.repo.create(payload.source, payload.destination, payload.latency)

    async def list_edges(self) -> list[Edge]:
        return await self.repo.get_all()

    async def delete_edge(self, edge_id: int) -> None:
        edge = await self.repo.get_by_id(edge_id)
        if not edge:
            raise NodeNotFoundError(str(edge_id))
        await self.repo.delete(edge)
