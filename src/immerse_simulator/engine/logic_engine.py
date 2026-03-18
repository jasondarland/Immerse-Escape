from __future__ import annotations

from immerse_simulator.models.package import ShowPackage


class LogicEngine:
    def __init__(self, package: ShowPackage | None = None) -> None:
        self.package = package

    def bind_package(self, package: ShowPackage) -> None:
        self.package = package

    def evaluate_input(self, action: str, value: str) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        if not self.package:
            return results
        if action == "keypad" and value == "0426":
            results.extend([
                {"type": "puzzle_solved", "puzzle_id": "lab_a_keypad"},
                {"type": "device_state", "device_id": "lab_a_door", "state": "unlocked"},
                {"type": "play_audio", "asset_id": "sfx_unlock"},
            ])
        elif action == "rfid" and value == "RFID-ALPHA":
            results.extend([
                {"type": "puzzle_solved", "puzzle_id": "lab_b_rfid"},
                {"type": "state", "key": "lab_b_enabled", "value": True},
                {"type": "device_state", "device_id": "lab_b_console", "state": "armed"},
            ])
        elif action == "sequence" and value == "RGBY":
            results.extend([
                {"type": "puzzle_solved", "puzzle_id": "lab_b_sequence"},
                {"type": "device_state", "device_id": "final_door", "state": "unlocked"},
                {"type": "play_audio", "asset_id": "finale_theme"},
                {"type": "play_video", "asset_id": "finale_video"},
                {"type": "effect", "device_id": "fogger_finale", "state": "active"},
            ])
        return results
