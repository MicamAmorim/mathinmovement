from __future__ import annotations

import ast
import json
import runpy
from pathlib import Path
from typing import Iterable

import yaml

from ..config import CONTENT_ROOT, PROJECT_ROOT
from ..registry import Registry, validate_manifest


LEGACY_ENEM_ROOT = PROJECT_ROOT / "enem"


def _load_scene_map(specs: list[dict]) -> dict[str, dict]:
    render_all = LEGACY_ENEM_ROOT / "render_all.py"
    tree = ast.parse(render_all.read_text(encoding="utf-8"))
    scenes = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "SCENES" for t in node.targets):
                scenes = ast.literal_eval(node.value)
                break
    if scenes is None:
        raise ValueError("Não foi possível localizar SCENES em enem/render_all.py")
    if len(scenes) != len(specs):
        raise ValueError(
            f"Quantidade de cenas ({len(scenes)}) difere da quantidade de specs ({len(specs)})."
        )

    result = {}
    for spec, scene_rec in zip(specs, scenes):
        _, filename, scene_name = scene_rec
        result[str(spec["id"])] = {
            "source": f"enem/videos/{filename}",
            "scene": str(scene_name),
            "cwd": "enem",
            "formats": ["vertical", "horizontal"],
        }
    return result


def _load_sources():
    questions = json.loads((LEGACY_ENEM_ROOT / "data" / "questions.json").read_text(encoding="utf-8"))
    specs = runpy.run_path(str(LEGACY_ENEM_ROOT / "specs.py"))["SPECS"]
    narrations_path = LEGACY_ENEM_ROOT / "narrations" / "narrations.json"
    audio_path = LEGACY_ENEM_ROOT / "audio" / "manifest.json"
    narrations = json.loads(narrations_path.read_text(encoding="utf-8")) if narrations_path.exists() else {}
    audio = json.loads(audio_path.read_text(encoding="utf-8")) if audio_path.exists() else {}
    scene_map = _load_scene_map(specs)

    q_by_id = {str(q["canonical_id"]): q for q in questions}
    s_by_id = {str(s["id"]): s for s in specs}
    ids = sorted(set(q_by_id) | set(s_by_id))
    missing_q = [cid for cid in ids if cid not in q_by_id]
    missing_s = [cid for cid in ids if cid not in s_by_id]
    missing_scene = [cid for cid in ids if cid not in scene_map]
    if missing_q or missing_s or missing_scene:
        pieces = []
        if missing_q:
            pieces.append("sem question: " + ", ".join(missing_q))
        if missing_s:
            pieces.append("sem spec: " + ", ".join(missing_s))
        if missing_scene:
            pieces.append("sem cena: " + ", ".join(missing_scene))
        raise ValueError("Fontes legadas inconsistentes: " + "; ".join(pieces))
    return q_by_id, s_by_id, narrations, audio, scene_map


def _segments_for(content_id: str, narrations: dict, audio: dict) -> list[dict]:
    narr = (narrations.get(content_id) or {}).get("segments") or []
    audio_by_key = audio.get(content_id) or {}
    result = []
    for segment in narr:
        key = str(segment["key"])
        rec = audio_by_key.get(key) or {}
        out = {
            "key": key,
            "text": str(segment.get("text", "")),
            "duration": float(rec.get("duration", segment.get("estimated_seconds", 2.5))),
        }
        rel = rec.get("file")
        if rel:
            out["audio"] = str(Path("enem") / rel).replace("\\", "/")
        result.append(out)
    return result


def build_manifest(
    question: dict,
    spec: dict,
    narrations: dict,
    audio: dict,
    compatibility: dict,
    *,
    status: str = "draft",
) -> dict:
    content_id = str(question["canonical_id"])
    visuals = {}
    if spec.get("statement_visual"):
        visuals["statement"] = {
            "renderer": str(spec["statement_visual"]),
            "description": str(question.get("visual_description", "")),
        }
    if spec.get("visual"):
        visuals["concept"] = {
            "renderer": str(spec["visual"]),
            "note": str(spec.get("visual_note", "")),
        }

    manifest = {
        "schema_version": 1,
        "id": content_id,
        "type": "qenem",
        "status": status,
        "title": f'ENEM {question["year"]} — Q{question["question_number"]}',
        "tags": ["enem", f'enem-{question["year"]}'],
        "exam": {
            "name": "ENEM",
            "year": int(question["year"]),
            "canonical_id": content_id,
            "question_number": int(question["question_number"]),
            "booklet": str(question.get("caderno", "")),
        },
        "source": {
            "page": question.get("source_page"),
            "exam_file": question.get("source_exam_file"),
            "answer_key_file": question.get("source_key_file"),
        },
        "question": {
            "stem": str(question["stem"]),
            "options": {letter: question["options"][letter] for letter in "ABCDE"},
            "answer": str(question["answer"]),
        },
        "solution": {
            "data": list(spec.get("data") or []),
            "goal": str(spec.get("goal", "")),
            "hook": str(spec.get("hook", "")),
            "strategy": list(spec.get("plan") or []),
            "steps": [
                {"label": str(label), "math": str(math)}
                for label, math in (spec.get("steps") or [])
            ],
            "final_answer": str(spec["answer"]),
        },
        "visuals": visuals,
        "render": {
            "production_engine": "compatibility",
            "formats": ["vertical", "horizontal"],
            "native_formats": ["vertical", "horizontal"],
            "default_format": "vertical",
            "native_engine": "unified-v2",
            "native_ready": False,
            "compatibility": compatibility,
        },
        "narration": {
            "enabled": bool((narrations.get(content_id) or {}).get("segments")),
            "language": "pt-BR",
            "voice": "pt-BR-AntonioNeural",
            "segments": _segments_for(content_id, narrations, audio),
        },
    }
    validate_manifest(manifest, source=content_id)
    return manifest


def migrate_legacy_enem(
    *,
    output_root: Path = CONTENT_ROOT,
    replace: bool = False,
    status: str = "draft",
    only: Iterable[str] = (),
) -> dict:
    """Migra o ENEM legado preservando paridade visual como engine de produção."""
    q_by_id, s_by_id, narrations, audio, scene_map = _load_sources()
    selected = set(map(str, only))
    ids = sorted(q_by_id)
    if selected:
        unknown = sorted(selected - set(ids))
        if unknown:
            raise ValueError("IDs não encontrados no legado: " + ", ".join(unknown))
        ids = [cid for cid in ids if cid in selected]

    output_root = Path(output_root)
    enem_root = output_root / "enem"

    created = []
    skipped = []
    for content_id in ids:
        destination = enem_root / content_id
        manifest_path = destination / "manifest.yaml"
        if manifest_path.exists() and not replace:
            skipped.append(content_id)
            continue

        manifest = build_manifest(
            q_by_id[content_id],
            s_by_id[content_id],
            narrations,
            audio,
            scene_map[content_id],
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
        "total_legacy": len(q_by_id),
    }
