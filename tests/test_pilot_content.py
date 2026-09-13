from __future__ import annotations

import unittest

from mathinmovement.registry import Registry


class PilotContentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_two_pilots_are_registered(self):
        ids = {record.id for record in self.registry.all()}
        self.assertIn("area-triangulo", ids)
        self.assertIn("ENEM-2021-MT-11", ids)

    def test_qenem_keeps_corrected_answer(self):
        q = self.registry.get("ENEM-2021-MT-11")
        self.assertEqual(q.manifest["question"]["answer"], "D")
        self.assertEqual(q.manifest["solution"]["final_answer"], "D")
        self.assertIn("8 cm", q.manifest["question"]["stem"])

    def test_pilots_prefer_dsl_with_unified_native_fallback(self):
        for content_id in ("area-triangulo", "ENEM-2021-MT-11"):
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(render["production_engine"], "dsl")
            self.assertEqual(render["native_engine"], "unified-v2")
            self.assertEqual(record.manifest["dsl_shadow"]["approved_formats"], ["vertical"])
            self.assertNotIn("compatibility", render)

    def test_native_format_policy(self):
        demo = self.registry.get("area-triangulo").manifest["render"]
        qenem = self.registry.get("ENEM-2021-MT-11").manifest["render"]
        self.assertIn("vertical", demo["native_formats"])
        self.assertIn("horizontal", demo["native_formats"])
        self.assertIn("vertical", qenem["native_formats"])
        self.assertIn("horizontal", qenem["native_formats"])


if __name__ == "__main__":
    unittest.main()
