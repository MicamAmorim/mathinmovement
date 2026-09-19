from __future__ import annotations

import os
import re
import shutil
import subprocess
from copy import deepcopy
from pathlib import Path

import numpy as np
from manim import VGroup, ValueTracker, always_redraw

from ..config import PROJECT_ROOT
from .errors import DSLError, DSLReferenceError, DSLVersionError
from .expressions import eval_expression, resolve_value
from .registry import get_action, get_object

# Registra built-ins por import lateral explícito.
from . import objects2d as _objects2d  # noqa: F401
from . import objects3d as _objects3d  # noqa: F401
from . import actions as _actions  # noqa: F401


_VERSION_RE = re.compile(r"^1(?:\.\d+)?$")
_STANDARD_AUDIO_TAGS = {
    "countdown-5s": {
        "prepared_path": Path(
            "assets/audio/countdown-5s-original_90porc.mp3"
        ),
        "source_paths": (
            Path("assets/audio/countdown-5s.mp3"),
            Path("assets/audio/countdown-5s-original.mp3"),
        ),
        "speed": 0.9,
        # Compatibilidade com a versão antiga de ~11 s do arquivo original.
        "legacy_trim_start": 4.83265306122449,
        "legacy_trim_end": 11.023673469387756,
        "legacy_duration_threshold": 7.0,
    },
}


def _fast_preview_enabled():
    return os.getenv("MIM_FAST_PREVIEW", "0").lower() in {
        "1",
        "true",
        "yes",
    }


def _media_binary(name):
    path = shutil.which(name)
    if path is None:
        raise DSLError(
            f"{name} não encontrado no PATH. "
            "Ele é necessário para preparar o countdown a 90%."
        )
    return path


def _probe_audio_duration(path):
    ffprobe = _media_binary("ffprobe")
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise DSLError(
            f"ffprobe falhou ao inspecionar {path}: "
            f"{result.stderr.strip()}"
        )
    try:
        return float(result.stdout.strip())
    except ValueError as exc:
        raise DSLError(
            f"ffprobe retornou duração inválida para {path}."
        ) from exc


def _prepare_countdown_audio(spec):
    prepared = (PROJECT_ROOT / spec["prepared_path"]).resolve()
    if prepared.is_file():
        return prepared

    source = None
    for relative in spec.get("source_paths", ()):
        candidate = (PROJECT_ROOT / relative).resolve()
        if candidate.is_file():
            source = candidate
            break
    if source is None:
        expected = ", ".join(
            str((PROJECT_ROOT / relative).resolve())
            for relative in spec.get("source_paths", ())
        )
        raise DSLError(
            "Fonte do countdown não encontrada. "
            f"Esperado em: {expected}"
        )

    duration = _probe_audio_duration(source)
    filters = []
    threshold = float(spec.get("legacy_duration_threshold", 7.0))
    if duration > threshold:
        start = float(spec["legacy_trim_start"])
        end = float(spec["legacy_trim_end"])
        filters.extend(
            [
                f"atrim=start={start}:end={end}",
                "asetpts=PTS-STARTPTS",
            ]
        )
    filters.append(f"atempo={float(spec.get('speed', 0.9))}")

    ffmpeg = _media_binary("ffmpeg")
    prepared.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(source),
            "-vn",
            "-af",
            ",".join(filters),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "256k",
            str(prepared),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode or not prepared.is_file():
        raise DSLError(
            "FFmpeg falhou ao preparar o countdown a 90%: "
            f"{result.stderr.strip()}"
        )

    print(
        f"[audio] countdown preparado a 90%: {prepared.name}"
    )
    return prepared


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
        self.program = validate_program(deepcopy(program))
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
        if tag == "countdown-5s":
            return _prepare_countdown_audio(spec)
        return None

    def play_audio_tags(self, step):
        """Toca efeitos marcados pelo mesmo mecanismo da narração."""
        if _fast_preview_enabled():
            return

        for tag in _normalize_step_tags(step):
            path = self._materialize_standard_audio(tag)
            if path is None:
                continue
            self.scene.add_sound(str(path))
            print(
                f"[audio] {tag} via Manim @ "
                f"{float(getattr(self.scene, 'time', 0.0)):.3f}s"
            )

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
