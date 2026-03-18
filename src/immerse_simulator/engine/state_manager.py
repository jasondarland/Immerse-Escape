from __future__ import annotations

from datetime import datetime, UTC


class StateManager:
    def __init__(self) -> None:
        self._state: dict[str, dict[str, object]] = {}

    def bulk_load(self, initial_state: dict[str, object]) -> None:
        for key, value in initial_state.items():
            self.set_state(key, value)

    def set_state(self, key: str, value: object, category: str = "runtime") -> None:
        self._state[key] = {
            "value": value,
            "category": category,
            "updated_at": datetime.now(UTC),
        }

    def get_state(self, key: str, default: object | None = None) -> object | None:
        return self._state.get(key, {}).get("value", default)

    def snapshot(self) -> dict[str, dict[str, object]]:
        return dict(sorted(self._state.items()))
