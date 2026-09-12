from __future__ import annotations

import os
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


def render_record(
    record: ContentRecord,
    *,
    video_format: str = "vertical",
    quality: str = "draft",
    preview: bool = False,
    dry_run: bool = False,
    fast_preview: bool = False,
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

    build_dir = PROJECT_ROOT / ".mim_build" / _safe_filename(record.id) / video_format / quality
    output_dir = PROJECT_ROOT / "media" / record.type / video_format
    output = output_dir / f"{_safe_filename(record.id)}.mp4"
    wrapper = build_dir / "_mim_scene.py"

    if not dry_run:
        shutil.rmtree(build_dir, ignore_errors=True)
        build_dir.mkdir(parents=True, exist_ok=True)
        wrapper.write_text(
            "from mathinmovement.engine.scene import UnifiedContentScene\n"
            "class MIMScene(UnifiedContentScene):\n"
            "    pass\n",
            encoding="utf-8",
        )

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
    cmd += [str(wrapper), "MIMScene"]

    env = os.environ.copy()
    env["MIM_CONTENT_ID"] = record.id
    env["MIM_FORMAT"] = video_format
    env["MIM_QUALITY"] = quality
    if fast_preview:
        env["MIM_FAST_PREVIEW"] = "1"

    print(f"[{record.type}] {record.id} · {video_format} · {quality}" + (" · FAST" if fast_preview else ""))
    print(">", subprocess.list2cmdline(cmd))

    if dry_run:
        print(f"Saída normalizada: {output}")
        return output

    result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env)
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
