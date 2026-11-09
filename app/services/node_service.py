from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateNodeError, NodeNotFoundError
from app.models.network import Node
from app.repositories.edge_repository import EdgeRepository
from app.repositories.node_repository import NodeRepository
from app.schemas.network import NodeCreate


class NodeService:
    def __init__(self, db: AsyncSession):
        self.repo = NodeRepository(db)
        self.edge_repo = EdgeRepository(db)

    async def create_node(self, payload: NodeCreate) -> Node:
        # Reject if a node with the same name already exists
        existing = await self.repo.get_by_name(payload.name)
        if existing:
            raise DuplicateNodeError(payload.name)

        return await self.repo.create(payload.name)

    async def list_nodes(self) -> list[Node]:
        return await self.repo.get_all()

    async def delete_node(self, node_id: int) -> None:
        node = await self.repo.get_by_id(node_id)
        if not node:
            raise NodeNotFoundError(str(node_id))

        # Delete all edges referencing this node first to avoid FK constraint errors
        await self.edge_repo.delete_by_node_name(node.name)

        await self.repo.delete(node)
