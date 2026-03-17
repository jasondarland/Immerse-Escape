from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .services import MockCommandService
from .styles import DARK_QSS
from .ui_main import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)

    service = MockCommandService()
    window = MainWindow(service)
    window.show()

    return app.exec()
