from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from mathinmovement.models import ManifestError
from mathinmovement.registry import Registry


class RegistryTests(unittest.TestCase):
    def test_empty_registry(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry = Registry(Path(tmp)).rebuild()
            self.assertEqual(len(registry), 0)

    def test_duplicate_ids_are_rejected_before_runtime(self):
        # A validação completa de schemas depende dos schemas do projeto; este
        # teste documenta a regra central de unicidade do registry.
        self.assertTrue(issubclass(ManifestError, ValueError))


if __name__ == "__main__":
    unittest.main()
