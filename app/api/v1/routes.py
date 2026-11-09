from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi_cache.decorator import cache
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.db.session import get_db
from app.schemas.network import RouteHistoryResponse, RouteRequest, RouteResponse
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post("/shortest", response_model=RouteResponse)
@limiter.limit("10/minute")
async def get_shortest_route(request: Request, payload: RouteRequest, db: AsyncSession = Depends(get_db)):
    service = RouteService(db)
    return await service.find_shortest_route(payload)


@router.get("/history", response_model=list[RouteHistoryResponse])
@limiter.limit("60/minute")
@cache(expire=30, namespace="history")
async def get_route_history(
    request: Request,
    source: Optional[str] = Query(None, min_length=1, max_length=100, description="Filter by source node"),
    destination: Optional[str] = Query(None, min_length=1, max_length=100, description="Filter by destination node"),
    limit: Optional[int] = Query(None, ge=1, le=500, description="Max number of records to return (max 500)"),
    date_from: Optional[datetime] = Query(None, description="Filter records from this datetime (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="Filter records up to this datetime (ISO 8601)"),
    db: AsyncSession = Depends(get_db),
):
    if date_from and date_to and date_from >= date_to:
        raise HTTPException(status_code=400, detail="date_from must be earlier than date_to")

    service = RouteService(db)
    return await service.get_history(
        source=source,
        destination=destination,
        limit=limit,
        date_from=date_from,
        date_to=date_to,
    )
