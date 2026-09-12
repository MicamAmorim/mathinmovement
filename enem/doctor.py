from __future__ import annotations

from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

from font_utils import TEXT_FONT


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def warn(msg: str) -> None:
    print(f"[AVISO] {msg}")


def fail(msg: str) -> None:
    print(f"[ERRO] {msg}")


def run(cmd, *, cwd=ROOT, timeout=120):
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        encoding="utf-8",
        errors="replace",
    )


def main() -> int:
    print("=== ENEM / Manim — diagnóstico do ambiente ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Executável: {sys.executable}")
    print(f"Projeto: {ROOT}")

    errors = []

    if importlib.util.find_spec("manim") is None:
        fail("O módulo 'manim' não está instalado neste ambiente virtual.")
        print(f"      Execute: {sys.executable} -m pip install -r \"{ROOT / 'requirements.txt'}\"")
        return 2

    try:
        import manim  # type: ignore
        ok(f"Manim {manim.__version__} importado")
    except Exception as exc:
        fail(f"Falha ao importar Manim: {exc!r}")
        return 2

    try:
        import av  # type: ignore
        ok(f"PyAV {getattr(av, '__version__', '?')} disponível")
    except Exception as exc:
        fail(f"PyAV não pode ser importado: {exc!r}")
        errors.append("pyav")

    # MathTex é usado em todas as 30 resoluções.
    latex = shutil.which("latex")
    dvisvgm = shutil.which("dvisvgm")
    if latex:
        ok(f"latex encontrado: {latex}")
    else:
        fail("'latex' não foi encontrado no PATH. MathTex não funcionará.")
        print("      No Windows, instale MiKTeX e abra um novo PowerShell depois da instalação.")
        errors.append("latex")

    if dvisvgm:
        ok(f"dvisvgm encontrado: {dvisvgm}")
    else:
        fail("'dvisvgm' não foi encontrado no PATH. O Manim precisa dele para MathTex.")
        print("      O MiKTeX normalmente instala/fornece dvisvgm.")
        errors.append("dvisvgm")

    try:
        import manimpango  # type: ignore
        fonts = {str(x).casefold() for x in manimpango.list_fonts()}
        if TEXT_FONT.casefold() in fonts or TEXT_FONT.casefold() == "sans":
            ok(f"Fonte de texto selecionada: {TEXT_FONT}")
        else:
            warn(f"Fonte selecionada '{TEXT_FONT}' não apareceu na lista do Pango; será usado fallback.")
    except Exception as exc:
        warn(f"Não consegui listar fontes via manimpango: {exc!r}")

    expected = [
        ROOT / "common.py",
        ROOT / "font_utils.py",
        ROOT / "specs.py",
        ROOT / "visuals.py",
        ROOT / "data" / "questions.json",
        ROOT / "narrations" / "narrations.json",
        ROOT / "videos" / "01_2021_q146_triangulo_equilatero.py",
    ]
    missing = [p for p in expected if not p.exists()]
    if missing:
        for p in missing:
            fail(f"Arquivo ausente: {p}")
        return 2
    ok("Estrutura essencial do projeto encontrada")

    # Verifica o CLI do mesmo Python que está rodando o runner.
    ver = run([sys.executable, "-m", "manim", "--version"], timeout=30)
    if ver.returncode:
        fail("'python -m manim --version' falhou:")
        print(ver.stdout[-3000:])
        return 2
    ok(ver.stdout.strip().splitlines()[-1] if ver.stdout.strip() else "CLI do Manim disponível")

    if errors:
        print("\nO smoke test foi pulado porque há dependências obrigatórias ausentes.")
        return 2

    # Teste mínimo que cobre exatamente os dois subsistemas compartilhados
    # por todas as cenas: Pango/Text e LaTeX/MathTex.
    smoke = ROOT / "logs" / "_smoke_test.py"
    smoke.parent.mkdir(exist_ok=True)
    smoke.write_text(
        "from manim import *\n"
        "class SmokeTest(Scene):\n"
        "    def construct(self):\n"
        f"        self.add(Text('ENEM', font={TEXT_FONT!r}))\n"
        "        self.add(MathTex(r'x^2+y^2=1').shift(DOWN))\n",
        encoding="utf-8",
    )
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "--dry_run",
        "--disable_caching",
        "--progress_bar",
        "none",
        str(smoke),
        "SmokeTest",
    ]
    print("\nExecutando smoke test Text + MathTex...")
    try:
        result = run(cmd, timeout=180)
    except subprocess.TimeoutExpired:
        fail("Smoke test excedeu 180 s.")
        return 2

    if result.returncode:
        fail("Smoke test do Manim falhou. Saída final:")
        lines = result.stdout.splitlines()
        print("\n".join(lines[-100:]))
        return result.returncode or 2

    ok("Smoke test Text + MathTex passou")
    print("\nAmbiente pronto para renderizar as resoluções.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
