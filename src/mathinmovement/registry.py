from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import yaml
from jsonschema import Draft202012Validator

from .config import CONTENT_ROOT, SCHEMA_ROOT
from .models import ContentRecord, ManifestError


TYPE_DIRS = {
    "qenem": "enem",
    "demo": "demos",
}


def load_manifest(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ManifestError(f"Falha ao ler {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError(f"{path}: manifest.yaml deve conter um objeto YAML.")
    return data


def schema_for(content_type: str) -> dict:
    schema_path = SCHEMA_ROOT / f"{content_type}.schema.json"
    if not schema_path.exists():
        raise ManifestError(f"Schema ausente para tipo {content_type!r}: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict, *, source: str | Path = "<manifest>") -> None:
    content_type = manifest.get("type")
    if content_type not in TYPE_DIRS:
        raise ManifestError(f"{source}: type deve ser 'qenem' ou 'demo'.")
    validator = Draft202012Validator(schema_for(content_type))
    errors = sorted(validator.iter_errors(manifest), key=lambda e: list(e.absolute_path))
    if errors:
        formatted = []
        for error in errors:
            where = ".".join(map(str, error.absolute_path)) or "<raiz>"
            formatted.append(f"{where}: {error.message}")
        raise ManifestError(f"{source}:\n  - " + "\n  - ".join(formatted))


class Registry:
    def __init__(self, content_root: Path = CONTENT_ROOT):
        self.content_root = Path(content_root)
        self._records: dict[str, ContentRecord] = {}

    def rebuild(self) -> "Registry":
        records: dict[str, ContentRecord] = {}
        for content_type, dirname in TYPE_DIRS.items():
            root = self.content_root / dirname
            if not root.exists():
                continue
            for manifest_path in sorted(root.glob("*/manifest.yaml")):
                manifest = load_manifest(manifest_path)
                validate_manifest(manifest, source=manifest_path)
                if manifest["type"] != content_type:
                    raise ManifestError(
                        f"{manifest_path}: conteúdo está em {dirname}/ mas declara type={manifest['type']!r}."
                    )
                cid = str(manifest["id"])
                if cid in records:
                    raise ManifestError(
                        f"ID duplicado {cid!r}: {records[cid].path} e {manifest_path.parent}"
                    )
                records[cid] = ContentRecord(
                    id=cid,
                    type=content_type,
                    title=str(manifest["title"]),
                    path=manifest_path.parent,
                    manifest=manifest,
                )
        self._records = records
        return self

    def __len__(self) -> int:
        return len(self._records)

    def get(self, content_id: str) -> ContentRecord:
        try:
            return self._records[content_id]
        except KeyError as exc:
            raise KeyError(f"Conteúdo não encontrado: {content_id}") from exc

    def all(self) -> list[ContentRecord]:
        return sorted(self._records.values(), key=lambda r: (r.type, r.id))

    def find(
        self,
        *,
        content_type: str | None = None,
        year: int | None = None,
        tags: Iterable[str] = (),
    ) -> list[ContentRecord]:
        wanted_tags = {str(x) for x in tags}
        result = []
        for record in self.all():
            if content_type and record.type != content_type:
                continue
            if year is not None and record.year != year:
                continue
            if wanted_tags and not wanted_tags.issubset(set(record.tags)):
                continue
            result.append(record)
        return result
