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
    id: str
    name: str
    type: str
    subtype: str
    room_id: str
    zone_id: str = "default"
    node_id: str = "node-gpio-1"
    protocol: str = "gpio"
    address: str = ""
    capabilities: list[str] = field(default_factory=list)
    default_state: str = "idle"
    fail_state: str = "safe"
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    simulated_properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineCue:
    id: str
    track: str
    start_time: int
    duration: int
    trigger_mode: str
    target: str
    action: str
    parameters: dict[str, Any] = field(default_factory=dict)
    preconditions: list[str] = field(default_factory=list)
    follow_actions: list[str] = field(default_factory=list)


@dataclass
class EscapeProject:
    project_id: str
    name: str
    description: str = ""
    author: str = ""
    version: str = "0.3.0"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    startup_scene: str = "room-1"
    default_timeline: str = "main"
    layouts: list[RoomLayout] = field(default_factory=lambda: [RoomLayout(room_id="room-1", room_name="Room 1")])
    devices: list[Device] = field(default_factory=list)
    puzzle_nodes: list[GraphNode] = field(default_factory=list)
    puzzle_edges: list[GraphEdge] = field(default_factory=list)
    logic_nodes: list[GraphNode] = field(default_factory=list)
    logic_edges: list[GraphEdge] = field(default_factory=list)
    states: list[dict[str, Any]] = field(default_factory=lambda: [{"key": "game_mode", "default": "idle", "persist": True}])
    timeline: list[TimelineCue] = field(default_factory=list)
    media: list[dict[str, Any]] = field(default_factory=list)
    operator_controls: list[dict[str, Any]] = field(default_factory=list)
    runtime_config: dict[str, Any] = field(default_factory=dict)
    settings: dict[str, Any] = field(
        default_factory=lambda: {
            "theme": "dark",
            "autosave_interval_s": 120,
            "default_project_path": "",
            "default_export_path": "",
            "timeline_snap_ms": 100,
            "default_room_scale": 0.01,
            "simulation_delay_ms": 50,
            "log_verbosity": "info",
            "validation_strictness": "normal",
            "runtime_pack_format_version": "1.0.0",
            "default_node_name_pattern": "node-{type}-{n}",
            "default_device_name_pattern": "{type}-{n}",
        }
    )
    recent_exports: list[dict[str, Any]] = field(default_factory=list)
    activity_log: list[str] = field(default_factory=list)
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

        devices = [Device(**d) if not isinstance(d, Device) else d for d in payload.get("devices", [])]
        timeline = [TimelineCue(**c) if not isinstance(c, TimelineCue) else c for c in payload.get("timeline", [])]

        return cls(
            project_id=payload.get("project_id", "project-001"),
            name=payload.get("name", "Untitled Project"),
            description=payload.get("description", ""),
            author=payload.get("author", ""),
            version=payload.get("version", "0.3.0"),
            created_at=payload.get("created_at", datetime.utcnow().isoformat()),
            updated_at=payload.get("updated_at", datetime.utcnow().isoformat()),
            startup_scene=payload.get("startup_scene", "room-1"),
            default_timeline=payload.get("default_timeline", "main"),
            layouts=layouts or [RoomLayout(room_id="room-1", room_name="Room 1")],
            devices=devices,
            puzzle_nodes=[GraphNode(**item) for item in payload.get("puzzle_nodes", [])],
            puzzle_edges=[GraphEdge(**item) for item in payload.get("puzzle_edges", [])],
            logic_nodes=[GraphNode(**item) for item in payload.get("logic_nodes", [])],
            logic_edges=[GraphEdge(**item) for item in payload.get("logic_edges", [])],
            states=payload.get("states", [{"key": "game_mode", "default": "idle", "persist": True}]),
            timeline=timeline,
            media=payload.get("media", []),
            operator_controls=payload.get("operator_controls", []),
            runtime_config=payload.get("runtime_config", {}),
            settings=payload.get("settings", {}),
            recent_exports=payload.get("recent_exports", []),
            activity_log=payload.get("activity_log", []),
            notes=payload.get("notes", ""),
        )
