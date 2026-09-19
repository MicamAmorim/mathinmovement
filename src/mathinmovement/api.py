import hashlib
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

from .config import MEDIA_ROOT, UPLOAD_ROOT
from .engine.renderer import production_formats
from .jobs import JOB_STATUSES, JobRecord, JobStore
from .models import ManifestError
from .package_io import ALLOWED_EXTENSIONS, import_package
from .registry import Registry


def _job_dict(job: JobRecord) -> dict[str, Any]:
    return {
        "id": job.id,
        "kind": job.kind,
        "status": job.status,
        "payload": job.payload,
        "result": job.result,
        "error": job.error,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }


def _content_dict(
    record,
    processing: dict[str, Any] | None = None,
) -> dict[str, Any]:
    narration = record.manifest.get("narration") or {}
    render = record.manifest.get("render") or {}
    return {
        "id": record.id,
        "type": record.type,
        "title": record.title,
        "year": record.year,
        "status": record.manifest.get("status", "production"),
        "tags": list(record.tags),
        "render": render,
        "production_formats": production_formats(record),
        "narration": {
            "enabled": bool(narration.get("enabled", False)),
            "segments": len(narration.get("segments", [])),
            "voice": narration.get("voice"),
        },
        "processed": bool(processing),
        "processed_count": int((processing or {}).get("count", 0)),
        "last_processed_at": (processing or {}).get("last_processed_at"),
    }


def _safe_upload_name(filename: str | None, fallback: str) -> str:
    name = Path(filename or fallback).name.strip()
    return name or fallback


