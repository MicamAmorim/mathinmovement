from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from manim import Dot, FadeIn, Scene, ValueTracker, Wait

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
from mathinmovement.engine.scene import UnifiedContentScene


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

    def test_countdown_tag_plays_audio_through_manim(self):
        program = {
            "dsl_version": "1.0",
            "objects": [],
            "timeline": [],
        }
        scene = Scene()
        runtime = DSLRuntime(scene, program)
        step = {"op": "wait", "duration": 0.1, "tags": ["countdown-5s"]}

        prepared = Path(
            "assets/audio/countdown-5s-original_90porc.mp3"
        )
        with (
            patch.object(
                runtime,
                "_materialize_standard_audio",
                return_value=prepared,
            ),
            patch.object(scene, "add_sound") as add_sound,
        ):
            runtime.play_audio_tags(step)

        add_sound.assert_called_once_with(str(prepared))

    def test_countdown_tag_is_skipped_in_fast_preview(self):
        scene = Scene()
        runtime = DSLRuntime(
            scene,
            {"dsl_version": "1.0", "objects": [], "timeline": []},
        )
        step = {"op": "wait", "duration": 0.1, "tags": ["countdown-5s"]}

        with (
            patch.dict(
                "os.environ",
                {"MIM_FAST_PREVIEW": "1"},
                clear=False,
            ),
            patch.object(scene, "add_sound") as add_sound,
        ):
            runtime.play_audio_tags(step)

        add_sound.assert_not_called()

    def test_narration_play_uses_one_low_level_audio_track(self):
        scene = MagicMock()
        scene.time = 3.25
        scene.renderer.skip_animations = False
        scene.audio_path.return_value = Path("intro.mp3")
        scene.segment_duration.return_value = 4.5
        runtime = DSLRuntime(
            scene,
            {"dsl_version": "1.0", "objects": [], "timeline": []},
        )

        get_action("narration.play").handler(
            runtime,
            {"op": "narration.play", "key": "intro"},
        )

        scene.renderer.file_writer.add_sound.assert_called_once_with(
            "intro.mp3",
            3.25,
        )
        scene.add_sound.assert_not_called()
        scene.wait.assert_called_once_with(4.5)

    def test_narration_begin_end_waits_only_remaining_audio(self):
        scene = MagicMock()
        scene.time = 2.0
        scene.renderer.skip_animations = False
        scene.audio_path.return_value = Path("intro.mp3")
        scene.segment_duration.return_value = 8.0
        runtime = DSLRuntime(
            scene,
            {"dsl_version": "1.0", "objects": [], "timeline": []},
        )

        get_action("narration.begin").handler(
            runtime,
            {"op": "narration.begin", "key": "intro"},
        )
        scene.renderer.file_writer.add_sound.assert_called_once_with(
            "intro.mp3",
            2.0,
        )

        scene.time = 6.5
        get_action("narration.end").handler(
            runtime,
            {"op": "narration.end", "key": "intro"},
        )

        scene.wait.assert_called_once_with(3.5)
        self.assertIsNone(runtime._active_narration)

    def test_narration_begin_rejects_overlapping_tracks(self):
        scene = MagicMock()
        scene.time = 0.0
        scene.renderer.skip_animations = False
        scene.audio_path.return_value = Path("intro.mp3")
        scene.segment_duration.return_value = 5.0
        runtime = DSLRuntime(
            scene,
            {"dsl_version": "1.0", "objects": [], "timeline": []},
        )

        get_action("narration.begin").handler(
            runtime,
            {"op": "narration.begin", "key": "first"},
        )
        with self.assertRaises(Exception):
            get_action("narration.begin").handler(
                runtime,
                {"op": "narration.begin", "key": "second"},
            )

    def test_motion_math_play_preserves_legacy_implicit_pacing(self):
        scene = object.__new__(UnifiedContentScene)
        scene._profile = "motion_math_v1"
        animation = FadeIn(Dot())

        with (
            patch.dict("os.environ", {"MANIM_PACE": "1.15"}, clear=False),
            patch.object(Scene, "play", return_value=None) as base_play,
        ):
            UnifiedContentScene.play(scene, animation)

        _, kwargs = base_play.call_args
        self.assertAlmostEqual(kwargs["run_time"], 1.15, places=6)

    def test_motion_math_play_does_not_override_wait_animation_duration(self):
        scene = object.__new__(UnifiedContentScene)
        scene._profile = "motion_math_v1"
        wait = Wait(run_time=7.25)

        with patch.object(Scene, "play", return_value=None) as base_play:
            UnifiedContentScene.play(scene, wait)

        _, kwargs = base_play.call_args
        self.assertNotIn("run_time", kwargs)
        self.assertAlmostEqual(wait.run_time, 7.25, places=6)

    def test_motion_math_play_clamps_explicit_run_time_to_one_frame(self):
        scene = object.__new__(UnifiedContentScene)
        scene._profile = "motion_math_v1"
        wait = Wait(run_time=1.0)

        with (
            patch.dict("os.environ", {"MANIM_PACE": "1.0"}, clear=False),
            patch(
                "mathinmovement.engine.scene.config",
                SimpleNamespace(frame_rate=15),
            ),
            patch.object(Scene, "play", return_value=None) as base_play,
        ):
            UnifiedContentScene.play(scene, wait, run_time=0.04)

        _, kwargs = base_play.call_args
        self.assertAlmostEqual(kwargs["run_time"], 1.0 / 15.0, places=6)

    def test_motion_math_play_scales_only_explicit_run_time(self):
        scene = object.__new__(UnifiedContentScene)
        scene._profile = "motion_math_v1"
        wait = Wait(run_time=7.25)

        with (
            patch.dict("os.environ", {"MANIM_PACE": "1.15"}, clear=False),
            patch.object(Scene, "play", return_value=None) as base_play,
        ):
            UnifiedContentScene.play(scene, wait, run_time=2.0)

        _, kwargs = base_play.call_args
        self.assertAlmostEqual(kwargs["run_time"], 2.3, places=6)

    def test_timeline_tags_validate_as_strings(self):
        with self.assertRaises(Exception):
            validate_program({
                "dsl_version": "1.0",
                "objects": [],
                "timeline": [{"op": "wait", "duration": 0.1, "tags": 5}],
            })


if __name__ == "__main__":
    unittest.main()
