from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

from immerse_runtime.services.package_loader import PackageLoader


OFFICIAL_MANIFEST = {
    "format": "IMMERSEPACK",
    "version": "1.0.0",
    "payload_root": "payload",
    "entry": "payload/immersepack.json",
}


def build_immersepack(source_dir: str | Path, output_file: str | Path, *, project_name: str | None = None, version: str = "1.0.0") -> Path:
    source = Path(source_dir)
    output = Path(output_file)
    output.parent.mkdir(parents=True, exist_ok=True)

    loader = PackageLoader()
    manifest = loader.load(source)

    archive_manifest = dict(OFFICIAL_MANIFEST)
    archive_manifest["project_name"] = project_name or manifest.name
    archive_manifest["package_version"] = version or manifest.version

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        payload_root = temp_root / "payload"
        shutil.copytree(source, payload_root, dirs_exist_ok=True)
        (temp_root / "manifest.json").write_text(json.dumps(archive_manifest, indent=2), encoding="utf-8")

        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file_path in temp_root.rglob("*"):
                if file_path.is_file():
                    archive.write(file_path, file_path.relative_to(temp_root).as_posix())

    return output
