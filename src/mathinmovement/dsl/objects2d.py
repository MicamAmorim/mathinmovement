from __future__ import annotations

import numpy as np
from manim import (
    Angle,
    Arc,
    ArcBetweenPoints,
    Arrow,
    Axes,
    BraceBetweenPoints,
    Circle,
    CurvedArrow,
    DashedLine,
    Dot,
    DoubleArrow,
    Ellipse,
    Line,
    MathTex,
    Polygon,
    Rectangle,
    RegularPolygon,
    RoundedRectangle,
    Sector,
    Square,
    Text,
    VGroup,
    VMobject,
    ValueTracker,
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
)

from .errors import DSLError, DSLReferenceError
from .registry import object_type


PALETTE = {
    "bg": "#0B1020",
    "white": "#EEF2FF",
    "cyan": "#55D6CF",
    "gold": "#FFCC78",
    "muted": "#9CAAC5",
    "pink": "#F28DB2",
    "green": "#8DE2A7",
    "red": "#FF7D7D",
    "blue": "#79A7FF",
}
DIRECTIONS = {
    "ORIGIN": ORIGIN,
    "UP": UP,
    "DOWN": DOWN,
    "LEFT": LEFT,
    "RIGHT": RIGHT,
    "UR": UP + RIGHT,
    "UL": UP + LEFT,
    "DR": DOWN + RIGHT,
    "DL": DOWN + LEFT,
}


def color(value, default=None):
    if value is None:
        return default
    return PALETTE.get(str(value).lower(), value)


def direction(value):
    if value is None:
        return RIGHT
    if isinstance(value, str):
        try:
            return DIRECTIONS[value.upper()]
        except KeyError as exc:
            raise DSLError(f"Direção DSL desconhecida: {value!r}") from exc
    return np.array(value, dtype=float)


def point(runtime, value):
    data = runtime.resolve(value)
    if len(data) == 2:
        data = [data[0], data[1], 0]
    if len(data) != 3:
        raise DSLError(f"Ponto DSL deve ter 2 ou 3 coordenadas: {value!r}")
    return np.array(data, dtype=float)


def style(spec):
    out = {}
    if spec.get("color") is not None:
        out["color"] = color(spec["color"])
    if spec.get("fill_color") is not None:
        out["fill_color"] = color(spec["fill_color"])
    if spec.get("fill_opacity") is not None:
        out["fill_opacity"] = float(spec["fill_opacity"])
    if spec.get("stroke_width") is not None:
        out["stroke_width"] = float(spec["stroke_width"])
    return out


def apply_layout(runtime, mob, spec):
    if spec.get("at") is not None:
        mob.move_to(point(runtime, spec["at"]))
    if spec.get("shift") is not None:
        mob.shift(point(runtime, spec["shift"]))
    if spec.get("scale") is not None:
        mob.scale(float(runtime.resolve(spec["scale"])))
    if spec.get("rotate") is not None:
        mob.rotate(float(runtime.resolve(spec["rotate"])))
    if spec.get("opacity") is not None:
        mob.set_opacity(float(runtime.resolve(spec["opacity"])))
    relation = spec.get("next_to")
    if relation:
        if not isinstance(relation, dict) or not relation.get("target"):
            raise DSLError("next_to exige target.")
        target = runtime.object(str(relation["target"]))
        mob.next_to(
            target,
            direction(relation.get("direction", "RIGHT")),
            buff=float(runtime.resolve(relation.get("buff", 0.25))),
        )
    return mob


@object_type("dynamic.tracker", aliases=("tracker",), description="Escalar animável.")
def make_tracker(runtime, spec):
    return ValueTracker(float(runtime.resolve(spec.get("value", 0))))


@object_type("2d.line", aliases=("line",))
def make_line(runtime, spec):
    return apply_layout(
        runtime,
        Line(point(runtime, spec["start"]), point(runtime, spec["end"]), **style(spec)),
        spec,
    )


@object_type("2d.dashed_line", aliases=("dashed_line",))
def make_dashed_line(runtime, spec):
    return apply_layout(
        runtime,
        DashedLine(point(runtime, spec["start"]), point(runtime, spec["end"]), **style(spec)),
        spec,
    )


