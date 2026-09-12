from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry


CANDIDATES = {
    "area-paralelogramo": "area_parallelogram_cut_v1",
    "area-trapezio": "area_trapezoid_double_v1",
    "area-losango": "area_rhombus_rearrange_v1",
    "area-triangulo-equilatero": "area_equilateral_height_v1",
}


class DemoNativeCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_candidates_are_native_ready_but_not_promoted(self):
        for content_id, renderer in CANDIDATES.items():
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(record.manifest["status"], "draft")
            self.assertEqual(render["production_engine"], "compatibility")
            self.assertTrue(render["native_ready"])
            self.assertEqual(render["native_formats"], ["vertical"])
            self.assertEqual(render["native_renderer"], renderer)

    def test_candidates_support_native_dry_run(self):
        for content_id in CANDIDATES:
            record = self.registry.get(content_id)
            output = render_record(
                record,
                dry_run=True,
                render_engine="native",
                video_format="vertical",
            )
            self.assertIn("media_native", output.parts)

    def test_candidates_keep_legacy_reference_for_parity(self):
        for content_id in CANDIDATES:
            record = self.registry.get(content_id)
            output = render_record(
                record,
                dry_run=True,
                render_engine="compatibility",
                video_format="vertical",
            )
            self.assertIn("media_compatibility", output.parts)


if __name__ == "__main__":
    unittest.main()
