from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry


class RenderModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_production_uses_native_engine_and_media_root(self):
        for content_id in ("area-triangulo", "ENEM-2021-MT-11"):
            record = self.registry.get(content_id)
            self.assertEqual(
                record.manifest["render"]["production_engine"],
                "native",
            )
            output = render_record(record, dry_run=True)
            self.assertIn("media", output.parts)
            self.assertNotIn("media_native", output.parts)

    def test_explicit_native_uses_isolated_media_root(self):
        for content_id in ("area-triangulo", "ENEM-2021-MT-11"):
            record = self.registry.get(content_id)
            output = render_record(
                record,
                dry_run=True,
                render_engine="native",
            )
            self.assertIn("media_native", output.parts)

    def test_qenem_supports_both_approved_formats(self):
        record = self.registry.get("ENEM-2021-MT-11")
        for video_format in ("vertical", "horizontal"):
            output = render_record(
                record,
                dry_run=True,
                video_format=video_format,
            )
            self.assertIn("media", output.parts)


if __name__ == "__main__":
    unittest.main()