async def _save_upload(
    upload: Any,
    destination: Path,
    *,
    max_bytes: int,
) -> tuple[int, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    total = 0

    try:
        with destination.open("wb") as handle:
            while True:
                chunk = await upload.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(
                        f"Arquivo excede o limite de {max_bytes // (1024 * 1024)} MB."
                    )
                digest.update(chunk)
                handle.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()

    return total, digest.hexdigest()


def create_app(*, store: JobStore | None = None):
    try:
        from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
        from fastapi.responses import FileResponse, RedirectResponse
        from fastapi.staticfiles import StaticFiles
        from pydantic import BaseModel, Field
    except ImportError as exc:
        raise RuntimeError(
            "API opcional não instalada. "
            'Execute: pip install -e ".[api]"'
        ) from exc

    store = store or JobStore()
    app = FastAPI(
        title="Math in Movement API",
        version="0.2",
    )

    studio_root = Path(__file__).with_name("studio")
    if studio_root.is_dir():
        app.mount(
            "/studio/assets",
            StaticFiles(directory=studio_root),
            name="studio-assets",
        )

        @app.get("/", include_in_schema=False)
        def root():
            return RedirectResponse(url="/studio")

        @app.get("/studio", include_in_schema=False)
        def studio():
            return FileResponse(studio_root / "index.html")

    class ProduceJobRequest(BaseModel):
        target: str
        format: str | None = Field(
            default=None,
            pattern="^(vertical|horizontal)$",
        )
        quality: str = Field(
            default="draft",
            pattern="^(draft|final)$",
        )
        voice: str | None = None
        skip_voice: bool = False
        force_voice: bool = False
        fast: bool = False
        dry_run: bool = False
        music: str | None = None
        music_volume: float = Field(default=0.12, ge=0)
        fade_in: float = Field(default=1.5, ge=0)
        fade_out: float = Field(default=2.5, ge=0)
        no_ducking: bool = False
        no_normalize: bool = False
        no_reuse_raw: bool = False

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/contents")
    def contents(
        type: str | None = Query(default=None),
        status: str | None = Query(default=None),
        year: int | None = Query(default=None),
    ) -> list[dict[str, Any]]:
        registry = Registry().rebuild()
        records = registry.find(
            content_type=type,
            status=status,
            year=year,
        )
        processed = store.processed_targets()
        return [
            _content_dict(record, processed.get(record.id))
            for record in records
        ]

    async def _import_upload(
        upload: UploadFile,
        *,
        replace: bool,
    ) -> dict[str, Any]:
        original_name = _safe_upload_name(
            upload.filename,
            "content.demo",
        )
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=(
                    f"{original_name}: envie um pacote .demo ou .qenem."
                ),
            )

        upload_dir = UPLOAD_ROOT / "packages"
        temporary = upload_dir / f"{uuid.uuid4().hex}{suffix}"
        try:
            await _save_upload(
                upload,
                temporary,
                max_bytes=50 * 1024 * 1024,
            )
            destination = import_package(
                temporary,
                replace=replace,
            )
            record = Registry().rebuild().get(destination.name)
            return {
                "name": original_name,
                "imported": True,
                "content": _content_dict(
                    record,
                    store.processed_targets().get(record.id),
                ),
            }
        except ManifestError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"{original_name}: {exc}",
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=413,
                detail=f"{original_name}: {exc}",
            ) from exc
        finally:
            temporary.unlink(missing_ok=True)

    @app.post("/imports", status_code=201)
    async def import_content(
        file: UploadFile = File(...),
        replace: bool = Form(False),
    ) -> dict[str, Any]:
        return await _import_upload(file, replace=replace)

    @app.post("/imports/batch", status_code=201)
    async def import_contents_batch(
        files: list[UploadFile] = File(...),
        replace: bool = Form(False),
    ) -> dict[str, Any]:
        if not files:
            raise HTTPException(
                status_code=422,
                detail="Selecione pelo menos um pacote.",
            )
        if len(files) > 50:
            raise HTTPException(
                status_code=422,
                detail="Importe no máximo 50 pacotes por vez.",
            )

        imported: list[dict[str, Any]] = []
        failed: list[dict[str, str]] = []
        for upload in files:
            original_name = _safe_upload_name(
                upload.filename,
                "content.demo",
            )
            try:
                imported.append(
                    await _import_upload(
                        upload,
                        replace=replace,
                    )
                )
            except HTTPException as exc:
                failed.append({
                    "name": original_name,
                    "error": str(exc.detail),
                })

        return {
            "total": len(files),
            "imported": imported,
            "failed": failed,
        }

    @app.post("/uploads/music", status_code=201)
    async def upload_music(
        file: UploadFile = File(...),
    ) -> dict[str, Any]:
        original_name = _safe_upload_name(file.filename, "music.mp3")
        suffix = Path(original_name).suffix.lower()
        allowed_audio = {
            ".mp3",
            ".wav",
            ".m4a",
            ".aac",
            ".flac",
            ".ogg",
        }
        if suffix not in allowed_audio:
            raise HTTPException(
                status_code=415,
                detail=(
                    "Formato de áudio não suportado. "
                    "Use MP3, WAV, M4A, AAC, FLAC ou OGG."
                ),
            )

        music_dir = UPLOAD_ROOT / "music"
        temporary = music_dir / f".{uuid.uuid4().hex}{suffix}"
        try:
            size, digest = await _save_upload(
                file,
                temporary,
                max_bytes=200 * 1024 * 1024,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=413,
                detail=str(exc),
            ) from exc

        safe_name = "".join(
            ch if ch.isalnum() or ch in " ._-" else "-"
            for ch in Path(original_name).stem
        ).strip(" ._-") or "music"
        destination = (
            music_dir
            / f"{digest[:12]}-{safe_name}{suffix}"
        )
        if destination.exists():
            temporary.unlink(missing_ok=True)
        else:
            shutil.move(str(temporary), str(destination))

        return {
            "name": original_name,
            "path": str(destination.resolve()),
            "size": size,
            "fingerprint": digest[:12],
        }

    @app.post("/system/open-media-folder")
    def open_media_folder() -> dict[str, str]:
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        path = MEDIA_ROOT.resolve()

        try:
            if sys.platform == "win32":
                os.startfile(str(path))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except (OSError, subprocess.SubprocessError) as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Não foi possível abrir a pasta de vídeos: {exc}",
            ) from exc

        return {
            "opened": str(path),
        }

    @app.post("/jobs", status_code=202)
    def create_job(
        request: ProduceJobRequest,
    ) -> dict[str, Any]:
        payload = request.model_dump(exclude_none=True)
        job = store.enqueue(
            kind="produce",
            payload=payload,
        )
        return _job_dict(job)

    @app.get("/jobs")
    def list_jobs(
        status: str | None = Query(default=None),
        limit: int = Query(default=5, ge=1, le=1000),
    ) -> list[dict[str, Any]]:
        if status is not None and status not in JOB_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=f"Status inválido: {status}",
            )
        return [
            _job_dict(job)
            for job in store.list(status=status, limit=limit)
        ]

    @app.get("/jobs/history")
    def job_history(
        status: str | None = Query(default=None),
        limit: int = Query(default=25, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
    ) -> dict[str, Any]:
        if status is not None and status not in JOB_STATUSES:
            raise HTTPException(
                status_code=422,
                detail=f"Status inválido: {status}",
            )
        return {
            "items": [
                _job_dict(job)
                for job in store.list(
                    status=status,
                    limit=limit,
                    offset=offset,
                )
            ],
            "total": store.count(status=status),
            "limit": limit,
            "offset": offset,
        }

    @app.get("/jobs/{job_id}")
    def get_job(job_id: str) -> dict[str, Any]:
        try:
            return _job_dict(store.get(job_id))
        except KeyError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc

    @app.post("/jobs/{job_id}/cancel")
    def cancel_job(job_id: str) -> dict[str, Any]:
        try:
            return _job_dict(store.cancel(job_id))
        except KeyError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=409,
                detail=str(exc),
            ) from exc

    return app


def serve(
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError(
            "Servidor API opcional não instalado. "
            'Execute: pip install -e ".[api]"'
        ) from exc

    uvicorn.run(
        "mathinmovement.api:create_app",
        factory=True,
        host=host,
        port=int(port),
        reload=reload,
    )
