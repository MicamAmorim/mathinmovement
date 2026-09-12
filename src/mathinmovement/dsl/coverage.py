from __future__ import annotations

from dataclasses import dataclass


DEMO_USAGE = {
    "area-triangulo": {"line","dashed_line","polygon","create","fade_out","write","translate","rotate","style","copy"},
    "area-paralelogramo": {"line","dashed_line","polygon","rectangle","brace","create","fade_out","translate"},
    "area-trapezio": {"polygon","brace","create","fade_in","fade_out","write","translate","rotate","style","copy"},
    "area-losango": {"line","polygon","rectangle","brace","create","fade_in","fade_out","write","rigid_motion"},
    "area-triangulo-equilatero": {"line","dashed_line","polygon","create","fade_in","write"},
    "area-poligonos-regulares": {"line","polygon","regular_polygon","create","write","lagged","highlight"},
    "comprimento-circunferencia-pi": {"line","circle","create","fade_out","write","tracker","dynamic_redraw","animate_value"},
    "area-circulo": {"sector","create","fade_out","rigid_motion","lagged"},
    "comprimento-arco": {"line","circle","arc","create","fade_out","write","style","lagged","copy"},
    "area-setor-circular": {"circle","arc","sector","create","fade_in","fade_out","write","style","lagged","copy"},
    "area-coroa-circular": {"line","circle","create","write","highlight"},
    "teorema-pitagoras": {"line","polygon","square","create","fade_in","write","lagged","copy"},
    "relacoes-metricas-triangulo-retangulo": {"line","dashed_line","polygon","angle","create","fade_in","write","highlight"},
    "razoes-trigonometricas-semelhanca": {"line","polygon","arc","create","write","transform_from_copy"},
    "lei-senos": {"line","dashed_line","polygon","create","fade_out","write"},
    "lei-cossenos": {"line","dashed_line","polygon","create","write","highlight"},
    "area-triangulo-seno": {"line","dashed_line","polygon","create","fade_in","write"},
    "escalas-comprimentos-areas-volumes": {"line","square","create","fade_in","fade_out","write","lagged","transform_from_copy","copy"},
    "relacao-euler-poliedros": {"line","dot","create","fade_in","fade_out","lagged"},
    "diagonal-paralelepipedo": {"line","polygon","create","fade_in","fade_out","write","style"},
    "area-prismas-planificacao": {"polygon","rectangle","brace","regular_polygon","create","lagged","transform"},
    "volume-prismas": {"polygon","brace","regular_polygon","create","fade_in","write","lagged","transform_from_copy","stretch","opacity","copy"},
    "area-cilindro": {"polygon","rectangle","circle","brace","create","lagged","transform"},
    "volume-cilindro": {"line","ellipse","create","lagged","transform_from_copy","copy"},
    "area-piramides-regulares": {"line","dashed_line","polygon","create","fade_in","fade_out","write","lagged"},
    "volume-piramide": {"line","polygon","square","dot","create","fade_in","highlight","copy"},
    "area-cone": {"line","ellipse","arc","sector","create","fade_in","fade_out","write"},
    "volume-cone": {"line","polygon","ellipse","regular_polygon","create","fade_in","lagged"},
    "volume-esfera": {"line","polygon","rectangle","arc","create","tracker","dynamic_redraw","animate_value"},
    "area-esfera": {"line","dashed_line","circle","create","fade_out","write"},
}

