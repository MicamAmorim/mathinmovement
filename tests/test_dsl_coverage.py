from __future__ import annotations

import unittest

from mathinmovement.registry import Registry
from mathinmovement.dsl.runtime import validate_program
from mathinmovement.dsl.coverage import (
    DEMO_USAGE,
    DEMO_VALIDATION_SET,
    QENEM_COMMON,
    QENEM_USAGE,
    QENEM_VALIDATION_SET,
    covered_by,
    minimum_cover,
    universe,
)


class DSLCoverageTests(unittest.TestCase):
    def test_demo_validation_set_is_exact_minimum_cover(self):
        result = minimum_cover(DEMO_USAGE)
        self.assertEqual(len(result.selected), 8)
        self.assertEqual(
            covered_by(DEMO_USAGE, DEMO_VALIDATION_SET),
            universe(DEMO_USAGE),
        )

    def test_qenem_validation_set_is_exact_minimum_cover(self):
        result = minimum_cover(QENEM_USAGE)
        self.assertEqual(len(result.selected), 6)
        self.assertEqual(
            covered_by(QENEM_USAGE, QENEM_VALIDATION_SET),
            universe(QENEM_USAGE),
        )

    def test_validation_videos_exist_in_production_catalog(self):
        registry = Registry().rebuild()
        for content_id in DEMO_VALIDATION_SET + QENEM_VALIDATION_SET:
            with self.subTest(content_id=content_id):
                record = registry.get(content_id)
                self.assertEqual(record.manifest.get("status"), "production")
                self.assertEqual(
                    record.manifest["render"]["production_engine"],
                    "native",
                )
                self.assertIn("dsl_shadow", record.manifest)

    def test_all_minimum_cover_shadow_programs_validate(self):
        registry = Registry().rebuild()
        for content_id in DEMO_VALIDATION_SET:
            with self.subTest(content_id=content_id):
                record = registry.get(content_id)
                validate_program(
                    record.manifest["dsl_shadow"]["visual_program"]
                )
        for content_id in QENEM_VALIDATION_SET:
            record = registry.get(content_id)
            visuals = record.manifest["dsl_shadow"]["visuals"]
            for name, spec in visuals.items():
                with self.subTest(content_id=content_id, visual=name):
                    validate_program(spec["program"])

    def test_every_demo_has_valid_shadow_program(self):
        registry = Registry().rebuild()
        demos = registry.find(content_type="demo")
        self.assertEqual(len(demos), 30)
        for record in demos:
            with self.subTest(content_id=record.id):
                shadow = record.manifest.get("dsl_shadow") or {}
                self.assertIn("visual_program", shadow)
                validate_program(shadow["visual_program"])

    def test_every_shadow_program_in_catalog_validates(self):
        registry = Registry().rebuild()
        count = 0
        for record in registry.all():
            shadow = record.manifest.get("dsl_shadow") or {}
            if shadow.get("visual_program"):
                validate_program(shadow["visual_program"])
                count += 1
            for name, spec in (shadow.get("visuals") or {}).items():
                if isinstance(spec, dict) and spec.get("program"):
                    with self.subTest(content_id=record.id, visual=name):
                        validate_program(spec["program"])
                    count += 1
        self.assertGreaterEqual(count, 27)

    def test_qenem_shadow_migration_has_reached_twelve_items(self):
        registry = Registry().rebuild()
        qenem = registry.find(content_type="qenem")
        migrated = [
            record
            for record in qenem
            if (record.manifest.get("dsl_shadow") or {}).get("visuals")
        ]
        self.assertGreaterEqual(len(migrated), 12)

    def test_common_qenem_profile_is_explicit(self):
        self.assertIn("replacement_transform", QENEM_COMMON)
        self.assertIn("rounded_rectangle", QENEM_COMMON)
        self.assertIn("math", QENEM_COMMON)


if __name__ == "__main__":
    unittest.main()
