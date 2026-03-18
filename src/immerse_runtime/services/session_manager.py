from __future__ import annotations

from datetime import datetime, timezone
from itertools import count

from immerse_runtime.models.entities import Session


class SessionManager:
    def __init__(self) -> None:
        self._ids = count(1)
        self.current = Session(id="SESSION-0000", room="Unassigned", preset="Default", state="idle")

    def start(self, room: str, preset: str) -> Session:
        self.current = Session(
            id=f"SESSION-{next(self._ids):04d}",
            room=room,
            preset=preset,
            state="running",
            started_at=datetime.now(timezone.utc),
        )
        return self.current

    def pause(self) -> None:
        self.current.state = "paused"

    def resume(self) -> None:
        self.current.state = "running"

    def stop(self) -> None:
        self.current.state = "stopped"

    def reset(self) -> None:
        self.current.state = "reset"
        self.current.elapsed_seconds = 0
        self.current.active_puzzles = 0
        self.current.solved_puzzles = 0
