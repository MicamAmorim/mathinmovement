from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Iterable

import yaml

from ..config import CONTENT_ROOT, PROJECT_ROOT
from ..registry import Registry, validate_manifest


LEGACY_DEMO_ROOT = PROJECT_ROOT / "videos"
LEGACY_RENDER_ALL = PROJECT_ROOT / "render_all.py"


def _slug_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^\d+_", "", stem)
    return stem.replace("_", "-")


def _call_name(node: ast.Call) -> str | None:
    func = node.func
    if (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id == "self"
    ):
        return func.attr
    return None


def _literal_arg(call: ast.Call, index: int, default: str = "") -> str:
    if len(call.args) <= index:
        return default
    value = ast.literal_eval(call.args[index])
    return str(value)


def _extract_scene_metadata(source_path: Path, expected_scene: str) -> dict:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    scene_class = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == expected_scene:
            scene_class = node
            break
    if scene_class is None:
        raise ValueError(f"{source_path}: classe {expected_scene!r} não encontrada.")

    construct = next(
        (
            node
            for node in scene_class.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == "construct"
        ),
        None,
    )
    if construct is None:
        raise ValueError(f"{source_path}: método construct() não encontrado.")

    header = None
    ordered_with_position: list[tuple[int, int, str, str]] = []
    for node in ast.walk(construct):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name == "header" and header is None:
            header = node
        elif name in {"caption", "equation"}:
            try:
                ordered_with_position.append(
                    (
                        int(getattr(node, "lineno", 0)),
                        int(getattr(node, "col_offset", 0)),
                        name,
                        _literal_arg(node, 0),
                    )
                )
            except Exception:
                pass

    ordered = [
        (kind, value)
        for _, _, kind, value in sorted(ordered_with_position)
    ]

    if header is None:
        raise ValueError(f"{source_path}: self.header(...) não encontrado.")

    number = _literal_arg(header, 0)
    title = _literal_arg(header, 1)
    formula = _literal_arg(header, 2)
    category = _literal_arg(header, 3, "GEOMETRIA")

    steps: list[dict] = []
    current: dict | None = None
    for kind, value in ordered:
        if kind == "caption":
            current = {"narration": value}
            steps.append(current)
        elif current is None:
            steps.append(
                {
                    "narration": "Registre a relação matemática mostrada na demonstração.",
                    "math": value,
                }
            )
        elif "math" not in current:
            current["math"] = value
        else:
            current = {
                "narration": "Continue a dedução algébrica indicada na animação.",
                "math": value,
            }
            steps.append(current)

    if not steps:
        steps = [
            {
                "narration": f"Demonstração visual de {title}.",
                "math": formula,
            }
        ]

    equations = [value for kind, value in ordered if kind == "equation"]
    result_math = equations[-1] if equations else formula

    return {
        "number": number,
        "title": title,
        "formula": formula,
        "category": category,
        "steps": steps,
        "result_math": result_math,
    }


def _load_scene_map() -> list[tuple[int, str, str]]:
    tree = ast.parse(LEGACY_RENDER_ALL.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SCENES"
            for target in node.targets
        ):
            records = ast.literal_eval(node.value)
            if len(records) != 30:
                raise ValueError(
                    f"Esperadas 30 cenas demo no legado; encontradas {len(records)}."
                )
            return records
    raise ValueError("Não foi possível localizar SCENES em render_all.py")


def build_manifest(
    number: int,
    filename: str,
    scene_name: str,
    *,
    status: str = "draft",
) -> dict:
    source_path = LEGACY_DEMO_ROOT / filename
    if not source_path.exists():
        raise ValueError(f"Cena demo legada ausente: {source_path}")

    meta = _extract_scene_metadata(source_path, scene_name)
    content_id = _slug_from_filename(filename)
    category_tag = (
        str(meta["category"])
        .lower()
        .replace("í", "i")
        .replace("â", "a")
        .replace("ã", "a")
        .replace("ó", "o")
        .replace("é", "e")
        .replace("ç", "c")
        .replace(" ", "-")
    )

    manifest = {
        "schema_version": 1,
        "id": content_id,
        "type": "demo",
        "status": status,
        "title": str(meta["title"]),
        "tags": ["demo", category_tag],
        "presentation": {
            "profile": "motion_math_v1",
            "number": f"{int(number):02d}",
            "category": str(meta["category"]),
            "formula": str(meta["formula"]),
            "signature": "MIQUÉIAS AMORIM",
        },
        "lesson": {
            "objective": f'Demonstrar visualmente {str(meta["title"]).lower()}.',
            "steps": meta["steps"],
        },
        "result": {"math": str(meta["result_math"])},
        "render": {
            "production_engine": "compatibility",
            "formats": ["vertical"],
            "default_format": "vertical",
            "native_engine": "unified-v2",
            "native_ready": False,
            "compatibility": {
                "source": f"videos/{filename}",
                "scene": str(scene_name),
                "cwd": ".",
                "formats": ["vertical"],
            },
        },
        "narration": {"enabled": False},
    }
    validate_manifest(manifest, source=content_id)
    return manifest


def migrate_legacy_demos(
    *,
    output_root: Path = CONTENT_ROOT,
    replace: bool = False,
    status: str = "draft",
    only: Iterable[str] = (),
) -> dict:
    scenes = _load_scene_map()
    selected = set(map(str, only))
    all_ids = [_slug_from_filename(filename) for _, filename, _ in scenes]
    if selected:
        unknown = sorted(selected - set(all_ids))
        if unknown:
            raise ValueError("IDs demo não encontrados no legado: " + ", ".join(unknown))

    created: list[str] = []
    skipped: list[str] = []
    output_root = Path(output_root)
    demos_root = output_root / "demos"

    for number, filename, scene_name in scenes:
        content_id = _slug_from_filename(filename)
        if selected and content_id not in selected:
            continue
        destination = demos_root / content_id
        manifest_path = destination / "manifest.yaml"
        if manifest_path.exists() and not replace:
            skipped.append(content_id)
            continue

        manifest = build_manifest(
            number,
            filename,
            scene_name,
            status=status,
        )
        destination.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            yaml.safe_dump(
                manifest,
                allow_unicode=True,
                sort_keys=False,
                width=110,
            ),
            encoding="utf-8",
        )
        created.append(content_id)

    if output_root.resolve() == CONTENT_ROOT.resolve():
        Registry().rebuild()

    return {
        "created": created,
        "skipped": skipped,
        "total_legacy": len(scenes),
    }
