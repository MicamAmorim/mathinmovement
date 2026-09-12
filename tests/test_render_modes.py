from __future__ import annotations

import unittest

from mathinmovement.engine.renderer import render_record
from mathinmovement.models import ManifestError
from mathinmovement.registry import Registry


class RenderModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_demo_production_uses_compatibility_output(self):
        record = self.registry.get("area-triangulo")
        output = render_record(record, dry_run=True)
        self.assertIn("media", output.parts)
        self.assertNotIn("media_native", output.parts)

    def test_demo_native_isolated_from_production_output(self):
        record = self.registry.get("area-triangulo")
        output = render_record(record, dry_run=True, render_engine="native")
        self.assertIn("media_native", output.parts)

    def test_demo_horizontal_requires_native_until_parity_is_approved(self):
        record = self.registry.get("area-triangulo")
        with self.assertRaises(ManifestError):
            render_record(record, dry_run=True, video_format="horizontal")
        output = render_record(
            record,
            dry_run=True,
            video_format="horizontal",
            render_engine="native",
        )
        self.assertIn("media_native", output.parts)

    def test_qenem_production_supports_both_formats_via_compatibility(self):
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
