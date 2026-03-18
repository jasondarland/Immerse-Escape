"""Application entry for Escape Room Designer."""
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parent
src_dir = repo_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from escape_room_designer.core.app import run


if __name__ == "__main__":
    run()
