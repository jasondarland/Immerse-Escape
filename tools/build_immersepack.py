from __future__ import annotations

import argparse
from pathlib import Path

from immerse_occ.pack_builder import export_immersepack


def main() -> int:
    parser = argparse.ArgumentParser(description="Build official .immersepack from project payload folder")
    parser.add_argument("project_root", help="Path to payload source folder")
    parser.add_argument("output", help="Output .immersepack path")
    parser.add_argument("--version", default="1.0.0", help="Manifest format version")
    args = parser.parse_args()

    output = export_immersepack(Path(args.project_root), Path(args.output), version=args.version)
    print(f"Built package: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
