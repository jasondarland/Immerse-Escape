from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path


def main() -> int:
    if importlib.util.find_spec("PySide6") is None:
        print(
            "IMMERSE Escape Simulator requires PySide6. "
            "Install it first, then run this app again.",
            file=sys.stderr,
        )
        return 1

    from PySide6.QtWidgets import QApplication, QMessageBox

    from immerse_simulator.ui.main_window import MainWindow
    from immerse_simulator.ui.theme import DARK_THEME

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
