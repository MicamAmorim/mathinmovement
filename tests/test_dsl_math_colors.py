from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from mathinmovement.dsl import objects2d


class _Runtime:
    @staticmethod
    def resolve(value):
        return value


class MathColorMapTests(unittest.TestCase):
    def test_math_inlines_colors_without_substring_splitting(self):
        spec = {
            "type": "math",
            "tex": r"6\div2\times(1+2)=?",
            "font_size": 72,
            "color": "white",
            "tex_to_color_map": {
                "+": "yellow",
                r"\times": "blue",
                r"\div": "green",
                "-": "red",
            },
        }

        fake_math = object()
        with (
            patch.object(objects2d, "MathTex", return_value=fake_math) as math_tex,
            patch.object(objects2d, "apply_layout", return_value=fake_math),
        ):
            result = objects2d.make_math(_Runtime(), spec)

        self.assertIs(result, fake_math)
        args, kwargs = math_tex.call_args
        self.assertEqual(kwargs["font_size"], 72.0)
        self.assertEqual(kwargs["color"], objects2d.PALETTE["white"])
        self.assertNotIn("tex_to_color_map", kwargs)
        self.assertIn(r"{\color[HTML]{FFD84D}+}", args[0])
        self.assertIn(r"{\color[HTML]{79A7FF}\times}", args[0])
        self.assertIn(r"{\color[HTML]{8DE2A7}\div}", args[0])

    def test_legacy_inline_color_commands_are_migrated_at_runtime(self):
        spec = {
            "type": "math",
            "tex": r"6{\color{green}\div}2{\color{blue}\times}(1{\color{yellow}+}2)=?",
        }

        fake_math = object()
        with (
            patch.object(objects2d, "MathTex", return_value=fake_math) as math_tex,
            patch.object(objects2d, "apply_layout", return_value=fake_math),
        ):
            objects2d.make_math(_Runtime(), spec)

        args, kwargs = math_tex.call_args
        self.assertNotIn("tex_to_color_map", kwargs)
        self.assertIn(r"{\color[HTML]{8DE2A7}\div}", args[0])
        self.assertIn(r"{\color[HTML]{79A7FF}\times}", args[0])
        self.assertIn(r"{\color[HTML]{FFD84D}+}", args[0])

    def test_color_map_keeps_fraction_and_quad_structurally_valid(self):
        tex = r"u=f_x\frac{X_c}{Z_c}+c_x,\quad v=f_y\frac{Y_c}{Z_c}+c_y"
        prepared = objects2d._apply_inline_math_colors(
            tex,
            {"u": "red", "v": "green", "Z_c": "gold"},
        )

        self.assertIn(r"\quad", prepared)
        self.assertIn(r"\frac{X_c}{{\color[HTML]{FFCC78}Z_c}}", prepared)
        self.assertIn(r"{\color[HTML]{FF7D7D}u}=f_x", prepared)
        self.assertIn(r"{\color[HTML]{8DE2A7}v}=f_y", prepared)
        self.assertNotIn(r"\q{\color", prepared)

    def test_fraction_color_map_is_not_forwarded_to_mathtex_splitter(self):
        spec = {
            "type": "math",
            "tex": r"u=f_x\frac{X_c}{Z_c}+c_x,\quad v=f_y\frac{Y_c}{Z_c}+c_y",
            "tex_to_color_map": {"u": "red", "v": "green", "Z_c": "gold"},
        }
        fake_math = object()
        with (
            patch.object(objects2d, "MathTex", return_value=fake_math) as math_tex,
            patch.object(objects2d, "apply_layout", return_value=fake_math),
        ):
            result = objects2d.make_math(_Runtime(), spec)

        self.assertIs(result, fake_math)
        args, kwargs = math_tex.call_args
        self.assertNotIn("tex_to_color_map", kwargs)
        self.assertIn(r"\frac{X_c}{{\color[HTML]{FFCC78}Z_c}}", args[0])
        self.assertIn(r"\quad", args[0])

    def test_challenge_template_does_not_embed_latex_color_commands(self):
        from pathlib import Path
        from mathinmovement.registry import load_manifest

        root = Path(__file__).resolve().parents[1]
        manifest = load_manifest(
            root / "examples" / "templates" / "demo-desafio-questao" / "manifest.yaml"
        )
        math_objects = [
            obj
            for obj in manifest["visual_program"]["objects"]
            if obj.get("type") == "math"
        ]

        self.assertTrue(any(obj.get("tex_to_color_map") for obj in math_objects))
        for obj in math_objects:
            self.assertNotIn(r"\color", obj.get("tex", ""))


if __name__ == "__main__":
    unittest.main()
