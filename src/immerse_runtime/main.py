from __future__ import annotations

import sys

from immerse_runtime.utils.logging_utils import configure_logging, install_exception_hooks, install_fault_handler


def main() -> int:
    install_fault_handler()
    install_exception_hooks()
    logger = configure_logging()

    try:
        from immerse_runtime.app.bootstrap import main as bootstrap_main
    except Exception:
        logger.exception("Failed to import application bootstrap. Verify PySide6 is installed and the app files are intact.")
        print("IMMERSE Runtime failed during startup import. See logs/immerse_runtime.log and logs/immerse_runtime_crash.log for details.")
        return 1

    try:
        return bootstrap_main()
    except Exception:
        logger.exception("Runtime crashed during execution")
        print("IMMERSE Runtime crashed. See logs/immerse_runtime.log and logs/immerse_runtime_crash.log for details.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
