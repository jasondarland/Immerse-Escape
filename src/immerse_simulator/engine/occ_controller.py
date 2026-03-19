from __future__ import annotations

from immerse_simulator.models.events import Event


class OCCController:
    def __init__(self, emit_event) -> None:
        self.emit_event = emit_event

    def trigger(self, action: str, room: str = "Global") -> None:
        self.emit_event(Event(source="OCC", event_type="operator", message=f"Operator action: {action}", room=room))
