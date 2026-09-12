from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.registry import Registry


class RenderModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_demo_production_now_uses_native_engine(self):
        record = self.registry.get("area-triangulo")
        self.assertEqual(record.manifest["render"]["production_engine"], "native")
        output = render_record(record, dry_run=True)
        self.assertIn("media", output.parts)
        self.assertNotIn("media_native", output.parts)

    def test_demo_native_isolated_when_explicitly_requested(self):
        record = self.registry.get("area-triangulo")
        output = render_record(record, dry_run=True, render_engine="native")
        self.assertIn("media_native", output.parts)

    def test_demo_horizontal_is_available_in_native_production(self):
        record = self.registry.get("area-triangulo")
        output = render_record(
            record,
            dry_run=True,
            video_format="horizontal",
        )
        self.assertIn("media", output.parts)
        explicit = render_record(
            record,
            dry_run=True,
            video_format="horizontal",
            render_engine="native",
        )
        self.assertIn("media_native", explicit.parts)

    def test_demo_legacy_reference_remains_available_vertical_only(self):
        record = self.registry.get("area-triangulo")
        output = render_record(
            record,
            dry_run=True,
            render_engine="compatibility",
        )
        self.assertIn("media_compatibility", output.parts)

    def test_qenem_production_now_uses_native_both_formats(self):
        record = self.registry.get("ENEM-2021-MT-11")
        self.assertEqual(record.manifest["render"]["production_engine"], "native")
        for video_format in ("vertical", "horizontal"):
            output = render_record(
                record,
                dry_run=True,
                video_format=video_format,
            )
            self.assertIn("media", output.parts)

    def test_qenem_legacy_reference_remains_available(self):
        record = self.registry.get("ENEM-2021-MT-11")
        for video_format in ("vertical", "horizontal"):
            output = render_record(
                record,
                dry_run=True,
                video_format=video_format,
                render_engine="compatibility",
            )
            self.assertIn("media_compatibility", output.parts)


if __name__ == "__main__":
    unittest.main()
