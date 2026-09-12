from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from .config import CONTENT_ROOT
from .models import ManifestError
from .registry import TYPE_DIRS, load_manifest, validate_manifest


ALLOWED_EXTENSIONS = {
    ".qenem": "qenem",
    ".demo": "demo",
}


def _safe_members(archive: zipfile.ZipFile) -> None:
    for member in archive.infolist():
        path = Path(member.filename)
        if path.is_absolute() or ".." in path.parts:
            raise ManifestError(f"Pacote contém caminho inseguro: {member.filename!r}")


def import_package(
    package_path: str | Path,
    *,
    content_root: Path = CONTENT_ROOT,
    replace: bool = False,
) -> Path:
    package_path = Path(package_path)
    expected_type = ALLOWED_EXTENSIONS.get(package_path.suffix.lower())
    if expected_type is None:
        raise ManifestError("O pacote deve terminar em .qenem ou .demo.")
    if not package_path.exists():
        raise ManifestError(f"Arquivo não encontrado: {package_path}")
    if not zipfile.is_zipfile(package_path):
        raise ManifestError(f"{package_path.name} não é um container ZIP válido.")

    with tempfile.TemporaryDirectory(prefix="mim-import-") as tmp_name:
        tmp = Path(tmp_name)
        with zipfile.ZipFile(package_path) as archive:
            _safe_members(archive)
            archive.extractall(tmp)

        manifest_path = tmp / "manifest.yaml"
        if not manifest_path.exists():
            raise ManifestError("Pacote inválido: manifest.yaml ausente na raiz.")

        manifest = load_manifest(manifest_path)
        validate_manifest(manifest, source=package_path)
        if manifest["type"] != expected_type:
            raise ManifestError(
                f"Extensão {package_path.suffix} exige type={expected_type!r}, "
                f"mas o manifesto declara {manifest['type']!r}."
            )

        destination = Path(content_root) / TYPE_DIRS[expected_type] / str(manifest["id"])
        if destination.exists():
            if not replace:
                raise ManifestError(
                    f"{manifest['id']!r} já existe em {destination}. Use --replace para substituir."
                )
            shutil.rmtree(destination)

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(tmp, destination)
        return destination
