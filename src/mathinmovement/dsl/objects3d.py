from __future__ import annotations

import numpy as np
from manim import (
    Arrow3D,
    Cube,
    Dot3D,
    Line3D,
    Prism,
    Rectangle,
    ThreeDAxes,
)

from .errors import DSLError
from .objects2d import color, point, style
from .registry import object_type


_X = np.array([1.0, 0.0, 0.0])
_Y = np.array([0.0, 1.0, 0.0])
_Z = np.array([0.0, 0.0, 1.0])


def _axis(runtime, value):
    axis = point(runtime, value)
    norm = float(np.linalg.norm(axis))
    if norm == 0:
        raise DSLError("Eixo 3D não pode ser o vetor zero.")
    return axis / norm


def apply_layout_3d(runtime, mob, spec):
    """Aplica transformações espaciais sem achatar o objeto no plano XY."""
    if spec.get("at") is not None:
        mob.move_to(point(runtime, spec["at"]))
    if spec.get("shift") is not None:
        mob.shift(point(runtime, spec["shift"]))
    if spec.get("scale") is not None:
        mob.scale(float(runtime.resolve(spec["scale"])))
    if spec.get("stretch") is not None:
        stretch = spec["stretch"]
        if isinstance(stretch, dict):
            factor = float(runtime.resolve(stretch.get("factor", 1)))
            dim = int(stretch.get("dim", 0))
        else:
            factor = float(runtime.resolve(stretch))
            dim = 0
        mob.stretch(factor, dim)

    rotations = (
        ("rotate_x", _X),
        ("rotate_y", _Y),
        ("rotate_z", _Z),
    )
    for key, axis in rotations:
        if spec.get(key) is not None:
            mob.rotate(float(runtime.resolve(spec[key])), axis=axis)

    rotate = spec.get("rotate")
    if rotate is not None:
        if isinstance(rotate, dict):
            angle = float(runtime.resolve(rotate.get("angle", 0)))
            axis = _axis(runtime, rotate.get("axis", [0, 0, 1]))
            about_point = (
                point(runtime, rotate["about_point"])
                if rotate.get("about_point") is not None
                else mob.get_center()
            )
            mob.rotate(angle, axis=axis, about_point=about_point)
        else:
            mob.rotate(float(runtime.resolve(rotate)), axis=_Z)

    if spec.get("opacity") is not None:
        mob.set_opacity(float(runtime.resolve(spec["opacity"])))
    return mob


def _solid_style(spec):
    kwargs = style(spec)
    base_color = color(spec.get("fill_color", spec.get("color", "cyan")))
    kwargs.setdefault("color", color(spec.get("color", "cyan")))
    kwargs.setdefault("fill_color", base_color)
    return kwargs


@object_type(
    "3d.cube",
    aliases=("cube3d",),
    description="Cubo tridimensional real renderizado pela ThreeDCamera.",
)
def make_cube(runtime, spec):
    return apply_layout_3d(
        runtime,
        Cube(
            side_length=float(
                runtime.resolve(spec.get("side", spec.get("side_length", 2)))
            ),
            **_solid_style(spec),
        ),
        spec,
    )


@object_type(
    "3d.prism",
    aliases=("prism3d",),
    description="Prisma retangular 3D com dimensões [x, y, z].",
)
def make_prism(runtime, spec):
    dimensions = runtime.resolve(spec.get("dimensions", [2, 1, 1]))
    if not isinstance(dimensions, (list, tuple)) or len(dimensions) != 3:
        raise DSLError("3d.prism.dimensions deve conter [x, y, z].")
    return apply_layout_3d(
        runtime,
        Prism(
            dimensions=[float(value) for value in dimensions],
            **_solid_style(spec),
        ),
        spec,
    )


@object_type(
    "3d.dot",
    aliases=("dot3d",),
    description="Ponto esférico em coordenadas 3D.",
)
def make_dot3d(runtime, spec):
    return apply_layout_3d(
        runtime,
        Dot3D(
            point=point(runtime, spec.get("point", spec.get("at", [0, 0, 0]))),
            radius=float(runtime.resolve(spec.get("radius", 0.08))),
            color=color(spec.get("color", "white")),
        ),
        {key: value for key, value in spec.items() if key != "at"},
    )


@object_type(
    "3d.line",
    aliases=("line3d",),
    description="Segmento tridimensional entre dois pontos.",
)
def make_line3d(runtime, spec):
    return apply_layout_3d(
        runtime,
        Line3D(
            start=point(runtime, spec["start"]),
            end=point(runtime, spec["end"]),
            thickness=float(runtime.resolve(spec.get("thickness", 0.025))),
            color=color(spec.get("color", "white")),
        ),
        spec,
    )


@object_type(
    "3d.arrow",
    aliases=("arrow3d",),
    description="Seta tridimensional entre dois pontos.",
)
def make_arrow3d(runtime, spec):
    kwargs = {
        "thickness": float(runtime.resolve(spec.get("thickness", 0.025))),
        "color": color(spec.get("color", "white")),
    }
    if spec.get("height") is not None:
        kwargs["height"] = float(runtime.resolve(spec["height"]))
    if spec.get("base_radius") is not None:
        kwargs["base_radius"] = float(runtime.resolve(spec["base_radius"]))
    return apply_layout_3d(
        runtime,
        Arrow3D(
            start=point(runtime, spec["start"]),
            end=point(runtime, spec["end"]),
            **kwargs,
        ),
        spec,
    )


@object_type(
    "3d.plane",
    aliases=("plane3d",),
    description=(
        "Plano retangular 3D. Use rotate_x/rotate_y/rotate_z ou rotate.axis "
        "para orientar o plano no espaço."
    ),
)
def make_plane3d(runtime, spec):
    return apply_layout_3d(
        runtime,
        Rectangle(
            width=float(runtime.resolve(spec.get("width", 3))),
            height=float(runtime.resolve(spec.get("height", 2))),
            **_solid_style(spec),
        ),
        spec,
    )


@object_type(
    "3d.axes",
    aliases=("axes3d",),
    description="Sistema cartesiano tridimensional.",
)
def make_axes3d(runtime, spec):
    axis_config = dict(spec.get("axis_config") or {})
    if axis_config.get("color") is not None:
        axis_config["color"] = color(axis_config["color"])

    kwargs = {
        "x_range": runtime.resolve(spec.get("x_range", [-4, 4, 1])),
        "y_range": runtime.resolve(spec.get("y_range", [-4, 4, 1])),
        "z_range": runtime.resolve(spec.get("z_range", [-4, 4, 1])),
        "x_length": float(runtime.resolve(spec.get("x_length", 8))),
        "y_length": float(runtime.resolve(spec.get("y_length", 8))),
        "z_length": float(runtime.resolve(spec.get("z_length", 6))),
        "axis_config": axis_config,
    }
    return apply_layout_3d(runtime, ThreeDAxes(**kwargs), spec)
