from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry


PROMOTED = {
    "area-paralelogramo": "area_parallelogram_cut_v1",
    "area-trapezio": "area_trapezoid_double_v1",
    "area-losango": "area_rhombus_rearrange_v1",
    "area-triangulo-equilatero": "area_equilateral_height_v1",
}


class DemoNativePromotedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_validated_demos_are_native_production(self):
        for content_id, renderer in PROMOTED.items():
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(record.manifest["status"], "production")
            self.assertEqual(render["production_engine"], "native")
            self.assertTrue(render["native_ready"])
            self.assertEqual(render["native_formats"], ["vertical"])
            self.assertEqual(render["native_renderer"], renderer)

    def test_production_routes_to_native(self):
        for content_id in PROMOTED:
            record = self.registry.get(content_id)
            output = render_record(
                record,
                dry_run=True,
                video_format="vertical",
            )
            self.assertIn("media", output.parts)

    def test_batch_supports_production_and_explicit_native_dry_runs(self):
        for content_id in PROMOTED:
            record = self.registry.get(content_id)
            production = render_record(
                record,
                dry_run=True,
                render_engine="production",
                video_format="vertical",
            )
            native = render_record(
                record,
                dry_run=True,
                render_engine="native",
                video_format="vertical",
            )
            self.assertIn("media", production.parts)
            self.assertIn("media_native", native.parts)


if __name__ == "__main__":
    unittest.main()
