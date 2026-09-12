from __future__ import annotations

import unittest

from mathinmovement.dsl.errors import DSLError
from mathinmovement.dsl.runtime import validate_program


class DSLLatexEscapeTests(unittest.TestCase):
    def test_single_latex_control_escape_is_valid(self):
        slash = chr(92)
        program = {
            "dsl_version": "1.0",
            "objects": [],
            "timeline": [
                {
                    "op": "equation",
                    "tex": f"1{slash}cdot{slash}frac{{{slash}ell a}}{{2}}",
                }
            ],
        }
        validate_program(program)

    def test_doubled_escape_before_control_word_is_rejected(self):
        doubled = chr(92) * 2
        program = {
            "dsl_version": "1.0",
            "objects": [],
            "timeline": [
                {
                    "op": "equation",
                    "tex": f"1{doubled}cdot{doubled}frac{{a}}{{2}}",
                }
            ],
        }
        with self.assertRaises(DSLError):
            validate_program(program)


if __name__ == "__main__":
    unittest.main()
