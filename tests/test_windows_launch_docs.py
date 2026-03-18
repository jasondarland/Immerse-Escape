from __future__ import annotations

import unittest
from pathlib import Path


class WindowsLaunchDocumentationTests(unittest.TestCase):
    def test_readme_contains_windows_powershell_activation(self):
        readme = Path('README.md').read_text(encoding='utf-8')
        self.assertIn('.\\.venv\\Scripts\\Activate.ps1', readme)
        self.assertIn('python -m immerse_runtime.main', readme)
        self.assertIn('run_runtime.ps1', readme)
        self.assertIn('run_runtime.bat', readme)

    def test_windows_launch_scripts_exist(self):
        self.assertTrue(Path('run_runtime.ps1').exists())
        self.assertTrue(Path('run_runtime.bat').exists())


if __name__ == '__main__':
    unittest.main()
