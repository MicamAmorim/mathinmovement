from __future__ import annotations

import argparse
import sys

from .config import REGISTRY_DB
from .database import database_stats
from .engine import RenderError, render_record
from .models import ManifestError
from .package_io import export_package, import_package
from .production import produce
from .registry import Registry
from .tts import prepare_narration
from .dsl.coverage import (
    DEMO_USAGE,
    DEMO_VALIDATION_SET,
    QENEM_COMMON,
    QENEM_USAGE,
    QENEM_VALIDATION_SET,
    minimum_cover,
    universe,
)


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
        formats = ",".join(
            (record.manifest.get("render") or {}).get("formats")
            or ["vertical"]
        )
        print(
            f"{record.id} [{record.type}] [{status}]"
            f"{year} · {record.title} · {formats}"
        )
    print(f"\nTotal: {len(records)}")
    return 0


def cmd_validate(_: argparse.Namespace) -> int:
    registry = Registry().rebuild()
    print(
        f"PASS: {len(registry)} conteúdo(s) válido(s), "
        "sem IDs duplicados."
    )
    print(f"SQLite sincronizado: {REGISTRY_DB}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    destination = import_package(
        args.package,
        replace=args.replace,
    )
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


def _print_voice_result(result) -> None:
    if result.total == 0:
        print("Narração: nenhum segmento TTS aplicável.")
        return
    print(
        "Narração: "
        f"{result.generated} gerado(s), "
        f"{result.cached} em cache, "
        f"{result.planned} planejado(s) · "
        f"voz {result.voice}"
    )


def cmd_voice(args: argparse.Namespace) -> int:
    record = Registry().rebuild().get(args.id)
    result = prepare_narration(
        record,
        voice_override=args.voice,
        force=args.force,
        dry_run=args.dry_run,
    )
    _print_voice_result(result)
    if result.manifest_updated:
        Registry().rebuild()
        print("Manifest atualizado e registry sincronizado.")
    return 0


