from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator


class NodeCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Node name cannot be blank")
        if len(v) > 100:
            raise ValueError("Node name cannot exceed 100 characters")
        if not all(c.isalnum() or c in (" ", "-", "_") for c in v):
            raise ValueError("Node name can only contain letters, numbers, spaces, hyphens, and underscores")
        return v


class NodeResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class EdgeCreate(BaseModel):
    source: str
    destination: str
    latency: float

    @field_validator("source", "destination")
    @classmethod
    def validate_node_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Node name cannot be blank")
        if len(v) > 100:
            raise ValueError("Node name cannot exceed 100 characters")
        return v

    @field_validator("latency")
    @classmethod
    def validate_latency(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Latency must be greater than 0")
        if v > 100_000:
            raise ValueError("Latency cannot exceed 100,000 ms")
        return round(v, 4)

    @model_validator(mode="after")
    def source_and_destination_must_differ(self) -> "EdgeCreate":
        if self.source.strip().lower() == self.destination.strip().lower():
            raise ValueError("Source and destination cannot be the same node")
        return self


class EdgeResponse(BaseModel):
    id: int
    source: str
    destination: str
    latency: float

    model_config = {"from_attributes": True}


class RouteRequest(BaseModel):
    source: str
    destination: str

    @field_validator("source", "destination")
    @classmethod
    def validate_node_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Node name cannot be blank")
        if len(v) > 100:
            raise ValueError("Node name cannot exceed 100 characters")
        return v

    @model_validator(mode="after")
    def source_and_destination_must_differ(self) -> "RouteRequest":
        if self.source.strip().lower() == self.destination.strip().lower():
            raise ValueError("Source and destination cannot be the same node")
        return self


class RouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class RouteHistoryResponse(BaseModel):
    id: int
    source: str
    destination: str
    total_latency: float
    path: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
