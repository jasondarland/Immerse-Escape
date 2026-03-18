from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from immerse_runtime.services.package_loader import PackageLoader
from immerse_runtime.utils.demo_package_utils import resolve_demo_package_path


class DemoPackageResolutionTests(unittest.TestCase):
    def test_resolve_demo_package_path_uses_source_tree_when_present(self):
        resolved = resolve_demo_package_path()
        manifest = PackageLoader().load(resolved)
        self.assertEqual(manifest.name, 'IMMERSE Demo Runtime Package')

    def test_resolve_demo_package_path_can_extract_when_external_folder_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_root = Path(temp_dir)
            fake_cwd = fake_root / 'runtime'
            fake_cwd.mkdir()
            fake_exe = fake_root / 'bin' / 'python'
            fake_exe.parent.mkdir()
            fake_exe.write_text('')
            with mock.patch('pathlib.Path.cwd', return_value=fake_cwd), \
                 mock.patch('sys.executable', str(fake_exe)), \
                 mock.patch('immerse_runtime.utils.demo_package_utils.app_data_dir', return_value=fake_root / 'appdata'):
                resolved = resolve_demo_package_path()
                self.assertTrue((resolved / 'immersepack.json').exists())
                self.assertEqual(PackageLoader().load(resolved).version, '1.0.0')
                shutil.rmtree(resolved)


if __name__ == '__main__':
    unittest.main()
