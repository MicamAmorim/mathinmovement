from __future__ import annotations

import numpy as np
from manim import (
    ApplyMethod,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    ReplacementTransform,
    Rotate,
    Transform,
    TransformFromCopy,
    UpdateFromAlphaFunc,
    Write,
    always_redraw,
    linear,
    smooth,
)

from .errors import DSLError, DSLReferenceError
from .objects2d import color, direction, point
from .registry import action_type, get_action


RATE_FUNCS = {"linear": linear, "smooth": smooth}


def _runtime(spec):
    return float(spec.get("run_time", 1.0))


def _rate(spec):
    name = str(spec.get("rate_func", "smooth"))
    try:
        return RATE_FUNCS[name]
    except KeyError as exc:
        raise DSLError(f"rate_func DSL desconhecida: {name!r}") from exc


def make_animation(runtime, spec):
    op = str(spec.get("op", ""))
    canonical = get_action(op).canonical
    target_id = spec.get("target")
    target = runtime.object(str(target_id)) if target_id is not None else None

    if canonical == "anim.create":
        return Create(target)
    if canonical == "anim.fade_in":
        kwargs = {}
        if spec.get("shift") is not None:
            kwargs["shift"] = point(runtime, spec["shift"])
        return FadeIn(target, **kwargs)
    if canonical == "anim.fade_out":
        return FadeOut(target)
    if canonical == "anim.write":
        return Write(target)
    if canonical == "anim.translate":
        return ApplyMethod(target.shift, point(runtime, spec["by"]))
    if canonical == "anim.rotate":
        about = (
            point(runtime, spec["about_point"])
            if spec.get("about_point") is not None
            else target.get_center()
        )
        return Rotate(
            target,
            float(runtime.resolve(spec.get("angle", 0))),
            about_point=about,
        )
    if canonical == "anim.scale":
        return ApplyMethod(target.scale, float(runtime.resolve(spec.get("factor", 1))))
    if canonical == "anim.opacity":
        return ApplyMethod(target.set_opacity, float(runtime.resolve(spec.get("value", 1))))
    if canonical == "anim.stretch":
        return ApplyMethod(
            target.stretch,
            float(runtime.resolve(spec.get("factor", 1))),
            int(spec.get("dim", 0)),
        )
    if canonical == "anim.highlight":
        return Indicate(
            target,
            color=color(spec.get("color", "gold")),
            scale_factor=float(runtime.resolve(spec.get("scale_factor", 1.04))),
        )
    if canonical == "anim.transform":
        return Transform(target, runtime.object(str(spec["to"])))
    if canonical == "anim.transform_from_copy":
        return TransformFromCopy(target, runtime.object(str(spec["to"])))
    if canonical == "anim.replacement_transform":
        return ReplacementTransform(target, runtime.object(str(spec["to"])))
    if canonical == "anim.rigid_motion":
        original = target.copy()
        angle = float(runtime.resolve(spec.get("angle", 0)))
        shift = point(runtime, spec.get("shift", [0, 0]))
        return UpdateFromAlphaFunc(
            target,
            lambda mob, alpha: mob.become(
                original.copy()
                .rotate(angle * alpha, about_point=spec.get("_origin", np.zeros(3)))
                .shift(alpha * shift)
            ),
        )
    if canonical == "dynamic.animate_value":
        value = float(runtime.resolve(spec["value"]))
        return target.animate.set_value(value)
    if canonical == "layout.move_to":
        return ApplyMethod(target.move_to, point(runtime, spec["point"]))
    if canonical == "layout.next_to":
        other = runtime.object(str(spec["other"]))
        return ApplyMethod(
            target.next_to,
            other,
            direction(spec.get("direction", "RIGHT")),
            float(runtime.resolve(spec.get("buff", 0.25))),
        )
    raise DSLError(f"Ação {op!r} não pode ser usada dentro de parallel/lagged.")


def _play(runtime, animation, spec):
    runtime.scene.play(
        animation,
        run_time=_runtime(spec),
        rate_func=_rate(spec),
    )


