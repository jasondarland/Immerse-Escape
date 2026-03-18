from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from immerse_runtime.models.entities import RuntimeEvent, Severity


class EventLogger:
    def __init__(self) -> None:
        self.events: list[RuntimeEvent] = []

    def log(self, severity: Severity, room: str, source: str, event_type: str, message: str) -> RuntimeEvent:
        event = RuntimeEvent(datetime.now(timezone.utc), severity, room, source, event_type, message)
        self.events.append(event)
        return event

    def export(self, path: str | Path) -> None:
        target = Path(path)
        target.write_text(
            "\n".join(
                f"{e.timestamp.isoformat()} [{e.severity.value.upper()}] {e.room} | {e.source} | {e.event_type} | {e.message}"
                for e in self.events
            ),
            encoding="utf-8",
        )
