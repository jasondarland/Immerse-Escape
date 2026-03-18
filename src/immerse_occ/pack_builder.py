from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path

DEFAULT_MANIFEST = {
    "format": "IMMERSEPACK",
    "version": "1.0.0",
    "payload_root": "payload",
    "entry": "payload/immersepack.json",
}


def export_immersepack(project_root: str | Path, output_file: str | Path, version: str = "1.0.0") -> Path:
    """Build an official .immersepack from a prepared project payload tree.

    Expected in `project_root`:
      immersepack.json
      project/project.json
      devices/devices.json
      devices/patch.json
      logic/logic_graph.json
      logic/states.json
      timeline/timeline.json
      media/media_index.json
      operator/operator_controls.json
      config/runtime_config.json
    """
    project_root = Path(project_root)
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)
        payload_dir = temp_dir / "payload"
        shutil.copytree(project_root, payload_dir)

        manifest = dict(DEFAULT_MANIFEST)
        manifest["version"] = version
        (temp_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        with zipfile.ZipFile(output_file, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in temp_dir.rglob("*"):
                if path.is_file():
                    zf.write(path, path.relative_to(temp_dir).as_posix())

    if output_file.suffix.lower() != ".immersepack":
        renamed = output_file.with_suffix(".immersepack")
        output_file.replace(renamed)
        return renamed
    return output_file
