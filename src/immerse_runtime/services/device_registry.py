from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from immerse_runtime.models.entities import Device


class DeviceRegistry:
    def __init__(self) -> None:
        self.devices: dict[str, Device] = {}

    def load(self, devices: list[dict]) -> None:
        self.devices = {
            device["id"]: Device(
                id=device["id"],
                name=device["name"],
                type=device["type"],
                room=device["room"],
                node=device["node"],
            )
            for device in devices
        }

    def update_state(self, device_id: str, state: str, status: str = "online", fault: str = "") -> None:
        device = self.devices[device_id]
        device.current_state = state
        device.status = status
        device.fault = fault
        device.last_update = datetime.now(timezone.utc)

    def by_room(self, room: str) -> list[Device]:
        return [d for d in self.devices.values() if d.room == room]

    def summary(self) -> dict[str, int]:
        by_type = defaultdict(int)
        for device in self.devices.values():
            by_type[device.type] += 1
        return dict(by_type)
