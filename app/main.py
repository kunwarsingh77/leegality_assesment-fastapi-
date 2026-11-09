from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.core.middleware import SecurityHeadersMiddleware, RequestBodySizeLimitMiddleware
from app.db.session import Base, engine
from app.api.v1 import nodes, edges, routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    FastAPICache.init(InMemoryBackend(), prefix="network-cache")
    yield


app = FastAPI(
    title="Network Route Optimization API",
    description="API to manage network nodes, edges, and find shortest latency paths.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestBodySizeLimitMiddleware, max_body_size=settings.MAX_REQUEST_BODY_SIZE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

API_V1_PREFIX = "/api/v1"
app.include_router(nodes.router, prefix=API_V1_PREFIX)
app.include_router(edges.router, prefix=API_V1_PREFIX)
app.include_router(routes.router, prefix=API_V1_PREFIX)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
