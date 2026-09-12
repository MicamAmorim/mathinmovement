from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mathinmovement.migrations.legacy_demos import migrate_legacy_demos
from mathinmovement.registry import Registry


class LegacyDemoMigrationTests(unittest.TestCase):
    def test_can_migrate_one_demo_without_touching_project_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = migrate_legacy_demos(
                output_root=root,
                only=["area-paralelogramo"],
            )
            self.assertEqual(result["total_legacy"], 30)
            self.assertEqual(result["created"], ["area-paralelogramo"])

            registry = Registry(content_root=root, database_path=None).rebuild()
            record = registry.get("area-paralelogramo")
            self.assertEqual(record.manifest["status"], "draft")
            self.assertEqual(
                record.manifest["render"]["production_engine"],
                "compatibility",
            )
            self.assertFalse(record.manifest["render"]["native_ready"])
            compat = record.manifest["render"]["compatibility"]
            self.assertEqual(compat["source"], "videos/02_area_paralelogramo.py")
            self.assertEqual(compat["scene"], "AreaParalelogramo")
            self.assertEqual(record.manifest["result"]["math"], r"A=b\cdot h")


if __name__ == "__main__":
    unittest.main()
