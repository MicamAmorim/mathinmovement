from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry
from mathinmovement.visuals.registry import concept_diagram, source_figure


CANDIDATES = {
    "ENEM-2021-MT-12": {
        "statement": "cup_frustum",
        "concept": "cone_frustum",
    },
    "ENEM-2021-MT-13": {
        "concept": "shape_areas",
    },
    "ENEM-2021-MT-17": {
        "concept": "box",
    },
    "ENEM-2021-MT-18": {
        "concept": "cylinder",
    },
    "ENEM-2021-MT-28": {
        "statement": "castle_scale",
        "concept": "scale",
    },
}


class QENEMBatch0206CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_batch_is_native_ready_but_not_promoted(self):
        for content_id in CANDIDATES:
            record = self.registry.get(content_id)
            render = record.manifest["render"]
            self.assertEqual(record.manifest["status"], "draft")
            self.assertEqual(render["production_engine"], "compatibility")
            self.assertTrue(render["native_ready"])
            self.assertEqual(
                render["native_formats"],
                ["vertical", "horizontal"],
            )

    def test_batch_supports_native_and_legacy_dry_runs_both_formats(self):
        for content_id in CANDIDATES:
            record = self.registry.get(content_id)
            for video_format in ("vertical", "horizontal"):
                native = render_record(
                    record,
                    dry_run=True,
                    render_engine="native",
                    video_format=video_format,
                )
                legacy = render_record(
                    record,
                    dry_run=True,
                    render_engine="compatibility",
                    video_format=video_format,
                )
                self.assertIn("media_native", native.parts)
                self.assertIn("media_compatibility", legacy.parts)

    def test_visual_catalog_entries_are_real_ported_diagrams(self):
        for content_id, visuals in CANDIDATES.items():
            with self.subTest(content_id=content_id):
                if "statement" in visuals:
                    fig = source_figure(visuals["statement"])
                    self.assertGreater(len(fig), 2)
                if "concept" in visuals:
                    fig = concept_diagram(visuals["concept"])
                    self.assertGreater(len(fig), 2)


if __name__ == "__main__":
    unittest.main()
