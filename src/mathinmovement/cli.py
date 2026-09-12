from __future__ import annotations

import argparse
import sys

from .engine import RenderError, render_record
from .models import ManifestError
from .package_io import import_package
from .registry import Registry


def cmd_list(args: argparse.Namespace) -> int:
    registry = Registry().rebuild()
    records = registry.find(content_type=args.type, year=args.year, tags=args.tag or ())
    if not records:
        print("Nenhum conteúdo encontrado.")
        return 0
    for record in records:
        year = f" · {record.year}" if record.year is not None else ""
        formats = ",".join((record.manifest.get("render") or {}).get("formats") or ["vertical"])
        print(f"{record.id} [{record.type}]{year} · {record.title} · {formats}")
    print(f"\nTotal: {len(records)}")
    return 0


def cmd_validate(_: argparse.Namespace) -> int:
    registry = Registry().rebuild()
    print(f"PASS: {len(registry)} conteúdo(s) válido(s), sem IDs duplicados.")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    destination = import_package(args.package, replace=args.replace)
    Registry().rebuild()
    print(f"Importado: {destination}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    registry = Registry().rebuild()

    if args.all:
        records = registry.find(content_type=args.type)
        if not records:
            print("Nenhum conteúdo selecionado para renderização.")
            return 0
    else:
        if not args.id:
            raise ManifestError("Informe um ID ou use --all.")
        records = [registry.get(args.id)]
        if args.type and records[0].type != args.type:
            raise ManifestError(
                f"{records[0].id} é do tipo {records[0].type!r}, não {args.type!r}."
            )

    failures: list[tuple[str, str]] = []
    for record in records:
        try:
            render_record(
                record,
                video_format=args.format,
                quality=args.quality,
                preview=args.preview,
                dry_run=args.dry_run,
            )
        except (ManifestError, RenderError) as exc:
            failures.append((record.id, str(exc)))
            print(f"ERRO: {exc}", file=sys.stderr)
            if not args.keep_going:
                return 2

    if failures:
        print("\nFalhas:", file=sys.stderr)
        for content_id, reason in failures:
            print(f"- {content_id}: {reason}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mathinmovement",
        description="CLI v2 do Math in Movement. O código legado continua disponível durante a migração.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="Lista conteúdos do registry.")
    p_list.add_argument("--type", choices=["qenem", "demo"])
    p_list.add_argument("--year", type=int)
    p_list.add_argument("--tag", action="append", help="Pode ser repetido.")
    p_list.set_defaults(func=cmd_list)

    p_validate = sub.add_parser("validate", help="Valida todos os manifestos.")
    p_validate.set_defaults(func=cmd_validate)

    p_import = sub.add_parser("import", help="Importa um pacote .qenem ou .demo.")
    p_import.add_argument("package")
    p_import.add_argument("--replace", action="store_true")
    p_import.set_defaults(func=cmd_import)

    p_render = sub.add_parser("render", help="Renderiza conteúdo pelo registry v2.")
    p_render.add_argument("id", nargs="?", help="ID do conteúdo.")
    p_render.add_argument("--all", action="store_true", help="Renderiza todos os conteúdos selecionados.")
    p_render.add_argument("--type", choices=["qenem", "demo"], help="Filtra o lote por tipo.")
    p_render.add_argument("--format", choices=["vertical", "horizontal"], default="vertical")
    p_render.add_argument("--quality", choices=["draft", "final"], default="draft")
    p_render.add_argument("--preview", action="store_true")
    p_render.add_argument("--dry-run", action="store_true", help="Mostra o comando sem executar o Manim.")
    p_render.add_argument("--keep-going", action="store_true")
    p_render.set_defaults(func=cmd_render)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        code = int(args.func(args) or 0)
    except (ManifestError, RenderError, KeyError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(code)
