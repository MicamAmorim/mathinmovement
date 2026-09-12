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

    def test_demo_and_qenem_use_same_registry(self):
        self.assertEqual(self.registry.get("area-triangulo").type, "demo")
        self.assertEqual(self.registry.get("ENEM-2021-MT-11").type, "qenem")


if __name__ == "__main__":
    unittest.main()
