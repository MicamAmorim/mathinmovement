from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys
import json
import time

ROOT = Path(__file__).resolve().parent
VIDEOS = ROOT / "videos"

SCENES = [
    (1, "01_area_triangulo.py", "AreaTriangulo"),
    (2, "02_area_paralelogramo.py", "AreaParalelogramo"),
    (3, "03_area_trapezio.py", "AreaTrapezio"),
    (4, "04_area_losango.py", "AreaLosango"),
    (5, "05_area_triangulo_equilatero.py", "AreaTrianguloEquilatero"),
    (6, "06_area_poligonos_regulares.py", "AreaPoligonosRegulares"),
    (7, "07_comprimento_circunferencia_pi.py", "ComprimentoCircunferenciaPi"),
    (8, "08_area_circulo.py", "AreaCirculo"),
    (9, "09_comprimento_arco.py", "ComprimentoArco"),
    (10, "10_area_setor_circular.py", "AreaSetorCircular"),
    (11, "11_area_coroa_circular.py", "AreaCoroaCircular"),
    (12, "12_teorema_pitagoras.py", "TeoremaPitagoras"),
    (13, "13_relacoes_metricas_triangulo_retangulo.py", "RelacoesMetricasTrianguloRetangulo"),
    (14, "14_razoes_trigonometricas_semelhanca.py", "RazoesTrigonometricasSemelhanca"),
    (15, "15_lei_senos.py", "LeiSenos"),
    (16, "16_lei_cossenos.py", "LeiCossenos"),
    (17, "17_area_triangulo_seno.py", "AreaTrianguloSeno"),
    (18, "18_escalas_comprimentos_areas_volumes.py", "EscalasComprimentosAreasVolumes"),
    (19, "19_relacao_euler_poliedros.py", "RelacaoEulerPoliedros"),
    (20, "20_diagonal_paralelepipedo.py", "DiagonalParalelepipedo"),
    (21, "21_area_prismas_planificacao.py", "AreaPrismasPlanificacao"),
    (22, "22_volume_prismas.py", "VolumePrismas"),
    (23, "23_area_cilindro.py", "AreaCilindro"),
    (24, "24_volume_cilindro.py", "VolumeCilindro"),
    (25, "25_area_piramides_regulares.py", "AreaPiramidesRegulares"),
    (26, "26_volume_piramide.py", "VolumePiramide"),
    (27, "27_area_cone.py", "AreaCone"),
    (28, "28_volume_cone.py", "VolumeCone"),
    (29, "29_volume_esfera.py", "VolumeEsfera"),
    (30, "30_area_esfera.py", "AreaEsfera"),
]


def main():
    parser = argparse.ArgumentParser(description="Renderiza a série Matemática em Movimento.")
    parser.add_argument("--from", dest="start", type=int, default=1, help="primeiro episódio")
    parser.add_argument("--to", dest="end", type=int, default=30, help="último episódio")
    parser.add_argument("--keep-going", action="store_true", help="continua após erro")
    parser.add_argument("--preview", action="store_true", help="abre o vídeo após cada render")
    parser.add_argument("--quality", choices=["draft", "final"], default="final")
    parser.add_argument("--smoke", action="store_true", help="executa a cena inteira, salvando só o quadro final")
    parser.add_argument("--dry-run", action="store_true", help="mostra comandos sem renderizar")
    parser.add_argument("--timeout", type=int, default=1800, help="limite em segundos por episódio")
    args = parser.parse_args()

    selected = [s for s in SCENES if args.start <= s[0] <= args.end]
    if not selected:
        raise SystemExit("Nenhum episódio no intervalo informado.")

    failures = []
    records = []
    logs = ROOT / "logs"
    if not args.dry_run:
        logs.mkdir(exist_ok=True)
    for number, filename, scene in selected:
        print(f"\n=== [{number:02d}] {scene} ===")
        cmd = [sys.executable, "-m", "manim", "--format", "mp4"]
        cmd += ["-r", "360,640" if args.quality == "draft" else "1080,1920",
                "--fps", "15" if args.quality == "draft" else "30", "--disable_caching"]
        if args.smoke:
            cmd.append("-s")
        if args.preview:
            cmd.append("-p")
        cmd += [str(VIDEOS / filename), scene]
        if args.dry_run:
            print(subprocess.list2cmdline(cmd))
            continue
        started = time.monotonic()
        logpath = logs / f"{number:02d}-{scene}.log"
        try:
            with logpath.open("w", encoding="utf-8") as log:
                result = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                        timeout=args.timeout)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
        records.append({"episode":number,"scene":scene,"returncode":code,
                        "seconds":round(time.monotonic()-started,2),"log":str(logpath),
                        "mode":"smoke" if args.smoke else args.quality})
        (logs / "render_report.json").write_text(json.dumps(records,indent=2),encoding="utf-8")
        print(f"{'OK' if code == 0 else 'ERRO'} — log: {logpath}")
        if code != 0:
            failures.append((number, scene))
            if not args.keep_going:
                raise SystemExit(code)

    if failures:
        print("\nFalharam:")
        for number, scene in failures:
            print(f"- {number:02d}: {scene}")
        raise SystemExit(1)
    print("\nComandos listados." if args.dry_run else
          "\nTeste das cenas concluído (apenas quadros finais)." if args.smoke else
          "\nTodos os vídeos selecionados foram renderizados.")


if __name__ == "__main__":
    main()