QENEM_USAGE = {
    "ENEM-2021-MT-11": {"line","dashed_line","polygon","next_to","move_to"},
    "ENEM-2021-MT-12": {"polygon","arc","arrow","double_arrow","next_to","move_to","translate","line","dashed_line"},
    "ENEM-2021-MT-13": {"polygon","square","circle","arrange"},
    "ENEM-2021-MT-17": {"line","rectangle","move_to"},
    "ENEM-2021-MT-18": {"line","ellipse","next_to","move_to","translate"},
    "ENEM-2021-MT-28": {"line","polygon","rectangle","next_to","move_to","translate","scale","square","arrow"},
    "ENEM-2022-MT-07": {"line","ellipse","next_to","move_to","translate"},
    "ENEM-2022-MT-10": {"line","dot","axes","next_to","dashed_line"},
    "ENEM-2022-MT-12": {"circle","arrange","scale"},
    "ENEM-2022-MT-13": {"line","dashed_line","ellipse","next_to","move_to"},
    "ENEM-2022-MT-25": {"square","arrow","translate","scale"},
    "ENEM-2022-MT-32": {"line","rectangle","move_to"},
    "ENEM-2022-MT-34": {"line","ellipse","next_to","move_to","translate"},
    "ENEM-2023-MT-04": {"polygon","move_to","line","rectangle"},
    "ENEM-2023-MT-06": {"polygon","circle","dot","next_to","line","sector","move_to"},
    "ENEM-2023-MT-07": {"square","arrow","double_arrow","move_to","line","rectangle"},
    "ENEM-2023-MT-15": {"line","dashed_line","polygon","ellipse","move_to","translate"},
    "ENEM-2023-MT-29": {"line","circle","dot","arrow","curved_arrow","next_to","axes","graph","translate","polyline","text","arrange"},
    "ENEM-2023-MT-31": {"line","ellipse","next_to","move_to","translate"},
    "ENEM-2023-MT-33": {"rectangle","circle","text","move_to","translate","line","ellipse","next_to"},
    "ENEM-2023-MT-41": {"line","move_to"},
    "ENEM-2023-MT-42": {"axes","polyline","move_to","scale"},
    "ENEM-2023-MT-44": {"polygon","arc","arc_between_points","move_to"},
    "ENEM-2024-MT-02": {"line","sector","move_to"},
    "ENEM-2024-MT-05": {"square","arrow","translate","scale"},
    "ENEM-2024-MT-11": {"line","ellipse","next_to","move_to","translate"},
    "ENEM-2024-MT-14": {"line","polygon","arrow","curved_arrow","move_to","dashed_line"},
    "ENEM-2024-MT-30": {"line","rectangle","ellipse","next_to","translate","scale","move_to"},
    "ENEM-2024-MT-34": {"polygon","square","arrange"},
    "ENEM-2025-MT-08": {"rectangle","circle","arc","dot","text","next_to","move_to","scale"},
}

QENEM_COMMON = {
    "text","math","rounded_rectangle","create","fade_in","fade_out",
    "write","lagged","replacement_transform","highlight",
}

DEMO_VALIDATION_SET = (
    "area-triangulo",
    "area-losango",
    "comprimento-circunferencia-pi",
    "relacoes-metricas-triangulo-retangulo",
    "area-prismas-planificacao",
    "volume-prismas",
    "volume-piramide",
    "area-cone",
)

QENEM_VALIDATION_SET = (
    "ENEM-2021-MT-11",
    "ENEM-2023-MT-06",
    "ENEM-2023-MT-07",
    "ENEM-2023-MT-29",
    "ENEM-2023-MT-44",
    "ENEM-2024-MT-30",
)


@dataclass(frozen=True, slots=True)
class CoverResult:
    selected: tuple[str, ...]
    universe: frozenset[str]


def universe(usage):
    return set().union(*usage.values()) if usage else set()


def covered_by(usage, selected):
    return set().union(*(usage[item] for item in selected)) if selected else set()


def minimum_cover(usage):
    """Set cover exato com branch-and-bound sobre bitmasks."""
    names = tuple(usage)
    features = tuple(sorted(universe(usage)))
    if not features:
        return CoverResult((), frozenset())

    bit = {feature: 1 << i for i, feature in enumerate(features)}
    masks = [
        sum(bit[feature] for feature in usage[name])
        for name in names
    ]
    full = (1 << len(features)) - 1
    candidates = {
        feature: [
            i for i, name in enumerate(names)
            if feature in usage[name]
        ]
        for feature in features
    }

    best = list(range(len(names)))
    seen = {}

    def search(mask, chosen):
        nonlocal best
        if mask == full:
            if len(chosen) < len(best):
                best = list(chosen)
            return
        if len(chosen) >= len(best):
            return
        previous = seen.get(mask)
        if previous is not None and previous <= len(chosen):
            return
        seen[mask] = len(chosen)

        missing = [
            feature for feature in features
            if not (mask & bit[feature])
        ]
        feature = min(
            missing,
            key=lambda item: sum(
                bool(masks[i] & ~mask)
                for i in candidates[item]
                if i not in chosen
            ),
        )
        for index in candidates[feature]:
            if index in chosen:
                continue
            added = masks[index] & ~mask
            if not added:
                continue
            search(mask | masks[index], chosen + (index,))

    search(0, ())
    if not best and full:
        raise RuntimeError("Catálogo sem cobertura possível.")
    selected = tuple(names[i] for i in best)
    return CoverResult(selected, frozenset(features))
