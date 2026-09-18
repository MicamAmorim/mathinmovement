from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mathinmovement.engine.scene import UnifiedContentScene


class DemoNarrationTests(unittest.TestCase):
    def _scene(self, root: Path, narration: dict):
        scene = object.__new__(UnifiedContentScene)
        scene.record = type("Record", (), {
            "id": "demo-audio",
            "path": root,
        })()
        scene.manifest = {"narration": narration}
        scene.narr = {
            str(segment["key"]): segment
            for segment in narration.get("segments", [])
            if isinstance(segment, dict) and segment.get("key")
        }
        return scene

    def test_master_audio_is_added_at_scene_start(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audio = root / "assets" / "audio" / "master.wav"
            audio.parent.mkdir(parents=True)
            audio.write_bytes(b"fake")

            scene = self._scene(root, {
                "enabled": True,
                "master_audio": "assets/audio/master.wav",
                "segments": [
                    {
                        "key": "opening",
                        "audio": "assets/audio/opening.mp3",
                        "start": 0.0,
                    },
                    {
                        "key": "closing",
                        "audio": "assets/audio/closing.mp3",
                        "start": 21.0,
                    },
                ],
            })

            with patch.object(UnifiedContentScene, "add_sound") as add_sound:
                scene._schedule_demo_narration()

            add_sound.assert_called_once_with(str(audio.resolve()))

    def test_segments_are_scheduled_by_absolute_start_when_no_master(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audio_dir = root / "assets" / "audio"
            audio_dir.mkdir(parents=True)
            opening = audio_dir / "opening.mp3"
            closing = audio_dir / "closing.mp3"
            opening.write_bytes(b"fake")
            closing.write_bytes(b"fake")

            scene = self._scene(root, {
                "enabled": True,
                "segments": [
                    {
                        "key": "opening",
                        "audio": "assets/audio/opening.mp3",
                        "start": 0.0,
                    },
                    {
                        "key": "closing",
                        "audio": "assets/audio/closing.mp3",
                        "start": 21.0,
                    },
                ],
            })

            with patch.object(UnifiedContentScene, "add_sound") as add_sound:
                scene._schedule_demo_narration()

            self.assertEqual(add_sound.call_count, 2)
            add_sound.assert_any_call(str(opening.resolve()), time_offset=0.0)
            add_sound.assert_any_call(str(closing.resolve()), time_offset=21.0)

    def test_disabled_narration_adds_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            scene = self._scene(Path(td), {
                "enabled": False,
                "segments": [],
            })
            with patch.object(UnifiedContentScene, "add_sound") as add_sound:
                scene._schedule_demo_narration()
            add_sound.assert_not_called()


if __name__ == "__main__":
    unittest.main()
