from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from immerse_runtime.services.runtime_service import RuntimeService
from immerse_runtime.ui.main_window import MainWindow
from immerse_runtime.ui.theme import DARK_THEME


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    runtime = RuntimeService()
    demo_path = Path(__file__).resolve().parents[3] / "demo_package"
    runtime.load_package(demo_path)
    window = MainWindow(runtime)
    window.show()
    return app.exec()
