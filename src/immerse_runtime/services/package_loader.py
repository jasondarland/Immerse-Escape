from __future__ import annotations

import json
from pathlib import Path

from immerse_runtime.models.entities import PackageManifest


class PackageValidationError(Exception):
    pass


class PackageLoader:
    REQUIRED_FILES = {
        "immersepack.json": "manifest",
        "project/project.json": "project",
        "devices/devices.json": "devices",
        "devices/patch.json": "patch",
        "logic/logic_graph.json": "logic_graph",
        "logic/states.json": "states",
        "timeline/timeline.json": "timeline",
        "media/media_index.json": "media_index",
        "operator/operator_controls.json": "operator_controls",
        "config/runtime_config.json": "runtime_config",
    }

    def load(self, root: str | Path) -> PackageManifest:
        base = Path(root)
        missing = [rel for rel in self.REQUIRED_FILES if not (base / rel).exists()]
        if missing:
            raise PackageValidationError(f"Missing required package files: {', '.join(missing)}")

        loaded: dict[str, object] = {}
        for rel, key in self.REQUIRED_FILES.items():
            with (base / rel).open("r", encoding="utf-8") as fh:
                loaded[key] = json.load(fh)

        manifest = loaded["manifest"]
        return PackageManifest(
            name=manifest.get("name", "Unnamed Runtime Package"),
            version=manifest.get("version", "0.0.0"),
            project=loaded["project"],
            devices=loaded["devices"]["devices"],
            patch=loaded["patch"]["connections"],
            logic_graph=loaded["logic_graph"],
            states=loaded["states"],
            timeline=loaded["timeline"],
            media_index=loaded["media_index"],
            operator_controls=loaded["operator_controls"],
            runtime_config=loaded["runtime_config"],
        )
