from __future__ import annotations

from datetime import timedelta


class SessionManager:
    def __init__(self) -> None:
        self.status = "stopped"
        self.elapsed = timedelta(0)
        self.speed = 1.0
        self.operator_mode = "Training"

    def start(self) -> None:
        self.status = "running"

    def pause(self) -> None:
        self.status = "paused"

    def stop(self) -> None:
        self.status = "stopped"
        self.elapsed = timedelta(0)

    def tick(self, seconds: float) -> None:
        if self.status == "running":
            self.elapsed += timedelta(seconds=seconds * self.speed)
