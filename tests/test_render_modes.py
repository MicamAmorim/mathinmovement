from __future__ import annotations

import unittest
from pathlib import Path

from mathinmovement.engine.renderer import _resolve_engine, render_record
from mathinmovement.models import ContentRecord
from mathinmovement.registry import Registry


class RenderModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = Registry().rebuild()

    def test_production_prefers_dsl_and_uses_media_root(self):
        for content_id in ("area-triangulo", "ENEM-2021-MT-11"):
            record = self.registry.get(content_id)
            self.assertEqual(
                record.manifest["render"]["production_engine"],
                "dsl",
            )
            output = render_record(record, dry_run=True)
            self.assertIn("media", output.parts)
            self.assertNotIn("media_dsl", output.parts)

    def test_production_falls_back_to_native_for_unapproved_dsl_format(self):
        record = self.registry.get("area-triangulo")
        self.assertEqual(record.manifest["dsl_shadow"]["formats"], ["vertical"])
        output = render_record(
            record,
            dry_run=True,
            video_format="horizontal",
        )
        self.assertIn("media", output.parts)
        self.assertNotIn("media_native", output.parts)

    def test_production_engine_resolution_is_format_aware(self):
        demo = self.registry.get("area-triangulo")
        qenem = self.registry.get("ENEM-2021-MT-11")

        self.assertEqual(
            _resolve_engine(demo, "production", video_format="vertical"),
            ("dsl", "media"),
        )
        self.assertEqual(
            _resolve_engine(demo, "production", video_format="horizontal"),
            ("native", "media"),
        )
        self.assertEqual(
            _resolve_engine(qenem, "production", video_format="horizontal"),
            ("native", "media"),
        )

    def test_canonical_demo_dsl_needs_no_shadow_block(self):
        record = ContentRecord(
            id="demo-canonical",
            type="demo",
            title="Demo canônica",
            path=Path("."),
            manifest={
                "render": {
                    "production_engine": "dsl",
                    "formats": ["vertical"],
                },
                "visual_program": {
                    "dsl_version": "1.0",
                    "objects": [],
                    "timeline": [],
                },
            },
        )
        self.assertEqual(
            _resolve_engine(
                record,
                "production",
                video_format="vertical",
            ),
            ("dsl", "media"),
        )
        output = render_record(
            record,
            dry_run=True,
            render_engine="dsl",
        )
        self.assertIn("media_dsl", output.parts)

    def test_canonical_qenem_visual_program_needs_no_shadow_block(self):
        record = ContentRecord(
            id="qenem-canonical",
            type="qenem",
            title="qENEM canônica",
            path=Path("."),
            manifest={
                "render": {
                    "production_engine": "dsl",
                    "formats": ["vertical"],
                },
                "visuals": {
                    "concept": {
                        "program": {
                            "dsl_version": "1.0",
                            "objects": [],
                            "timeline": [],
                        }
                    }
                },
            },
        )
        self.assertEqual(
            _resolve_engine(
                record,
                "production",
                video_format="vertical",
            ),
            ("dsl", "media"),
        )

    def test_explicit_native_uses_isolated_media_root(self):
        for content_id in ("area-triangulo", "ENEM-2021-MT-11"):
            record = self.registry.get(content_id)
            output = render_record(
                record,
                dry_run=True,
                render_engine="native",
            )
            self.assertIn("media_native", output.parts)

    def test_dsl_shadow_uses_isolated_media_root(self):
        record = self.registry.get("area-triangulo")
        # O catálogo de produção só passa a exigir shadow quando o port existe.
        record.manifest["dsl_shadow"] = {
            "formats": ["vertical"],
            "visual_program": {
                "dsl_version": "1.0",
                "objects": [],
                "timeline": [],
            },
        }
        output = render_record(
            record,
            dry_run=True,
            render_engine="dsl",
        )
        self.assertIn("media_dsl", output.parts)

    def test_catalog_shadow_ports_use_media_dsl(self):
        for content_id in (
            "area-triangulo",
            "area-losango",
            "comprimento-circunferencia-pi",
            "relacoes-metricas-triangulo-retangulo",
            "area-prismas-planificacao",
            "volume-prismas",
            "volume-piramide",
            "area-cone",
            "ENEM-2021-MT-11",
            "ENEM-2023-MT-06",
            "ENEM-2023-MT-07",
            "ENEM-2023-MT-29",
            "ENEM-2023-MT-44",
            "ENEM-2024-MT-30",
        ):
            with self.subTest(content_id=content_id):
                record = self.registry.get(content_id)
                output = render_record(
                    record,
                    dry_run=True,
                    render_engine="dsl",
                )
                self.assertIn("media_dsl", output.parts)

    def test_qenem_supports_both_dsl_formats_but_only_vertical_is_promoted(self):
        record = self.registry.get("ENEM-2021-MT-11")
        self.assertEqual(
            record.manifest["dsl_shadow"]["formats"],
            ["vertical", "horizontal"],
        )
        self.assertEqual(
            record.manifest["dsl_shadow"]["approved_formats"],
            ["vertical"],
        )
        for video_format in ("vertical", "horizontal"):
            output = render_record(
                record,
                dry_run=True,
                video_format=video_format,
            )
            self.assertIn("media", output.parts)


if __name__ == "__main__":
    unittest.main()
