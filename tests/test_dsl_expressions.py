from __future__ import annotations

import unittest

from mathinmovement.dsl.errors import DSLError
from mathinmovement.dsl.expressions import eval_expression, resolve_value


class DSLExpressionTests(unittest.TestCase):
    def test_safe_math_and_tracker_variable(self):
        value = eval_expression("2*cos(t)+sqrt(4)", {"t": 0.0})
        self.assertAlmostEqual(value, 4.0)

    def test_recursive_resolution(self):
        self.assertEqual(resolve_value(["=t", "=t+1"], {"t": 2.0}), [2.0, 3.0])

    def test_attribute_access_is_rejected(self):
        with self.assertRaises(DSLError):
            eval_expression("(1).__class__", {})

    def test_import_is_impossible(self):
        with self.assertRaises(DSLError):
            eval_expression("__import__('os')", {})


if __name__ == "__main__":
    unittest.main()
