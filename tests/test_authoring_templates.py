from __future__ import annotations

from pathlib import Path
import unittest

from mathinmovement.dsl.runtime import validate_program
from mathinmovement.registry import load_manifest, validate_manifest


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = (
    ROOT / "examples" / "templates" / "demo-minimal" / "manifest.yaml",
    ROOT / "examples" / "templates" / "demo-complete" / "manifest.yaml",
    ROOT / "examples" / "templates" / "qenem-minimal" / "manifest.yaml",
    ROOT / "examples" / "templates" / "qenem-complete" / "manifest.yaml",
)


class AuthoringTemplateTests(unittest.TestCase):
    def test_templates_validate_against_schema_and_dsl(self):
        for path in TEMPLATES:
            with self.subTest(template=path.parent.name):
                manifest = load_manifest(path)
                validate_manifest(manifest, source=path)

                self.assertEqual(manifest["status"], "draft")
                self.assertEqual(
                    manifest["render"]["production_engine"],
                    "dsl",
                )
                self.assertEqual(
                    manifest["render"]["formats"],
                    ["vertical"],
                )
                self.assertNotIn("dsl_shadow", manifest)

                if manifest["type"] == "demo":
                    validate_program(manifest["visual_program"])
                else:
                    programs = 0
                    for spec in (manifest.get("visuals") or {}).values():
                        if isinstance(spec, dict) and spec.get("program"):
                            validate_program(spec["program"])
                            programs += 1
                    self.assertGreater(programs, 0)

    def test_qenem_templates_keep_answer_contract(self):
        for path in TEMPLATES:
            manifest = load_manifest(path)
            if manifest["type"] != "qenem":
                continue
            self.assertEqual(
                manifest["question"]["answer"],
                manifest["solution"]["final_answer"],
            )


if __name__ == "__main__":
    unittest.main()
