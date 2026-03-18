from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ValidationMessage:
    severity: str
    message: str


@dataclass(slots=True)
class Device:
    device_id: str
    name: str
    node_type: str
    room: str
    kind: str
    state: str = "idle"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Puzzle:
    puzzle_id: str
    name: str
    room: str
    puzzle_type: str
    solved: bool = False
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Cue:
    cue_id: str
    name: str
    track: str
    trigger_mode: str
    target_device: str
    action: str
    duration: float = 0.0
    state: str = "pending"


@dataclass(slots=True)
class ShowPackage:
    name: str
    version: str
    root_path: Path
    manifest: dict[str, Any]
    rooms: list[dict[str, Any]]
    devices: list[Device]
    puzzles: list[Puzzle]
    states: dict[str, Any]
    timeline: list[Cue]
    operator_controls: dict[str, Any]
    runtime_config: dict[str, Any]
    validation_messages: list[ValidationMessage] = field(default_factory=list)
