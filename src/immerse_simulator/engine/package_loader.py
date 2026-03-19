from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from immerse_simulator.models.package import Cue, Device, Puzzle, ShowPackage, ValidationMessage


class PackageLoader:
    REQUIRED_PATHS = [
        "project/project.json",
        "devices/devices.json",
        "devices/patch.json",
        "logic/logic_graph.json",
        "logic/states.json",
        "timeline/timeline.json",
        "media/media_index.json",
        "operator/operator_controls.json",
        "config/runtime_config.json",
    ]

    def __init__(self) -> None:
        self._temp_dirs: list[str] = []

    def _resolve_root(self, source: str | Path) -> Path:
        path = Path(source)
        if path.is_dir():
            return path
        if path.suffix in {".immersepack", ".zip"}:
            temp_dir = tempfile.mkdtemp(prefix="immerse_sim_")
            self._temp_dirs.append(temp_dir)
            with zipfile.ZipFile(path) as archive:
                archive.extractall(temp_dir)
            return Path(temp_dir)
        raise ValueError(f"Unsupported package source: {source}")

    def load(self, source: str | Path) -> ShowPackage:
        root = self._resolve_root(source)
        messages: list[ValidationMessage] = []
        manifest = self._read_json_if_exists(root / "manifest.json") or {}
        immerse_config = self._read_json_if_exists(root / "payload/immersepack.json") or self._read_json_if_exists(root / "immersepack.json") or {}
        for rel_path in self.REQUIRED_PATHS:
            if not (root / rel_path).exists():
                messages.append(ValidationMessage("warning", f"Missing {rel_path}"))
        project = self._read_json_if_exists(root / "project/project.json") or {}
        devices_data = self._read_json_if_exists(root / "devices/devices.json") or {"devices": []}
        states_data = self._read_json_if_exists(root / "logic/states.json") or {"states": {}}
        timeline_data = self._read_json_if_exists(root / "timeline/timeline.json") or {"cues": []}
        operator_controls = self._read_json_if_exists(root / "operator/operator_controls.json") or {}
        runtime_config = self._read_json_if_exists(root / "config/runtime_config.json") or {}

        devices = [Device(**device) for device in devices_data.get("devices", [])]
        puzzles = [Puzzle(**puzzle) for puzzle in project.get("puzzles", [])]
        cues = [Cue(**cue) for cue in timeline_data.get("cues", [])]
        return ShowPackage(
            name=project.get("name", immerse_config.get("name", "Unnamed Package")),
            version=str(project.get("version", "1.0")),
            root_path=root,
            manifest=manifest,
            rooms=project.get("rooms", []),
            devices=devices,
            puzzles=puzzles,
            states=states_data.get("states", {}),
            timeline=cues,
            operator_controls=operator_controls,
            runtime_config=runtime_config,
            validation_messages=messages,
        )

    @staticmethod
    def _read_json_if_exists(path: Path) -> dict | None:
        if path.exists():
            return json.loads(path.read_text())
        return None

    def cleanup(self) -> None:
        for directory in self._temp_dirs:
            shutil.rmtree(directory, ignore_errors=True)
        self._temp_dirs.clear()
