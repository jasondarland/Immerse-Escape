from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from immerse_simulator.models.events import Event


class EventBus(QObject):
    event_emitted = Signal(object)

    def emit_event(self, event: Event) -> None:
        self.event_emitted.emit(event)
