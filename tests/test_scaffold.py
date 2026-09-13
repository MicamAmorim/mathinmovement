from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from mathinmovement.registry import load_manifest, validate_manifest
from mathinmovement.scaffold import scaffold_content


class ScaffoldTests(unittest.TestCase):
    def test_demo_scaffold_is_valid_and_packagable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            destination, package = scaffold_content(
                "demo",
                "demo-teste",
                output_dir=root / "demo-teste",
                package=True,
            )
            manifest = load_manifest(destination / "manifest.yaml")
            validate_manifest(manifest, source=destination / "manifest.yaml")

            self.assertEqual(manifest["type"], "demo")
            self.assertEqual(
                manifest["render"]["production_engine"],
                "dsl",
            )
            self.assertIsNotNone(package)
            self.assertEqual(package.suffix, ".demo")
            with zipfile.ZipFile(package) as archive:
                self.assertIn("manifest.yaml", archive.namelist())

    def test_qenem_scaffold_uses_requested_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            destination, package = scaffold_content(
                "qenem",
                "EXEMPLO-2030-MT-01",
                output_dir=root / "qenem-teste",
                title="Questão de teste",
                year=2030,
                question_number=42,
                package=True,
            )
            manifest = load_manifest(destination / "manifest.yaml")
            validate_manifest(manifest, source=destination / "manifest.yaml")

            self.assertEqual(manifest["type"], "qenem")
            self.assertEqual(manifest["title"], "Questão de teste")
            self.assertEqual(manifest["exam"]["year"], 2030)
            self.assertEqual(manifest["exam"]["question_number"], 42)
            self.assertEqual(
                manifest["question"]["answer"],
                manifest["solution"]["final_answer"],
            )
            self.assertIsNotNone(package)
            self.assertEqual(package.suffix, ".qenem")

    def test_existing_destination_requires_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "existing"
            root.mkdir()
            with self.assertRaises(ValueError):
                scaffold_content(
                    "demo",
                    "demo-existente",
                    output_dir=root,
                )


if __name__ == "__main__":
    unittest.main()
