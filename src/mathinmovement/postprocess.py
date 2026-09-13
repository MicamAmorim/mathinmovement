from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .models import ManifestError


class PostProcessError(RuntimeError):
    """Falha ao inspecionar ou pós-processar mídia."""


@dataclass(frozen=True, slots=True)
class PostProcessResult:
    input_video: Path
    output_video: Path
    soundtrack: Path | None
    command: tuple[str, ...] | None
    copied: bool


def _require_binary(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise PostProcessError(
            f"{name} não encontrado no PATH. Instale FFmpeg/ffprobe."
        )
    return path


def probe_duration(path: str | Path) -> float:
    media = Path(path)
    if not media.exists():
        raise ManifestError(f"Mídia não encontrada: {media}")
    ffprobe = _require_binary("ffprobe")
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise PostProcessError(
            f"ffprobe falhou ao medir duração de {media}: "
            f"{result.stderr.strip()}"
        )
    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        raise PostProcessError(
            f"ffprobe retornou duração inválida para {media!s}: "
            f"{result.stdout!r}"
        ) from exc
    if duration <= 0:
        raise PostProcessError(f"Duração inválida para {media}: {duration}")
    return duration


def probe_has_audio(path: str | Path) -> bool:
    media = Path(path)
    if not media.exists():
        raise ManifestError(f"Mídia não encontrada: {media}")
    ffprobe = _require_binary("ffprobe")
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(media),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise PostProcessError(
            f"ffprobe falhou ao inspecionar áudio de {media}: "
            f"{result.stderr.strip()}"
        )
    return bool(result.stdout.strip())


def _fmt(value: float) -> str:
    text = f"{float(value):.6f}".rstrip("0").rstrip(".")
    return text or "0"


def build_ffmpeg_command(
    input_video: str | Path,
    output_video: str | Path,
    *,
    soundtrack: str | Path | None,
    duration: float,
    has_source_audio: bool,
    music_volume: float = 0.12,
    fade_in: float = 1.5,
    fade_out: float = 2.5,
    ducking: bool = True,
    normalize: bool = True,
) -> list[str]:
    if duration <= 0:
        raise ManifestError("duration deve ser positiva.")
    if music_volume < 0:
        raise ManifestError("music_volume não pode ser negativo.")
    if fade_in < 0 or fade_out < 0:
        raise ManifestError("fade_in/fade_out não podem ser negativos.")

    ffmpeg = _require_binary("ffmpeg")
    input_video = Path(input_video)
    output_video = Path(output_video)
    music = Path(soundtrack) if soundtrack is not None else None

    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(input_video),
    ]

    if music is not None:
        cmd += [
            "-stream_loop",
            "-1",
            "-i",
            str(music),
        ]

    filters: list[str] = []
    audio_label: str | None = None

    if music is not None:
        safe_fade_in = min(float(fade_in), duration)
        safe_fade_out = min(float(fade_out), duration)
        fade_out_start = max(0.0, duration - safe_fade_out)
        music_filters = [
            f"volume={_fmt(music_volume)}",
            f"atrim=0:{_fmt(duration)}",
            "asetpts=N/SR/TB",
        ]
        if safe_fade_in > 0:
            music_filters.append(
                f"afade=t=in:st=0:d={_fmt(safe_fade_in)}"
            )
        if safe_fade_out > 0:
            music_filters.append(
                "afade=t=out:"
                f"st={_fmt(fade_out_start)}:"
                f"d={_fmt(safe_fade_out)}"
            )
        filters.append(f"[1:a]{','.join(music_filters)}[music]")

        if has_source_audio:
            if ducking:
                filters.append(
                    "[music][0:a]"
                    "sidechaincompress="
                    "threshold=0.02:ratio=8:attack=20:release=300"
                    "[bg]"
                )
            else:
                filters.append("[music]anull[bg]")
            filters.append(
                "[0:a][bg]"
                "amix=inputs=2:duration=first:"
                "dropout_transition=2:normalize=0"
                "[mix]"
            )
            audio_label = "mix"
        else:
            audio_label = "music"
    elif has_source_audio:
        audio_label = "0:a"

    if audio_label is not None and normalize:
        source = f"[{audio_label}]" if ":" not in audio_label else f"[{audio_label}]"
        filters.append(
            f"{source}loudnorm=I=-16:LRA=11:TP=-1.5[aout]"
        )
        audio_label = "aout"

    cmd += ["-map", "0:v:0"]
    if filters:
        cmd += ["-filter_complex", ";".join(filters)]
    if audio_label is not None:
        if audio_label == "0:a":
            cmd += ["-map", "0:a:0"]
        else:
            cmd += ["-map", f"[{audio_label}]"]
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    else:
        cmd += ["-an"]

    cmd += [
        "-c:v",
        "copy",
        "-movflags",
        "+faststart",
        "-shortest",
        str(output_video),
    ]
    return cmd


def postprocess_video(
    input_video: str | Path,
    output_video: str | Path,
    *,
    soundtrack: str | Path | None = None,
    music_volume: float = 0.12,
    fade_in: float = 1.5,
    fade_out: float = 2.5,
    ducking: bool = True,
    normalize: bool = True,
    dry_run: bool = False,
) -> PostProcessResult:
    source = Path(input_video)
    output = Path(output_video)
    music = Path(soundtrack) if soundtrack is not None else None

    if not dry_run and not source.exists():
        raise ManifestError(f"Vídeo bruto não encontrado: {source}")
    if music is not None and not music.exists():
        raise ManifestError(f"Trilha sonora não encontrada: {music}")

    if music is None and not normalize:
        if not dry_run:
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, output)
        return PostProcessResult(
            input_video=source,
            output_video=output,
            soundtrack=None,
            command=None,
            copied=True,
        )

    duration = probe_duration(source)
    has_audio = probe_has_audio(source)
    command = build_ffmpeg_command(
        source,
        output,
        soundtrack=music,
        duration=duration,
        has_source_audio=has_audio,
        music_volume=music_volume,
        fade_in=fade_in,
        fade_out=fade_out,
        ducking=ducking,
        normalize=normalize,
    )

    if dry_run:
        return PostProcessResult(
            input_video=source,
            output_video=output,
            soundtrack=music,
            command=tuple(command),
            copied=False,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command)
    if result.returncode:
        raise PostProcessError(
            f"FFmpeg terminou com código {result.returncode}."
        )

    return PostProcessResult(
        input_video=source,
        output_video=output,
        soundtrack=music,
        command=tuple(command),
        copied=False,
    )
