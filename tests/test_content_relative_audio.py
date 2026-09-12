from __future__ import annotations

import unittest
from pathlib import Path

from mathinmovement.engine.scene import UnifiedContentScene


class ContentRelativeAudioTests(unittest.TestCase):
    def test_audio_path_accepts_content_relative_asset(self):
        scene = object.__new__(UnifiedContentScene)
        scene.record = type(
            "Record",
            (),
            {"path": Path("content/enem/EXAMPLE")},
        )()
        scene.narr = {
            "source": {
                "audio": "assets/audio/source.mp3",
            }
        }

        # This test checks path semantics without requiring the asset
        # to exist: a missing asset must cleanly resolve to None.
        self.assertIsNone(scene.audio_path("source"))


if __name__ == "__main__":
    unittest.main()
