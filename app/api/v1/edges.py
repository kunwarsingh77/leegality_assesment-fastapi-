from fastapi import APIRouter, Depends, Request, status
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.db.session import get_db
from app.schemas.network import EdgeCreate, EdgeResponse
from app.services.edge_service import EdgeService

router = APIRouter(prefix="/edges", tags=["Edges"])


@router.post("", response_model=EdgeResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def add_edge(request: Request, payload: EdgeCreate, db: AsyncSession = Depends(get_db)):
    service = EdgeService(db)
    edge = await service.create_edge(payload)

    # Bust the edge list cache so the next GET reflects the new edge
    await FastAPICache.clear(namespace="edges")

    return edge


@router.get("", response_model=list[EdgeResponse])
@limiter.limit("60/minute")
@cache(expire=60, namespace="edges")  # cache for 60 seconds
async def list_edges(request: Request, db: AsyncSession = Depends(get_db)):
    service = EdgeService(db)
    return await service.list_edges()


@router.delete("/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def delete_edge(request: Request, edge_id: int, db: AsyncSession = Depends(get_db)):
    service = EdgeService(db)
    await service.delete_edge(edge_id)

    # Bust the edge cache after deletion
    await FastAPICache.clear(namespace="edges")
