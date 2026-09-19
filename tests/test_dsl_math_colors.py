from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from mathinmovement.dsl import objects2d


class _Runtime:
    @staticmethod
    def resolve(value):
        return value


class MathColorMapTests(unittest.TestCase):
    def test_math_passes_portable_substring_color_map_to_manim(self):
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
        _, kwargs = math_tex.call_args
        self.assertEqual(kwargs["font_size"], 72.0)
        self.assertEqual(kwargs["color"], objects2d.PALETTE["white"])
        self.assertEqual(
            kwargs["tex_to_color_map"],
            {
                "+": objects2d.PALETTE["yellow"],
                r"\times": objects2d.PALETTE["blue"],
                r"\div": objects2d.PALETTE["green"],
                "-": objects2d.PALETTE["red"],
            },
        )

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
        self.assertEqual(args[0], r"6\div2\times(1+2)=?")
        self.assertEqual(
            kwargs["tex_to_color_map"],
            {
                r"\div": objects2d.PALETTE["green"],
                r"\times": objects2d.PALETTE["blue"],
                "+": objects2d.PALETTE["yellow"],
            },
        )

    def test_single_letter_color_does_not_split_latex_control_sequence(self):
        tex = r"u=f_x\\frac{X_c}{Z_c}+c_x,\\quad v=f_y\\frac{Y_c}{Z_c}+c_y"
        prepared, safe, deferred = objects2d._prepare_math_color_map(
            tex,
            {"u": "red", "v": "green", "Z_c": "gold"},
        )

        self.assertIn(r"{{u}}=", prepared)
        self.assertIn(r"{{v}}=", prepared)
        self.assertIn(r"\\quad", prepared)
        self.assertNotIn("u", safe)
        self.assertNotIn("v", safe)
        self.assertEqual(safe["Z_c"], "gold")
        self.assertEqual(deferred, {"u": "red", "v": "green"})

    def test_risky_color_tokens_are_applied_after_mathtex_build(self):
        spec = {
            "type": "math",
            "tex": r"u=1,\\quad v=2",
            "tex_to_color_map": {"u": "red", "v": "green"},
        }
        fake_math = MagicMock()
        with (
            patch.object(objects2d, "MathTex", return_value=fake_math) as math_tex,
            patch.object(objects2d, "apply_layout", return_value=fake_math),
        ):
            result = objects2d.make_math(_Runtime(), spec)

        self.assertIs(result, fake_math)
        args, kwargs = math_tex.call_args
        self.assertEqual(args[0], r"{{u}}=1,\\quad {{v}}=2")
        self.assertNotIn("tex_to_color_map", kwargs)
        fake_math.set_color_by_tex.assert_any_call(
            "u", objects2d.PALETTE["red"], substring=False
        )
        fake_math.set_color_by_tex.assert_any_call(
            "v", objects2d.PALETTE["green"], substring=False
        )
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
