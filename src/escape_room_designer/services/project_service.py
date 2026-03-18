"""Project save/load/autosave services."""
from __future__ import annotations

import json
import zipfile
from datetime import datetime
from pathlib import Path

from escape_room_designer.models.project_model import EscapeProject


class ProjectService:
    """Handles project persistence and version snapshots."""

    PROJECT_FILE_NAME = "project.json"
    PACK_EXTENSIONS = {".immersepack", ".zip"}
    PACK_PROJECT_CANDIDATES = (
        "project/project.json",
        "project.json",
    )

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or Path.cwd() / "projects"
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def save_project(self, project: EscapeProject, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        project.updated_at = datetime.utcnow().isoformat()

        project_file = target_dir / self.PROJECT_FILE_NAME
        project_file.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")

        self._ensure_project_dirs(target_dir)
        self._snapshot_version(target_dir, project)
        return project_file

    def load_project(self, project_path: Path) -> EscapeProject:
        payload = self._load_project_payload(project_path)
        return EscapeProject.from_dict(payload)

    def autosave(self, project: EscapeProject, target_dir: Path) -> Path:
        autosave_dir = target_dir / ".autosave"
        autosave_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = autosave_dir / f"autosave_{timestamp}.json"
        file_path.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
        return file_path

    def _load_project_payload(self, project_path: Path) -> dict:
        path = Path(project_path)
        if path.is_dir():
            return self._read_json(path / self.PROJECT_FILE_NAME)
        if path.suffix.lower() in self.PACK_EXTENSIONS:
            return self._load_from_pack(path)
        return self._read_json(path)

    def _load_from_pack(self, pack_path: Path) -> dict:
        with zipfile.ZipFile(pack_path) as archive:
            members = set(archive.namelist())
            project_member = next((name for name in self.PACK_PROJECT_CANDIDATES if name in members), None)
            if not project_member:
                raise ValueError(f"Package '{pack_path}' does not contain a supported project manifest")

            self._validate_archive_members(members)
            with archive.open(project_member) as handle:
                return json.loads(handle.read().decode("utf-8"))

    def _validate_archive_members(self, members: set[str]) -> None:
        for member in members:
            normalized = Path(member)
            if normalized.is_absolute() or ".." in normalized.parts:
                raise ValueError(f"Unsafe archive entry '{member}' detected")

    def _read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _snapshot_version(self, target_dir: Path, project: EscapeProject) -> None:
        versions = target_dir / ".versions"
        versions.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        (versions / f"project_{stamp}.json").write_text(
            json.dumps(project.to_dict(), indent=2), encoding="utf-8"
        )

    def _ensure_project_dirs(self, target_dir: Path) -> None:
        folders = [
            "project",
            "layout/backgrounds",
            "puzzles",
            "logic",
            "timeline",
            "media/audio",
            "media/video",
            "media/images",
            "devices",
            "operator",
            "reports",
            "notes",
            "config",
        ]
        for folder in folders:
            (target_dir / folder).mkdir(parents=True, exist_ok=True)
