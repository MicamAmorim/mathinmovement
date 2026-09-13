from __future__ import annotations

import shutil
import zipfile
from datetime import datetime
from pathlib import Path

import yaml

from .models import ManifestError
from .registry import validate_manifest
from .dsl.runtime import validate_program


def _demo_manifest(content_id: str, title: str) -> dict:
    program = {
        "dsl_version": "1.0",
        "objects": [
            {
                "id": "shape",
                "type": "polygon",
                "points": [[-2.5, -1.0], [2.5, -1.0], [0.0, 2.0]],
                "color": "cyan",
                "fill_opacity": 0.16,
                "stroke_width": 3,
            },
            {
                "id": "formula",
                "type": "math",
                "tex": r"A=\frac{bh}{2}",
                "font_size": 42,
                "color": "white",
                "at": [0, -3.5],
            },
        ],
        "timeline": [
            {"op": "create", "target": "shape", "run_time": 1.4},
            {"op": "write", "target": "formula", "run_time": 1.0},
            {"op": "wait", "duration": 1.2},
        ],
    }
    return {
        "schema_version": 1,
        "id": content_id,
        "type": "demo",
        "status": "draft",
        "title": title,
        "tags": ["draft", "demo"],
        "lesson": {
            "objective": "Substitua pelo objetivo didático.",
            "steps": [
                {
                    "narration": "Substitua pela primeira etapa da demonstração.",
                    "math": r"A=\frac{bh}{2}",
                }
            ],
        },
        "result": {"math": r"A=\frac{bh}{2}"},
        "render": {
            "production_engine": "dsl",
            "formats": ["vertical"],
            "default_format": "vertical",
        },
        "narration": {"enabled": False},
        "visual_program": program,
    }


def _qenem_manifest(
    content_id: str,
    title: str,
    *,
    year: int,
    question_number: int,
) -> dict:
    concept = {
        "dsl_version": "1.0",
        "objects": [
            {
                "id": "formula",
                "type": "math",
                "tex": r"A=3^2=9",
                "font_size": 42,
                "color": "white",
                "at": [0, 0],
            }
        ],
        "timeline": [],
    }
    return {
        "schema_version": 1,
        "id": content_id,
        "type": "qenem",
        "status": "draft",
        "title": title,
        "tags": ["draft", "qenem"],
        "exam": {
            "name": "Exemplo",
            "year": year,
            "canonical_id": content_id,
            "question_number": question_number,
            "booklet": "Substitua pela fonte correta",
        },
        "question": {
            "stem": "Substitua pelo enunciado completo.",
            "options": {
                "A": "Alternativa A",
                "B": "Alternativa B",
                "C": "Alternativa C",
                "D": "Alternativa D",
                "E": "Alternativa E",
            },
            "answer": "A",
        },
        "solution": {
            "data": ["Substitua pelos dados úteis."],
            "goal": "Substitua pelo objetivo da questão.",
            "strategy": ["Substitua pela estratégia de resolução."],
            "steps": [
                {
                    "label": "Primeiro passo",
                    "math": r"A=3^2=9",
                }
            ],
            "final_answer": "A",
        },
        "visuals": {
            "concept": {
                "note": "Substitua pela interpretação visual.",
                "program": concept,
                "show": ["formula"],
            }
        },
        "render": {
            "production_engine": "dsl",
            "formats": ["vertical"],
            "default_format": "vertical",
        },
        "narration": {"enabled": False},
    }


def scaffold_content(
    content_type: str,
    content_id: str,
    *,
    output_dir: str | Path | None = None,
    title: str | None = None,
    year: int | None = None,
    question_number: int = 1,
    package: bool = False,
    force: bool = False,
) -> tuple[Path, Path | None]:
    if content_type not in {"demo", "qenem"}:
        raise ManifestError("scaffold aceita apenas 'demo' ou 'qenem'.")
    content_id = str(content_id).strip()
    if not content_id:
        raise ManifestError("ID do conteúdo não pode ser vazio.")

    title = title or content_id.replace("-", " ").strip().title()
    destination = Path(output_dir) if output_dir else Path.cwd() / content_id

    if destination.exists():
        if not force:
            raise ManifestError(
                f"Destino já existe: {destination}. Use --force para substituir."
            )
        if destination.is_dir():
            shutil.rmtree(destination)
        else:
            destination.unlink()

    if content_type == "demo":
        manifest = _demo_manifest(content_id, title)
    else:
        manifest = _qenem_manifest(
            content_id,
            title,
            year=year or datetime.now().year,
            question_number=question_number,
        )

    validate_manifest(manifest, source=f"scaffold:{content_id}")
    if content_type == "demo":
        validate_program(manifest["visual_program"])
    else:
        validate_program(manifest["visuals"]["concept"]["program"])

    destination.mkdir(parents=True, exist_ok=False)
    (destination / "assets").mkdir()
    manifest_path = destination / "manifest.yaml"
    manifest_path.write_text(
        yaml.safe_dump(
            manifest,
            allow_unicode=True,
            sort_keys=False,
            width=100,
        ),
        encoding="utf-8",
    )

    package_path: Path | None = None
    if package:
        suffix = ".demo" if content_type == "demo" else ".qenem"
        package_path = destination.parent / f"{content_id}{suffix}"
        if package_path.exists() and not force:
            raise ManifestError(
                f"Pacote já existe: {package_path}. Use --force para substituir."
            )
        with zipfile.ZipFile(
            package_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for path in sorted(destination.rglob("*")):
                if path.is_file():
                    archive.write(
                        path,
                        path.relative_to(destination).as_posix(),
                    )

    return destination, package_path
