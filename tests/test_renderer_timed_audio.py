from pathlib import Path
import unittest

from mathinmovement.engine.renderer import (
    _align_events_to_manifest,
    _manifest_timed_audio_starts,
    _should_mix_timed_audio_events,
)
from mathinmovement.postprocess import TimedAudioEvent


class TimedAudioManifestTests(unittest.TestCase):
    def manifest(self):
        return {
            "visual_program": {
                "timeline": [
                    {"op": "add", "target": "brand"},
                    {"op": "add", "target": "expr"},
                    {
                        "op": "opacity",
                        "target": "brand",
                        "value": 1,
                        "run_time": 3.1,
                    },
                    {"op": "add", "target": "ring"},
                    {
                        "op": "add",
                        "target": "n5",
                        "tags": ["countdown-5s"],
                    },
                ]
            }
        }

    def test_manifest_resolves_countdown_start_after_intro_hold(self):
        starts = _manifest_timed_audio_starts(self.manifest())
        self.assertEqual(len(starts), 1)
        self.assertEqual(starts[0][0], "countdown-5s")
        self.assertAlmostEqual(starts[0][1], 3.1, places=6)

    def test_timeline_narration_without_effect_tags_is_not_remixed(self):
        manifest = {
            "narration": {"enabled": True, "sync": "timeline"},
            "visual_program": {
                "timeline": [
                    {"op": "narration.play", "key": "intro"},
                    {"op": "wait", "duration": 1.0},
                ]
            },
        }
        self.assertFalse(_should_mix_timed_audio_events(manifest))

    def test_timeline_narration_keeps_explicit_effect_mix(self):
        manifest = {
            "narration": {"enabled": True, "sync": "timeline"},
            "visual_program": {
                "timeline": [
                    {"op": "narration.play", "key": "intro"},
                    {"op": "add", "target": "n5", "tags": ["countdown-5s"]},
                ]
            },
        }
        self.assertTrue(_should_mix_timed_audio_events(manifest))

    def test_runtime_zero_timestamp_is_replaced_by_manifest_timestamp(self):
        events = [
            TimedAudioEvent(
                tag="countdown-5s",
                start=0.0,
                audio=Path("countdown.mp3"),
                speed=0.9,
            )
        ]
        aligned = _align_events_to_manifest(self.manifest(), events)
        self.assertEqual(len(aligned), 1)
        self.assertAlmostEqual(aligned[0].start, 3.1, places=6)


if __name__ == "__main__":
    unittest.main()
