"""IMMERSEPACK export builder."""
from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from escape_room_designer.models.project_model import EscapeProject


class ImmersePackExporter:
    """Create runtime-oriented IMMERSEPACK.ZIP packages."""

    def export(self, project: EscapeProject, output_zip: Path) -> Path:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_master(project, root)
            self._write_layouts(project, root)
            self._write_devices(project, root)
            self._write_logic(project, root)
            self._write_timeline(project, root)
            self._write_media(project, root)
            self._write_config(project, root)

            with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in root.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(root).as_posix())
        return output_zip

    def _write_master(self, project: EscapeProject, root: Path) -> None:
        master = {
            "project_name": project.name,
            "version": project.version,
            "startup_behavior": {"entrypoint": "logic/logic.json", "autoload": True},
            "rooms": [{"room_id": r.room_id, "room_name": r.room_name} for r in project.layouts],
            "device_registry": "devices/devices.json",
            "logic": "logic/logic.json",
            "timeline": "timeline/timeline.json",
        }
        (root / "immersepack.json").write_text(json.dumps(master, indent=2), encoding="utf-8")

    def _copy_if_exists(self, src: str, dst: Path) -> str:
        if not src:
            return ""
        source = Path(src)
        if not source.exists() or not source.is_file():
            return ""
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dst)
        return dst.as_posix()

    def _write_layouts(self, project: EscapeProject, root: Path) -> None:
        layout_dir = root / "layout"
        layout_dir.mkdir(parents=True, exist_ok=True)
        exported_layouts = []
        for room in project.layouts:
            bg_name = f"{room.room_id}_background{Path(room.background_image).suffix}" if room.background_image else ""
            bg_rel = f"layout/{bg_name}" if bg_name else ""
            if bg_name:
                self._copy_if_exists(room.background_image, root / bg_rel)

            objects = []
            for obj in room.objects:
                obj_payload = {
                    "object_id": obj.object_id,
                    "object_type": obj.object_type,
                    "name": obj.name,
                    "x": obj.x,
                    "y": obj.y,
                    "width": obj.width,
                    "height": obj.height,
                    "rotation": obj.rotation,
                    "layer": obj.layer,
                    "metadata": obj.metadata,
                    "image": "",
                }
                if obj.image_path:
                    img_name = f"{room.room_id}_{obj.object_id}{Path(obj.image_path).suffix}"
                    rel = f"layout/{img_name}"
                    copied = self._copy_if_exists(obj.image_path, root / rel)
                    obj_payload["image"] = copied
                objects.append(obj_payload)

            exported_layouts.append(
                {
                    "room_id": room.room_id,
                    "room_name": room.room_name,
                    "scale_m_per_px": room.scale_m_per_px,
                    "background_locked": room.background_locked,
                    "background_image": bg_rel,
                    "objects": objects,
                }
            )
        (layout_dir / "layouts.json").write_text(json.dumps(exported_layouts, indent=2), encoding="utf-8")

    def _write_devices(self, project: EscapeProject, root: Path) -> None:
        devices_dir = root / "devices"
        devices_dir.mkdir(parents=True, exist_ok=True)
        payload = []
        for dev in project.devices:
            payload.append(
                {
                    "runtime_id": dev.runtime_id,
                    "name": dev.name,
                    "type": dev.device_type,
                    "room_id": dev.room_id,
                    "node_assignment": dev.node_assignment,
                    "address": dev.address,
                    "io_mapping": dev.io_mapping,
                    "state": dev.state,
                    "metadata": dev.metadata,
                }
            )
        (devices_dir / "devices.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _write_logic(self, project: EscapeProject, root: Path) -> None:
        logic_dir = root / "logic"
        logic_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "nodes": [
                {"node_id": n.node_id, "node_type": n.node_type, "label": n.label, "x": n.x, "y": n.y, "data": n.data}
                for n in project.logic_nodes
            ],
            "edges": [{"source": e.source, "target": e.target, "label": e.label} for e in project.logic_edges],
            "execution": {"mode": "event_driven", "deterministic": True},
        }
        (logic_dir / "logic.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _write_timeline(self, project: EscapeProject, root: Path) -> None:
        tdir = root / "timeline"
        tdir.mkdir(parents=True, exist_ok=True)
        payload = {
            "start_timecode": "00:00:00:000",
            "duration_mode": "unlimited",
            "tracks": [
                {"cue_id": c.cue_id, "track": c.track, "timecode_ms": c.timecode_ms, "action": c.action, "target": c.target, "payload": c.payload}
                for c in project.timeline
            ],
        }
        (tdir / "timeline.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _write_media(self, project: EscapeProject, root: Path) -> None:
        media_root = root / "media"
        for folder in ("audio", "video", "images"):
            (media_root / folder).mkdir(parents=True, exist_ok=True)

        manifest = []
        for item in project.media:
            item_type = item.get("type", "images")
            src = item.get("path", "")
            target_folder = "images"
            if item_type == "audio":
                target_folder = "audio"
            elif item_type == "video":
                target_folder = "video"
            name = Path(src).name if src else f"{item.get('name','asset')}.dat"
            rel = f"media/{target_folder}/{name}"
            copied = self._copy_if_exists(src, root / rel)
            manifest.append({**item, "pack_path": copied or rel})
        (media_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def _write_config(self, project: EscapeProject, root: Path) -> None:
        cdir = root / "config"
        cdir.mkdir(parents=True, exist_ok=True)
        payload = {
            "system": "IMMERSE Designer – Escape Room Edition",
            "operator_controls": project.operator_controls,
            "runtime": {"low_latency": True, "frame_sync_capable": True, "network_dispatch_ready": True},
        }
        (cdir / "system.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
