from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .models import ContentRecord


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS contents (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    year INTEGER,
    status TEXT NOT NULL,
    manifest_path TEXT NOT NULL,
    manifest_json TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    indexed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS content_tags (
    content_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (content_id, tag),
    FOREIGN KEY (content_id) REFERENCES contents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_contents_type ON contents(type);
CREATE INDEX IF NOT EXISTS idx_contents_year ON contents(year);
CREATE INDEX IF NOT EXISTS idx_contents_status ON contents(status);
CREATE INDEX IF NOT EXISTS idx_content_tags_tag ON content_tags(tag);
"""


def canonical_manifest_json(record: ContentRecord) -> str:
    return json.dumps(
        record.manifest,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def manifest_fingerprint(record: ContentRecord) -> str:
    payload = canonical_manifest_json(record).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def rebuild_database(records: Iterable[ContentRecord], path: Path) -> None:
    """Reconstrói o índice e fecha explicitamente o arquivo SQLite."""
    records = list(records)
    now = datetime.now(timezone.utc).isoformat()
    with closing(connect(path)) as conn:
        try:
            conn.execute("BEGIN")
            conn.execute("DELETE FROM content_tags")
            conn.execute("DELETE FROM contents")
            for record in records:
                manifest_json = canonical_manifest_json(record)
                status = str(record.manifest.get("status", "production"))
                conn.execute(
                    """
                    INSERT INTO contents (
                        id, type, title, year, status,
                        manifest_path, manifest_json, fingerprint, indexed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.id,
                        record.type,
                        record.title,
                        record.year,
                        status,
                        str(record.path / "manifest.yaml"),
                        manifest_json,
                        manifest_fingerprint(record),
                        now,
                    ),
                )
                conn.executemany(
                    "INSERT INTO content_tags(content_id, tag) VALUES (?, ?)",
                    [(record.id, tag) for tag in record.tags],
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def database_stats(path: Path) -> dict:
    if not path.exists():
        return {
            "exists": False,
            "path": str(path),
            "total": 0,
            "by_type": {},
            "by_status": {},
            "tags": 0,
        }

    with closing(connect(path)) as conn:
        total = conn.execute("SELECT COUNT(*) FROM contents").fetchone()[0]
        by_type = {
            row["type"]: row["n"]
            for row in conn.execute(
                "SELECT type, COUNT(*) AS n FROM contents GROUP BY type ORDER BY type"
            )
        }
        by_status = {
            row["status"]: row["n"]
            for row in conn.execute(
                "SELECT status, COUNT(*) AS n FROM contents GROUP BY status ORDER BY status"
            )
        }
        tags = conn.execute("SELECT COUNT(*) FROM content_tags").fetchone()[0]
        newest = conn.execute("SELECT MAX(indexed_at) FROM contents").fetchone()[0]

    return {
        "exists": True,
        "path": str(path),
        "total": int(total),
        "by_type": by_type,
        "by_status": by_status,
        "tags": int(tags),
        "indexed_at": newest,
    }
