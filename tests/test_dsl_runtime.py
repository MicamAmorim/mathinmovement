from __future__ import annotations

import unittest

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
        # Layout e dynamic_redraw também são ações registradas.
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


if __name__ == "__main__":
    unittest.main()
