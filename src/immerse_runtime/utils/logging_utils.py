from __future__ import annotations

import faulthandler
import logging
import os
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO


LOG_DIR_NAME = "logs"
LOG_FILE_NAME = "immerse_runtime.log"
CRASH_FILE_NAME = "immerse_runtime_crash.log"


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[3]


def app_data_dir() -> Path:
    path = _app_root()
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_dir() -> Path:
    path = app_data_dir() / LOG_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_file() -> Path:
    return log_dir() / LOG_FILE_NAME


def crash_file() -> Path:
    return log_dir() / CRASH_FILE_NAME


_FAULT_HANDLER_STREAM: TextIO | None = None


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("immerse_runtime")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    file_handler = logging.FileHandler(log_file(), encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.propagate = False
    logger.info("Logging initialized")
    return logger


def install_fault_handler() -> None:
    global _FAULT_HANDLER_STREAM
    if _FAULT_HANDLER_STREAM is not None:
        return
    _FAULT_HANDLER_STREAM = open(crash_file(), "a", encoding="utf-8")
    faulthandler.enable(file=_FAULT_HANDLER_STREAM, all_threads=True)


def _write_crash_report(exc_type, exc_value, exc_traceback) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    report = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    with crash_file().open("a", encoding="utf-8") as handle:
        handle.write(f"\n[{timestamp}] Unhandled exception\n{report}\n")


def install_exception_hooks() -> None:
    logger = configure_logging()

    def handle_exception(exc_type, exc_value, exc_traceback):
        _write_crash_report(exc_type, exc_value, exc_traceback)
        logger.exception("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

    def handle_thread_exception(args):
        _write_crash_report(args.exc_type, args.exc_value, args.exc_traceback)
        logger.exception(
            "Unhandled thread exception",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = handle_exception
    threading.excepthook = handle_thread_exception


def runtime_environment_summary() -> dict[str, str]:
    return {
        "python": sys.version.replace("\n", " "),
        "platform": sys.platform,
        "cwd": os.getcwd(),
        "log_file": str(log_file()),
        "crash_file": str(crash_file()),
    }
