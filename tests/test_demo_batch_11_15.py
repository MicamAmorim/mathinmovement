from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry


CANDIDATES = {
    "area-coroa-circular": "annulus_subtraction_v1",
    "teorema-pitagoras": "pythagoras_four_triangles_v1",
    "relacoes-metricas-triangulo-retangulo": "right_triangle_metric_relations_v1",
    "razoes-trigonometricas-semelhanca": "trig_similarity_ratios_v1",
    "lei-senos": "law_of_sines_altitudes_v1",
}


class DemoBatch1115PromotedTests(unittest.TestCase):
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
