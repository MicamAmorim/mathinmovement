from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import zlib
from copy import deepcopy
from pathlib import Path

import numpy as np
from manim import VGroup, ValueTracker, always_redraw

from ..config import CACHE_ROOT, PROJECT_ROOT
from .errors import DSLError, DSLReferenceError, DSLVersionError
from .expressions import eval_expression, resolve_value
from .registry import get_action, get_object

# Registra built-ins por import lateral explícito.
from . import objects2d as _objects2d  # noqa: F401
from . import actions as _actions  # noqa: F401


_VERSION_RE = re.compile(r"^1(?:\.\d+)?$")
_STANDARD_AUDIO_TAGS = {
    "countdown-5s": {
        "parts": [
            Path("assets/audio/countdown-5s.wav.zlib.b64.part1"),
            Path("assets/audio/countdown-5s.wav.zlib.b64.part2"),
            Path("assets/audio/countdown-5s.wav.zlib.b64.part3"),
        ],
        "cache_name": "countdown-5s.wav",
        "sha256": "22c9dbe32df19b6150dfb76127918b468a61aa0b36e6ce72bb8ee31ccbdff966",
        "speed": 0.9,
        "volume": 1.0,
    },
}


def _validate_tex_escapes(value, path="visual_program"):
    """Reject accidental doubled escapes before LaTeX control words.

    A genuine LaTeX line break such as \\[4pt] remains allowed; what we
    reject is the common JSON/DSL mistake that turns \frac into \\frac.
    """
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if key == "tex" and isinstance(item, str):
                doubled = chr(92) * 2
                for index in range(len(item) - 2):
                    if (
                        item.startswith(doubled, index)
                        and item[index + 2].isalpha()
                    ):
                        raise DSLError(
                            f"{child_path}: escape LaTeX duplicado antes de "
                            f"{item[index + 2:]!r}."
                        )
            _validate_tex_escapes(item, child_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_tex_escapes(item, f"{path}[{index}]")


def _normalize_step_tags(step):
    raw = step.get("tags") or []
    if isinstance(raw, str):
        return [raw]
    if not isinstance(raw, (list, tuple)):
        raise DSLError("timeline.tags deve ser uma lista de strings.")
    tags = []
    for value in raw:
        tag = str(value).strip()
        if not tag:
            raise DSLError("timeline.tags não pode conter tag vazia.")
        tags.append(tag)
    return tags


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
        _normalize_step_tags(step)

    _validate_tex_escapes(program)
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

    def _materialize_standard_audio(self, tag):
        spec = _STANDARD_AUDIO_TAGS.get(tag)
        if spec is None:
            return None

        cache_dir = CACHE_ROOT / "shared_audio"
        cache_dir.mkdir(parents=True, exist_ok=True)
        output = (cache_dir / spec["cache_name"]).resolve()

        if output.is_file():
            digest = hashlib.sha256(output.read_bytes()).hexdigest()
            if digest == spec["sha256"]:
                return output

        encoded_parts = []
        for relative in spec["parts"]:
            source = (PROJECT_ROOT / relative).resolve()
            if not source.is_file():
                raise DSLError(
                    f"Asset de áudio padrão da tag {tag!r} não encontrado: {source}"
                )
            encoded_parts.append(source.read_text(encoding="ascii").strip())

        try:
            compressed = base64.b64decode("".join(encoded_parts), validate=True)
            audio = zlib.decompress(compressed)
        except Exception as exc:
            raise DSLError(
                f"Asset de áudio padrão da tag {tag!r} está corrompido."
            ) from exc

        digest = hashlib.sha256(audio).hexdigest()
        if digest != spec["sha256"]:
            raise DSLError(
                f"Checksum inválido para o áudio padrão da tag {tag!r}."
            )

        output.write_bytes(audio)
        return output

    def play_audio_tags(self, step):
        event_file_value = os.getenv("MIM_TIMED_AUDIO_EVENTS_FILE")
        if not event_file_value:
            return

        event_file = Path(event_file_value)
        event_file.parent.mkdir(parents=True, exist_ok=True)
        for tag in _normalize_step_tags(step):
            path = self._materialize_standard_audio(tag)
            if path is None:
                continue
            spec = _STANDARD_AUDIO_TAGS[tag]
            event = {
                "tag": tag,
                "start": float(self.scene.time),
                "audio": str(path),
                "speed": float(spec.get("speed", 1.0)),
                "volume": float(spec.get("volume", 1.0)),
            }
            with event_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def run(self):
        self.build_objects()
        for step in self.program.get("timeline", []):
            self.play_audio_tags(step)
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
