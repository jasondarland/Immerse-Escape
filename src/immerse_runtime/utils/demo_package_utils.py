from __future__ import annotations

import shutil
import sys
from importlib import resources
from pathlib import Path
from typing import Iterable

from immerse_runtime.services.package_loader import PackageLoader, PackageValidationError
from immerse_runtime.utils.logging_utils import app_data_dir


def _candidate_demo_paths() -> list[Path]:
    candidates: list[Path] = []
    candidates.append(Path.cwd() / "demo_package")
    candidates.append(Path(sys.executable).resolve().parent / "demo_package")

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "demo_package")

    candidates.append(Path(__file__).resolve().parents[3] / "demo_package")

    seen: set[Path] = set()
    unique_candidates: list[Path] = []
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            unique_candidates.append(resolved)
            seen.add(resolved)
    return unique_candidates


def _is_valid_package(path: Path) -> bool:
    try:
        PackageLoader().load(path)
        return True
    except (PackageValidationError, FileNotFoundError, OSError, KeyError, ValueError, TypeError):
        return False


def _walk_resources(root) -> Iterable[tuple[object, Path]]:
    for entry in root.iterdir():
        relative = Path(str(entry.name))
        yield entry, relative
        if entry.is_dir():
            for child, child_relative in _walk_resources(entry):
                yield child, relative / child_relative


def _extract_packaged_demo(target_root: Path) -> Path:
    destination = target_root / "demo_package"
    destination.mkdir(parents=True, exist_ok=True)

    package_root = resources.files("immerse_runtime.demo_package")
    for resource, relative in _walk_resources(package_root):
        if resource.is_dir():
            (destination / relative).mkdir(parents=True, exist_ok=True)
            continue
        if resource.name == "__init__.py":
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with resources.as_file(resource) as source_path:
            shutil.copy2(source_path, target)
    return destination


def resolve_demo_package_path() -> Path:
    for candidate in _candidate_demo_paths():
        if _is_valid_package(candidate):
            return candidate

    extracted = _extract_packaged_demo(app_data_dir())
    if _is_valid_package(extracted):
        return extracted

    raise PackageValidationError("Bundled demo package could not be found or reconstructed from packaged resources")


def demo_package_search_summary() -> dict[str, str | list[str]]:
    return {
        "cwd": str(Path.cwd()),
        "executable": str(Path(sys.executable).resolve()),
        "meipass": str(getattr(sys, "_MEIPASS", "")),
        "candidates": [str(path) for path in _candidate_demo_paths()],
        "app_data_dir": str(app_data_dir()),
    }
