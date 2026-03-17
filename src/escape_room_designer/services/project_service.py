"""Project save/load/autosave services."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from escape_room_designer.models.project_model import EscapeProject


class ProjectService:
    """Handles project persistence and version snapshots."""

    def __init__(self, root_dir: Path | None = None) -> None:
        self.root_dir = root_dir or Path.cwd() / "projects"
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def save_project(self, project: EscapeProject, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        project.updated_at = datetime.utcnow().isoformat()

        project_file = target_dir / "project.json"
        project_file.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")

        self._ensure_project_dirs(target_dir)
        self._snapshot_version(target_dir, project)
        return project_file

    def load_project(self, project_file: Path) -> EscapeProject:
        payload = json.loads(project_file.read_text(encoding="utf-8"))
        return EscapeProject.from_dict(payload)

    def autosave(self, project: EscapeProject, target_dir: Path) -> Path:
        autosave_dir = target_dir / ".autosave"
        autosave_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = autosave_dir / f"autosave_{timestamp}.json"
        file_path.write_text(json.dumps(project.to_dict(), indent=2), encoding="utf-8")
        return file_path

    def _snapshot_version(self, target_dir: Path, project: EscapeProject) -> None:
        versions = target_dir / ".versions"
        versions.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        (versions / f"project_{stamp}.json").write_text(
            json.dumps(project.to_dict(), indent=2), encoding="utf-8"
        )

    def _ensure_project_dirs(self, target_dir: Path) -> None:
        folders = [
            "layout",
            "puzzles",
            "logic",
            "timeline",
            "media/audio",
            "media/video",
            "media/images",
            "devices",
            "reports",
            "notes",
            "config",
        ]
        for folder in folders:
            (target_dir / folder).mkdir(parents=True, exist_ok=True)
