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

    def test_pilots_use_unified_engine(self):
        for content_id in ("area-triangulo", "ENEM-2021-MT-11"):
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(render["engine"], "unified-v2")
            self.assertNotIn("adapter", render)

    def test_both_pilots_support_horizontal(self):
        for content_id in ("area-triangulo", "ENEM-2021-MT-11"):
            record = self.registry.get(content_id)
            self.assertIn("horizontal", record.manifest["render"]["formats"])


if __name__ == "__main__":
    unittest.main()
