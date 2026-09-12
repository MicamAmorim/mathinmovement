from __future__ import annotations

import ast
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
        tree = ast.parse(source)

        imported_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                # Relative imports inside mathinmovement are expected. We only
                # reject direct imports from the legacy top-level packages.
                if node.level == 0 and node.module:
                    imported_modules.add(node.module)

        forbidden_roots = {"common", "specs", "enem", "videos"}
        offenders = sorted(
            module
            for module in imported_modules
            if module.split(".", 1)[0] in forbidden_roots
        )
        self.assertEqual(
            offenders,
            [],
            f"Engine nativo ainda importa módulos legados: {offenders}",
        )


if __name__ == "__main__":
    unittest.main()
