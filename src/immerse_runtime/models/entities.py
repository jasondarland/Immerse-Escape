from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RuntimeStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    RESET_NEEDED = "reset_needed"
    FAULT = "fault"
    EMERGENCY = "emergency"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PackageManifest:
    name: str
    version: str
    project: dict[str, Any]
    devices: list[dict[str, Any]]
    patch: list[dict[str, Any]]
    logic_graph: dict[str, Any]
    states: dict[str, Any]
    timeline: dict[str, Any]
    media_index: dict[str, Any]
    operator_controls: dict[str, Any]
    runtime_config: dict[str, Any]


@dataclass
class Device:
    id: str
    name: str
    type: str
    room: str
    node: str
    status: str = "online"
    current_state: str = "idle"
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    fault: str = ""


@dataclass
class Node:
    id: str
    name: str
    type: str
    transport: str
    status: str = "online"
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RuntimeEvent:
    timestamp: datetime
    severity: Severity
    room: str
    source: str
    event_type: str
    message: str


@dataclass
class OutputAction:
    target: str
    room: str
    action: str
    started_at: datetime
    expected_duration: float
    state: str


@dataclass
class Alert:
    id: str
    severity: Severity
    source: str
    message: str
    active: bool = True
    acknowledged: bool = False
    resolution_notes: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Session:
    id: str
    room: str
    preset: str
    state: str
    started_at: datetime | None = None
    elapsed_seconds: int = 0
    active_puzzles: int = 0
    solved_puzzles: int = 0
    notes: str = ""
