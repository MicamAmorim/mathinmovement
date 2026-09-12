from __future__ import annotations

import argparse
import sys

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
        print(f"{record.id} [{record.type}]{year} · {record.title}")
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

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        code = int(args.func(args) or 0)
    except (ManifestError, KeyError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(code)
