from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry


CANDIDATES = {
    "lei-cossenos": "law_of_cosines_projection_v1",
    "area-triangulo-seno": "triangle_area_sine_v1",
    "escalas-comprimentos-areas-volumes": "scale_dimension_exponents_v1",
    "relacao-euler-poliedros": "euler_polyhedra_reduction_v1",
    "diagonal-paralelepipedo": "cuboid_space_diagonal_v1",
}


class DemoBatch1620PromotedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_batch_prefers_dsl_production_with_native_fallback(self):
        for content_id, renderer in CANDIDATES.items():
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(record.manifest["status"], "production")
            self.assertEqual(render["production_engine"], "dsl")
            self.assertTrue(render["native_ready"])
            self.assertEqual(render["native_formats"], ["vertical"])
            self.assertEqual(render["native_renderer"], renderer)
            self.assertEqual(record.manifest["dsl_shadow"]["approved_formats"], ["vertical"])

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
