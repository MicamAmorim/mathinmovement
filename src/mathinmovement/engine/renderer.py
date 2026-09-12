from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from ..config import PROJECT_ROOT
from ..models import ContentRecord, ManifestError


class RenderError(RuntimeError):
    """Falha ao preparar ou executar uma renderização."""


RESOLUTIONS = {
    ("vertical", "draft"): ("360,640", 15),
    ("vertical", "final"): ("1080,1920", 30),
    ("horizontal", "draft"): ("640,360", 15),
    ("horizontal", "final"): ("1920,1080", 30),
}


def _safe_filename(value: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "-" for c in value).strip("-")


def _legacy_adapter(record: ContentRecord) -> dict:
    render = record.manifest.get("render") or {}
    adapter = render.get("adapter") or {}
    if adapter.get("kind") != "legacy_manim_scene":
        raise ManifestError(
            f"{record.id}: ainda não há renderer compatível. "
            "Durante a migração o conteúdo precisa declarar render.adapter.kind=legacy_manim_scene."
        )
    if not adapter.get("source") or not adapter.get("scene"):
        raise ManifestError(f"{record.id}: adapter precisa de source e scene.")
    return adapter


def render_record(
    record: ContentRecord,
    *,
    video_format: str = "vertical",
    quality: str = "draft",
    preview: bool = False,
    dry_run: bool = False,
) -> Path:
    render = record.manifest.get("render") or {}
    allowed = render.get("formats") or ["vertical"]
    if video_format not in allowed:
        raise ManifestError(
            f"{record.id}: formato {video_format!r} não suportado. "
            f"Disponíveis: {', '.join(map(str, allowed))}."
        )
    try:
        resolution, fps = RESOLUTIONS[(video_format, quality)]
    except KeyError as exc:
        raise ManifestError(f"Combinação inválida: {video_format}/{quality}") from exc

    adapter = _legacy_adapter(record)
    source = (PROJECT_ROOT / str(adapter["source"])).resolve()
    if not source.exists():
        raise RenderError(f"{record.id}: cena não encontrada: {source}")

    cwd = (PROJECT_ROOT / str(adapter.get("cwd", "."))).resolve()
    if not cwd.exists():
        raise RenderError(f"{record.id}: diretório de execução não encontrado: {cwd}")

    build_dir = PROJECT_ROOT / ".mim_build" / _safe_filename(record.id) / video_format / quality
    output_dir = PROJECT_ROOT / "media" / record.type / video_format
    output = output_dir / f"{_safe_filename(record.id)}.mp4"

    if not dry_run:
        shutil.rmtree(build_dir, ignore_errors=True)
        build_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        "-m",
        "manim",
        "--format",
        "mp4",
        "--disable_caching",
        "--progress_bar",
        "none",
        "-r",
        resolution,
        "--fps",
        str(fps),
        "--media_dir",
        str(build_dir),
    ]
    if preview:
        cmd.append("-p")
    cmd += [str(source), str(adapter["scene"])]

    env = os.environ.copy()
    if record.type == "qenem":
        # Mantém compatibilidade com o layout responsivo já existente no ENEM.
        env["ENEM_FORMAT"] = video_format
    for key, value in (adapter.get("env") or {}).items():
        env[str(key)] = str(value)

    print(f"[{record.type}] {record.id} · {video_format} · {quality}")
    print(">", subprocess.list2cmdline(cmd))

    if dry_run:
        print(f"Saída normalizada: {output}")
        return output

    result = subprocess.run(cmd, cwd=cwd, env=env)
    if result.returncode:
        raise RenderError(f"{record.id}: Manim terminou com código {result.returncode}.")

    candidates = [
        path
        for path in build_dir.rglob("*.mp4")
        if "partial_movie_files" not in path.parts
    ]
    if not candidates:
        raise RenderError(f"{record.id}: Manim terminou sem produzir MP4 em {build_dir}.")

    rendered = max(candidates, key=lambda p: (p.stat().st_mtime_ns, p.stat().st_size))
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(rendered, output)
    print(f"OK: {output}")
    return output
