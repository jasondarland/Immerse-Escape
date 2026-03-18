from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from immerse_simulator.ui.main_window import MainWindow
from immerse_simulator.ui.theme import DARK_THEME


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)
    demo_path = Path(__file__).resolve().parent / "assets" / "demo_package"
    try:
        window = MainWindow(demo_path)
    except Exception as exc:
        QMessageBox.critical(
            None,
            "IMMERSE Escape Simulator",
            f"The simulator failed to start.\n\n{exc}\n\n{traceback.format_exc()}",
        )
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
