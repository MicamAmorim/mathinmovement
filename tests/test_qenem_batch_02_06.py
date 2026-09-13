from __future__ import annotations

import unittest

from manim import Text

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry
from mathinmovement.visuals.registry import concept_diagram, source_figure


CANDIDATES = {
    "ENEM-2021-MT-12": {
        "statement": "cup_frustum",
        "concept": "cone_frustum",
    },
    "ENEM-2021-MT-13": {"concept": "shape_areas"},
    "ENEM-2021-MT-17": {"concept": "box"},
    "ENEM-2021-MT-18": {"concept": "cylinder"},
    "ENEM-2021-MT-28": {
        "statement": "castle_scale",
        "concept": "scale",
    },
    "ENEM-2022-MT-07": {"concept": "cylinder_compare"},
    "ENEM-2022-MT-10": {
        "statement": "roads",
        "concept": "reflection",
    },
    "ENEM-2022-MT-12": {"concept": "sphere_scale"},
    "ENEM-2022-MT-13": {
        "statement": "cone_dims",
        "concept": "cone",
    },
    "ENEM-2022-MT-25": {"concept": "scale"},
}


class QENEMBatch0211PromotedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_batch_has_exactly_ten_items(self):
        self.assertEqual(len(CANDIDATES), 10)

    def test_batch_prefers_dsl_production_with_native_fallback(self):
        for content_id in CANDIDATES:
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(
                record.manifest["status"],
                "production",
            )
            self.assertEqual(
                render["production_engine"],
                "dsl",
            )
            self.assertTrue(render["native_ready"])
            self.assertEqual(record.manifest["dsl_shadow"]["approved_formats"], ["vertical"])
            self.assertNotIn("compatibility", render)

    def test_batch_supports_production_and_native_dry_runs(self):
        for content_id in CANDIDATES:
            record = self.registry.get(content_id)
            for video_format in ("vertical", "horizontal"):
                production = render_record(
                    record,
                    dry_run=True,
                    render_engine="production",
                    video_format=video_format,
                )
                native = render_record(
                    record,
                    dry_run=True,
                    render_engine="native",
                    video_format=video_format,
                )
                self.assertIn("media", production.parts)
                self.assertIn("media_native", native.parts)

    def test_visual_catalog_entries_are_ported_not_fallbacks(self):
        for content_id, visuals in CANDIDATES.items():
            with self.subTest(content_id=content_id):
                if "statement" in visuals:
                    fig = source_figure(visuals["statement"])
                    self.assertFalse(
                        any(isinstance(x, Text) for x in fig)
                    )
                if "concept" in visuals:
                    fig = concept_diagram(visuals["concept"])
                    self.assertFalse(
                        any(isinstance(x, Text) for x in fig)
                    )


if __name__ == "__main__":
    unittest.main()
