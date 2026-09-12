from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mathinmovement.migrations.legacy_enem import migrate_legacy_enem
from mathinmovement.registry import Registry


class LegacyEnemMigrationTests(unittest.TestCase):
    def test_can_migrate_one_question_without_touching_project_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = migrate_legacy_enem(
                output_root=root,
                only=["ENEM-2021-MT-11"],
                status="draft",
            )
            self.assertEqual(result["created"], ["ENEM-2021-MT-11"])
            self.assertTrue((root / "enem" / "ENEM-2021-MT-11" / "manifest.yaml").exists())

            registry = Registry(root, database_path=None).rebuild()
            q = registry.get("ENEM-2021-MT-11")
            self.assertEqual(q.manifest["question"]["answer"], "D")
            self.assertEqual(q.manifest["solution"]["final_answer"], "D")
            self.assertEqual(q.manifest["status"], "draft")

    def test_migrated_question_contains_narration_segments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            migrate_legacy_enem(
                output_root=root,
                only=["ENEM-2021-MT-11"],
            )
            registry = Registry(root, database_path=None).rebuild()
            segments = registry.get("ENEM-2021-MT-11").manifest["narration"]["segments"]
            self.assertTrue(any(s["key"] == "source" for s in segments))
            self.assertTrue(any(s["key"] == "answer" for s in segments))


if __name__ == "__main__":
    unittest.main()
