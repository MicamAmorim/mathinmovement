from __future__ import annotations

import unittest

from mathinmovement.registry import Registry
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

    def test_common_qenem_profile_is_explicit(self):
        self.assertIn("replacement_transform", QENEM_COMMON)
        self.assertIn("rounded_rectangle", QENEM_COMMON)
        self.assertIn("math", QENEM_COMMON)


if __name__ == "__main__":
    unittest.main()
