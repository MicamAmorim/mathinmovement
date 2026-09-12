# Matemática em Movimento — 30 cenas revisadas

Pacote de código, não de vídeos renderizados. Leia REVISAO.md sobre correções e limites dos testes.

## Instalação

Extraia em pasta nova; não misture common.py antigo com as cenas revisadas.
Use Python 3.11 ou 3.12 e o ambiente anterior que já renderizava, se disponível.

Windows PowerShell:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt

Também são necessários LaTeX (ex.: MiKTeX), dvisvgm e FFmpeg. Linux pode precisar de bibliotecas de desenvolvimento Cairo/Pango e pkg-config. requirements.txt não instala dependências do sistema.

## Verificar

    python validate.py
    python render_all.py --smoke --quality draft --keep-going

O primeiro verifica sintaxe e geometria sem Manim. O segundo executa cada cena e salva só o quadro final. É necessário também assistir às animações intermediárias.

## Renderizar

    python render_all.py --from 7 --to 8 --quality draft
    python render_all.py --quality draft --keep-going
    python render_all.py --quality final --keep-going

Draft: 360 × 640, 15 fps. Final: 1080 × 1920, 30 fps.
Vídeos em media/videos; logs e relatório JSON em logs.
--preview abre o resultado. --timeout 3600 permite uma hora por cena.
--dry-run somente imprime comandos. Atalhos .bat/.sh aceitam os mesmos argumentos.

Cena individual:

    python -m manim --format mp4 -r 1080,1920 --fps 30 videos/07_comprimento_circunferencia_pi.py ComprimentoCircunferenciaPi

## Ritmo e fonte

Há pausas de leitura automáticas. MANIM_PACE altera apenas durações de animação; padrão 1.15. Exemplo PowerShell:

    $env:MANIM_PACE="1.25"
    $env:MANIM_FONT="Arial"
    python render_all.py --from 7 --to 7 --quality draft

Linux/WSL:

    MANIM_PACE=1.25 MANIM_FONT="DejaVu Sans" python render_all.py --from 7 --to 7 --quality draft

A fonte deve existir. Sem escolha explícita, são procuradas DejaVu Sans, Arial e Liberation Sans. Fórmulas usam MathTex/LaTeX.

## Conteúdo

- videos/: 30 cenas.
- common.py: identidade, movimentos rígidos, texto, ritmo.
- planejamento.md: roteiro revisado por episódio.
- planejamento-original.md: referência histórica, não especificação atual.
- REVISAO.md: diagnóstico e validações.
- validate.py: testes reproduzíveis sem render.
- render_all.py e atalhos: render em lote.

Não inclui novas músicas ou narração.

