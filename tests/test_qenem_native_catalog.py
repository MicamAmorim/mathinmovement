from __future__ import annotations

import unittest

from mathinmovement.registry import Registry
from mathinmovement.visuals.registry import (
    CONCEPT_RENDERERS,
    SOURCE_RENDERERS,
    concept_diagram,
    source_figure,
)


class QENEMNativeCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()
        cls.records = [r for r in cls.registry.all() if r.type == "qenem"]

    def test_all_thirty_qenem_are_native_production(self):
        self.assertEqual(len(self.records), 30)
        for record in self.records:
            render = record.manifest["render"]
            self.assertEqual(record.manifest["status"], "production", record.id)
            self.assertEqual(render["production_engine"], "native", record.id)
            self.assertTrue(render["native_ready"], record.id)
            self.assertEqual(
                render["native_formats"],
                ["vertical", "horizontal"],
                record.id,
            )

    def test_every_declared_visual_renderer_is_supported(self):
        for record in self.records:
            visuals = record.manifest.get("visuals") or {}
            statement = visuals.get("statement") or {}
            concept = visuals.get("concept") or {}

            if statement:
                renderer = str(statement["renderer"])
                self.assertIn(renderer, SOURCE_RENDERERS, record.id)
                figure = source_figure(renderer)
                self.assertGreater(len(figure), 0, record.id)

            if concept:
                renderer = str(concept["renderer"])
                self.assertIn(renderer, CONCEPT_RENDERERS, record.id)
                figure = concept_diagram(renderer)
                self.assertGreater(len(figure), 0, record.id)

    def test_ferris_question_keeps_graphical_alternatives_contract(self):
        record = self.registry.get("ENEM-2023-MT-29")
        self.assertEqual(
            record.manifest["visuals"]["statement"]["renderer"],
            "ferris_choices",
        )


if __name__ == "__main__":
    unittest.main()
