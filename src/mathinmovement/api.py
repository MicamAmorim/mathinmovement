from pathlib import Path
from typing import Any

from .jobs import JOB_STATUSES, JobRecord, JobStore
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


def create_app(*, store: JobStore | None = None):
    try:
        from fastapi import FastAPI, HTTPException, Query
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
        return [
            {
                "id": record.id,
                "type": record.type,
                "title": record.title,
                "year": record.year,
                "status": record.manifest.get(
                    "status",
                    "production",
                ),
                "tags": list(record.tags),
                "render": record.manifest.get("render") or {},
            }
            for record in records
        ]

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
        limit: int = Query(default=100, ge=1, le=1000),
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
