"""Project data models for serialization and persistence."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any


@dataclass
class LayoutObject:
    object_id: str
    object_type: str
    name: str
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0
    color: str = "#3a4a62"
    layer: str = "architecture"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphNode:
    node_id: str
    node_type: str
    label: str
    x: float
    y: float
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    source: str
    target: str
    label: str = ""


@dataclass
class EscapeProject:
    name: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    layout: list[LayoutObject] = field(default_factory=list)
    puzzle_nodes: list[GraphNode] = field(default_factory=list)
    puzzle_edges: list[GraphEdge] = field(default_factory=list)
    logic_nodes: list[GraphNode] = field(default_factory=list)
    logic_edges: list[GraphEdge] = field(default_factory=list)
    devices: list[dict[str, Any]] = field(default_factory=list)
    media: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EscapeProject":
        return cls(
            name=payload.get("name", "Untitled Project"),
            created_at=payload.get("created_at", datetime.utcnow().isoformat()),
            updated_at=payload.get("updated_at", datetime.utcnow().isoformat()),
            layout=[LayoutObject(**item) for item in payload.get("layout", [])],
            puzzle_nodes=[GraphNode(**item) for item in payload.get("puzzle_nodes", [])],
            puzzle_edges=[GraphEdge(**item) for item in payload.get("puzzle_edges", [])],
            logic_nodes=[GraphNode(**item) for item in payload.get("logic_nodes", [])],
            logic_edges=[GraphEdge(**item) for item in payload.get("logic_edges", [])],
            devices=payload.get("devices", []),
            media=payload.get("media", []),
            notes=payload.get("notes", ""),
        )
