from __future__ import annotations

from copy import deepcopy


class StateManager:
    def __init__(self) -> None:
        self.initial_state: dict = {}
        self.state: dict = {}

    def load(self, states: dict) -> None:
        self.initial_state = deepcopy(states)
        self.state = deepcopy(states)

    def reset(self) -> None:
        self.state = deepcopy(self.initial_state)

    def set_value(self, key: str, value) -> None:
        self.state["variables"][key] = value

    def get_value(self, key: str, default=None):
        return self.state.get("variables", {}).get(key, default)
