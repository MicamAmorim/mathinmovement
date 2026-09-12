from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

from .config import PROJECT_ROOT
from .models import ContentRecord, ManifestError
from .registry import validate_manifest


DEFAULT_VOICE = "pt-BR-AntonioNeural"
DEFAULT_RATE = "+4%"
DEFAULT_VOLUME = "+0%"
DEFAULT_PITCH = "+0Hz"


@dataclass(frozen=True, slots=True)
class TTSResult:
    content_id: str
    total: int
    generated: int
    cached: int
    planned: int
    voice: str | None
    manifest_updated: bool


def _safe_key(value: str) -> str:
    safe = "".join(
        c if c.isalnum() or c in "._-" else "-"
        for c in value
    ).strip("-")
    if not safe:
        raise ManifestError("Segmento de narração possui key inválida.")
    return safe


def narration_fingerprint(
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> str:
    raw = "\0".join(
        [text, voice, rate, volume, pitch]
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:20]


def synthesize_edge_tts(
    text: str,
    output: Path,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> None:
    try:
        import edge_tts
    except ImportError as exc:
        raise ManifestError(
            "edge-tts não está instalado. "
            'Execute: python -m pip install -e ".[render]"'
        ) from exc

    async def _run() -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
        await communicate.save(str(output))

    asyncio.run(_run())


def mp3_duration(path: Path) -> float:
    try:
        from mutagen.mp3 import MP3
    except ImportError as exc:
        raise ManifestError(
            "mutagen não está instalado. "
            'Execute: python -m pip install -e ".[render]"'
        ) from exc
    return round(float(MP3(path).info.length), 3)


def _write_manifest(path: Path, manifest: dict) -> None:
    validate_manifest(manifest, source=path)
    original = path.read_text(encoding="utf-8")
    if original.lstrip().startswith("{"):
        payload = json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        ) + "\n"
    else:
        payload = yaml.safe_dump(
            manifest,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )
    tmp = path.with_suffix(".yaml.tmp")
    tmp.write_text(payload, encoding="utf-8")
    tmp.replace(path)


def prepare_narration(
    record: ContentRecord,
    *,
    voice_override: str | None = None,
    force: bool = False,
    dry_run: bool = False,
    project_root: Path = PROJECT_ROOT,
    synthesizer: Callable[
        [str, Path, str, str, str, str],
        None,
    ] = synthesize_edge_tts,
    duration_reader: Callable[[Path], float] = mp3_duration,
) -> TTSResult:
    manifest = record.manifest
    narration = manifest.get("narration") or {}

    if not narration.get("enabled", False):
        return TTSResult(
            record.id, 0, 0, 0, 0, None, False
        )

    segments = narration.get("segments") or []
    if not segments:
        return TTSResult(
            record.id,
            0,
            0,
            0,
            0,
            str(voice_override or narration.get("voice") or DEFAULT_VOICE),
            False,
        )

    voice = str(
        voice_override
        or narration.get("voice")
        or DEFAULT_VOICE
    )
    rate = str(narration.get("rate") or DEFAULT_RATE)
    volume = str(narration.get("volume") or DEFAULT_VOLUME)
    pitch = str(narration.get("pitch") or DEFAULT_PITCH)
    voice_changed = (
        voice_override is not None
        and str(narration.get("voice") or DEFAULT_VOICE) != voice
    )

    generated = 0
    cached = 0
    planned = 0
    updated = False
    root = Path(project_root).resolve()

    for segment in segments:
        if not isinstance(segment, dict):
            raise ManifestError(
                f"{record.id}: narration.segments deve conter objetos."
            )
        key = str(segment.get("key") or "").strip()
        text = str(segment.get("text") or "").strip()
        if not key or not text:
            raise ManifestError(
                f"{record.id}: cada segmento precisa de key e text."
            )

        safe_key = _safe_key(key)
        canonical = record.path / "assets" / "audio" / f"{safe_key}.mp3"
        try:
            canonical_rel = canonical.resolve().relative_to(root).as_posix()
        except ValueError as exc:
            raise ManifestError(
                f"{record.id}: diretório do conteúdo está fora do projeto: "
                f"{record.path}"
            ) from exc

        current_rel = segment.get("audio")
        current_path = (
            root / str(current_rel)
            if current_rel
            else canonical
        )
        fp = narration_fingerprint(
            text,
            voice,
            rate,
            volume,
            pitch,
        )
        previous_fp = segment.get("tts_fingerprint")

        should_generate = (
            force
            or voice_changed
            or not current_path.is_file()
            or (
                previous_fp is not None
                and str(previous_fp) != fp
            )
        )

        if should_generate:
            if dry_run:
                planned += 1
                continue

            canonical.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            synthesizer(
                text,
                canonical,
                voice,
                rate,
                volume,
                pitch,
            )
            if not canonical.is_file():
                raise ManifestError(
                    f"{record.id}/{key}: TTS não produziu {canonical}."
                )
            duration = duration_reader(canonical)
            segment["audio"] = canonical_rel
            segment["duration"] = duration
            segment["tts_fingerprint"] = fp
            generated += 1
            updated = True
            continue

        cached += 1
        if segment.get("duration") is None:
            if not dry_run:
                segment["duration"] = duration_reader(
                    current_path
                )
                updated = True

    if voice_override is not None and not dry_run:
        if narration.get("voice") != voice:
            narration["voice"] = voice
            updated = True

    if updated and not dry_run:
        manifest["narration"] = narration
        _write_manifest(
            record.path / "manifest.yaml",
            manifest,
        )

    return TTSResult(
        content_id=record.id,
        total=len(segments),
        generated=generated,
        cached=cached,
        planned=planned,
        voice=voice,
        manifest_updated=updated,
    )