@action_type("anim.create", aliases=("create",))
def action_create(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.fade_in", aliases=("fade_in",))
def action_fade_in(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.fade_out", aliases=("fade_out",))
def action_fade_out(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.write", aliases=("write",))
def action_write(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.translate", aliases=("translate",))
def action_translate(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.rotate", aliases=("rotate",))
def action_rotate(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.scale", aliases=("scale",))
def action_scale(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.opacity", aliases=("opacity",))
def action_opacity(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.stretch", aliases=("stretch",))
def action_stretch(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.highlight", aliases=("highlight",))
def action_highlight(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.transform", aliases=("transform",))
def action_transform(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.transform_from_copy", aliases=("transform_from_copy",))
def action_transform_from_copy(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.replacement_transform", aliases=("replacement_transform",))
def action_replacement_transform(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.rigid_motion", aliases=("rigid_motion",))
def action_rigid_motion(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("dynamic.animate_value", aliases=("animate_value",))
def action_animate_value(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("anim.lagged", aliases=("lagged",))
def action_lagged(runtime, spec):
    animations = [make_animation(runtime, child) for child in spec.get("actions", [])]
    runtime.scene.play(
        LaggedStart(
            *animations,
            lag_ratio=float(runtime.resolve(spec.get("lag_ratio", 0.1))),
        ),
        run_time=_runtime(spec),
    )


@action_type("anim.parallel", aliases=("parallel",))
def action_parallel(runtime, spec):
    animations = [make_animation(runtime, child) for child in spec.get("actions", [])]
    runtime.scene.play(*animations, run_time=_runtime(spec), rate_func=_rate(spec))


@action_type("anim.wait", aliases=("wait",))
def action_wait(runtime, spec):
    runtime.scene.wait(float(runtime.resolve(spec.get("duration", 1))))


@action_type("scene.add", aliases=("add",))
def action_add(runtime, spec):
    runtime.scene.add(runtime.object(str(spec["target"])))


@action_type("scene.remove", aliases=("remove",))
def action_remove(runtime, spec):
    runtime.scene.remove(runtime.object(str(spec["target"])))


@action_type("scene.copy", aliases=("copy",))
def action_copy(runtime, spec):
    source = runtime.object(str(spec["source"]))
    new_id = str(spec["id"])
    if new_id in runtime.objects:
        raise DSLError(f"ID DSL duplicado: {new_id}")
    clone = source.copy()
    if spec.get("color") is not None:
        clone.set_color(color(spec["color"]))
    runtime.objects[new_id] = clone
    if spec.get("add", False):
        runtime.scene.add(clone)


@action_type("anim.style", aliases=("style",))
def action_style(runtime, spec):
    target = runtime.object(str(spec["target"]))
    animations = []
    if spec.get("color") is not None:
        animations.append(ApplyMethod(target.set_color, color(spec["color"])))
    if spec.get("opacity") is not None:
        animations.append(
            ApplyMethod(target.set_opacity, float(runtime.resolve(spec["opacity"])))
        )
    if animations:
        runtime.scene.play(*animations, run_time=_runtime(spec))


@action_type("layout.move_to", aliases=("move_to",))
def action_move_to(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("layout.next_to", aliases=("next_to",))
def action_next_to(runtime, spec):
    _play(runtime, make_animation(runtime, spec), spec)


@action_type("layout.arrange", aliases=("arrange",))
def action_arrange(runtime, spec):
    target = runtime.object(str(spec["target"]))
    target.arrange(
        direction(spec.get("direction", "RIGHT")),
        buff=float(runtime.resolve(spec.get("buff", 0.25))),
    )


@action_type("dynamic.redraw", aliases=("dynamic_redraw",))
def action_dynamic_redraw(runtime, spec):
    target_id = str(spec["target"])
    original_spec = runtime.specs.get(target_id)
    if original_spec is None:
        raise DSLReferenceError(f"Objeto sem spec para redraw: {target_id}")
    factory = runtime.factory_for(original_spec)
    dynamic = always_redraw(lambda: factory(runtime, original_spec))
    old = runtime.objects[target_id]
    runtime.scene.remove(old)
    runtime.objects[target_id] = dynamic
    runtime.scene.add(dynamic)