@object_type("2d.polygon", aliases=("polygon",))
def make_polygon(runtime, spec):
    points = [point(runtime, p) for p in spec.get("points", [])]
    if len(points) < 3:
        raise DSLError("polygon exige ao menos 3 pontos.")
    return apply_layout(runtime, Polygon(*points, **style(spec)), spec)


@object_type("2d.regular_polygon", aliases=("regular_polygon",))
def make_regular_polygon(runtime, spec):
    return apply_layout(
        runtime,
        RegularPolygon(
            int(runtime.resolve(spec.get("n", 3))),
            radius=float(runtime.resolve(spec.get("radius", 1))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.rectangle", aliases=("rectangle",))
def make_rectangle(runtime, spec):
    return apply_layout(
        runtime,
        Rectangle(
            width=float(runtime.resolve(spec.get("width", 2))),
            height=float(runtime.resolve(spec.get("height", 1))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.rounded_rectangle", aliases=("rounded_rectangle",))
def make_rounded_rectangle(runtime, spec):
    return apply_layout(
        runtime,
        RoundedRectangle(
            width=float(runtime.resolve(spec.get("width", 2))),
            height=float(runtime.resolve(spec.get("height", 1))),
            corner_radius=float(runtime.resolve(spec.get("corner_radius", 0.15))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.square", aliases=("square",))
def make_square(runtime, spec):
    return apply_layout(
        runtime,
        Square(
            side_length=float(runtime.resolve(spec.get("side", spec.get("side_length", 1)))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.circle", aliases=("circle",))
def make_circle(runtime, spec):
    return apply_layout(
        runtime,
        Circle(radius=float(runtime.resolve(spec.get("radius", 1))), **style(spec)),
        spec,
    )


@object_type("2d.ellipse", aliases=("ellipse",))
def make_ellipse(runtime, spec):
    return apply_layout(
        runtime,
        Ellipse(
            width=float(runtime.resolve(spec.get("width", 2))),
            height=float(runtime.resolve(spec.get("height", 1))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.arc", aliases=("arc",))
def make_arc(runtime, spec):
    kwargs = style(spec)
    kwargs.update(
        radius=float(runtime.resolve(spec.get("radius", 1))),
        start_angle=float(runtime.resolve(spec.get("start_angle", 0))),
        angle=float(runtime.resolve(spec.get("angle", np.pi / 2))),
    )
    if spec.get("center") is not None:
        kwargs["arc_center"] = point(runtime, spec["center"])
    return apply_layout(runtime, Arc(**kwargs), spec)


@object_type("2d.sector", aliases=("sector",))
def make_sector(runtime, spec):
    return apply_layout(
        runtime,
        Sector(
            radius=float(runtime.resolve(spec.get("radius", 1))),
            start_angle=float(runtime.resolve(spec.get("start_angle", 0))),
            angle=float(runtime.resolve(spec.get("angle", np.pi / 2))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.arc_between_points", aliases=("arc_between_points",))
def make_arc_between_points(runtime, spec):
    return apply_layout(
        runtime,
        ArcBetweenPoints(
            point(runtime, spec["start"]),
            point(runtime, spec["end"]),
            angle=float(runtime.resolve(spec.get("angle", np.pi / 2))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.dot", aliases=("dot",))
def make_dot(runtime, spec):
    return apply_layout(
        runtime,
        Dot(
            point(runtime, spec.get("point", spec.get("at", [0, 0]))),
            radius=float(runtime.resolve(spec.get("radius", 0.08))),
            **style(spec),
        ),
        {k: v for k, v in spec.items() if k != "at"},
    )


@object_type("2d.arrow", aliases=("arrow",))
def make_arrow(runtime, spec):
    return apply_layout(
        runtime,
        Arrow(
            point(runtime, spec["start"]),
            point(runtime, spec["end"]),
            buff=float(runtime.resolve(spec.get("buff", 0))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.double_arrow", aliases=("double_arrow",))
def make_double_arrow(runtime, spec):
    return apply_layout(
        runtime,
        DoubleArrow(
            point(runtime, spec["start"]),
            point(runtime, spec["end"]),
            buff=float(runtime.resolve(spec.get("buff", 0))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.curved_arrow", aliases=("curved_arrow",))
def make_curved_arrow(runtime, spec):
    return apply_layout(
        runtime,
        CurvedArrow(
            point(runtime, spec["start"]),
            point(runtime, spec["end"]),
            angle=float(runtime.resolve(spec.get("angle", -0.5))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.brace", aliases=("brace",))
def make_brace(runtime, spec):
    return apply_layout(
        runtime,
        BraceBetweenPoints(
            point(runtime, spec["start"]),
            point(runtime, spec["end"]),
            direction(runtime.resolve(spec.get("direction", "DOWN"))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.angle", aliases=("angle",))
def make_angle(runtime, spec):
    vertex = point(runtime, spec["vertex"])
    a = point(runtime, spec["a"])
    b = point(runtime, spec["b"])
    return apply_layout(
        runtime,
        Angle(
            Line(vertex, a),
            Line(vertex, b),
            radius=float(runtime.resolve(spec.get("radius", 0.45))),
            **style(spec),
        ),
        spec,
    )


@object_type("2d.axes", aliases=("axes",))
def make_axes(runtime, spec):
    axis_config = dict(spec.get("axis_config") or {})
    if "color" in axis_config:
        axis_config["color"] = color(axis_config["color"])
    return apply_layout(
        runtime,
        Axes(
            x_range=runtime.resolve(spec.get("x_range", [0, 10, 1])),
            y_range=runtime.resolve(spec.get("y_range", [0, 10, 1])),
            x_length=float(runtime.resolve(spec.get("x_length", 6))),
            y_length=float(runtime.resolve(spec.get("y_length", 4))),
            tips=bool(spec.get("tips", False)),
            axis_config=axis_config,
        ),
        spec,
    )


@object_type("2d.polyline", aliases=("polyline",))
def make_polyline(runtime, spec):
    mob = VMobject(**style(spec))
    mob.set_points_as_corners([point(runtime, p) for p in spec.get("points", [])])
    return apply_layout(runtime, mob, spec)


@object_type("2d.graph", aliases=("graph",))
def make_graph(runtime, spec):
    axes_id = str(spec.get("axes", ""))
    if not axes_id:
        raise DSLError("graph exige referência axes.")
    axes = runtime.object(axes_id)
    expression = str(spec.get("expression", "x"))
    x_range = runtime.resolve(spec.get("x_range", [0, 1]))
    mob = axes.plot(
        lambda x: runtime.eval(expression, {"x": x}),
        x_range=x_range,
        color=color(spec.get("color", "cyan")),
        stroke_width=float(runtime.resolve(spec.get("stroke_width", 3))),
    )
    return apply_layout(runtime, mob, spec)


@object_type("2d.text", aliases=("text",))
def make_text(runtime, spec):
    kwargs = {
        "font_size": float(runtime.resolve(spec.get("font_size", 28))),
        "color": color(spec.get("color", "white")),
    }
    if spec.get("font"):
        kwargs["font"] = str(spec["font"])
    return apply_layout(runtime, Text(str(spec.get("text", "")), **kwargs), spec)


@object_type("2d.math", aliases=("math",))
def make_math(runtime, spec):
    return apply_layout(
        runtime,
        MathTex(
            str(spec.get("tex", spec.get("text", ""))),
            font_size=float(runtime.resolve(spec.get("font_size", 42))),
            color=color(spec.get("color", "white")),
        ),
        spec,
    )


@object_type("layout.group", aliases=("group",))
def make_group(runtime, spec):
    ids = [str(x) for x in spec.get("children", [])]
    try:
        group = VGroup(*[runtime.object(x) for x in ids])
    except DSLReferenceError:
        raise
    arrange = spec.get("arrange")
    if arrange:
        if isinstance(arrange, str):
            arrange = {"direction": arrange}
        group.arrange(
            direction(arrange.get("direction", "RIGHT")),
            buff=float(runtime.resolve(arrange.get("buff", 0.25))),
        )
    return apply_layout(runtime, group, spec)
