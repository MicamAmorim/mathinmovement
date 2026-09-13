from __future__ import annotations

import subprocess
import sys

from .config import PROJECT_ROOT, REGISTRY_DB
from .database import database_stats
from .dsl.runtime import validate_program
from .engine import RenderError, render_record
from .models import ManifestError
from .registry import Registry


def _run_python(*args: str) -> None:
    cmd = [sys.executable, *args]
    print("\n>", subprocess.list2cmdline(cmd))
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    if result.returncode:
        raise RuntimeError(
            f"Comando terminou com código {result.returncode}: "
            f"{subprocess.list2cmdline(cmd)}"
        )


def _validate_catalog(registry: Registry) -> tuple[int, int]:
    records = registry.all()
    production = [
        record
        for record in records
        if record.manifest.get("status") == "production"
    ]
    demos = [record for record in production if record.type == "demo"]
    qenem = [record for record in production if record.type == "qenem"]

    if len(production) != 60:
        raise RuntimeError(
            "Baseline de produção esperado: 60 conteúdos; "
            f"encontrado: {len(production)}."
        )
    if len(demos) != 30 or len(qenem) != 30:
        raise RuntimeError(
            "Baseline de produção esperado: 30 demos + 30 qENEM; "
            f"encontrado: {len(demos)} demos + {len(qenem)} qENEM."
        )

    demo_shadows = 0
    qenem_shadows = 0

    for record in records:
        canonical_program = record.manifest.get("visual_program")
        if canonical_program:
            validate_program(canonical_program)

        for name, spec in (record.manifest.get("visuals") or {}).items():
            if isinstance(spec, dict) and spec.get("program"):
                validate_program(spec["program"])

        shadow = record.manifest.get("dsl_shadow") or {}
        if shadow.get("visual_program"):
            validate_program(shadow["visual_program"])
            if (
                record.manifest.get("status") == "production"
                and record.type == "demo"
            ):
                demo_shadows += 1

        visual_count = 0
        for name, spec in (shadow.get("visuals") or {}).items():
            if isinstance(spec, dict) and spec.get("program"):
                validate_program(spec["program"])
                visual_count += 1

        if (
            record.manifest.get("status") == "production"
            and record.type == "qenem"
            and visual_count
        ):
            qenem_shadows += 1

        if record.manifest.get("status") == "production":
            supported_formats = list(shadow.get("formats") or [])
            approved_formats = list(shadow.get("approved_formats") or [])
            if "vertical" not in approved_formats:
                raise RuntimeError(
                    f"{record.id}: DSL vertical ainda não está aprovada para produção."
                )
            unsupported_approvals = sorted(
                set(approved_formats) - set(supported_formats)
            )
            if unsupported_approvals:
                raise RuntimeError(
                    f"{record.id}: approved_formats contém formato(s) não "
                    f"suportado(s): {unsupported_approvals}."
                )

    if demo_shadows != 30:
        raise RuntimeError(
            f"DSL demo incompleta: esperado 30/30; encontrado {demo_shadows}/30."
        )
    if qenem_shadows != 30:
        raise RuntimeError(
            f"DSL qENEM incompleta: esperado 30/30; encontrado {qenem_shadows}/30."
        )

    for record in production:
        production_engine = str(
            (record.manifest.get("render") or {}).get(
                "production_engine",
                "native",
            )
        )
        if production_engine != "dsl":
            raise RuntimeError(
                f"{record.id}: production_engine esperado 'dsl'; "
                f"encontrado {production_engine!r}."
            )

    return demo_shadows, qenem_shadows


def verify_local(*, render_dsl: bool = False, keep_going: bool = False) -> int:
    """Quality gate local para uso enquanto CI remota não está disponível."""

    print("=== Math in Movement · verificação local ===")

    print("\n[1/5] Compilação Python")
    _run_python("-m", "compileall", "-q", "src", "tests")

    print("\n[2/5] Testes unitários")
    _run_python("-m", "unittest", "discover", "-s", "tests", "-v")

    print("\n[3/5] Catálogo, manifests e SQLite")
    registry = Registry().rebuild()
    demo_shadows, qenem_shadows = _validate_catalog(registry)

    stats = database_stats(REGISTRY_DB)
    if not stats.get("exists") or stats.get("total") != len(registry):
        raise RuntimeError(
            "SQLite não ficou sincronizado com o catálogo atual."
        )
    print(
        f"PASS: {len(registry)} conteúdo(s) válido(s) · "
        "baseline produção 60 · "
        f"DSL demos {demo_shadows}/30 · "
        f"DSL qENEM {qenem_shadows}/30."
    )

    print("\n[4/5] Preparação de render DSL por formato")
    failures: list[tuple[str, str, str]] = []
    checked = 0

    for record in registry.all():
        shadow = record.manifest.get("dsl_shadow") or {}
        canonical = bool(
            record.manifest.get("visual_program")
            or any(
                isinstance(spec, dict) and spec.get("program")
                for spec in (record.manifest.get("visuals") or {}).values()
            )
        )
        if not shadow and not canonical:
            continue
        formats = (
            (record.manifest.get("render") or {}).get("formats")
            if canonical
            else shadow.get("formats")
        ) or ["vertical"]
        for video_format in formats:
            checked += 1
            try:
                render_record(
                    record,
                    video_format=str(video_format),
                    quality="draft",
                    preview=False,
                    dry_run=not render_dsl,
                    fast_preview=render_dsl,
                    render_engine="dsl",
                )
            except (ManifestError, RenderError, RuntimeError) as exc:
                failures.append((record.id, str(video_format), str(exc)))
                print(
                    f"ERRO: {record.id} · {video_format} · {exc}",
                    file=sys.stderr,
                )
                if not keep_going:
                    raise

    if failures:
        details = "\n".join(
            f"- {content_id} · {fmt}: {reason}"
            for content_id, fmt, reason in failures
        )
        raise RuntimeError(
            f"{len(failures)} falha(s) na regressão DSL:\n{details}"
        )

    print(
        f"PASS: {checked} combinação(ões) conteúdo/formato "
        + ("renderizada(s)." if render_dsl else "validada(s) em dry-run.")
    )

    print("\n[5/5] Resultado")
    print("PASS: quality gate local concluído sem falhas.")
    return 0
