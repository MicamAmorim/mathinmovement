from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from manim import Cube, Dot3D, Line3D, ThreeDAxes, ThreeDScene

from mathinmovement.dsl.registry import action_capabilities, object_capabilities
from mathinmovement.dsl.runtime import DSLRuntime, validate_program
from mathinmovement.engine.scene import UnifiedContentScene


PROGRAM_3D = {
    "dsl_version": "1.0",
    "objects": [
        {
            "id": "axes",
            "type": "3d.axes",
            "x_range": [-3, 3, 1],
            "y_range": [-3, 3, 1],
            "z_range": [-3, 3, 1],
        },
        {
            "id": "cube",
            "type": "3d.cube",
            "side": 1.5,
            "at": [1, 0, 2],
            "color": "cyan",
            "fill_opacity": 0.18,
        },
        {
            "id": "point",
            "type": "3d.dot",
            "point": [0, 1, 2],
            "color": "gold",
        },
        {
            "id": "ray",
            "type": "3d.line",
            "start": [-1, 0, 0],
            "end": [0, 1, 2],
            "color": "red",
        },
    ],
    "timeline": [],
}


class DSL3DTests(unittest.TestCase):
    def test_true_3d_objects_validate_and_build(self):
        validate_program(PROGRAM_3D)
        runtime = DSLRuntime(ThreeDScene(), PROGRAM_3D)
        runtime.build_objects()

        self.assertIsInstance(runtime.object("axes"), ThreeDAxes)
        self.assertIsInstance(runtime.object("cube"), Cube)
        self.assertIsInstance(runtime.object("point"), Dot3D)
        self.assertIsInstance(runtime.object("ray"), Line3D)

    def test_3d_capabilities_are_registered(self):
        object_names = {cap.canonical for cap in object_capabilities()}
        action_names = {cap.canonical for cap in action_capabilities()}

        self.assertTrue(
            {
                "3d.axes",
                "3d.cube",
                "3d.prism",
                "3d.dot",
                "3d.line",
                "3d.arrow",
                "3d.plane",
            }.issubset(object_names)
        )
        self.assertTrue(
            {
                "camera.set_orientation",
                "camera.move",
                "camera.begin_ambient_rotation",
                "camera.stop_ambient_rotation",
                "scene.fixed_in_frame",
                "scene.fixed_orientation",
            }.issubset(action_names)
        )

    def test_unified_scene_uses_three_d_camera(self):
        self.assertTrue(issubclass(UnifiedContentScene, ThreeDScene))

    def test_camera_orientation_action_dispatches_to_scene(self):
        scene = MagicMock(spec=ThreeDScene)
        program = {
            "dsl_version": "1.0",
            "objects": [],
            "timeline": [
                {
                    "op": "camera.set_orientation",
                    "phi": "=pi/3",
                    "theta": "=-pi/4",
                    "zoom": 0.9,
                }
            ],
        }

        DSLRuntime(scene, program).run()

        scene.set_camera_orientation.assert_called_once()
        kwargs = scene.set_camera_orientation.call_args.kwargs
        self.assertAlmostEqual(kwargs["phi"], 3.141592653589793 / 3)
        self.assertAlmostEqual(kwargs["theta"], -3.141592653589793 / 4)
        self.assertAlmostEqual(kwargs["zoom"], 0.9)


if __name__ == "__main__":
    unittest.main()
