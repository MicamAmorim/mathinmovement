from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

from ..config import PROJECT_ROOT
from ..models import ContentRecord, ManifestError
from ..postprocess import load_timed_audio_events, mix_timed_audio_events


class RenderError(RuntimeError):
    """Falha ao preparar ou executar uma renderização."""


RESOLUTIONS = {
    ("vertical", "draft"): ("360,640", 15),
    ("vertical", "final"): ("1080,1920", 30),
    ("horizontal", "draft"): ("640,360", 15),
    ("horizontal", "final"): ("1920,1080", 30),
}


def _safe_filename(value: str) -> str:
    return "".join(
        c if c.isalnum() or c in "._-" else "-" for c in value
    ).strip("-")


def _short_build_dir(
    record: ContentRecord,
    *,
    engine: str,
    video_format: str,
    quality: str,
) -> Path:
    """Caminho curto e determinístico para evitar MAX_PATH no Windows."""
    if engine not in {"native", "dsl"}:
        raise ManifestError(f"Engine desconhecido: {engine!r}")
    digest = hashlib.sha1(record.id.encode("utf-8")).hexdigest()[:10]
    format_code = "v" if video_format == "vertical" else "h"
    quality_code = "d" if quality == "draft" else "f"
    engine_code = "s" if engine == "dsl" else "n"
    return PROJECT_ROOT / ".mim_build" / engine_code / digest / format_code / quality_code


def _has_canonical_dsl(record: ContentRecord) -> bool:
    manifest = record.manifest
    if manifest.get("visual_program"):
        return True
    visuals = manifest.get("visuals") or {}
    return any(
        isinstance(spec, dict) and bool(spec.get("program"))
        for spec in visuals.values()
    )


def _has_shadow_dsl(record: ContentRecord) -> bool:
    shadow = record.manifest.get("dsl_shadow") or {}
    if shadow.get("visual_program"):
        return True
    visuals = shadow.get("visuals") or {}
    return any(
        isinstance(spec, dict) and bool(spec.get("program"))
        for spec in visuals.values()
    )


def _engine_formats(
    record: ContentRecord,
    engine: str,
) -> list[str]:
    render = record.manifest.get("render") or {}
    if engine == "dsl":
        if _has_canonical_dsl(record):
            return list(render.get("formats") or ["vertical"])
        shadow = record.manifest.get("dsl_shadow") or {}
        if not _has_shadow_dsl(record):
            return []
        return list(
            shadow.get("formats")
            or render.get("formats")
            or render.get("native_formats")
            or ["vertical"]
        )
    if engine == "native":
        if render.get("native_ready") is not True:
            return []
        return list(
            render.get("native_formats")
            or render.get("formats")
            or ["vertical"]
        )
    raise ManifestError(f"Engine desconhecido: {engine!r}")


def _resolve_engine(
    record: ContentRecord,
    requested: str,
    *,
    video_format: str,
) -> tuple[str, str]:
    render = record.manifest.get("render") or {}
    production = str(render.get("production_engine", "native"))
    if production not in {"native", "dsl"}:
        raise ManifestError(
            f"{record.id}: production_engine inválido: {production!r}."
        )

    if requested == "production":
        if _has_canonical_dsl(record):
            approved_formats = _engine_formats(record, "dsl")
        else:
            shadow = record.manifest.get("dsl_shadow") or {}
            approved_formats = list(
                shadow.get("approved_formats")
                or _engine_formats(record, "dsl")
            )
        if (
            production == "dsl"
            and video_format in approved_formats
        ):
            return "dsl", "media"
        return "native", "media"

    if requested == "native":
        return "native", "media_native"

    if requested == "dsl":
        if not (_has_canonical_dsl(record) or _has_shadow_dsl(record)):
            raise ManifestError(
                f"{record.id}: nenhum programa DSL foi declarado."
            )
        return "dsl", "media_dsl"

    raise ManifestError(f"Engine desconhecido: {requested!r}")


def production_formats(record: ContentRecord) -> list[str]:
    """Formatos que a rota production consegue renderizar de fato."""
    formats: list[str] = []
    candidates = ("vertical", "horizontal")
    render = record.manifest.get("render") or {}

    for video_format in candidates:
        try:
            resolved_engine, _ = _resolve_engine(
                record,
                "production",
                video_format=video_format,
            )
        except ManifestError:
            continue

        allowed = _engine_formats(record, resolved_engine)
        if video_format not in allowed:
            continue
        if (
            resolved_engine == "native"
            and render.get("native_ready") is not True
        ):
            continue
        formats.append(video_format)

    return formats


