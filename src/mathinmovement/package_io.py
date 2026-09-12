from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from .config import CONTENT_ROOT
from .models import ManifestError
from .registry import TYPE_DIRS, Registry, load_manifest, validate_manifest


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

    # O conteúdo em disco é a fonte de verdade; o SQLite é sincronizado depois.
    if Path(content_root).resolve() == CONTENT_ROOT.resolve():
        Registry().rebuild()

    return destination


def export_package(
    content_id: str,
    output_path: str | Path | None = None,
) -> Path:
    record = Registry().rebuild().get(content_id)
    suffix = ".qenem" if record.type == "qenem" else ".demo"
    output = Path(output_path) if output_path else Path.cwd() / f"{record.id}{suffix}"
    if output.suffix.lower() != suffix:
        raise ManifestError(
            f"{record.id} é do tipo {record.type}; o arquivo deve terminar em {suffix}."
        )
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(record.path.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(record.path).as_posix())

    return output