def cmd_produce(args: argparse.Namespace) -> int:
    result = produce(
        args.target,
        replace=args.replace,
        video_format=args.format,
        quality=args.quality,
        preview=args.preview,
        fast_preview=args.fast,
        skip_voice=args.skip_voice,
        force_voice=args.force_voice,
        voice=args.voice,
        dry_run=args.dry_run,
    )
    if result.imported:
        print(f"Importado e registrado: {result.record.id}")
    else:
        print(f"Conteúdo selecionado: {result.record.id}")
    if result.voice is not None:
        _print_voice_result(result.voice)
    print(f"Vídeo: {result.output}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    registry = Registry().rebuild()

    if args.all:
        records = registry.find(
            content_type=args.type,
            status=None if args.status == "all" else args.status,
        )
        if not records:
            print("Nenhum conteúdo selecionado para renderização.")
            return 0
    else:
        if not args.id:
            raise ManifestError("Informe um ID ou use --all.")
        records = [registry.get(args.id)]
        if args.type and records[0].type != args.type:
            raise ManifestError(
                f"{records[0].id} é do tipo "
                f"{records[0].type!r}, não {args.type!r}."
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


def cmd_dsl_ops(_: argparse.Namespace) -> int:
    # Importa runtime para registrar os built-ins.
    from .dsl.runtime import validate_program  # noqa: F401
    from .dsl.registry import action_capabilities, object_capabilities

    print("Objetos DSL:")
    for cap in object_capabilities():
        aliases = f" ({', '.join(cap.aliases)})" if cap.aliases else ""
        print(f"- {cap.canonical}{aliases} · desde {cap.since}")
    print("\nAções DSL:")
    for cap in action_capabilities():
        aliases = f" ({', '.join(cap.aliases)})" if cap.aliases else ""
        print(f"- {cap.canonical}{aliases} · desde {cap.since}")
    return 0


def cmd_dsl_audit(_: argparse.Namespace) -> int:
    demos = minimum_cover(DEMO_USAGE)
    qenem = minimum_cover(QENEM_USAGE)
    print(
        f"Demos: {len(universe(DEMO_USAGE))} capacidades · "
        f"cobertura mínima {len(demos.selected)} vídeo(s)"
    )
    for content_id in DEMO_VALIDATION_SET:
        print(f"- {content_id}")
    print(
        f"\nqENEM: {len(universe(QENEM_USAGE))} capacidades específicas + "
        f"{len(QENEM_COMMON)} comuns · "
        f"cobertura mínima {len(qenem.selected)} vídeo(s)"
    )
    for content_id in QENEM_VALIDATION_SET:
        print(f"- {content_id}")
    return 0


def cmd_dsl_validate(args: argparse.Namespace) -> int:
    from .dsl.runtime import validate_program

    record = Registry().rebuild().get(args.id)
    programs = []
    if record.manifest.get("visual_program"):
        programs.append(("visual_program", record.manifest["visual_program"]))
    visuals = record.manifest.get("visuals") or {}
    for name in ("statement", "concept", "options"):
        spec = visuals.get(name) or {}
        if isinstance(spec, dict) and spec.get("program"):
            programs.append((f"visuals.{name}.program", spec["program"]))
    shadow = record.manifest.get("dsl_shadow") or {}
    if shadow.get("visual_program"):
        programs.append(("dsl_shadow.visual_program", shadow["visual_program"]))
    shadow_visuals = shadow.get("visuals") or {}
    for name in ("statement", "concept", "options"):
        spec = shadow_visuals.get(name) or {}
        if isinstance(spec, dict) and spec.get("program"):
            programs.append((f"dsl_shadow.visuals.{name}.program", spec["program"]))
    if not programs:
        raise ManifestError(f"{record.id}: nenhum programa DSL declarado.")
    for label, program in programs:
        validate_program(program)
        print(f"PASS: {record.id} · {label} · DSL {program.get('dsl_version')}")
    return 0


def cmd_dsl_regress(args: argparse.Namespace) -> int:
    registry = Registry().rebuild()
    if args.scope == "all":
        records = [
            record for record in registry.all()
            if record.manifest.get("dsl_shadow")
            and (args.type == "all" or record.type == args.type)
        ]
        ids = tuple(record.id for record in records)
    elif args.type == "demo":
        ids = DEMO_VALIDATION_SET
    elif args.type == "qenem":
        ids = QENEM_VALIDATION_SET
    else:
        ids = DEMO_VALIDATION_SET + QENEM_VALIDATION_SET

    failures = []
    for content_id in ids:
        record = registry.get(content_id)
        try:
            render_record(
                record,
                video_format=args.format,
                quality=args.quality,
                preview=args.preview,
                dry_run=args.dry_run,
                fast_preview=args.fast,
                render_engine="dsl",
            )
        except (ManifestError, RenderError) as exc:
            failures.append((content_id, str(exc)))
            print(f"ERRO: {exc}", file=sys.stderr)
            if not args.keep_going:
                return 2
    if failures:
        return 1
    print(f"PASS: {len(ids)} shadow port(s) DSL processado(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mathinmovement",
        description="CLI do Math in Movement.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser(
        "list",
        help="Lista conteúdos do registry.",
    )
    p_list.add_argument("--type", choices=["qenem", "demo"])
    p_list.add_argument("--year", type=int)
    p_list.add_argument(
        "--tag",
        action="append",
        help="Pode ser repetido.",
    )
    p_list.add_argument(
        "--status",
        choices=[
            "draft",
            "validated",
            "production",
            "deprecated",
        ],
    )
    p_list.set_defaults(func=cmd_list)

    p_validate = sub.add_parser(
        "validate",
        help="Valida manifestos e sincroniza o SQLite.",
    )
    p_validate.set_defaults(func=cmd_validate)

    p_import = sub.add_parser(
        "import",
        help="Importa um pacote .qenem ou .demo.",
    )
    p_import.add_argument("package")
    p_import.add_argument("--replace", action="store_true")
    p_import.set_defaults(func=cmd_import)

    p_export = sub.add_parser(
        "export",
        help="Empacota um conteúdo como .qenem/.demo.",
    )
    p_export.add_argument("id")
    p_export.add_argument("-o", "--output")
    p_export.set_defaults(func=cmd_export)

    p_db = sub.add_parser(
        "db",
        help="Inspeciona ou reconstrói o índice SQLite.",
    )
    db_sub = p_db.add_subparsers(
        dest="db_command",
        required=True,
    )
    p_db_status = db_sub.add_parser("status")
    p_db_status.set_defaults(func=cmd_db_status)
    p_db_rebuild = db_sub.add_parser("rebuild")
    p_db_rebuild.set_defaults(func=cmd_db_rebuild)

    p_dsl = sub.add_parser(
        "dsl",
        help="Inspeciona e valida a DSL visual.",
    )
    dsl_sub = p_dsl.add_subparsers(dest="dsl_command", required=True)
    p_dsl_ops = dsl_sub.add_parser("ops", help="Lista capacidades registradas.")
    p_dsl_ops.set_defaults(func=cmd_dsl_ops)
    p_dsl_audit = dsl_sub.add_parser(
        "audit",
        help="Mostra a cobertura mínima dos vídeos de regressão.",
    )
    p_dsl_audit.set_defaults(func=cmd_dsl_audit)
    p_dsl_validate = dsl_sub.add_parser(
        "validate",
        help="Valida programas DSL de um conteúdo.",
    )
    p_dsl_validate.add_argument("id")
    p_dsl_validate.set_defaults(func=cmd_dsl_validate)

    p_dsl_regress = dsl_sub.add_parser(
        "regress",
        help="Renderiza o conjunto mínimo de regressão em media_dsl/.",
    )
    p_dsl_regress.add_argument("--type", choices=["all", "demo", "qenem"], default="all")
    p_dsl_regress.add_argument(
        "--scope",
        choices=["cover", "all"],
        default="cover",
        help="cover usa os 14 representantes mínimos; all usa todo conteúdo com dsl_shadow.",
    )
    p_dsl_regress.add_argument("--format", choices=["vertical", "horizontal"], default="vertical")
    p_dsl_regress.add_argument("--quality", choices=["draft", "final"], default="draft")
    p_dsl_regress.add_argument("--preview", action="store_true")
    p_dsl_regress.add_argument("--fast", action="store_true")
    p_dsl_regress.add_argument("--dry-run", action="store_true")
    p_dsl_regress.add_argument("--keep-going", action="store_true")
    p_dsl_regress.set_defaults(func=cmd_dsl_regress)

    p_voice = sub.add_parser(
        "voice",
        help="Gera/cacheia TTS para os segmentos de um conteúdo.",
    )
    p_voice.add_argument("id")
    p_voice.add_argument("--voice")
    p_voice.add_argument("--force", action="store_true")
    p_voice.add_argument("--dry-run", action="store_true")
    p_voice.set_defaults(func=cmd_voice)

    p_produce = sub.add_parser(
        "produce",
        help=(
            "Importa opcionalmente um .qenem/.demo, prepara voz "
            "e renderiza em uma única operação."
        ),
    )
    p_produce.add_argument(
        "target",
        help="ID existente ou caminho para .qenem/.demo.",
    )
    p_produce.add_argument("--replace", action="store_true")
    p_produce.add_argument(
        "--format",
        choices=["vertical", "horizontal"],
        default=None,
    )
    p_produce.add_argument(
        "--quality",
        choices=["draft", "final"],
        default="draft",
    )
    p_produce.add_argument("--voice")
    p_produce.add_argument(
        "--skip-voice",
        action="store_true",
    )
    p_produce.add_argument(
        "--force-voice",
        action="store_true",
    )
    p_produce.add_argument("--preview", action="store_true")
    p_produce.add_argument("--fast", action="store_true")
    p_produce.add_argument("--dry-run", action="store_true")
    p_produce.set_defaults(func=cmd_produce)

    p_render = sub.add_parser(
        "render",
        help="Renderiza conteúdo pelo engine unificado.",
    )
    p_render.add_argument(
        "id",
        nargs="?",
        help="ID do conteúdo.",
    )
    p_render.add_argument(
        "--all",
        action="store_true",
        help="Renderiza todos os conteúdos selecionados.",
    )
    p_render.add_argument(
        "--type",
        choices=["qenem", "demo"],
        help="Filtra o lote por tipo.",
    )
    p_render.add_argument(
        "--status",
        choices=[
            "all",
            "draft",
            "validated",
            "production",
            "deprecated",
        ],
        default="production",
        help="Filtra por status; use 'all' para todos.",
    )
    p_render.add_argument(
        "--format",
        choices=["vertical", "horizontal"],
        default="vertical",
    )
    p_render.add_argument(
        "--quality",
        choices=["draft", "final"],
        default="draft",
    )
    p_render.add_argument(
        "--engine",
        choices=["production", "native", "dsl"],
        default="production",
        help=(
            "production grava em media/; native em media_native/; "
            "dsl renderiza o shadow port em media_dsl/."
        ),
    )
    p_render.add_argument("--preview", action="store_true")
    p_render.add_argument(
        "--fast",
        action="store_true",
        help="Prévia rápida: reduz esperas e não toca áudio.",
    )
    p_render.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o comando sem executar o Manim.",
    )
    p_render.add_argument("--keep-going", action="store_true")
    p_render.set_defaults(func=cmd_render)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        code = int(args.func(args) or 0)
    except (
        ManifestError,
        RenderError,
        KeyError,
        ValueError,
    ) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(code)
