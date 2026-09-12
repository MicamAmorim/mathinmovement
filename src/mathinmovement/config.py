from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTENT_ROOT = PROJECT_ROOT / "content"
ENEM_CONTENT = CONTENT_ROOT / "enem"
DEMO_CONTENT = CONTENT_ROOT / "demos"
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
CACHE_ROOT = PROJECT_ROOT / "cache"
