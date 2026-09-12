from __future__ import annotations

from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
VIDEOS = ROOT / "videos"
SCENES = [
    (1, "01_2021_q146_triangulo_equilatero.py", "Resolucao01"),
    (2, "02_2021_q147_caneca_tronco_cone.py", "Resolucao02"),
    (3, "03_2021_q148_areas_cartoes.py", "Resolucao03"),
    (4, "04_2021_q152_area_container.py", "Resolucao04"),
    (5, "05_2021_q153_volume_reservatorio.py", "Resolucao05"),
    (6, "06_2021_q163_escala_castelo.py", "Resolucao06"),
    (7, "07_2022_q142_capacidade_cilindros.py", "Resolucao07"),
    (8, "08_2022_q145_menor_caminho.py", "Resolucao08"),
    (9, "09_2022_q147_escala_esferas.py", "Resolucao09"),
    (10, "10_2022_q148_volume_cone.py", "Resolucao10"),
    (11, "11_2022_q160_escala_refrigerador.py", "Resolucao11"),
    (12, "12_2022_q167_area_piscina.py", "Resolucao12"),
    (13, "13_2022_q169_cilindro_em_esferas.py", "Resolucao13"),
    (14, "14_2023_q139_area_escada.py", "Resolucao14"),
    (15, "15_2023_q141_setor_circular.py", "Resolucao15"),
    (16, "16_2023_q142_area_calcada.py", "Resolucao16"),
    (17, "17_2023_q150_escultura_cones.py", "Resolucao17"),
    (18, "18_2023_q164_roda_gigante.py", "Resolucao18"),
    (19, "19_2023_q166_reservatorio.py", "Resolucao19"),
    (20, "20_2023_q168_vazao_cisterna.py", "Resolucao20"),
    (21, "21_2023_q176_cabos_mastro.py", "Resolucao21"),
    (22, "22_2023_q177_escala_voo.py", "Resolucao22"),
    (23, "23_2023_q179_pizzas_lei_cossenos.py", "Resolucao23"),
    (24, "24_2024_q137_area_setor.py", "Resolucao24"),
    (25, "25_2024_q140_escala_area.py", "Resolucao25"),
    (26, "26_2024_q146_cilindro_cubo.py", "Resolucao26"),
    (27, "27_2024_q149_solido_revolucao.py", "Resolucao27"),
    (28, "28_2024_q165_embalagens_cilindricas.py", "Resolucao28"),
    (29, "29_2024_q169_poligono_maior_area.py", "Resolucao29"),
    (30, "30_2025_q143_ciclovia.py", "Resolucao30"),
]


def tail(path: Path, n: int = 80) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lines[-n:])
    except Exception as exc:
        return f"<não foi possível ler {path}: {exc}>"


def preflight() -> int:
    doctor = ROOT / "doctor.py"
    if not doctor.exists():
        return 0
    print("Verificando ambiente antes da renderização...\n")
    return subprocess.run([sys.executable, str(doctor)], cwd=ROOT).returncode


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", type=int, default=1)
    p.add_argument("--to", dest="end", type=int, default=30)
    p.add_argument("--quality", choices=["draft", "final"], default="draft")
    p.add_argument("--format", dest="video_format", choices=["vertical", "horizontal"], default="vertical",
                   help="vertical=9:16 (padrão atual), horizontal=16:9")
    p.add_argument("--keep-going", action="store_true")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--timeout", type=int, default=3600)
    p.add_argument("--no-preflight", action="store_true", help="Pula doctor.py")
    p.add_argument("--tail-lines", type=int, default=80, help="Linhas finais do log exibidas quando uma cena falha")
    a = p.parse_args()

    if not a.no_preflight:
        code = preflight()
        if code:
            print("\nPré-teste falhou. As 30 cenas NÃO serão tentadas até o ambiente ser corrigido.")
            raise SystemExit(code)
        print()

    if a.video_format == "horizontal":
        resolution = "640,360" if a.quality == "draft" else "1920,1080"
        report_name = "render_report_horizontal.json"
        log_suffix = "_horizontal"
    else:
        resolution = "360,640" if a.quality == "draft" else "1080,1920"
        report_name = "render_report.json"
        log_suffix = ""

    print(f"Formato: {a.video_format} · resolução: {resolution.replace(',', '×')}")

    logs = ROOT / "logs"
    logs.mkdir(exist_ok=True)
    records = []
    failures = []
    render_env = os.environ.copy()
    render_env["ENEM_FORMAT"] = a.video_format

    for number, file, scene in SCENES:
        if not a.start <= number <= a.end:
            continue

        scene_path = VIDEOS / file
        if not scene_path.exists():
            print(f"[{number:02d}] ERRO: arquivo não encontrado: {scene_path}")
            failures.append(number)
            if not a.keep_going:
                raise SystemExit(2)
            continue

        cmd = [
            sys.executable,
            "-m",
            "manim",
            "--format",
            "mp4",
            "--disable_caching",
            "--progress_bar",
            "none",
            "-r",
            resolution,
            "--fps",
            "15" if a.quality == "draft" else "30",
        ]
        # Horizontal output is isolated so it cannot overwrite the existing
        # vertical renders. Vertical keeps the exact historical media path.
        if a.video_format == "horizontal":
            cmd += ["--media_dir", str(ROOT / "media_horizontal")]
        if a.preview:
            cmd.append("-p")
        cmd += [str(scene_path), scene]

        logpath = logs / f"{number:02d}{log_suffix}.log"
        start = time.monotonic()
        print(f"[{number:02d}] {scene}")

        try:
            with logpath.open("w", encoding="utf-8") as log:
                result = subprocess.run(
                    cmd,
                    cwd=ROOT,
                    env=render_env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    timeout=a.timeout,
                    text=True,
                )
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
            with logpath.open("a", encoding="utf-8") as log:
                log.write(f"\nTIMEOUT após {a.timeout}s\n")

        seconds = round(time.monotonic() - start, 1)
        records.append(
            {
                "episode": number,
                "returncode": code,
                "seconds": seconds,
                "format": a.video_format,
                "resolution": resolution,
                "log": str(logpath),
                "command": cmd,
            }
        )
        (logs / report_name).write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

        if code:
            failures.append(number)
            print(f"    FALHOU (código {code}, {seconds}s). Últimas linhas de {logpath.name}:")
            print("    " + "-" * 72)
            snippet = tail(logpath, max(10, a.tail_lines))
            print("\n".join("    " + line for line in snippet.splitlines()))
            print("    " + "-" * 72)
            if not a.keep_going:
                raise SystemExit(code)
        else:
            print(f"    OK ({seconds}s)")

    if failures:
        print("\nFalharam:", failures)
        print(f"Relatório: {logs / report_name}")
        raise SystemExit(1)

    print("\nRenderização concluída.")
    if a.video_format == "horizontal":
        print(f"Saída horizontal isolada em: {ROOT / 'media_horizontal'}")


if __name__ == "__main__":
    main()
