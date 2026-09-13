from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .engine import render_record
from .config import MEDIA_ROOT, RAW_MEDIA_ROOT
from .models import ContentRecord, ManifestError
from .package_io import ALLOWED_EXTENSIONS, import_package
from .registry import Registry
from .tts import TTSResult, prepare_narration
from .postprocess import PostProcessResult, postprocess_video


@dataclass(frozen=True, slots=True)
class ProductionResult:
    record: ContentRecord
    imported: bool
    voice: TTSResult | None
    output: Path
    raw_output: Path | None = None
    postprocess: PostProcessResult | None = None


def resolve_target(
    target: str | Path,
    *,
    replace: bool = False,
) -> tuple[ContentRecord, bool]:
    candidate = Path(target)
    suffix = candidate.suffix.lower()

    if suffix in ALLOWED_EXTENSIONS:
        if not candidate.exists():
            raise ManifestError(
                f"Pacote não encontrado: {candidate}"
            )
        destination = import_package(
            candidate,
            replace=replace,
        )
        record = Registry().rebuild().get(destination.name)
        return record, True

    record = Registry().rebuild().get(str(target))
    return record, False


def produce(
    target: str | Path,
    *,
    replace: bool = False,
    video_format: str | None = None,
    quality: str = "draft",
    preview: bool = False,
    fast_preview: bool = False,
    skip_voice: bool = False,
    force_voice: bool = False,
    voice: str | None = None,
    dry_run: bool = False,
    soundtrack: str | Path | None = None,
    music_volume: float = 0.12,
    fade_in: float = 1.5,
    fade_out: float = 2.5,
    ducking: bool = True,
    normalize_audio: bool = True,
    reuse_raw: bool = True,
) -> ProductionResult:
    record, imported = resolve_target(
        target,
        replace=replace,
    )

    voice_result: TTSResult | None = None
    if not skip_voice:
        voice_result = prepare_narration(
            record,
            voice_override=voice,
            force=force_voice,
            dry_run=dry_run,
        )
        if voice_result.manifest_updated:
            record = Registry().rebuild().get(record.id)

    render = record.manifest.get("render") or {}
    chosen_format = str(
        video_format
        or render.get("default_format")
        or "vertical"
    )

    if soundtrack is None:
        output = render_record(
            record,
            video_format=chosen_format,
            quality=quality,
            preview=preview,
            dry_run=dry_run,
            fast_preview=fast_preview,
            render_engine="production",
        )
        return ProductionResult(
            record=record,
            imported=imported,
            voice=voice_result,
            output=output,
        )

    raw_output = (
        RAW_MEDIA_ROOT
        / record.type
        / chosen_format
        / f"{record.id}.mp4"
    )
    if not (reuse_raw and raw_output.exists() and not dry_run):
        raw_output = render_record(
            record,
            video_format=chosen_format,
            quality=quality,
            preview=preview,
            dry_run=dry_run,
            fast_preview=fast_preview,
            render_engine="production",
            output_root=RAW_MEDIA_ROOT,
        )

    output = (
        MEDIA_ROOT
        / record.type
        / chosen_format
        / f"{record.id}.mp4"
    )
    post_result = postprocess_video(
        raw_output,
        output,
        soundtrack=soundtrack,
        music_volume=music_volume,
        fade_in=fade_in,
        fade_out=fade_out,
        ducking=ducking,
        normalize=normalize_audio,
        dry_run=dry_run,
    )
    return ProductionResult(
        record=record,
        imported=imported,
        voice=voice_result,
        output=output,
        raw_output=raw_output,
        postprocess=post_result,
    )
