from __future__ import annotations

import argparse
import sys

from .config import REGISTRY_DB
from .database import database_stats
from .engine import RenderError, render_record
from .migrations import migrate_legacy_enem
from .models import ManifestError
from .package_io import export_package, import_package
from .registry import Registry


def cmd_list(args: argparse.Namespace) -> int:
    registry = Registry().rebuild()
    records = registry.find(
        content_type=args.type,
        year=args.year,
        tags=args.tag or (),
        status=args.status,
    )
    if not records:
        print("Nenhum conteúdo encontrado.")
        return 0
    for record in records:
        year = f" · {record.year}" if record.year is not None else ""
        status = str(record.manifest.get("status", "production"))
        formats = ",".join((record.manifest.get("render") or {}).get("formats") or ["vertical"])
        print(f"{record.id} [{record.type}] [{status}]{year} · {record.title} · {formats}")
    print(f"\nTotal: {len(records)}")
    return 0


def cmd_validate(_: argparse.Namespace) -> int:
    registry = Registry().rebuild()
    print(f"PASS: {len(registry)} conteúdo(s) válido(s), sem IDs duplicados.")
    print(f"SQLite sincronizado: {REGISTRY_DB}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    destination = import_package(args.package, replace=args.replace)
    print(f"Importado: {destination}")
    print(f"SQLite sincronizado: {REGISTRY_DB}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    output = export_package(args.id, args.output)
    print(f"Exportado: {output}")
    return 0


def cmd_db_status(_: argparse.Namespace) -> int:
    stats = database_stats(REGISTRY_DB)
    if not stats["exists"]:
        print(f"SQLite ainda não existe: {REGISTRY_DB}")
        return 0
    print(f"SQLite: {stats['path']}")
    print(f"Conteúdos: {stats['total']}")
    print(f"Por tipo: {stats['by_type']}")
    print(f"Por status: {stats['by_status']}")
    print(f"Relações de tags: {stats['tags']}")
    if stats.get("indexed_at"):
        print(f"Última reconstrução: {stats['indexed_at']}")
    return 0


def cmd_db_rebuild(_: argparse.Namespace) -> int:
    registry = Registry().rebuild()
    print(f"SQLite reconstruído: {REGISTRY_DB}")
    print(f"Conteúdos indexados: {len(registry)}")
    return 0


def cmd_migrate_legacy_enem(args: argparse.Namespace) -> int:
    result = migrate_legacy_enem(
        replace=args.replace,
        status=args.status,
        only=args.id or (),
    )
    print(f"Legado ENEM detectado: {result['total_legacy']}")
    print(f"Gerados/atualizados: {len(result['created'])}")
    for content_id in result["created"]:
        print(f"  + {content_id}")
    if result["skipped"]:
        print(f"Preservados por já existirem: {len(result['skipped'])}")
    print(f"SQLite sincronizado: {REGISTRY_DB}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    registry = Registry().rebuild()

    if args.all:
        records = registry.find(content_type=args.type, status=args.status)
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
                fast_preview=args.fast,
                render_engine=args.engine,
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
        description="CLI v2 do Math in Movement.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="Lista conteúdos do registry.")
    p_list.add_argument("--type", choices=["qenem", "demo"])
    p_list.add_argument("--year", type=int)
    p_list.add_argument("--tag", action="append", help="Pode ser repetido.")
    p_list.add_argument("--status", choices=["draft", "validated", "production", "deprecated"])
    p_list.set_defaults(func=cmd_list)

    p_validate = sub.add_parser("validate", help="Valida manifestos e sincroniza o SQLite.")
    p_validate.set_defaults(func=cmd_validate)

    p_import = sub.add_parser("import", help="Importa um pacote .qenem ou .demo.")
    p_import.add_argument("package")
    p_import.add_argument("--replace", action="store_true")
    p_import.set_defaults(func=cmd_import)

    p_export = sub.add_parser("export", help="Empacota um conteúdo do registry como .qenem/.demo.")
    p_export.add_argument("id")
    p_export.add_argument("-o", "--output")
    p_export.set_defaults(func=cmd_export)

    p_db = sub.add_parser("db", help="Inspeciona ou reconstrói o índice SQLite.")
    db_sub = p_db.add_subparsers(dest="db_command", required=True)
    p_db_status = db_sub.add_parser("status")
    p_db_status.set_defaults(func=cmd_db_status)
    p_db_rebuild = db_sub.add_parser("rebuild")
    p_db_rebuild.set_defaults(func=cmd_db_rebuild)

    p_migrate = sub.add_parser("migrate", help="Ferramentas de migração do código legado.")
    migrate_sub = p_migrate.add_subparsers(dest="migration", required=True)
    p_legacy_enem = migrate_sub.add_parser(
        "legacy-enem",
        help="Converte questions.json + specs.py + narração legados em manifests qenem.",
    )
    p_legacy_enem.add_argument("--replace", action="store_true")
    p_legacy_enem.add_argument(
        "--status",
        choices=["draft", "validated", "production", "deprecated"],
        default="draft",
    )
    p_legacy_enem.add_argument(
        "--id",
        action="append",
        help="Migra somente este canonical_id; pode ser repetido.",
    )
    p_legacy_enem.set_defaults(func=cmd_migrate_legacy_enem)

    p_render = sub.add_parser("render", help="Renderiza conteúdo pelo engine v2.")
    p_render.add_argument("id", nargs="?", help="ID do conteúdo.")
    p_render.add_argument("--all", action="store_true", help="Renderiza todos os conteúdos selecionados.")
    p_render.add_argument("--type", choices=["qenem", "demo"], help="Filtra o lote por tipo.")
    p_render.add_argument("--status", choices=["draft", "validated", "production", "deprecated"], default="production")
    p_render.add_argument("--format", choices=["vertical", "horizontal"], default="vertical")
    p_render.add_argument("--quality", choices=["draft", "final"], default="draft")
    p_render.add_argument(
        "--engine",
        choices=["production", "native", "compatibility"],
        default="production",
        help="production usa o renderer aprovado; native testa o engine v2; compatibility força a cena anterior.",
    )
    p_render.add_argument("--preview", action="store_true")
    p_render.add_argument("--fast", action="store_true", help="Prévia rápida: reduz esperas e não toca áudio.")
    p_render.add_argument("--dry-run", action="store_true", help="Mostra o comando sem executar o Manim.")
    p_render.add_argument("--keep-going", action="store_true")
    p_render.set_defaults(func=cmd_render)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        code = int(args.func(args) or 0)
    except (ManifestError, RenderError, KeyError, ValueError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(code)
