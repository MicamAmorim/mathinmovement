from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import _short_build_dir
from mathinmovement.registry import Registry


class WindowsBuildPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = Registry().rebuild().get(
            "relacoes-metricas-triangulo-retangulo"
        )

    def test_build_path_is_short_and_deterministic(self):
        first = _short_build_dir(
            self.record,
            engine="native",
            video_format="vertical",
            quality="draft",
        )
        second = _short_build_dir(
            self.record,
            engine="native",
            video_format="vertical",
            quality="draft",
        )
        self.assertEqual(first, second)
        self.assertIn(".mim_build", first.parts)
        self.assertLess(len(str(first)), 180)

    def test_format_and_quality_paths_do_not_collide(self):
        vertical = _short_build_dir(
            self.record,
            engine="native",
            video_format="vertical",
            quality="draft",
        )
        horizontal = _short_build_dir(
            self.record,
            engine="native",
            video_format="horizontal",
            quality="final",
        )
        self.assertNotEqual(vertical, horizontal)


if __name__ == "__main__":
    unittest.main()
