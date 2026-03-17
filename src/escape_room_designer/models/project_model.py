"""Project data models for serialization and persistence."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    image_path: str = ""
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
class RoomLayout:
    room_id: str
    room_name: str
    background_image: str = ""
    scale_m_per_px: float = 0.01
    background_locked: bool = True
    objects: list[LayoutObject] = field(default_factory=list)


@dataclass
class Device:
    runtime_id: str
    name: str
    device_type: str
    room_id: str
    node_assignment: str = ""
    address: str = ""
    io_mapping: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    state: str = "offline"


@dataclass
class TimelineCue:
    cue_id: str
    track: str
    timecode_ms: int
    action: str
    target: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class EscapeProject:
    name: str
    version: str = "0.1.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    layouts: list[RoomLayout] = field(default_factory=lambda: [RoomLayout(room_id="room-1", room_name="Room 1")])
    devices: list[Device] = field(default_factory=list)
    puzzle_nodes: list[GraphNode] = field(default_factory=list)
    puzzle_edges: list[GraphEdge] = field(default_factory=list)
    logic_nodes: list[GraphNode] = field(default_factory=list)
    logic_edges: list[GraphEdge] = field(default_factory=list)
    timeline: list[TimelineCue] = field(default_factory=list)
    media: list[dict[str, Any]] = field(default_factory=list)
    operator_controls: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {"id": "start_game", "label": "Start Game", "endpoint": "operator/start"},
            {"id": "reset", "label": "Reset", "endpoint": "operator/reset"},
            {"id": "skip_puzzle", "label": "Skip Puzzle", "endpoint": "operator/skip"},
            {"id": "hint", "label": "Hint Trigger", "endpoint": "operator/hint"},
            {"id": "emergency_unlock", "label": "Emergency Unlock", "endpoint": "operator/emergency_unlock"},
        ]
    )
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "EscapeProject":
        raw_layouts = payload.get("layouts")
        if raw_layouts is None:
            legacy_objects = [LayoutObject(**item) for item in payload.get("layout", [])]
            raw_layouts = [{"room_id": "room-1", "room_name": "Main Room", "background_image": "", "objects": legacy_objects}]

        layouts = []
        for room in raw_layouts:
            objects = [obj if isinstance(obj, LayoutObject) else LayoutObject(**obj) for obj in room.get("objects", [])]
            layouts.append(
                RoomLayout(
                    room_id=room.get("room_id", "room-1"),
                    room_name=room.get("room_name", "Room"),
                    background_image=room.get("background_image", ""),
                    scale_m_per_px=room.get("scale_m_per_px", 0.01),
                    background_locked=room.get("background_locked", True),
                    objects=objects,
                )
            )

        raw_devices = payload.get("devices", [])
        devices = [d if isinstance(d, Device) else Device(**d) for d in raw_devices]
        timeline = [c if isinstance(c, TimelineCue) else TimelineCue(**c) for c in payload.get("timeline", [])]

        return cls(
            name=payload.get("name", "Untitled Project"),
            version=payload.get("version", "0.1.0"),
            created_at=payload.get("created_at", datetime.utcnow().isoformat()),
            updated_at=payload.get("updated_at", datetime.utcnow().isoformat()),
            layouts=layouts or [RoomLayout(room_id="room-1", room_name="Room 1")],
            devices=devices,
            puzzle_nodes=[GraphNode(**item) for item in payload.get("puzzle_nodes", [])],
            puzzle_edges=[GraphEdge(**item) for item in payload.get("puzzle_edges", [])],
            logic_nodes=[GraphNode(**item) for item in payload.get("logic_nodes", [])],
            logic_edges=[GraphEdge(**item) for item in payload.get("logic_edges", [])],
            timeline=timeline,
            media=payload.get("media", []),
            operator_controls=payload.get("operator_controls", []),
            notes=payload.get("notes", ""),
        )
