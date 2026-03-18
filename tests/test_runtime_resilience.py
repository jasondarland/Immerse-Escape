from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from immerse_runtime.services.package_loader import PackageLoader, PackageValidationError
from immerse_runtime.utils.logging_utils import configure_logging, crash_file, log_dir, log_file, runtime_environment_summary


class RuntimeResilienceTests(unittest.TestCase):
    def test_logging_paths_are_created(self):
        logger = configure_logging()
        logger.info('resilience test log entry')
        self.assertTrue(log_dir().exists())
        self.assertTrue(log_file().exists())
        self.assertTrue(str(crash_file()).endswith('immerse_runtime_crash.log'))

    def test_environment_summary_contains_log_targets(self):
        summary = runtime_environment_summary()
        self.assertIn('python', summary)
        self.assertIn('log_file', summary)
        self.assertIn('crash_file', summary)

    def test_package_loader_reports_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            shutil.copytree('demo_package', tmp_path / 'pkg', dirs_exist_ok=True)
            (tmp_path / 'pkg' / 'logic' / 'states.json').unlink()
            with self.assertRaises(PackageValidationError):
                PackageLoader().load(tmp_path / 'pkg')


if __name__ == '__main__':
    unittest.main()
