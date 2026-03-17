"""Qt application bootstrap."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from escape_room_designer.ui.main_window import MainWindow
from escape_room_designer.ui.theme import build_stylesheet


def run() -> None:
    """Launch the desktop application."""
    # Ensure src/ is importable when running from repository root.
    repo_root = Path(__file__).resolve().parents[3]
    src_dir = repo_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    app = QApplication(sys.argv)
    app.setApplicationName("IMMERSE Designer – Escape Room Edition")
    app.setStyleSheet(build_stylesheet())

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())
