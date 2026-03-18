from __future__ import annotations

import json
import logging
import shutil
import tempfile
import uuid
import zipfile
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

    def __init__(self) -> None:
        self.logger = logging.getLogger("immerse_runtime.package_loader")
        self._extracted_roots: list[Path] = []
        self.last_loaded_root: Path | None = None
        self.last_package_metadata: dict | None = None

    def load(self, source: str | Path) -> PackageManifest:
        base = self._resolve_source_root(source)
        self.last_loaded_root = base
        loaded = self._load_required_json(base)
        self.logger.info("Validation passed")

        manifest = loaded["manifest"]
        package_manifest = PackageManifest(
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
        self.last_package_metadata = self.describe_source(source, package_manifest)
        return package_manifest

    def describe_source(self, source: str | Path, package_manifest: PackageManifest | None = None) -> dict:
        path = Path(source)
        manifest = package_manifest or (self.load(path))
        return {
            "source": str(path),
            "project_name": manifest.name,
            "version": manifest.version,
            "rooms": manifest.project.get("rooms", []),
            "device_count": len(manifest.devices),
            "payload_root": str(self.last_loaded_root) if self.last_loaded_root else "",
        }

    def cleanup(self) -> None:
        for root in self._extracted_roots:
            shutil.rmtree(root, ignore_errors=True)
        self._extracted_roots.clear()

    def _resolve_source_root(self, source: str | Path) -> Path:
        path = Path(source)
        if path.is_dir():
            self.logger.info("Loading package from folder %s", path)
            return self._resolve_payload_root(path)

        if path.suffix.lower() in {".immersepack", ".zip"}:
            self.logger.info("Loading IMMERSEPACK from archive %s", path)
            extracted_root = self._extract_archive(path)
            self._extracted_roots.append(extracted_root)
            return self._resolve_payload_root(extracted_root)

        raise PackageValidationError(f"Unsupported package source: {path}")

    def _extract_archive(self, archive_path: Path) -> Path:
        if not archive_path.exists():
            raise PackageValidationError(f"Package source does not exist: {archive_path}")

        temp_root = Path(tempfile.gettempdir()) / "immerse_runtime" / str(uuid.uuid4())
        temp_root.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(archive_path, "r") as archive:
            for member in archive.infolist():
                member_path = Path(member.filename)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise PackageValidationError("Invalid IMMERSEPACK: unsafe archive path detected")
                destination = (temp_root / member.filename).resolve()
                if temp_root.resolve() not in destination.parents and destination != temp_root.resolve():
                    raise PackageValidationError("Invalid IMMERSEPACK: path traversal attempt detected")
                if member.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member, "r") as source_file, destination.open("wb") as output_file:
                    shutil.copyfileobj(source_file, output_file)

        return temp_root

    def _resolve_payload_root(self, extracted_root: Path) -> Path:
        manifest_path = extracted_root / "manifest.json"
        if manifest_path.exists():
            try:
                archive_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                self.logger.error("Invalid manifest")
                raise PackageValidationError("Invalid IMMERSEPACK: invalid manifest") from exc
            payload_root = archive_manifest.get("payload_root", "payload")
            resolved = extracted_root / payload_root
            self.logger.info("Detected payload root %s", resolved)
            return resolved

        payload_dir = extracted_root / "payload"
        if payload_dir.exists():
            self.logger.info("Detected payload root %s", payload_dir)
            return payload_dir

        self.logger.info("Detected payload root %s", extracted_root)
        return extracted_root

    def _load_required_json(self, base: Path) -> dict[str, object]:
        missing = [rel for rel in self.REQUIRED_FILES if not (base / rel).exists()]
        if missing:
            self.logger.error("Missing required files: %s", ", ".join(missing))
            raise PackageValidationError("Invalid IMMERSEPACK: missing required files")

        loaded: dict[str, object] = {}
        for rel, key in self.REQUIRED_FILES.items():
            with (base / rel).open("r", encoding="utf-8") as fh:
                loaded[key] = json.load(fh)
        return loaded
