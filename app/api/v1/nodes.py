from fastapi import APIRouter, Depends, Request, status
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.db.session import get_db
from app.schemas.network import NodeCreate, NodeResponse
from app.services.node_service import NodeService

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.post("", response_model=NodeResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def add_node(request: Request, payload: NodeCreate, db: AsyncSession = Depends(get_db)):
    service = NodeService(db)
    node = await service.create_node(payload)

    # Bust the node list cache so the next GET reflects the new node
    await FastAPICache.clear(namespace="nodes")

    return node


@router.get("", response_model=list[NodeResponse])
@limiter.limit("60/minute")
@cache(expire=60, namespace="nodes")  # cache for 60 seconds
async def list_nodes(request: Request, db: AsyncSession = Depends(get_db)):
    service = NodeService(db)
    return await service.list_nodes()


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_node(request: Request, node_id: int, db: AsyncSession = Depends(get_db)):
    service = NodeService(db)
    await service.delete_node(node_id)

    # Bust both node and edge caches — deleting a node affects edges too
    await FastAPICache.clear(namespace="nodes")
    await FastAPICache.clear(namespace="edges")
