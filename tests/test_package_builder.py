from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from immerse_runtime.utils.package_builder import OFFICIAL_MANIFEST, build_immersepack


class PackageBuilderTests(unittest.TestCase):
    def test_builder_writes_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / 'runtime.immersepack'
            build_immersepack('demo_package', target, project_name='Demo Export')
            with zipfile.ZipFile(target, 'r') as archive:
                manifest = json.loads(archive.read('manifest.json').decode('utf-8'))
                self.assertEqual(manifest['format'], OFFICIAL_MANIFEST['format'])
                self.assertEqual(manifest['payload_root'], 'payload')
                self.assertEqual(manifest['project_name'], 'Demo Export')


if __name__ == '__main__':
    unittest.main()
