# Auditoria dos 30 roteiros

## Principais problemas encontrados no pacote original

1. **Não havia camada de narração.** As esperas eram calculadas por quantidade de palavras, o que não se mantém sincronizado quando uma voz real é adicionada.
2. **Figura e modelo didático eram tratados como a mesma coisa.** Em questões nas quais a figura carrega dados, isso podia fazer o vídeo saltar informação indispensável.
3. **Alternativas visuais eram textualizadas.** O caso mais importante é ENEM-2023-MT-29 (Q164), cujas cinco respostas são gráficos.
4. **Q146/2021 continha um dado incorreto no roteiro:** `h=7,7 cm`. A figura usa `h=8 cm`. O roteiro foi refeito para chegar a `P=16√3≈27,2 cm`, cuja alternativa mais próxima é 27,18.
5. **Q145/2022 continha coordenadas incorretas:** o roteiro usava aproximadamente A=(10,40) e B=(40,10). A reconstrução correta usa A=(20,40), B=(50,20), reflete B para (50,-20) e encontra a interseção em x=40, ponto IV.
6. Em alguns vídeos, a explicação começava direto na fórmula. Agora há uma ponte explícita entre leitura, dados, objetivo, estratégia e representação visual.

## Novo ritmo pedagógico

Cada vídeo agora segue:

1. fonte e identificação;
2. leitura narrada do problema em páginas curtas;
3. figura da questão, quando existe;
4. alternativas — e alternativas gráficas desenhadas quando necessário;
5. dados relevantes;
6. objetivo + estratégia;
7. modelo visual didático;
8. resolução em passos pequenos, um segmento de voz por passo;
9. resposta final.

A vantagem de segmentar a voz é que a animação usa a duração real do MP3. Se uma voz for trocada por outra mais lenta, o código continua sincronizado sem editar manualmente dezenas de `wait()`.

## Auditoria de figuras

| # | Questão | Figura/tabela/gráfico no enunciado? | Tratamento na v2 |
|---:|---|:---:|---|
| 01 | ENEM-2021-MT-11 · Q146 | Sim | instrumento + equilátero com altura 8 cm |
| 02 | ENEM-2021-MT-12 · Q147 | Sim | caneca/tronco de cone com D=10, d=8 e h=12 |
| 03 | ENEM-2021-MT-13 · Q148 | Não | modelos geométricos entram no visual didático |
| 04 | ENEM-2021-MT-17 · Q152 | Não | contêiner modelado didaticamente |
| 05 | ENEM-2021-MT-18 · Q153 | Não | cilindro modelado didaticamente |
| 06 | ENEM-2021-MT-28 · Q163 | Sim | castelo/ponte reconstruídos esquematicamente |
| 07 | ENEM-2022-MT-07 · Q142 | Não | comparação de cilindros no modelo didático |
| 08 | ENEM-2022-MT-10 · Q145 | Sim | plano cartesiano com A=(20,40), B=(50,20), I–V |
| 09 | ENEM-2022-MT-12 · Q147 | Não | comparação de esferas no modelo didático |
| 10 | ENEM-2022-MT-13 · Q148 | Sim | cone com diâmetro 8 cm e altura 10 cm |
| 11 | ENEM-2022-MT-25 · Q160 | Não | a planta é descrita em texto; dimensões usadas diretamente |
| 12 | ENEM-2022-MT-32 · Q167 | Não | piscina/área interna modelada didaticamente |
| 13 | ENEM-2022-MT-34 · Q169 | Não | cilindro → esferas no visual didático |
| 14 | ENEM-2023-MT-04 · Q139 | Sim | escada com três degraus e medidas |
| 15 | ENEM-2023-MT-06 · Q141 | Sim | lua circular + telhado triangular |
| 16 | ENEM-2023-MT-07 · Q142 | Sim | piscina quadrada + faixa de 5 m |
| 17 | ENEM-2023-MT-15 · Q150 | Sim | cone, retirada do cone menor e perfuração cilíndrica |
| 18 | ENEM-2023-MT-29 · Q164 | Sim | roda-gigante + cinco alternativas desenhadas como gráficos |
| 19 | ENEM-2023-MT-31 · Q166 | Não | reservatório cilíndrico no modelo didático |
| 20 | ENEM-2023-MT-33 · Q168 | Sim | cisterna + tabela tempo × nível |
| 21 | ENEM-2023-MT-41 · Q176 | Sim | mastro, solo e cabo formando triângulo retângulo |
| 22 | ENEM-2023-MT-42 · Q177 | Sim | gráfico em malha e trajetória por segmentos |
| 23 | ENEM-2023-MT-44 · Q179 | Sim | triângulo/círculos e pizzas/semicírculos |
| 24 | ENEM-2024-MT-02 · Q137 | Sim | setor circular de raio R e ângulo α |
| 25 | ENEM-2024-MT-05 · Q140 | Não | comparação de escala de área no modelo didático |
| 26 | ENEM-2024-MT-11 · Q146 | Não | cilindro → cubo no modelo didático |
| 27 | ENEM-2024-MT-14 · Q149 | Sim | trapézio e eixo de rotação |
| 28 | ENEM-2024-MT-30 · Q165 | Sim | duas maneiras de enrolar a folha 10×20 |
| 29 | ENEM-2024-MT-34 · Q169 | Não | polígonos regulares no modelo didático |
| 30 | ENEM-2025-MT-08 · Q143 | Sim | ciclovia circular e arco protegido de 400 m |

**Total: 18 questões com figura/tabela/gráfico de enunciado reconstruído na v2.**

## Observação sobre fidelidade visual

As imagens são reconstruções vetoriais didáticas, não cópias rasterizadas do caderno. Para uma versão futura que exija fidelidade gráfica pixel a pixel, o melhor caminho é extrair/cortar as figuras diretamente dos PDFs canônicos e manter as reconstruções apenas na etapa explicativa.
