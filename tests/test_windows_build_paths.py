from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import _short_build_dir
from mathinmovement.registry import Registry


class WindowsBuildPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_long_demo_ids_get_short_deterministic_build_paths(self):
        record = self.registry.get("relacoes-metricas-triangulo-retangulo")
        path = _short_build_dir(
            record,
            engine="compatibility",
            video_format="vertical",
            quality="draft",
        )
        self.assertEqual(path.parts[-4], "c")
        self.assertEqual(path.parts[-2:], ("v", "d"))
        self.assertLessEqual(len(path.parts[-3]), 10)
        self.assertNotIn(record.id, str(path))

    def test_native_and_compatibility_paths_do_not_collide(self):
        record = self.registry.get("razoes-trigonometricas-semelhanca")
        native = _short_build_dir(
            record,
            engine="native",
            video_format="vertical",
            quality="draft",
        )
        legacy = _short_build_dir(
            record,
            engine="compatibility",
            video_format="vertical",
            quality="draft",
        )
        self.assertNotEqual(native, legacy)


if __name__ == "__main__":
    unittest.main()
