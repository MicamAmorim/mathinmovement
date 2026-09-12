from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    """Erro de validação ou consistência de um conteúdo."""


@dataclass(frozen=True, slots=True)
class ContentRecord:
    id: str
    type: str
    title: str
    path: Path
    manifest: dict[str, Any]

    @property
    def tags(self) -> tuple[str, ...]:
        return tuple(str(x) for x in self.manifest.get("tags", []))

    @property
    def year(self) -> int | None:
        exam = self.manifest.get("exam") or {}
        value = exam.get("year")
        return int(value) if value is not None else None
