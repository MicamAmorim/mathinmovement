from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .jobs import JobRecord, JobStore
from .production import produce


SUPPORTED_JOB_KINDS = {"produce"}


def _produce_job(payload: dict[str, Any]) -> dict[str, Any]:
    result = produce(
        payload["target"],
        replace=bool(payload.get("replace", False)),
        video_format=payload.get("format"),
        quality=str(payload.get("quality", "draft")),
        preview=False,
        fast_preview=bool(payload.get("fast", False)),
        skip_voice=bool(payload.get("skip_voice", False)),
        force_voice=bool(payload.get("force_voice", False)),
        voice=payload.get("voice"),
        dry_run=bool(payload.get("dry_run", False)),
        soundtrack=payload.get("music"),
        music_volume=float(payload.get("music_volume", 0.12)),
        fade_in=float(payload.get("fade_in", 1.5)),
        fade_out=float(payload.get("fade_out", 2.5)),
        ducking=not bool(payload.get("no_ducking", False)),
        normalize_audio=not bool(
            payload.get("no_normalize", False)
        ),
        reuse_raw=not bool(payload.get("no_reuse_raw", False)),
    )
    return {
        "content_id": result.record.id,
        "output": str(Path(result.output)),
        "raw_output": (
            str(Path(result.raw_output))
            if result.raw_output is not None
            else None
        ),
        "imported": result.imported,
    }


def execute_job(job: JobRecord) -> dict[str, Any]:
    if job.kind == "produce":
        return _produce_job(job.payload)
    raise ValueError(f"Tipo de job não suportado: {job.kind!r}")


def run_worker_once(
    store: JobStore | None = None,
) -> JobRecord | None:
    store = store or JobStore()
    job = store.claim_next(kinds=SUPPORTED_JOB_KINDS)
    if job is None:
        return None

    try:
        result = execute_job(job)
    except Exception as exc:
        return store.fail(job.id, f"{type(exc).__name__}: {exc}")

    return store.succeed(job.id, result)


def run_worker(
    *,
    store: JobStore | None = None,
    poll_interval: float = 1.0,
) -> None:
    store = store or JobStore()
    interval = max(0.1, float(poll_interval))
    while True:
        completed = run_worker_once(store)
        if completed is None:
            time.sleep(interval)
