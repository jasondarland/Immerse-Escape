from __future__ import annotations

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from .services import MockCommandService
from .styles import DARK_QSS
from .ui_main import MainWindow


def run() -> int:
    def _excepthook(exc_type, exc_value, exc_tb):
        message = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(message, file=sys.stderr)
        QMessageBox.critical(
            None,
            "Unexpected Application Error",
            "The OCC encountered an unexpected error and must close.\n\n"
            "Error details have been printed to stderr."
        )

    sys.excepthook = _excepthook
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)

    service = MockCommandService()
    window = MainWindow(service)
    window.show()

    return app.exec()
