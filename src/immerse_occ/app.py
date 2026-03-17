from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path


STARTUP_LOG_PATH = Path.home() / ".immerse_occ_startup.log"


def _write_startup_log(message: str) -> None:
    """Write boot/runtime failures to disk for diagnostics before Qt is available."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        STARTUP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STARTUP_LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(f"[{timestamp}] {message}\n")
    except Exception:
        # Never raise from logging path.
        pass


def run() -> int:
    """Start OCC UI with early-failure logging and safe exception handling."""

    try:
        from PySide6.QtWidgets import QApplication, QMessageBox

        from .services import MockCommandService
        from .styles import DARK_QSS
        from .ui_main import MainWindow
    except Exception:
        message = "".join(traceback.format_exc())
        _write_startup_log("Import/bootstrap failure:\n" + message)
        print(message, file=sys.stderr)
        return 1

    def _excepthook(exc_type, exc_value, exc_tb):
        message = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        _write_startup_log("Unhandled exception:\n" + message)
        print(message, file=sys.stderr)
        app = QApplication.instance()
        if app is not None:
            try:
                QMessageBox.critical(
                    None,
                    "Unexpected Application Error",
                    "The OCC encountered an unexpected error and must close.\n\n"
                    f"A diagnostic log was written to:\n{STARTUP_LOG_PATH}"
                )
            except Exception:
                _write_startup_log("Failed to display crash dialog.")

    sys.excepthook = _excepthook

    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(DARK_QSS)

        service = MockCommandService()
        window = MainWindow(service)
        window.show()

        return app.exec()
    except Exception:
        message = "".join(traceback.format_exc())
        _write_startup_log("Runtime startup failure:\n" + message)
        print(message, file=sys.stderr)
        return 1
