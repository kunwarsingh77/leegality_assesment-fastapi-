from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NodeNotFoundError, NoPathError
from app.repositories.edge_repository import EdgeRepository
from app.repositories.node_repository import NodeRepository
from app.repositories.route_history_repository import RouteHistoryRepository
from app.schemas.network import RouteHistoryResponse, RouteRequest, RouteResponse


class RouteService:
    def __init__(self, db: AsyncSession):
        self.node_repo = NodeRepository(db)
        self.edge_repo = EdgeRepository(db)
        self.history_repo = RouteHistoryRepository(db)

    async def _build_adjacency_map(self) -> dict[str, list[tuple[str, float]]]:
        # Builds a dict like {"ServerA": [("ServerB", 10.5), ...]} from all edges in DB
        edges = await self.edge_repo.get_all()
        adjacency: dict[str, list[tuple[str, float]]] = {}
        for edge in edges:
            if edge.source not in adjacency:
                adjacency[edge.source] = []
            adjacency[edge.source].append((edge.destination, edge.latency))
        return adjacency

    def _find_cheapest_path(
        self,
        adjacency: dict[str, list[tuple[str, float]]],
        source: str,
        destination: str,
    ) -> tuple[list[str], float] | None:
        # Tries every possible path and returns the one with the lowest total latency
        best_path: list[str] | None = None
        best_latency: float = float("inf")

        # Stack holds: (current_node, path_so_far, accumulated_latency, visited_set)
        stack = [(source, [source], 0.0, {source})]

        while stack:
            current_node, path, current_latency, visited = stack.pop()

            if current_node == destination:
                if current_latency < best_latency:
                    best_latency = current_latency
                    best_path = path
                continue

            # Prune branches that are already more expensive than the best found
            if current_latency >= best_latency:
                continue

            for neighbor, latency in adjacency.get(current_node, []):
                if neighbor not in visited:
                    stack.append((
                        neighbor,
                        path + [neighbor],
                        current_latency + latency,
                        visited | {neighbor},
                    ))

        if best_path is None:
            return None

        return best_path, round(best_latency, 4)

    async def find_shortest_route(self, payload: RouteRequest) -> RouteResponse:
        source_node = await self.node_repo.get_by_name(payload.source)
        if not source_node:
            raise NodeNotFoundError(payload.source)

        dest_node = await self.node_repo.get_by_name(payload.destination)
        if not dest_node:
            raise NodeNotFoundError(payload.destination)

        adjacency = await self._build_adjacency_map()
        result = self._find_cheapest_path(adjacency, payload.source, payload.destination)

        if result is None:
            raise NoPathError(payload.source, payload.destination)

        path, total_latency = result

        await self.history_repo.create(
            source=payload.source,
            destination=payload.destination,
            total_latency=total_latency,
            path=path,
        )

        return RouteResponse(total_latency=total_latency, path=path)

    async def get_history(
        self,
        source: Optional[str],
        destination: Optional[str],
        limit: Optional[int],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> list[RouteHistoryResponse]:
        records = await self.history_repo.get_history(
            source=source,
            destination=destination,
            limit=limit,
            date_from=date_from,
            date_to=date_to,
        )
        return [RouteHistoryResponse.model_validate(r) for r in records]