def _manim_command(
    record: ContentRecord,
    *,
    video_format: str,
    quality: str,
    preview: bool,
    build_dir: Path,
) -> tuple[list[str], dict[str, str], Path]:
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
    event_file = build_dir / "_mim_audio_events.jsonl"
    event_file.unlink(missing_ok=True)
    env["MIM_TIMED_AUDIO_EVENTS_FILE"] = str(event_file)
    return cmd, env, PROJECT_ROOT


def render_record(
    record: ContentRecord,
    *,
    video_format: str = "vertical",
    quality: str = "draft",
    preview: bool = False,
    dry_run: bool = False,
    fast_preview: bool = False,
    render_engine: str = "production",
    output_root: str | Path | None = None,
    output_filename: str | None = None,
) -> Path:
    try:
        resolution, fps = RESOLUTIONS[(video_format, quality)]
    except KeyError as exc:
        raise ManifestError(
            f"Combinação inválida: {video_format}/{quality}"
        ) from exc

    resolved_engine, output_root_name = _resolve_engine(
        record,
        render_engine,
        video_format=video_format,
    )
    safe_id = _safe_filename(record.id)
    build_dir = _short_build_dir(
        record,
        engine=resolved_engine,
        video_format=video_format,
        quality=quality,
    )
    root = (
        Path(output_root)
        if output_root is not None
        else PROJECT_ROOT / output_root_name
    )
    if not root.is_absolute():
        root = PROJECT_ROOT / root
    output_dir = root / record.type / video_format
    filename = output_filename or f"{safe_id}.mp4"
    if Path(filename).name != filename:
        raise ManifestError("output_filename deve ser apenas um nome de arquivo.")
    if not filename.lower().endswith(".mp4"):
        raise ManifestError("output_filename deve terminar em .mp4.")
    output = output_dir / filename

    render = record.manifest.get("render") or {}
    allowed = _engine_formats(record, resolved_engine)
    if video_format not in allowed:
        label = "DSL" if resolved_engine == "dsl" else "renderer nativo"
        raise ManifestError(
            f"{record.id}: {label} não suporta {video_format!r}. "
            f"Disponíveis: {', '.join(map(str, allowed))}."
        )
    if (
        resolved_engine == "native"
        and render.get("native_ready") is False
    ):
        raise ManifestError(
            f"{record.id}: renderer nativo ainda não foi validado."
        )

    wrapper = build_dir / "_mim_scene.py"
    if dry_run:
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
            str(wrapper),
            "MIMScene",
        ]
        env = os.environ.copy()
        cwd = PROJECT_ROOT
    else:
        shutil.rmtree(build_dir, ignore_errors=True)
        build_dir.mkdir(parents=True, exist_ok=True)
        cmd, env, cwd = _manim_command(
            record,
            video_format=video_format,
            quality=quality,
            preview=preview,
            build_dir=build_dir,
        )

    if fast_preview:
        env["MIM_FAST_PREVIEW"] = "1"
    env["MIM_RENDER_ENGINE"] = resolved_engine
    if resolved_engine == "dsl":
        # Compatibilidade com cenas/branches anteriores à promoção canônica.
        env["MIM_DSL_SHADOW"] = "1"

    label = (
        f"production→{resolved_engine}"
        if render_engine == "production"
        else ("dsl" if render_engine == "dsl" else "native")
    )
    print(
        f"[{record.type}] {record.id} · {video_format} · "
        f"{quality} · {label}"
        + (" · FAST" if fast_preview else "")
    )
    print(">", subprocess.list2cmdline(cmd))

    if dry_run:
        print(f"Saída normalizada: {output}")
        return output

    result = subprocess.run(cmd, cwd=cwd, env=env)
    if result.returncode:
        raise RenderError(
            f"{record.id}: Manim terminou com código {result.returncode}."
        )

    candidates = [
        path
        for path in build_dir.rglob("*.mp4")
        if "partial_movie_files" not in path.parts
    ]
    if not candidates:
        raise RenderError(
            f"{record.id}: Manim terminou sem produzir MP4 em {build_dir}."
        )

    rendered = max(
        candidates,
        key=lambda p: (p.stat().st_mtime_ns, p.stat().st_size),
    )

    event_file = build_dir / "_mim_audio_events.jsonl"
    timed_events = load_timed_audio_events(event_file)
    if timed_events:
        mixed = build_dir / "_mim_timed_audio_mix.mp4"
        mix_timed_audio_events(
            rendered,
            mixed,
            events=timed_events,
        )
        rendered = mixed

    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(rendered, output)
    print(f"OK: {output}")
    return output
