from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RoomHealth(str, Enum):
    READY = "ready"
    ACTIVE = "active"
    PAUSED = "paused"
    FAULT = "fault"
    RESET_NEEDED = "reset needed"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class Puzzle:
    id: str
    name: str
    status: str = "pending"


@dataclass
class Room:
    id: str
    name: str
    health: RoomHealth = RoomHealth.READY
    game_running: bool = False
    elapsed_seconds: int = 0
    current_puzzle: str = "Not started"
    notes: str = ""
    active_issue: str = ""
    reset_checklist: list[str] = field(default_factory=list)
    puzzles: list[Puzzle] = field(default_factory=list)


@dataclass
class DeviceState:
    id: str
    name: str
    room_id: str
    kind: str
    status: str


@dataclass
class ShowElement:
    id: str
    name: str
    room_id: str
    category: str
    status: str
    requires_confirmation: bool = False
    auto_reset: bool = False
    reset_required: bool = False
    notes: str = ""
    linked_device_id: str = ""
    last_triggered: Optional[datetime] = None


@dataclass
class Event:
    at: datetime
    room_id: str
    message: str
    severity: Severity = Severity.INFO
