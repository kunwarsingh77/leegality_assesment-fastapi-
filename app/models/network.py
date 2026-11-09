from datetime import datetime, timezone

from sqlalchemy import Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)


class Edge(Base):
    __tablename__ = "edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(255), ForeignKey("nodes.name"), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), ForeignKey("nodes.name"), nullable=False)
    latency: Mapped[float] = mapped_column(Float, nullable=False)


class RouteHistory(Base):
    __tablename__ = "route_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    total_latency: Mapped[float] = mapped_column(Float, nullable=False)
    path: Mapped[list] = mapped_column(JSON, nullable=False)  # stored as JSON array e.g. ["A", "B", "C"]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
