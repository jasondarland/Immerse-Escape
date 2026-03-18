from __future__ import annotations

import json
import logging
import re
import shutil
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import DeviceState, Puzzle, Room, ShowElement

logger = logging.getLogger(__name__)

REQUIRED_FILES = [
    "immersepack.json",
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


class PackageValidationError(Exception):
    """Raised when a package does not satisfy IMMERSEPACK requirements."""


@dataclass
class PackData:
    rooms: list[Room]
    devices: list[DeviceState]
    show_elements: list[ShowElement]


@dataclass
class LoadedPackage:
    project_name: str
    version: str
    payload_root: Path
    extract_root: Path | None
    data: PackData


def _slug(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return value or "item"


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_extract_zip(archive_path: Path) -> Path:
    temp_root = Path(tempfile.gettempdir()) / "immerse_runtime" / str(uuid.uuid4())
    temp_root.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path, "r") as zf:
        for member in zf.infolist():
            target = (temp_root / member.filename).resolve()
            if not str(target).startswith(str(temp_root.resolve())):
                raise PackageValidationError("Invalid package: blocked path traversal entry")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)

    return temp_root


def _resolve_payload_root(base_root: Path) -> tuple[Path, dict[str, Any] | None]:
    manifest_path: Path | None = None
    manifests = sorted(base_root.rglob("manifest.json"), key=lambda p: len(p.parts))
    if manifests:
        manifest_path = manifests[0]

    manifest: dict[str, Any] | None = None
    if manifest_path is not None:
        try:
            manifest = _load_json(manifest_path)
        except Exception as exc:
            logger.error("Invalid manifest")
            raise PackageValidationError(f"Invalid manifest: {exc}") from exc

        payload_rel = str(manifest.get("payload_root") or "payload")
        payload_root = (manifest_path.parent / payload_rel).resolve()
        logger.info("Detected payload root: %s", payload_root)
        if payload_root.exists():
            return payload_root, manifest

    payload_dirs = sorted(
        [p for p in base_root.rglob("payload") if p.is_dir()], key=lambda p: len(p.parts)
    )
    if payload_dirs:
        logger.info("Detected payload root: %s", payload_dirs[0])
        return payload_dirs[0].resolve(), manifest

    logger.info("Detected payload root: %s", base_root)
    return base_root.resolve(), manifest


def _validate_required(payload_root: Path) -> None:
    missing = [rel for rel in REQUIRED_FILES if not (payload_root / rel).exists()]
    if missing:
        logger.error("Missing required files")
        raise PackageValidationError(
            "Invalid IMMERSEPACK: missing required files: " + ", ".join(missing)
        )
    logger.info("Validation passed")


def _build_room(item: dict[str, Any], index: int) -> Room:
    room_name = str(item.get("name") or f"Room {index + 1}")
    room_id = str(item.get("id") or _slug(room_name))
    puzzles = [
        Puzzle(
            id=str(p.get("id") or f"{room_id}_p{n + 1}"),
            name=str(p.get("name") or f"Puzzle {n + 1}"),
            status=str(p.get("status") or "pending"),
        )
        for n, p in enumerate(item.get("puzzles") or [])
        if isinstance(p, dict)
    ]
    checklist = [str(x) for x in (item.get("reset_checklist") or [])]
    return Room(id=room_id, name=room_name, puzzles=puzzles, reset_checklist=checklist)


def _build_device(item: dict[str, Any], index: int, fallback_room: str) -> DeviceState:
    name = str(item.get("name") or f"Device {index + 1}")
    return DeviceState(
        id=str(item.get("id") or _slug(name)),
        name=name,
        room_id=str(item.get("room_id") or fallback_room),
        kind=str(item.get("kind") or item.get("type") or "utility").lower(),
        status=str(item.get("status") or "idle"),
    )


def _build_element(item: dict[str, Any], index: int, fallback_room: str) -> ShowElement:
    name = str(item.get("name") or f"Cue {index + 1}")
    return ShowElement(
        id=str(item.get("id") or _slug(name)),
        name=name,
        room_id=str(item.get("room_id") or fallback_room),
        category=str(item.get("category") or "Utility / Overrides"),
        status=str(item.get("status") or "ready"),
        requires_confirmation=bool(item.get("requires_confirmation", False)),
        auto_reset=bool(item.get("auto_reset", False)),
        reset_required=bool(item.get("reset_required", False)),
        notes=str(item.get("notes") or ""),
        linked_device_id=str(item.get("linked_device_id") or ""),
    )


