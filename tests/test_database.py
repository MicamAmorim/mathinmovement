from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mathinmovement.database import database_stats
from mathinmovement.registry import Registry


class DatabaseTests(unittest.TestCase):
    def test_registry_can_build_reconstructable_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "registry.sqlite"
            registry = Registry(database_path=db_path).rebuild()
            stats = database_stats(db_path)
            self.assertTrue(stats["exists"])
            self.assertEqual(stats["total"], len(registry))
            self.assertEqual(stats["by_type"].get("demo"), 1)
            self.assertEqual(stats["by_type"].get("qenem"), 1)


if __name__ == "__main__":
    unittest.main()
