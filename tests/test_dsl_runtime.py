from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from manim import Scene, ValueTracker

from mathinmovement.dsl.coverage import (
    DEMO_USAGE,
    QENEM_COMMON,
    QENEM_USAGE,
    universe,
)
from mathinmovement.dsl.registry import (
    action_capabilities,
    get_action,
    get_object,
    object_capabilities,
)
from mathinmovement.dsl.runtime import DSLRuntime, validate_program


PROGRAM = {
    "dsl_version": "1.0",
    "objects": [
        {"id": "t", "type": "tracker", "value": 0},
        {
            "id": "moving",
            "type": "circle",
            "radius": 0.5,
            "at": ["=t", 0],
            "dynamic": True,
            "color": "cyan",
        },
        {
            "id": "axis",
            "type": "axes",
            "x_range": [0, 4, 1],
            "y_range": [0, 2, 1],
        },
        {
            "id": "curve",
            "type": "graph",
            "axes": "axis",
            "expression": "1+0.5*cos(x)",
            "x_range": [0, 4],
        },
    ],
    "timeline": [
        {"op": "create", "target": "moving"},
        {"op": "animate_value", "target": "t", "value": 2},
        {"op": "wait", "duration": 0.1},
    ],
}


class DSLRuntimeTests(unittest.TestCase):
    def test_program_validates_and_builds_dynamic_objects(self):
        validate_program(PROGRAM)
        runtime = DSLRuntime(Scene(), PROGRAM)
        runtime.build_objects()
        self.assertIsInstance(runtime.object("t"), ValueTracker)
        self.assertIn("moving", runtime.objects)
        self.assertIn("curve", runtime.objects)

    def test_audited_semantic_capabilities_are_registered(self):
        semantic = universe(DEMO_USAGE) | universe(QENEM_USAGE) | QENEM_COMMON
        for name in semantic:
            with self.subTest(name=name):
                try:
                    get_object(name)
                except Exception:
                    get_action(name)

    def test_namespaces_are_available_for_future_extension(self):
        object_names = {cap.canonical for cap in object_capabilities()}
        action_names = {cap.canonical for cap in action_capabilities()}
        self.assertIn("2d.circle", object_names)
        self.assertIn("dynamic.tracker", object_names)
        self.assertIn("anim.rigid_motion", action_names)
        self.assertIn("dynamic.redraw", action_names)

    def test_countdown_tag_registers_ffmpeg_event_without_manim_audio(self):
        program = {
            "dsl_version": "1.0",
            "objects": [],
            "timeline": [],
        }
        scene = Scene()
        runtime = DSLRuntime(scene, program)
        step = {"op": "wait", "duration": 0.1, "tags": ["countdown-5s"]}

        with tempfile.TemporaryDirectory() as tmp:
            event_file = Path(tmp) / "events.jsonl"
            with (
                patch.dict(
                    "os.environ",
                    {"MIM_TIMED_AUDIO_EVENTS_FILE": str(event_file)},
                    clear=False,
                ),
                patch.object(scene, "add_sound") as add_sound,
            ):
                runtime.play_audio_tags(step)

            add_sound.assert_not_called()
            payload = __import__("json").loads(
                event_file.read_text(encoding="utf-8").strip()
            )
            path = Path(payload["audio"])
            self.assertEqual(payload["tag"], "countdown-5s")
            self.assertEqual(payload["start"], 0.0)
            self.assertEqual(payload["speed"], 0.9)
            self.assertEqual(payload["volume"], 1.0)
            self.assertEqual(path.name, "countdown-5s.wav")
            self.assertTrue(path.is_file())
            self.assertEqual(path.read_bytes()[:4], b"RIFF")
            self.assertEqual(path.read_bytes()[8:12], b"WAVE")

    def test_timeline_tags_validate_as_strings(self):
        with self.assertRaises(Exception):
            validate_program({
                "dsl_version": "1.0",
                "objects": [],
                "timeline": [{"op": "wait", "duration": 0.1, "tags": 5}],
            })


if __name__ == "__main__":
    unittest.main()
