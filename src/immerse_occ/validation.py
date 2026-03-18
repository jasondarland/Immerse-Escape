from __future__ import annotations

from pathlib import Path

from .package_loader import REQUIRED_FILES, PackageValidationError


def validate_payload_root(payload_root: str | Path) -> None:
    """Validate official IMMERSEPACK required payload files."""
    root = Path(payload_root)
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing:
        raise PackageValidationError(
            "Invalid IMMERSEPACK: missing required files: " + ", ".join(missing)
        )
