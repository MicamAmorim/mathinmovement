from __future__ import annotations

import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("manim") is not None, "Manim não instalado")
class RenderImportTests(unittest.TestCase):
    def test_visual_registry_imports_with_installed_manim(self):
        from mathinmovement.visuals import build_visual, run_demo_action

        self.assertTrue(callable(build_visual))
        self.assertTrue(callable(run_demo_action))

    def test_unified_scene_imports_with_installed_manim(self):
        from mathinmovement.engine.scene import UnifiedContentScene

        self.assertIsNotNone(UnifiedContentScene)


if __name__ == "__main__":
    unittest.main()
