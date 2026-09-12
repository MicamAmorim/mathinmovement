# Relatório de revisão

## Diagnóstico

- O log mostra falha no episódio 27: Sector(outer_radius=...) passa outer_radius duas vezes ao AnnularSector. Corrigido para radius. Mesmo padrão existia em 08 e 10.
- Avisos de DejaVu Sans ausente no Windows: adicionada seleção de fonte instalada.
- right_angle usava comparação de arrays NumPy em tuplas, sujeita a valor lógico ambíguo. Agora usa componentes escalares.
- common.py sobrescrevia pixels/fps e impedia rascunhos menores.
- 07: círculo de raio 2, reta de comprimento 6,3 e suposto diâmetro de tamanho 2; escala incoerente.
- 06: triângulos mudavam de proporção no rearranjo.
- 08: setores viravam triângulos sem conservar área; retângulo final não correspondia à união das peças.
- 18: divisão do quadrado fora do meio.
- 20: diagonal frontal chamada de diagonal da base.
- 25: altura g desenhada fora da altura da face.
- 29: cone invertido em relação à fórmula πy²; figuras não permaneciam lado a lado.

## Modificações

01–03 preservam a estrutura. 04 mantém a prova com movimentos rígidos.
06, 07, 08, 19, 21, 23, 29 e 30 foram reescritos. Demais cenas receberam correções localizadas e/ou etapas adicionais, além do ritmo compartilhado. Ver planejamento.md.

O renderizador oferece rascunho/final, teste sem vídeo, timeout, log por episódio e relatório JSON. --keep-going continua após falhas, mas retorna código 1 se houve erro. --smoke executa a construção e salva só o quadro final; não verifica estados intermediários. --dry-run somente imprime comandos.

## Testes executados e aprovados

- Compilação sintática dos arquivos Python com compileall.
- validate.py: 30 nomes de cena e argumentos Sector; invariantes geométricos de 02, 04, 07, 08, 13, 19, 27, 29.
- --dry-run do renderizador para 07–08.

Os testes geométricos verificam exemplos e endpoints, não todos os quadros.

## Testes NÃO executados

Manim não pôde ser instalado por ausência de dependências nativas e bloqueio de permissão na instalação. Não houve renderização, compilação LaTeX nem inspeção visual de MP4. Aprovação estática não garante renderização sem erros.

## Conferência local

1. python validate.py
2. python render_all.py --smoke --quality draft --keep-going
3. python render_all.py --from 7 --to 8 --quality draft
4. Assistir aos rascunhos, sobretudo 04, 08, 13, 19, 21, 23, 26, 29 e 30.
5. python render_all.py --quality final --keep-going

Erros ficam em logs/NN-NomeDaCena.log. render_report.json registra apenas a última execução selecionada.

