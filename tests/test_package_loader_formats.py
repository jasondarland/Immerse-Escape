from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from immerse_runtime.services.package_loader import PackageLoader, PackageValidationError
from immerse_runtime.utils.package_builder import build_immersepack


class PackageLoaderFormatTests(unittest.TestCase):
    def setUp(self):
        self.loader = PackageLoader()

    def tearDown(self):
        self.loader.cleanup()

    def test_loads_folder_package(self):
        manifest = self.loader.load('demo_package')
        self.assertEqual(manifest.name, 'IMMERSE Demo Runtime Package')

    def test_builds_and_loads_immersepack_archive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = Path(temp_dir) / 'demo_v1.immersepack'
            build_immersepack('demo_package', archive_path)
            manifest = self.loader.load(archive_path)
            self.assertEqual(manifest.name, 'IMMERSE Demo Runtime Package')
            with zipfile.ZipFile(archive_path, 'r') as archive:
                self.assertIn('manifest.json', archive.namelist())
                self.assertIn('payload/immersepack.json', archive.namelist())

    def test_loads_legacy_zip_without_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / 'legacy.zip'
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                for file_path in Path('demo_package').rglob('*'):
                    if file_path.is_file():
                        archive.write(file_path, file_path.relative_to('demo_package').as_posix())
            manifest = self.loader.load(zip_path)
            self.assertEqual(manifest.version, '1.0.0')

    def test_uses_manifest_payload_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / 'custom.immersepack'
            payload_root = Path(temp_dir) / 'build' / 'custom_payload'
            payload_root.mkdir(parents=True)
            shutil.copytree('demo_package', payload_root, dirs_exist_ok=True)
            manifest_json = {
                'format': 'IMMERSEPACK',
                'version': '1.0.0',
                'payload_root': 'custom_payload',
                'entry': 'custom_payload/immersepack.json',
            }
            build_root = Path(temp_dir) / 'build'
            (build_root / 'manifest.json').write_text(json.dumps(manifest_json), encoding='utf-8')
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                for file_path in build_root.rglob('*'):
                    if file_path.is_file():
                        archive.write(file_path, file_path.relative_to(build_root).as_posix())
            loaded = self.loader.load(zip_path)
            self.assertEqual(loaded.name, 'IMMERSE Demo Runtime Package')

    def test_rejects_path_traversal_archive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / 'bad.immersepack'
            with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('../evil.txt', 'nope')
            with self.assertRaises(PackageValidationError):
                self.loader.load(zip_path)

    def test_reports_missing_required_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            broken = Path(temp_dir) / 'broken'
            shutil.copytree('demo_package', broken, dirs_exist_ok=True)
            (broken / 'logic' / 'states.json').unlink()
            with self.assertRaises(PackageValidationError) as context:
                self.loader.load(broken)
            self.assertEqual(str(context.exception), 'Invalid IMMERSEPACK: missing required files')


if __name__ == '__main__':
    unittest.main()
