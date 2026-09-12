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


class DemoBatch1620CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_batch_is_native_ready_but_not_promoted(self):
        for content_id, renderer in CANDIDATES.items():
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(record.manifest["status"], "draft")
            self.assertEqual(render["production_engine"], "compatibility")
            self.assertTrue(render["native_ready"])
            self.assertEqual(render["native_formats"], ["vertical"])
            self.assertEqual(render["native_renderer"], renderer)

    def test_batch_supports_native_and_legacy_dry_runs(self):
        for content_id in CANDIDATES:
            record = self.registry.get(content_id)
            native = render_record(
                record,
                dry_run=True,
                render_engine="native",
                video_format="vertical",
            )
            legacy = render_record(
                record,
                dry_run=True,
                render_engine="compatibility",
                video_format="vertical",
            )
            self.assertIn("media_native", native.parts)
            self.assertIn("media_compatibility", legacy.parts)

    def test_scale_equations_keep_prime_notation(self):
        record = self.registry.get("escalas-comprimentos-areas-volumes")
        steps = record.manifest["lesson"]["steps"]
        self.assertEqual(steps[1]["math"], "A'=(2L)^2=4L^2=2^2A")
        self.assertEqual(steps[3]["math"], "V'=2\\cdot2\\cdot2\\,V=8V")
        self.assertEqual(steps[4]["math"], "V'=(kL)^3=k^3V")


if __name__ == "__main__":
    unittest.main()
