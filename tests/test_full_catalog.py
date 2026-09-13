from __future__ import annotations

import unittest

from mathinmovement.registry import Registry


class FullCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()
        cls.records = cls.registry.all()

    def test_catalog_contains_exactly_30_demos_and_30_qenem(self):
        demos = [r for r in self.records if r.type == "demo"]
        qenem = [r for r in self.records if r.type == "qenem"]
        self.assertEqual(len(self.records), 60)
        self.assertEqual(len(demos), 30)
        self.assertEqual(len(qenem), 30)

    def test_catalog_prefers_dsl_production_with_native_fallback(self):
        production = [
            r for r in self.records
            if r.manifest.get("status") == "production"
        ]
        drafts = [
            r for r in self.records
            if r.manifest.get("status") == "draft"
        ]
        self.assertEqual(len(production), 60)
        self.assertEqual(drafts, [])

        for record in production:
            render = record.manifest["render"]
            self.assertEqual(
                render["production_engine"],
                "dsl",
                record.id,
            )
            self.assertTrue(render["native_ready"], record.id)
            self.assertTrue(record.manifest.get("dsl_shadow"), record.id)
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
