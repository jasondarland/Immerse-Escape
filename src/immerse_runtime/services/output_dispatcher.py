from __future__ import annotations

from datetime import datetime, timezone

from immerse_runtime.models.entities import OutputAction


class OutputDispatcher:
    def __init__(self) -> None:
        self.active_outputs: list[OutputAction] = []

    def dispatch(self, target: str, room: str, action: str, expected_duration: float = 2.0) -> OutputAction:
        output = OutputAction(target, room, action, datetime.now(timezone.utc), expected_duration, "active")
        self.active_outputs.append(output)
        return output

    def stop_all(self) -> None:
        for output in self.active_outputs:
            output.state = "stopped"
