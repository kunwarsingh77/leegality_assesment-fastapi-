from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.network import Node


class NodeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(self, name: str) -> Node | None:
        result = await self.db.execute(select(Node).where(Node.name == name))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Node]:
        result = await self.db.execute(select(Node))
        return list(result.scalars().all())

    async def create(self, name: str) -> Node:
        node = Node(name=name)
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        return node

    async def delete(self, node: Node) -> None:
        await self.db.delete(node)
        await self.db.commit()

    async def get_by_id(self, node_id: int) -> Node | None:
        result = await self.db.execute(select(Node).where(Node.id == node_id))
        return result.scalar_one_or_none()
