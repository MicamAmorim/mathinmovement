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

    def test_validated_pilots_use_native_production_and_keep_legacy_reference(self):
        for content_id in ("area-triangulo", "ENEM-2021-MT-11"):
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(render["production_engine"], "native")
            self.assertEqual(render["native_engine"], "unified-v2")
            self.assertIn("compatibility", render)

    def test_native_format_policy_matches_reference_coverage(self):
        demo = self.registry.get("area-triangulo").manifest["render"]
        qenem = self.registry.get("ENEM-2021-MT-11").manifest["render"]
        self.assertIn("vertical", demo["native_formats"])
        self.assertIn("horizontal", demo["native_formats"])
        self.assertIn("vertical", qenem["native_formats"])
        self.assertIn("horizontal", qenem["native_formats"])


if __name__ == "__main__":
    unittest.main()
