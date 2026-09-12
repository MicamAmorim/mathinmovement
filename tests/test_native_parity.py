from __future__ import annotations

from pathlib import Path
import unittest

from mathinmovement.registry import Registry


class NativeParityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_demo_manifest_preserves_approved_identity_and_copy(self):
        demo = self.registry.get("area-triangulo").manifest
        presentation = demo["presentation"]
        self.assertEqual(presentation["profile"], "motion_math_v1")
        self.assertEqual(presentation["number"], "01")
        self.assertEqual(presentation["category"], "ÁREAS")
        self.assertEqual(presentation["signature"], "MIQUÉIAS AMORIM")
        self.assertEqual(
            presentation["captions"]["base_height"],
            "Uma base. Uma altura perpendicular.",
        )
        self.assertEqual(
            presentation["captions"]["duplicate"],
            "Duas cópias iguais completam um paralelogramo.",
        )

    def test_qenem_manifest_preserves_approved_visual_copy(self):
        q = self.registry.get("ENEM-2021-MT-11").manifest
        self.assertIn("h = 8 cm", q["visuals"]["statement"]["description"])
        self.assertIn("30°–60°–90°", q["visuals"]["concept"]["note"])

    def test_native_scene_has_no_legacy_runtime_imports(self):
        import mathinmovement.engine.scene as scene_module

        source = Path(scene_module.__file__).read_text(encoding="utf-8")
        forbidden = [
            "from common import",
            "from specs import",
            "enem.common",
            "enem.visuals",
            "questions.json",
        ]
        for marker in forbidden:
            self.assertNotIn(marker, source)


if __name__ == "__main__":
    unittest.main()
