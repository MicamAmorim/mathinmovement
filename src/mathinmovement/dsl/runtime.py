from __future__ import annotations

import re
from copy import deepcopy

import numpy as np
from manim import VGroup, ValueTracker, always_redraw

from .errors import DSLError, DSLReferenceError, DSLVersionError
from .expressions import eval_expression, resolve_value
from .registry import get_action, get_object

# Registra built-ins por import lateral explícito.
from . import objects2d as _objects2d  # noqa: F401
from . import actions as _actions  # noqa: F401


_VERSION_RE = re.compile(r"^1(?:\.\d+)?$")


def validate_program(program):
    if not isinstance(program, dict):
        raise DSLError("visual_program deve ser um objeto.")
    version = str(program.get("dsl_version", ""))
    if not _VERSION_RE.match(version):
        raise DSLVersionError(
            f"dsl_version não suportada: {version!r}; esperado 1.x."
        )
    objects = program.get("objects")
    timeline = program.get("timeline")
    if not isinstance(objects, list):
        raise DSLError("visual_program.objects deve ser lista.")
    if not isinstance(timeline, list):
        raise DSLError("visual_program.timeline deve ser lista.")

    ids = set()
    for spec in objects:
        if not isinstance(spec, dict):
            raise DSLError("Cada objeto DSL deve ser um objeto.")
        object_id = str(spec.get("id", "")).strip()
        object_type = str(spec.get("type", "")).strip()
        if not object_id or not object_type:
            raise DSLError("Cada objeto DSL exige id e type.")
        if object_id in ids:
            raise DSLError(f"ID DSL duplicado: {object_id}")
        ids.add(object_id)
        get_object(object_type)

    for step in timeline:
        if not isinstance(step, dict) or not step.get("op"):
            raise DSLError("Cada passo da timeline exige op.")
        get_action(str(step["op"]))
    return program


class DSLRuntime:
    def __init__(self, scene, program):
        self.scene = scene
        self.program = validate_program(program)
        self.objects = {}
        self.specs = {}
        self.trackers = {}

    def variables(self, extra=None):
        values = {
            key: float(tracker.get_value())
            for key, tracker in self.trackers.items()
        }
        if extra:
            values.update({str(k): float(v) for k, v in extra.items()})
        return values

    def eval(self, expression, extra=None):
        text = str(expression)
        if text.startswith("="):
            text = text[1:].strip()
        return eval_expression(text, self.variables(extra))

    def resolve(self, value, extra=None):
        return resolve_value(value, self.variables(extra))

    def object(self, object_id):
        try:
            return self.objects[str(object_id)]
        except KeyError as exc:
            raise DSLReferenceError(f"Objeto DSL não encontrado: {object_id}") from exc

    def factory_for(self, spec):
        return get_object(str(spec["type"])).handler

    def build_object(self, spec):
        object_id = str(spec["id"])
        if object_id in self.objects:
            raise DSLError(f"ID DSL duplicado: {object_id}")
        self.specs[object_id] = deepcopy(spec)
        factory = self.factory_for(spec)
        capability = get_object(str(spec["type"]))

        if capability.canonical == "dynamic.tracker":
            mob = factory(self, spec)
            self.trackers[object_id] = mob
        elif spec.get("dynamic", False):
            base_spec = deepcopy(spec)
            base_spec["dynamic"] = False
            mob = always_redraw(lambda: factory(self, base_spec))
        else:
            mob = factory(self, spec)

        self.objects[object_id] = mob
        return mob

    def build_objects(self):
        for spec in self.program.get("objects", []):
            self.build_object(spec)
        return self.objects

    def run(self):
        self.build_objects()
        for step in self.program.get("timeline", []):
            get_action(str(step["op"])).handler(self, step)
        return self


def run_visual_program(scene, program):
    return DSLRuntime(scene, program).run()


def build_visual_group(scene, program, ids=None):
    runtime = DSLRuntime(scene, program)
    runtime.build_objects()
    chosen = ids or [
        spec["id"]
        for spec in program.get("objects", [])
        if get_object(str(spec["type"])).canonical != "dynamic.tracker"
    ]
    return VGroup(*[runtime.object(str(item)) for item in chosen]), runtime
