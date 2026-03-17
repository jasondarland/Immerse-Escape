"""IMMERSEPACK export builder for direct runtime consumption."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from escape_room_designer.models.project_model import EscapeProject
from escape_room_designer.services.validation_service import ValidationResult


class ImmersePackExporter:
    """Create runtime-oriented IMMERSEPACK.ZIP packages."""

    def export(self, project: EscapeProject, output_zip: Path, validation: ValidationResult) -> Path:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_project(project, root)
            required_assets = self._write_layout(project, root)
            patch_nodes = self._write_devices(project, root)
            self._write_logic(project, root)
            self._write_timeline(project, root)
            required_assets.extend(self._write_media(project, root))
            self._write_operator(project, root)
            self._write_runtime_config(project, root)
            self._write_reports(project, root, validation)
            self._write_manifest(project, root, required_assets, patch_nodes)

            with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in root.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(root).as_posix())
        return output_zip

    def _json(self, path: Path, payload: dict | list) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _copy_if_exists(self, src: str, dst: Path) -> str:
        if not src:
            return ""
        source = Path(src)
        if not source.exists() or not source.is_file():
            return ""
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dst)
        return dst.as_posix()

    def _write_project(self, project: EscapeProject, root: Path) -> None:
        self._json(root / "project" / "project.json", project.to_dict())

    def _write_layout(self, project: EscapeProject, root: Path) -> list[str]:
        assets: list[str] = []
        rooms = []
        for room in project.layouts:
            bg_rel = ""
            if room.background_image:
                bg_rel = f"layout/backgrounds/{room.room_id}{Path(room.background_image).suffix}"
                copied = self._copy_if_exists(room.background_image, root / bg_rel)
                if copied:
                    assets.append(bg_rel)
            objects = []
            for obj in room.objects:
                image_rel = ""
                if obj.image_path:
                    image_rel = f"layout/backgrounds/{room.room_id}_{obj.object_id}{Path(obj.image_path).suffix}"
                    copied = self._copy_if_exists(obj.image_path, root / image_rel)
                    if copied:
                        assets.append(image_rel)
                objects.append({
                    "object_id": obj.object_id,
                    "object_type": obj.object_type,
                    "name": obj.name,
                    "x": obj.x,
                    "y": obj.y,
                    "width": obj.width,
                    "height": obj.height,
                    "rotation": obj.rotation,
                    "layer": obj.layer,
                    "zone_id": obj.metadata.get("zone_id", "default"),
                    "metadata": obj.metadata,
                    "image": image_rel,
                })
            rooms.append({
                "room_id": room.room_id,
                "room_name": room.room_name,
                "scale_m_per_px": room.scale_m_per_px,
                "background_locked": room.background_locked,
                "background_image": bg_rel,
                "objects": objects,
            })
        self._json(root / "layout" / "rooms.json", {"rooms": rooms})
        return assets

    def _write_devices(self, project: EscapeProject, root: Path) -> list[dict]:
        devices = []
        nodes: dict[str, dict] = {}
        for d in project.devices:
            devices.append({
                "id": d.id,
                "name": d.name,
                "type": d.type,
                "subtype": d.subtype,
                "room_id": d.room_id,
                "zone_id": d.zone_id,
                "node_id": d.node_id,
                "protocol": d.protocol,
                "address": d.address,
                "capabilities": d.capabilities,
                "default_state": d.default_state,
                "fail_state": d.fail_state,
                "tags": d.tags,
                "notes": d.notes,
                "simulated_properties": d.simulated_properties,
            })
            nodes.setdefault(d.node_id, {
                "node_id": d.node_id,
                "network_endpoint": "",
                "universe_mappings": [],
                "gpio_mappings": [],
                "relay_channel_mappings": [],
                "audio_output_assignments": [],
                "video_output_assignments": [],
                "room_ids": [],
            })
            if d.room_id not in nodes[d.node_id]["room_ids"]:
                nodes[d.node_id]["room_ids"].append(d.room_id)

            if d.protocol in {"gpio", "local_runtime_virtual"}:
                nodes[d.node_id]["gpio_mappings"].append({"device_id": d.id, "address": d.address})
            if d.protocol in {"dmx", "artnet", "sacn"}:
                nodes[d.node_id]["universe_mappings"].append({"device_id": d.id, "address": d.address})
            if d.type == "relay":
                nodes[d.node_id]["relay_channel_mappings"].append({"device_id": d.id, "address": d.address})
            if d.type == "speaker_zone":
                nodes[d.node_id]["audio_output_assignments"].append({"device_id": d.id, "address": d.address})
            if d.type in {"video_output", "projector"}:
                nodes[d.node_id]["video_output_assignments"].append({"device_id": d.id, "address": d.address})

        self._json(root / "devices" / "devices.json", {"devices": devices})
        patch = {"nodes": list(nodes.values())}
        self._json(root / "devices" / "patch.json", patch)
        return list(nodes.values())

    def _write_logic(self, project: EscapeProject, root: Path) -> None:
        self._json(
            root / "logic" / "logic_graph.json",
            {
                "graph_nodes": [
                    {
                        "id": n.node_id,
                        "type": n.node_type,
                        "label": n.label,
                        "x": n.x,
                        "y": n.y,
                        "event_inputs": n.data.get("event_inputs", []),
                        "conditions": n.data.get("conditions", []),
                        "actions": n.data.get("actions", []),
                        "state_reads": n.data.get("state_reads", []),
                        "state_writes": n.data.get("state_writes", []),
                    }
                    for n in project.logic_nodes
                ],
                "graph_edges": [{"source": e.source, "target": e.target, "label": e.label} for e in project.logic_edges],
                "execution_order": [n.node_id for n in project.logic_nodes],
                "dependencies": [{"from": e.source, "to": e.target} for e in project.logic_edges],
                "execution": {"event_driven": True, "deterministic": True, "parallel_branches": True},
            },
        )
        self._json(root / "logic" / "states.json", {"states": project.states})

    def _write_timeline(self, project: EscapeProject, root: Path) -> None:
        self._json(
            root / "timeline" / "timeline.json",
            {
                "start": "00:00:00:000",
                "duration_mode": "unlimited",
                "cues": [
                    {
                        "id": c.id,
                        "track": c.track,
                        "start_time": c.start_time,
                        "duration": c.duration,
                        "trigger_mode": c.trigger_mode,
                        "target": c.target,
                        "action": c.action,
                        "parameters": c.parameters,
                        "preconditions": c.preconditions,
                        "follow_actions": c.follow_actions,
                    }
                    for c in project.timeline
                ],
            },
        )

    def _write_media(self, project: EscapeProject, root: Path) -> list[str]:
        assets: list[str] = []
        index = []
        for item in project.media:
            media_type = item.get("media_type", item.get("type", "image"))
            folder = "images"
            if media_type == "audio":
                folder = "audio"
            elif media_type == "video":
                folder = "video"
            src = item.get("path", "")
            name = Path(src).name if src else f"{item.get('asset_id', item.get('name', 'asset'))}.dat"
            rel = f"media/{folder}/{name}"
            copied = self._copy_if_exists(src, root / rel)
            if copied:
                assets.append(rel)
            index.append(
                {
                    "asset_id": item.get("asset_id", item.get("name", "asset")),
                    "file_path": rel,
                    "media_type": media_type,
                    "duration": item.get("duration", 0),
                    "target_outputs": item.get("target_outputs", []),
                    "playback_mode": item.get("playback_mode", "trigger"),
                    "loop": item.get("loop", False),
                    "volume": item.get("volume", 1.0),
                    "fade_in": item.get("fade_in", 0),
                    "fade_out": item.get("fade_out", 0),
                    "sync_group": item.get("sync_group", ""),
                    "preloading_rules": item.get("preloading_rules", "on_demand"),
                }
            )
        self._json(root / "media" / "media_index.json", {"assets": index})
        return assets

    def _write_operator(self, project: EscapeProject, root: Path) -> None:
        self._json(root / "operator" / "operator_controls.json", {"controls": project.operator_controls})

    def _write_runtime_config(self, project: EscapeProject, root: Path) -> None:
        self._json(root / "config" / "runtime_config.json", project.runtime_config)

    def _write_reports(self, project: EscapeProject, root: Path, validation: ValidationResult) -> None:
        payload = {
            "project_id": project.project_id,
            "project_name": project.name,
            "build_time": datetime.utcnow().isoformat(),
            "validation": validation.to_dict(),
        }
        self._json(root / "reports" / "build_manifest.json", payload)

    def _write_manifest(self, project: EscapeProject, root: Path, required_assets: list[str], nodes: list[dict]) -> None:
        hash_input = json.dumps(project.to_dict(), sort_keys=True).encode("utf-8")
        checksum = hashlib.sha256(hash_input).hexdigest()
        manifest = {
            "project_id": project.project_id,
            "project_name": project.name,
            "project_version": project.version,
            "pack_format_version": "1.0.0",
            "created_by": "IMMERSE Designer – Escape Room Edition",
            "created_on": datetime.utcnow().isoformat(),
            "startup_scene": project.startup_scene,
            "default_timeline": project.default_timeline,
            "device_registry_file": "devices/devices.json",
            "patch_file": "devices/patch.json",
            "logic_file": "logic/logic_graph.json",
            "state_file": "logic/states.json",
            "media_index_file": "media/media_index.json",
            "operator_controls_file": "operator/operator_controls.json",
            "runtime_config_file": "config/runtime_config.json",
            "required_assets": sorted(set(required_assets)),
            "build": {"checksum_sha256": checksum, "node_count": len(nodes), "device_count": len(project.devices)},
        }
        self._json(root / "immersepack.json", manifest)
