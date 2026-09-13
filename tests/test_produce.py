from __future__ import annotations

import unittest

from mathinmovement.cli import build_parser
from mathinmovement.production import resolve_target


class ProduceTests(unittest.TestCase):
    def test_cli_accepts_existing_id(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "produce",
                "ENEM-2021-MT-11",
                "--format",
                "horizontal",
                "--quality",
                "draft",
                "--skip-voice",
                "--dry-run",
            ]
        )
        self.assertEqual(args.target, "ENEM-2021-MT-11")
        self.assertEqual(args.format, "horizontal")
        self.assertTrue(args.skip_voice)
        self.assertTrue(args.dry_run)

    def test_cli_accepts_music_postproduction_options(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "produce",
                "ENEM-2021-MT-11",
                "--music",
                "music.mp3",
                "--music-volume",
                "0.1",
                "--fade-in",
                "2",
                "--fade-out",
                "3",
                "--no-ducking",
                "--no-normalize",
                "--no-reuse-raw",
                "--dry-run",
            ]
        )
        self.assertEqual(args.music, "music.mp3")
        self.assertEqual(args.music_volume, 0.1)
        self.assertEqual(args.fade_in, 2.0)
        self.assertEqual(args.fade_out, 3.0)
        self.assertTrue(args.no_ducking)
        self.assertTrue(args.no_normalize)
        self.assertTrue(args.no_reuse_raw)

    def test_cli_accepts_standalone_postprocess(self):
        parser = build_parser()
        args = parser.parse_args(
            [
                "postprocess",
                "media_raw/demo/vertical/demo.mp4",
                "--music",
                "music.mp3",
                "-o",
                "media/demo/vertical/demo.mp4",
                "--dry-run",
            ]
        )
        self.assertEqual(args.input, "media_raw/demo/vertical/demo.mp4")
        self.assertEqual(args.music, "music.mp3")
        self.assertTrue(args.dry_run)

    def test_resolve_existing_id(self):
        record, imported = resolve_target("ENEM-2021-MT-11")
        self.assertFalse(imported)
        self.assertEqual(record.id, "ENEM-2021-MT-11")
        self.assertEqual(record.type, "qenem")


if __name__ == "__main__":
    unittest.main()
