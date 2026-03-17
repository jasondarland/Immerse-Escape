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
    version: str = "0.2.0"
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
    operator_controls: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {"control_id": "start_game", "label": "Start Game", "action_type": "runtime_command", "target": "show", "confirmation_required": False, "permission_level": "operator", "runtime_effect": "start"},
            {"control_id": "pause_game", "label": "Pause Game", "action_type": "runtime_command", "target": "show", "confirmation_required": False, "permission_level": "operator", "runtime_effect": "pause"},
            {"control_id": "reset_game", "label": "Reset Game", "action_type": "runtime_command", "target": "show", "confirmation_required": True, "permission_level": "lead", "runtime_effect": "reset"},
            {"control_id": "skip_puzzle", "label": "Skip Puzzle", "action_type": "logic_override", "target": "puzzle", "confirmation_required": False, "permission_level": "operator", "runtime_effect": "force_complete"},
            {"control_id": "trigger_hint", "label": "Trigger Hint", "action_type": "logic_override", "target": "hint", "confirmation_required": False, "permission_level": "operator", "runtime_effect": "hint"},
            {"control_id": "emergency_unlock", "label": "Emergency Unlock", "action_type": "safety", "target": "doors", "confirmation_required": True, "permission_level": "lead", "runtime_effect": "unlock_all"},
            {"control_id": "trigger_finale", "label": "Trigger Finale", "action_type": "timeline_trigger", "target": "timeline/finale", "confirmation_required": False, "permission_level": "operator", "runtime_effect": "play"},
            {"control_id": "stop_all_media", "label": "Stop All Media", "action_type": "media", "target": "all", "confirmation_required": False, "permission_level": "operator", "runtime_effect": "stop"},
            {"control_id": "restore_defaults", "label": "Restore Defaults", "action_type": "runtime_command", "target": "system", "confirmation_required": True, "permission_level": "lead", "runtime_effect": "restore_defaults"},
        ]
    )
    runtime_config: dict[str, Any] = field(
        default_factory=lambda: {
            "startup_logic": "event_graph_boot",
            "watchdog_enabled": True,
            "watchdog_timeout_ms": 3000,
            "heartbeat_interval_ms": 250,
            "logging_verbosity": "info",
            "fail_safe_behavior": "unlock_safe_devices",
            "boot_scene": "room-1",
            "reset_behavior": "soft_reset",
            "simulation_defaults": {"enabled": True},
            "network_discovery": {"enabled": True, "method": "mdns"},
        }
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

        devices: list[Device] = []
        for d in payload.get("devices", []):
            if isinstance(d, Device):
                devices.append(d)
            else:
                devices.append(
                    Device(
                        id=d.get("id", d.get("runtime_id", "dev-unknown")),
                        name=d.get("name", "Device"),
                        type=d.get("type", d.get("device_type", "button")),
                        subtype=d.get("subtype", "generic"),
                        room_id=d.get("room_id", "room-1"),
                        zone_id=d.get("zone_id", d.get("zone", "default")),
                        node_id=d.get("node_id", d.get("node_assignment", "node-gpio-1")),
                        protocol=d.get("protocol", "gpio"),
                        address=d.get("address", ""),
                        capabilities=d.get("capabilities", []),
                        default_state=d.get("default_state", "idle"),
                        fail_state=d.get("fail_state", "safe"),
                        tags=d.get("tags", []),
                        notes=d.get("notes", ""),
                        simulated_properties=d.get("simulated_properties", {}),
                    )
                )

        timeline: list[TimelineCue] = []
        for c in payload.get("timeline", []):
            if isinstance(c, TimelineCue):
                timeline.append(c)
            else:
                timeline.append(
                    TimelineCue(
                        id=c.get("id", c.get("cue_id", "cue-1")),
                        track=c.get("track", "automation"),
                        start_time=c.get("start_time", c.get("timecode_ms", 0)),
                        duration=c.get("duration", 0),
                        trigger_mode=c.get("trigger_mode", "absolute_time"),
                        target=c.get("target", ""),
                        action=c.get("action", "noop"),
                        parameters=c.get("parameters", c.get("payload", {})),
                        preconditions=c.get("preconditions", []),
                        follow_actions=c.get("follow_actions", []),
                    )
                )

        return cls(
            project_id=payload.get("project_id", "project-001"),
            name=payload.get("name", "Untitled Project"),
            version=payload.get("version", "0.2.0"),
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
            notes=payload.get("notes", ""),
        )
