from __future__ import annotations

import sys
from pathlib import Path

from immerse_runtime.utils.logging_utils import configure_logging, runtime_environment_summary


def main() -> int:
    logger = configure_logging()
    logger.info("Starting IMMERSE Runtime")
    logger.info("Environment summary: %s", runtime_environment_summary())

    from PySide6.QtWidgets import QApplication, QMessageBox

    from immerse_runtime.services.runtime_service import RuntimeService
    from immerse_runtime.ui.main_window import MainWindow
    from immerse_runtime.ui.theme import DARK_THEME

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    runtime = RuntimeService()
    demo_path = Path(__file__).resolve().parents[3] / "demo_package"
    logger.info("Resolved demo package path: %s", demo_path)

    try:
        runtime.load_package(demo_path)
    except Exception as exc:
        logger.exception("Failed to load bundled demo package")
        QMessageBox.critical(
            None,
            "Package Load Error",
            f"The bundled demo package could not be loaded.\n\n{exc}\n\nSee logs/immerse_runtime.log for details.",
        )
        return 1

    window = MainWindow(runtime)
    window.show()
    logger.info("Main window shown successfully")
    return app.exec()
