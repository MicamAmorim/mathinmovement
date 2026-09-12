from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]


class DSLVersionSchemaTests(unittest.TestCase):
    def _program_schema(self, filename: str, *, shadow: bool = False):
        schema = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
        if shadow:
            return schema["properties"]["dsl_shadow"]["properties"]["visual_program"]
        return schema["properties"]["visual_program"]

    def _program(self, version: str):
        return {
            "dsl_version": version,
            "objects": [],
            "timeline": [],
        }

    def test_version_1_0_is_accepted_by_demo_and_qenem_schemas(self):
        for filename in ("demo.schema.json", "qenem.schema.json"):
            for shadow in (False, True):
                with self.subTest(filename=filename, shadow=shadow):
                    validator = Draft202012Validator(
                        self._program_schema(filename, shadow=shadow)
                    )
                    validator.validate(self._program("1.0"))

    def test_version_1_12_is_accepted(self):
        validator = Draft202012Validator(
            self._program_schema("demo.schema.json", shadow=True)
        )
        validator.validate(self._program("1.12"))

    def test_major_version_2_is_rejected(self):
        validator = Draft202012Validator(
            self._program_schema("demo.schema.json", shadow=True)
        )
        with self.assertRaises(ValidationError):
            validator.validate(self._program("2.0"))


if __name__ == "__main__":
    unittest.main()
