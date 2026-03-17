from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal

from .models import DeviceState, Event, Room, RoomHealth, Severity, ShowElement
from .sample_data import build_devices, build_rooms, build_show_elements


@dataclass
class AppState:
    rooms: dict[str, Room]
    devices: dict[str, DeviceState]
    show_elements: dict[str, ShowElement]
    events: list[Event]


class MockCommandService(QObject):
    event_added = Signal(object)
    state_changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        rooms = {r.id: r for r in build_rooms()}
        devices = {d.id: d for d in build_devices()}
        elements = {e.id: e for e in build_show_elements()}
        self.state = AppState(rooms, devices, elements, [])

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _log(self, room_id: str, message: str, severity: Severity = Severity.INFO) -> None:
        event = Event(datetime.now(), room_id, message, severity)
        self.state.events.append(event)
        self.event_added.emit(event)

    def _tick(self) -> None:
        for room in self.state.rooms.values():
            if room.game_running:
                room.elapsed_seconds += 1

        if random.random() < 0.04:
            room = random.choice(list(self.state.rooms.values()))
            msg = random.choice(
                [
                    "Sensor heartbeat drop detected",
                    "Door contact stable",
                    "Audio bus latency normalized",
                    "Light controller acknowledged cue",
                ]
            )
            sev = Severity.WARNING if "drop" in msg else Severity.INFO
            self._log(room.id, msg, sev)

        self.state_changed.emit()

    def execute(self, room_id: str, command: str, payload: str = "") -> None:
        if room_id not in self.state.rooms:
            return
        room = self.state.rooms[room_id]
        cmd = command.lower()

        if cmd == "start game":
            room.game_running = True
            room.health = RoomHealth.ACTIVE
            room.current_puzzle = room.puzzles[0].name
        elif cmd == "pause game":
            room.game_running = False
            room.health = RoomHealth.PAUSED
        elif cmd == "resume game":
            room.game_running = True
            room.health = RoomHealth.ACTIVE
        elif cmd == "stop game":
            room.game_running = False
            room.health = RoomHealth.RESET_NEEDED
        elif cmd in {"reset room", "full reset"}:
            room.game_running = False
            room.elapsed_seconds = 0
            room.current_puzzle = "Not started"
            room.health = RoomHealth.READY
            for p in room.puzzles:
                p.status = "pending"
        elif cmd == "skip puzzle":
            pending = [p for p in room.puzzles if p.status != "complete"]
            if pending:
                pending[0].status = "complete"
                next_pending = next((p for p in room.puzzles if p.status != "complete"), None)
                room.current_puzzle = next_pending.name if next_pending else "All puzzles complete"
        elif cmd in {"trigger hint", "trigger custom hint 1", "trigger custom hint 2"}:
            room.notes = f"Last hint issued: {command}"
        elif cmd == "trigger finale":
            room.health = RoomHealth.ACTIVE
            room.current_puzzle = "Finale running"
        elif cmd == "emergency unlock all":
            for dev in self.state.devices.values():
                if dev.kind == "door":
                    dev.status = "unlocked"
        elif cmd == "lock all doors":
            for dev in self.state.devices.values():
                if dev.kind == "door":
                    dev.status = "locked"
        elif cmd == "stop all audio":
            for dev in self.state.devices.values():
                if dev.kind == "audio":
                    dev.status = "stopped"
        elif cmd == "stop all video":
            for dev in self.state.devices.values():
                if dev.kind == "video":
                    dev.status = "stopped"
        elif cmd == "blackout / kill effects":
            for dev in self.state.devices.values():
                if dev.kind in {"lighting", "effects", "props", "scenic"}:
                    dev.status = "killed"
        elif cmd == "restore default state":
            for dev in self.state.devices.values():
                if dev.kind == "door":
                    dev.status = "locked"
                else:
                    dev.status = "idle"

        if payload:
            self._log(room_id, f"{command}: {payload}")
        else:
            self._log(room_id, command)
        self.state_changed.emit()

    def trigger_element(self, element_id: str) -> None:
        if element_id not in self.state.show_elements:
            return
        el = self.state.show_elements[element_id]
        el.status = "triggered"
        el.last_triggered = datetime.now()
        if el.reset_required:
            el.status = "awaiting reset"
        if el.linked_device_id and el.linked_device_id in self.state.devices:
            self.state.devices[el.linked_device_id].status = "active"
        self._log(el.room_id, f"Cue fired: {el.name}")
        self.state_changed.emit()
