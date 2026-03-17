from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import DeviceState, Puzzle, Room, ShowElement


@dataclass
class PackData:
    rooms: list[Room]
    devices: list[DeviceState]
    show_elements: list[ShowElement]


def _slug(text: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return value or "item"


def _read_json_from_zip(zip_ref: zipfile.ZipFile, name: str) -> Any | None:
    target = name.lower()
    for member in zip_ref.namelist():
        if member.lower().endswith(target):
            with zip_ref.open(member) as handle:
                return json.loads(handle.read().decode("utf-8"))
    return None


def _build_room(item: dict[str, Any], index: int) -> Room:
    room_name = str(item.get("name") or f"Room {index + 1}")
    room_id = str(item.get("id") or _slug(room_name))
    puzzle_items = item.get("puzzles") or []
    puzzles = [
        Puzzle(
            id=str(p.get("id") or f"{room_id}_p{n + 1}"),
            name=str(p.get("name") or f"Puzzle {n + 1}"),
            status=str(p.get("status") or "pending"),
        )
        for n, p in enumerate(puzzle_items)
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


def _normalize_from_structured_payload(payload: dict[str, Any]) -> PackData:
    rooms_data = payload.get("rooms") or []
    rooms = [_build_room(r, i) for i, r in enumerate(rooms_data) if isinstance(r, dict)]
    if not rooms:
        raise ValueError("No rooms found in immerse pack payload.")
    room_ids = {r.id for r in rooms}
    default_room = rooms[0].id

    devices_data = payload.get("devices") or []
    devices = []
    for i, item in enumerate(devices_data):
        if not isinstance(item, dict):
            continue
        dev = _build_device(item, i, default_room)
        if dev.room_id not in room_ids:
            dev.room_id = default_room
        devices.append(dev)

    elements_data = payload.get("show_elements") or payload.get("elements") or []
    elements = []
    for i, item in enumerate(elements_data):
        if not isinstance(item, dict):
            continue
        el = _build_element(item, i, default_room)
        if el.room_id not in room_ids:
            el.room_id = default_room
        elements.append(el)

    return PackData(rooms=rooms, devices=devices, show_elements=elements)


def _normalize_from_room_folders(zip_ref: zipfile.ZipFile) -> PackData | None:
    room_names: set[str] = set()
    for member in zip_ref.namelist():
        lower = member.lower()
        if "/rooms/" in lower:
            right = member.split("/rooms/", 1)[1]
            top = right.split("/", 1)[0].strip()
            if top:
                room_names.add(top)

    if not room_names:
        return None

    rooms = [Room(id=_slug(name), name=name.replace("_", " ").title()) for name in sorted(room_names)]
    return PackData(rooms=rooms, devices=[], show_elements=[])


def load_immersepack_zip(zip_path: str | Path) -> PackData:
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError(f"Pack file not found: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        manifest = (
            _read_json_from_zip(zip_ref, "immersepack.json")
            or _read_json_from_zip(zip_ref, "manifest.json")
            or _read_json_from_zip(zip_ref, "pack.json")
        )

        if isinstance(manifest, dict):
            return _normalize_from_structured_payload(manifest)

        rooms = _read_json_from_zip(zip_ref, "rooms.json")
        devices = _read_json_from_zip(zip_ref, "devices.json")
        show_elements = _read_json_from_zip(zip_ref, "show_elements.json")
        if isinstance(rooms, list):
            payload = {
                "rooms": rooms,
                "devices": devices if isinstance(devices, list) else [],
                "show_elements": show_elements if isinstance(show_elements, list) else [],
            }
            return _normalize_from_structured_payload(payload)

        fallback = _normalize_from_room_folders(zip_ref)
        if fallback:
            return fallback

    raise ValueError(
        "Unable to parse immerse pack. Expected immersepack.json/manifest.json/pack.json, "
        "or rooms.json (+ optional devices/show_elements), or /rooms/<room-name>/ structure."
    )
