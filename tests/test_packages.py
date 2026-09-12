from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from mathinmovement.package_io import export_package, import_package
from mathinmovement.registry import Registry


class PackageTests(unittest.TestCase):
    def test_qenem_export_and_import_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            package = export_package(
                "ENEM-2021-MT-11",
                tmp_path / "ENEM-2021-MT-11.qenem",
            )
            self.assertTrue(package.exists())
            with zipfile.ZipFile(package) as archive:
                self.assertIn("manifest.yaml", archive.namelist())

            imported_root = tmp_path / "imported"
            destination = import_package(
                package,
                content_root=imported_root,
            )
            self.assertTrue((destination / "manifest.yaml").exists())

            registry = Registry(imported_root, database_path=None).rebuild()
            self.assertEqual(registry.get("ENEM-2021-MT-11").type, "qenem")

    def test_demo_export_has_demo_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "area-triangulo.demo"
            package = export_package("area-triangulo", output)
            self.assertEqual(package.suffix, ".demo")
            self.assertTrue(package.exists())


if __name__ == "__main__":
    unittest.main()
