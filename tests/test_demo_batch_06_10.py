from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry


CANDIDATES = {
    "area-poligonos-regulares": "regular_polygon_apothem_v1",
    "comprimento-circunferencia-pi": "circumference_roll_pi_v1",
    "area-circulo": "circle_sector_rearrange_v1",
    "comprimento-arco": "arc_fraction_v1",
    "area-setor-circular": "sector_fraction_v1",
}


class DemoBatch0610PromotedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_batch_is_native_production(self):
        for content_id, renderer in CANDIDATES.items():
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(record.manifest["status"], "production")
            self.assertEqual(render["production_engine"], "native")
            self.assertTrue(render["native_ready"])
            self.assertEqual(render["native_formats"], ["vertical"])
            self.assertEqual(render["native_renderer"], renderer)

    def test_batch_supports_production_and_explicit_native_dry_runs(self):
        for content_id in CANDIDATES:
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
