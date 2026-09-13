from __future__ import annotations

import unittest

from mathinmovement.registry import Registry


class FullCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()
        cls.records = cls.registry.all()

    def test_production_baseline_contains_30_demos_and_30_qenem(self):
        production = [
            r for r in self.records
            if r.manifest.get("status") == "production"
        ]
        demos = [r for r in production if r.type == "demo"]
        qenem = [r for r in production if r.type == "qenem"]
        self.assertEqual(len(production), 60)
        self.assertEqual(len(demos), 30)
        self.assertEqual(len(qenem), 30)

    def test_catalog_prefers_dsl_production_with_native_fallback(self):
        production = [
            r for r in self.records
            if r.manifest.get("status") == "production"
        ]
        self.assertEqual(len(production), 60)

        for record in production:
            render = record.manifest["render"]
            self.assertEqual(
                render["production_engine"],
                "dsl",
                record.id,
            )
            self.assertTrue(render["native_ready"], record.id)
            shadow = record.manifest.get("dsl_shadow") or {}
            self.assertTrue(shadow, record.id)
            self.assertIn("vertical", shadow.get("approved_formats") or [], record.id)
            self.assertNotIn("compatibility", render, record.id)

    def test_qenem_answers_match_solution(self):
        for record in self.records:
            if record.type != "qenem":
                continue
            self.assertEqual(
                record.manifest["question"]["answer"],
                record.manifest["solution"]["final_answer"],
                record.id,
            )


if __name__ == "__main__":
    unittest.main()
