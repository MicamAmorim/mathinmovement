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
            self.assertGreaterEqual(stats["total"], 60)
            self.assertEqual(stats["by_status"].get("production"), 60)
            self.assertGreaterEqual(stats["by_type"].get("demo", 0), 30)
            self.assertGreaterEqual(stats["by_type"].get("qenem", 0), 30)

            # Regressão Windows: nenhuma conexão pode manter o arquivo aberto.
            db_path.unlink()
            self.assertFalse(db_path.exists())


if __name__ == "__main__":
    unittest.main()
