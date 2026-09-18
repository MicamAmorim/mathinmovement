from __future__ import annotations

import unittest
from unittest.mock import patch

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
