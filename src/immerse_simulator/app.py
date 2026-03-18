from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from immerse_simulator.ui.main_window import MainWindow
from immerse_simulator.ui.theme import DARK_THEME


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    demo_path = Path(__file__).resolve().parent / "assets" / "demo_package"
    window = MainWindow(demo_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