def _normalize_payload(
    immersepack: dict[str, Any],
    project_json: dict[str, Any],
    devices_json: Any,
    operator_json: dict[str, Any],
) -> tuple[str, str, PackData]:
    rooms_src = immersepack.get("rooms") or operator_json.get("rooms") or []
    rooms = [_build_room(item, i) for i, item in enumerate(rooms_src) if isinstance(item, dict)]

    device_items: list[dict[str, Any]] = []
    if isinstance(devices_json, list):
        device_items = [d for d in devices_json if isinstance(d, dict)]
    elif isinstance(devices_json, dict):
        vals = devices_json.get("devices")
        if isinstance(vals, list):
            device_items = [d for d in vals if isinstance(d, dict)]

    if not rooms:
        # fallback from unique room_id in devices
        seen = sorted({str(d.get("room_id")) for d in device_items if d.get("room_id")})
        rooms = [Room(id=_slug(name), name=name) for name in seen]

    if not rooms:
        rooms = [Room(id="room_1", name="Room 1")]

    room_ids = {r.id for r in rooms}
    default_room = rooms[0].id

    devices = []
    for i, item in enumerate(device_items):
        dev = _build_device(item, i, default_room)
        if dev.room_id not in room_ids:
            dev.room_id = default_room
        devices.append(dev)

    cues_src = immersepack.get("show_elements") or immersepack.get("elements") or operator_json.get("show_elements") or []
    elements = []
    for i, item in enumerate(cues_src):
        if not isinstance(item, dict):
            continue
        el = _build_element(item, i, default_room)
        if el.room_id not in room_ids:
            el.room_id = default_room
        elements.append(el)

    project_name = str(
        project_json.get("name")
        or immersepack.get("project_name")
        or immersepack.get("name")
        or "Untitled IMMERSE Project"
    )
    version = str(
        project_json.get("version")
        or immersepack.get("version")
        or "unknown"
    )
    return project_name, version, PackData(rooms=rooms, devices=devices, show_elements=elements)


def _legacy_load_from_folder(root: Path) -> LoadedPackage:
    logger.info("Loading legacy package fallback from folder")
    # Old support: rooms/devices/show_elements in root or nested.
    def find_json(name: str) -> Any | None:
        candidates = sorted(root.rglob(name), key=lambda p: len(p.parts))
        if not candidates:
            return None
        return _load_json(candidates[0])

    rooms = find_json("rooms.json")
    devices = find_json("devices.json")
    elements = find_json("show_elements.json")

    if isinstance(rooms, list):
        payload = {
            "rooms": rooms,
            "devices": devices if isinstance(devices, list) else [],
            "show_elements": elements if isinstance(elements, list) else [],
        }
        immersepack = payload
        project = {"name": "Legacy ZIP/Folder", "version": "legacy"}
        operator = {}
        pname, ver, data = _normalize_payload(immersepack, project, payload["devices"], operator)
        return LoadedPackage(project_name=pname, version=ver, payload_root=root, extract_root=None, data=data)

    # Room folder fallback
    room_names: set[str] = set()
    for member in root.rglob("*"):
        if not member.is_dir():
            continue
        parts_lower = [p.lower() for p in member.parts]
        if "rooms" in parts_lower:
            idx = parts_lower.index("rooms")
            if len(member.parts) > idx + 1:
                room_names.add(member.parts[idx + 1])

    if room_names:
        rooms_data = [Room(id=_slug(name), name=name.replace("_", " ").title()) for name in sorted(room_names)]
        data = PackData(rooms=rooms_data, devices=[], show_elements=[])
        return LoadedPackage(
            project_name="Legacy ZIP/Folders",
            version="legacy",
            payload_root=root,
            extract_root=None,
            data=data,
        )

    raise PackageValidationError(
        "Invalid IMMERSEPACK: missing required files"
    )


def load_package(path: str | Path) -> LoadedPackage:
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"Package path not found: {src}")

    lower_name = src.name.lower()
    is_archive = src.is_file() and (lower_name.endswith(".immersepack") or lower_name.endswith(".zip"))
    strict_immersepack = src.is_file() and lower_name.endswith(".immersepack")

    logger.info("Loading IMMERSEPACK")
    extract_root: Path | None = None

    if is_archive:
        extract_root = _safe_extract_zip(src)
        payload_root, manifest = _resolve_payload_root(extract_root)
    elif src.is_dir():
        payload_root, manifest = _resolve_payload_root(src)
    else:
        raise PackageValidationError("Unsupported package source. Use .immersepack, .zip, or folder path.")

    try:
        _validate_required(payload_root)

        immersepack = _load_json(payload_root / "immersepack.json")
        project_json = _load_json(payload_root / "project/project.json")
        devices_json = _load_json(payload_root / "devices/devices.json")
        operator_json = _load_json(payload_root / "operator/operator_controls.json")

        project_name, version, data = _normalize_payload(
            immersepack if isinstance(immersepack, dict) else {},
            project_json if isinstance(project_json, dict) else {},
            devices_json,
            operator_json if isinstance(operator_json, dict) else {},
        )

        if manifest and not isinstance(manifest, dict):
            logger.error("Invalid manifest")
            raise PackageValidationError("Invalid manifest")

        return LoadedPackage(
            project_name=project_name,
            version=version,
            payload_root=payload_root,
            extract_root=extract_root,
            data=data,
        )
    except PackageValidationError:
        if strict_immersepack:
            raise
        # Backward compatibility for legacy zip/folder layouts.
        fallback_root = extract_root if extract_root is not None else src
        return _legacy_load_from_folder(fallback_root)


def load_immersepack_zip(zip_path: str | Path) -> PackData:
    """Backward-compatible function retained for existing OCC integration."""
    loaded = load_package(zip_path)
    return loaded.data
