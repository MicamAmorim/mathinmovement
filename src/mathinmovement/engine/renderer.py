from __future__ import annotations

import hashlib
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


def _short_build_dir(
    record: ContentRecord,
    *,
    engine: str,
    video_format: str,
    quality: str,
) -> Path:
    """Return a deterministic short build path, avoiding Windows MAX_PATH issues."""
    digest = hashlib.sha1(record.id.encode("utf-8")).hexdigest()[:10]
    engine_code = "n" if engine == "native" else "c"
    format_code = "v" if video_format == "vertical" else "h"
    quality_code = "d" if quality == "draft" else "f"
    return (
        PROJECT_ROOT
        / ".mim_build"
        / engine_code
        / digest
        / format_code
        / quality_code
    )


def probe_duration(path: Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe or not path.exists():
        return None
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return None
    try:
        return float(result.stdout.strip())
    except (TypeError, ValueError):
        return None


def _resolve_engine(record: ContentRecord, requested: str) -> tuple[str, str]:
    render = record.manifest.get("render") or {}
    production = str(render.get("production_engine", "native"))
    if requested == "production":
        return production, "media"
    if requested == "native":
        return "native", "media_native"
    if requested == "compatibility":
        return "compatibility", "media_compatibility"
    raise ManifestError(f"Engine desconhecido: {requested!r}")


def _native_command(
    record: ContentRecord,
    *,
    video_format: str,
    quality: str,
    preview: bool,
    build_dir: Path,
) -> tuple[list[str], dict[str, str], Path]:
    render = record.manifest.get("render") or {}
    if render.get("native_ready") is False:
        raise ManifestError(
            f"{record.id}: renderer nativo ainda não foi portado/validado."
        )
    allowed = render.get("native_formats") or render.get("formats") or ["vertical"]
    if video_format not in allowed:
        raise ManifestError(
            f"{record.id}: renderer nativo não suporta {video_format!r}. "
            f"Disponíveis: {', '.join(map(str, allowed))}."
        )

    wrapper = build_dir / "_mim_scene.py"
    wrapper.write_text(
        "from mathinmovement.engine.scene import UnifiedContentScene\n"
        "class MIMScene(UnifiedContentScene):\n"
        "    pass\n",
        encoding="utf-8",
    )

    resolution, fps = RESOLUTIONS[(video_format, quality)]
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
    return cmd, env, PROJECT_ROOT


def _compatibility_command(
    record: ContentRecord,
    *,
    video_format: str,
    quality: str,
    preview: bool,
    build_dir: Path,
) -> tuple[list[str], dict[str, str], Path]:
    render = record.manifest.get("render") or {}
    compat = render.get("compatibility") or {}
    if not compat:
        raise ManifestError(
            f"{record.id}: não existe renderer de compatibilidade configurado."
        )

    allowed = compat.get("formats") or ["vertical"]
    if video_format not in allowed:
        hint = ""
        native = render.get("native_formats") or render.get("formats") or []
        if video_format in native:
            hint = f" Use --engine native para testar {video_format} no renderer novo."
        raise ManifestError(
            f"{record.id}: produção/paridade não suporta {video_format!r}. "
            f"Disponíveis: {', '.join(map(str, allowed))}.{hint}"
        )

    source = (PROJECT_ROOT / str(compat.get("source", ""))).resolve()
    scene = str(compat.get("scene", "")).strip()
    cwd = (PROJECT_ROOT / str(compat.get("cwd", "."))).resolve()
    if not source.exists():
        raise RenderError(f"{record.id}: cena de compatibilidade não encontrada: {source}")
    if not scene:
        raise ManifestError(f"{record.id}: render.compatibility.scene está vazio.")
    if not cwd.exists():
        raise RenderError(f"{record.id}: cwd de compatibilidade não existe: {cwd}")

    resolution, fps = RESOLUTIONS[(video_format, quality)]
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
    cmd += [str(source), scene]

    env = os.environ.copy()
    if record.type == "qenem":
        env["ENEM_FORMAT"] = video_format
    for key, value in (compat.get("env") or {}).items():
        env[str(key)] = str(value)
    return cmd, env, cwd


def render_record(
    record: ContentRecord,
    *,
    video_format: str = "vertical",
    quality: str = "draft",
    preview: bool = False,
    dry_run: bool = False,
    fast_preview: bool = False,
    render_engine: str = "production",
) -> Path:
    try:
        RESOLUTIONS[(video_format, quality)]
    except KeyError as exc:
        raise ManifestError(f"Combinação inválida: {video_format}/{quality}") from exc

    resolved_engine, output_root_name = _resolve_engine(record, render_engine)
    if resolved_engine not in {"native", "compatibility"}:
        raise ManifestError(
            f"{record.id}: production_engine deve ser 'native' ou 'compatibility', "
            f"recebido {resolved_engine!r}."
        )

    safe_id = _safe_filename(record.id)
    build_dir = _short_build_dir(
        record,
        engine=resolved_engine,
        video_format=video_format,
        quality=quality,
    )
    output_dir = PROJECT_ROOT / output_root_name / record.type / video_format
    output = output_dir / f"{safe_id}.mp4"

    if not dry_run:
        shutil.rmtree(build_dir, ignore_errors=True)
        build_dir.mkdir(parents=True, exist_ok=True)
    else:
        # O builder nativo precisa de um caminho representativo no comando,
        # mas não deve escrever nada em dry-run.
        build_dir.parent.mkdir(parents=True, exist_ok=True)

    if resolved_engine == "native":
        if not dry_run:
            cmd, env, cwd = _native_command(
                record,
                video_format=video_format,
                quality=quality,
                preview=preview,
                build_dir=build_dir,
            )
        else:
            wrapper = build_dir / "_mim_scene.py"
            resolution, fps = RESOLUTIONS[(video_format, quality)]
            render = record.manifest.get("render") or {}
            if render.get("native_ready") is False:
                raise ManifestError(
                    f"{record.id}: renderer nativo ainda não foi portado/validado."
                )
            allowed = render.get("native_formats") or render.get("formats") or ["vertical"]
            if video_format not in allowed:
                raise ManifestError(
                    f"{record.id}: renderer nativo não suporta {video_format!r}."
                )
            cmd = [
                sys.executable, "-m", "manim", "--format", "mp4",
                "--disable_caching", "--progress_bar", "none",
                "-r", resolution, "--fps", str(fps),
                "--media_dir", str(build_dir),
                str(wrapper), "MIMScene",
            ]
            env = os.environ.copy()
            cwd = PROJECT_ROOT
    else:
        cmd, env, cwd = _compatibility_command(
            record,
            video_format=video_format,
            quality=quality,
            preview=preview,
            build_dir=build_dir,
        )

    if fast_preview:
        if resolved_engine == "native":
            env["MIM_FAST_PREVIEW"] = "1"
        elif record.type == "qenem":
            env["ENEM_FAST_PREVIEW"] = "1"

    label = render_engine
    if render_engine == "production":
        label = f"production→{resolved_engine}"
    print(
        f"[{record.type}] {record.id} · {video_format} · {quality} · {label}"
        + (" · FAST" if fast_preview else "")
    )
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
