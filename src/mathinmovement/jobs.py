from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .config import JOBS_DB


JOB_STATUSES = {
    "queued",
    "running",
    "succeeded",
    "failed",
    "canceled",
}

SCHEMA = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    result_json TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_jobs_status_created
ON jobs(status, created_at);
"""


@dataclass(frozen=True, slots=True)
class JobRecord:
    id: str
    kind: str
    status: str
    payload: dict[str, Any]
    result: dict[str, Any] | None
    error: str | None
    created_at: str
    started_at: str | None
    finished_at: str | None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _row_to_job(row: sqlite3.Row) -> JobRecord:
    return JobRecord(
        id=str(row["id"]),
        kind=str(row["kind"]),
        status=str(row["status"]),
        payload=json.loads(row["payload_json"]),
        result=(
            json.loads(row["result_json"])
            if row["result_json"]
            else None
        ),
        error=str(row["error"]) if row["error"] else None,
        created_at=str(row["created_at"]),
        started_at=(
            str(row["started_at"])
            if row["started_at"]
            else None
        ),
        finished_at=(
            str(row["finished_at"])
            if row["finished_at"]
            else None
        ),
    )


class JobStore:
    def __init__(self, path: str | Path = JOBS_DB):
        self.path = Path(path)

    def enqueue(
        self,
        *,
        kind: str,
        payload: dict[str, Any],
        job_id: str | None = None,
    ) -> JobRecord:
        job_id = job_id or uuid.uuid4().hex
        now = _now()
        with closing(_connect(self.path)) as conn:
            conn.execute(
                """
                INSERT INTO jobs(
                    id, kind, status, payload_json, created_at
                ) VALUES (?, ?, 'queued', ?, ?)
                """,
                (
                    job_id,
                    str(kind),
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    now,
                ),
            )
            conn.commit()
        return self.get(job_id)

    def get(self, job_id: str) -> JobRecord:
        with closing(_connect(self.path)) as conn:
            row = conn.execute(
                "SELECT * FROM jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Job não encontrado: {job_id}")
        return _row_to_job(row)

    def list(
        self,
        *,
        status: str | None = None,
        limit: int = 100,
    ) -> list[JobRecord]:
        if status is not None and status not in JOB_STATUSES:
            raise ValueError(f"Status de job inválido: {status!r}")
        limit = max(1, min(int(limit), 1000))
        with closing(_connect(self.path)) as conn:
            if status is None:
                rows = conn.execute(
                    """
                    SELECT * FROM jobs
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM jobs
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (status, limit),
                ).fetchall()
        return [_row_to_job(row) for row in rows]

    def claim_next(
        self,
        *,
        kinds: Iterable[str] | None = None,
    ) -> JobRecord | None:
        kinds_tuple = tuple(str(x) for x in (kinds or ()))
        with closing(_connect(self.path)) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                if kinds_tuple:
                    placeholders = ",".join(
                        "?" for _ in kinds_tuple
                    )
                    row = conn.execute(
                        f"""
                        SELECT * FROM jobs
                        WHERE status = 'queued'
                          AND kind IN ({placeholders})
                        ORDER BY created_at ASC
                        LIMIT 1
                        """,
                        kinds_tuple,
                    ).fetchone()
                else:
                    row = conn.execute(
                        """
                        SELECT * FROM jobs
                        WHERE status = 'queued'
                        ORDER BY created_at ASC
                        LIMIT 1
                        """
                    ).fetchone()

                if row is None:
                    conn.commit()
                    return None

                started = _now()
                updated = conn.execute(
                    """
                    UPDATE jobs
                    SET status = 'running',
                        started_at = ?
                    WHERE id = ?
                      AND status = 'queued'
                    """,
                    (started, row["id"]),
                ).rowcount
                if updated != 1:
                    conn.rollback()
                    return None
                conn.commit()
            except Exception:
                conn.rollback()
                raise

        return self.get(str(row["id"]))

    def succeed(
        self,
        job_id: str,
        result: dict[str, Any],
    ) -> JobRecord:
        with closing(_connect(self.path)) as conn:
            updated = conn.execute(
                """
                UPDATE jobs
                SET status = 'succeeded',
                    result_json = ?,
                    error = NULL,
                    finished_at = ?
                WHERE id = ?
                  AND status = 'running'
                """,
                (
                    json.dumps(
                        result,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    _now(),
                    job_id,
                ),
            ).rowcount
            conn.commit()
        if updated != 1:
            raise ValueError(
                f"Job {job_id!r} não está em execução."
            )
        return self.get(job_id)

    def fail(
        self,
        job_id: str,
        error: str,
    ) -> JobRecord:
        with closing(_connect(self.path)) as conn:
            updated = conn.execute(
                """
                UPDATE jobs
                SET status = 'failed',
                    error = ?,
                    finished_at = ?
                WHERE id = ?
                  AND status = 'running'
                """,
                (str(error), _now(), job_id),
            ).rowcount
            conn.commit()
        if updated != 1:
            raise ValueError(
                f"Job {job_id!r} não está em execução."
            )
        return self.get(job_id)

    def cancel(self, job_id: str) -> JobRecord:
        with closing(_connect(self.path)) as conn:
            updated = conn.execute(
                """
                UPDATE jobs
                SET status = 'canceled',
                    finished_at = ?
                WHERE id = ?
                  AND status = 'queued'
                """,
                (_now(), job_id),
            ).rowcount
            conn.commit()
        if updated != 1:
            current = self.get(job_id)
            if current.status == "canceled":
                return current
            raise ValueError(
                "Apenas jobs ainda enfileirados podem ser cancelados."
            )
        return self.get(job_id)
