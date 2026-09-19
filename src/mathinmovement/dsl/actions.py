from __future__ import annotations

import numpy as np
from manim import (
    ApplyMethod,
    Create,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    OUT,
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
        axis = (
            point(runtime, spec["axis"])
            if spec.get("axis") is not None
            else OUT
        )
        return Rotate(
            target,
            float(runtime.resolve(spec.get("angle", 0))),
            axis=axis,
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
        about = (
            point(runtime, spec["about_point"])
            if spec.get("about_point") is not None
            else np.zeros(3)
        )
        axis = (
            point(runtime, spec["axis"])
            if spec.get("axis") is not None
            else OUT
        )
        return UpdateFromAlphaFunc(
            target,
            lambda mob, alpha: mob.become(
                original.copy()
                .rotate(angle * alpha, axis=axis, about_point=about)
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


def _scene_method(runtime, name):
    method = getattr(runtime.scene, name, None)
    if method is None:
        raise DSLError(
            f"Ação 3D exige cena compatível com ThreeDScene: {name}."
        )
    return method


def _camera_kwargs(runtime, spec):
    kwargs = {}
    for key in ("phi", "theta", "gamma", "zoom", "focal_distance"):
        if spec.get(key) is not None:
            kwargs[key] = float(runtime.resolve(spec[key]))
    if spec.get("frame_center") is not None:
        kwargs["frame_center"] = point(runtime, spec["frame_center"])
    return kwargs


@action_type(
    "camera.set_orientation",
    aliases=("set_camera_orientation",),
    description="Define instantaneamente a orientação da câmera 3D.",
)
def action_camera_set_orientation(runtime, spec):
    _scene_method(runtime, "set_camera_orientation")(
        **_camera_kwargs(runtime, spec)
    )


@action_type(
    "camera.move",
    aliases=("move_camera",),
    description="Anima a câmera 3D até uma nova orientação/zoom.",
)
def action_camera_move(runtime, spec):
    kwargs = _camera_kwargs(runtime, spec)
    kwargs["run_time"] = _runtime(spec)
    kwargs["rate_func"] = _rate(spec)
    _scene_method(runtime, "move_camera")(**kwargs)


@action_type(
    "camera.begin_ambient_rotation",
    aliases=("begin_ambient_camera_rotation",),
    description="Inicia rotação ambiente da câmera 3D.",
)
def action_camera_begin_ambient_rotation(runtime, spec):
    _scene_method(runtime, "begin_ambient_camera_rotation")(
        rate=float(runtime.resolve(spec.get("rate", 0.02))),
        about=str(spec.get("about", "theta")),
    )
    runtime.scene._mim_camera_motion_active = True


@action_type(
    "camera.stop_ambient_rotation",
    aliases=("stop_ambient_camera_rotation",),
    description="Interrompe rotação ambiente da câmera 3D.",
)
def action_camera_stop_ambient_rotation(runtime, spec):
    _scene_method(runtime, "stop_ambient_camera_rotation")(
        about=str(spec.get("about", "theta")),
    )
    runtime.scene._mim_camera_motion_active = False


@action_type(
    "scene.fixed_in_frame",
    aliases=("fixed_in_frame",),
    description="Mantém um objeto 2D fixo no quadro enquanto a câmera 3D se move.",
)
def action_fixed_in_frame(runtime, spec):
    _scene_method(runtime, "add_fixed_in_frame_mobjects")(
        runtime.object(str(spec["target"]))
    )


@action_type(
    "scene.fixed_orientation",
    aliases=("fixed_orientation",),
    description="Mantém a orientação visual do objeto diante da câmera 3D.",
)
def action_fixed_orientation(runtime, spec):
    _scene_method(runtime, "add_fixed_orientation_mobjects")(
        runtime.object(str(spec["target"]))
    )


@action_type(
    "scene.unfix_in_frame",
    aliases=("unfix_in_frame",),
    description="Remove um objeto do conjunto fixo ao quadro da câmera 3D.",
)
def action_unfix_in_frame(runtime, spec):
    _scene_method(runtime, "remove_fixed_in_frame_mobjects")(
        runtime.object(str(spec["target"]))
    )


@action_type(
    "scene.unfix_orientation",
    aliases=("unfix_orientation",),
    description="Remove a orientação fixa de um objeto diante da câmera 3D.",
)
def action_unfix_orientation(runtime, spec):
    _scene_method(runtime, "remove_fixed_orientation_mobjects")(
        runtime.object(str(spec["target"]))
    )


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


def _lesson_step(runtime, index):
    steps = list((runtime.scene.manifest.get("lesson") or {}).get("steps") or [])
    try:
        return steps[int(index)]
    except (IndexError, ValueError, TypeError) as exc:
        raise DSLError(f"Etapa didática inexistente: {index!r}") from exc


@action_type("didactic.header", aliases=("header",))
def action_didactic_header(runtime, spec):
    del spec
    runtime.scene.demo_header_from_manifest()


@action_type("didactic.hide_intro", aliases=("hide_intro",))
def action_didactic_hide_intro(runtime, spec):
    del spec
    runtime.scene.demo_hide_intro_formula()


@action_type("didactic.caption", aliases=("caption",))
def action_didactic_caption(runtime, spec):
    text = spec.get("text")
    if text is None and spec.get("step") is not None:
        text = _lesson_step(runtime, spec["step"]).get("narration", "")
    if text is None and spec.get("presentation") is not None:
        captions = (runtime.scene.manifest.get("presentation") or {}).get("captions") or {}
        text = captions.get(str(spec["presentation"]), "")
    if text is None:
        raise DSLError("caption exige text, step ou presentation.")
    runtime.scene.demo_caption(
        str(text),
        color=color(spec.get("color", "white")),
        size=int(runtime.resolve(spec.get("size", 25))),
        y=float(runtime.resolve(spec.get("y", -3.28))),
    )


@action_type("didactic.equation", aliases=("equation",))
def action_didactic_equation(runtime, spec):
    tex = spec.get("tex")
    if tex is None and spec.get("step") is not None:
        tex = _lesson_step(runtime, spec["step"]).get("math")
    if not tex:
        raise DSLError("equation exige tex ou step com math.")
    runtime.scene.demo_equation(
        str(tex),
        color=color(spec.get("color", "white")),
        size=int(runtime.resolve(spec.get("size", 50))),
        y=float(runtime.resolve(spec.get("y", -4.75))),
        transform=bool(spec.get("transform", True)),
    )


@action_type("didactic.end", aliases=("end",))
def action_didactic_end(runtime, spec):
    runtime.scene.demo_end(
        pause=float(runtime.resolve(spec.get("pause", 2.4)))
    )
