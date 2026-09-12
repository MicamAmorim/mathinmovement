# Matemática em Movimento — roteiros revisados

## Direção editorial

Preservar a ideia dos quatro primeiros: a figura faz o argumento; a equação registra o que aconteceu. Não limitar a 30 segundos uma demonstração que precisa de mais etapas. As durações finais ainda não foram medidas em render.

1. Apresentar fórmula e desenhar a figura gradualmente.
2. Nomear medidas antes de usá-las; distinguir altura de lado inclinado.
3. Anunciar uma operação, executá-la e dar tempo para observar.
4. Em recortes planos, preservar comprimentos e área durante o movimento.
5. Cópias somente quando exigidas pela prova. Projeção de sólido e planificação são representações distintas: sua transição não é recorte plano.
6. Exibir passos algébricos intermediários com pausas.
7. Distinguir exemplo, definição, aproximação, limite e demonstração geral.
8. Encerrar sem empilhar equações.

## Sequência dos 30 episódios

| Nº | Tema | Encadeamento revisado |
|---:|---|---|
| 01 | Triângulo | Base e altura → cópia gira → paralelogramo → metade. Estrutura original preservada. |
| 02 | Paralelogramo | Cortar ponta → mover a própria peça → retângulo exato. Estrutura preservada. |
| 03 | Trapézio | Bases → girar cópia → somar B+b → metade. Estrutura preservada. |
| 04 | Losango | Diagonais → quatro peças → movimentos rígidos → retângulo D × d/2. Eliminada deformação de vértices. |
| 05 | Equilátero | Metade da base → triângulo retângulo → subtrair ℓ²/4 → obter 3ℓ²/4 → raiz positiva → substituir altura. |
| 06 | Polígono regular | Triangular sem deformar → apótema → destacar e somar seis áreas → generalizar a n → P=nℓ. |
| 07 | Circunferência | Mostrar d=2r → rolar sem escorregar → distância de uma volta → três diâmetros e resto → definir π. Ilustra a definição, não mede π independentemente. |
| 08 | Círculo | Setores reais → movimentos rígidos → 8, 16 e 32 peças → bordas aproximam retas → limite com base πr e altura r. A figura finita não é retângulo exato. |
| 09 | Arco | 120° → três arcos completam volta → um terço → proporção geral → graus/radianos. |
| 10 | Setor | 120° → três setores cobrem círculo → um terço da área → proporção → unidade angular explícita. |
| 11 | Coroa | Disco maior e máscara interna → raios → subtração → fatorar π. Máscara permanece opaca. |
| 12 | Pitágoras | Quatro triângulos → lados a,b → centro de lado c → ângulos justificam quadrado → igualdade de áreas → expandir/cancelar. |
| 13 | Relações métricas | Triângulo exatamente retângulo → altura → ângulos correspondentes → h/m=n/h → destacar subtriângulos → proporções dos catetos. |
| 14 | Trigonometria | Ampliar com mesmo ângulo → nomear op/adj/hip → fator k nos dois termos → cancelamento → razões. |
| 15 | Lei dos senos | Primeira altura → duas expressões → igualdade → segunda altura desenhada → terceiro quociente. Desenho do caso agudo. |
| 16 | Lei dos cossenos | Projeção b cos A → altura b sen A → trecho c−b cos A → Pitágoras → expansão → identidade. Desenho agudo; projeções orientadas estendem o argumento. |
| 17 | Área com seno | Base/altura → destacar triângulo auxiliar → seno fornece h → substituição explícita. |
| 18 | Escalas | Quadrado → quatro partes iguais → oito cubinhos em 2×2×2 → generalizar k, k², k³. |
| 19 | Euler | Cubo aberto em diagrama plano → retirar aresta de ciclo/região → árvore → folhas/arestas → um vértice → devolver face. O cubo ilustra o processo para superfície convexa. |
| 20 | Diagonal espacial | Diagonal da base AB₂ → triângulo horizontal → Pitágoras → triângulo AB₂C₂ → segundo Pitágoras. |
| 21 | Área de prisma | Faces projetadas → retângulos no plano → larguras somam P_b → lateral → duas bases. Mudança de representação, não movimento rígido plano. |
| 22 | Volume de prisma | Base projetada achatada → seções → camada A_bΔh → n camadas com nΔh=h → fórmula. Seções representam camadas, não objetos de volume positivo e espessura zero. |
| 23 | Área de cilindro | Lateral em faixas → abrir → uma volta vira largura → 2πrh → duas tampas. Projeção esquemática passa à planificação. |
| 24 | Volume de cilindro | Disco → seções paralelas → área constante → nπr²Δh → somar alturas. |
| 25 | Área de pirâmide | Faces → altura da face g → área individual → somar faces → perímetro → base. |
| 26 | Volume de pirâmide | Cubo → três pirâmides com vértice comum → simetria → 1/3 → esticar altura → seções t²A_b → Cavalieri. A generalização depende desse princípio. |
| 27 | Área de cone | Cone com r,g coerentes → setor de raio g → arco 2πr → proporção com círculo de raio g → lateral → base. |
| 28 | Volume de cone | Pirâmides em projeção horizontal → mais lados → círculo-limite → manter altura e 1/3. |
| 29 | Volume de esfera | Cortes axiais lado a lado → cone com vértice no nível zero → mover altura → disco/coroa de áreas iguais → Cavalieri → cilindro menos cone → duplicar. |
| 30 | Área de esfera | Faixa estreita → largura inclinada e raio local → semelhança → compensação ρ·R/ρ → área por altura → integrar ao longo de 2R. Uso de limite/diferencial explícito. |

## Ritmo implementado

Legendas quebradas em linhas, com pausa proporcional ao número de palavras; equações com pausa de 2 segundos. Animações 15% mais lentas por padrão (MANIM_PACE ajustável). Pausas finais mantidas. Sem trilha/narração. Fonte selecionada dentre as instaladas. Pixels/fps ficam na configuração/CLI, permitindo rascunhos menores.

## Limite de validação

Revisão de fontes, sintaxe e testes numéricos concluída. Não houve renderização Manim: dependências nativas ausentes e instalação bloqueada por permissão. Ainda é preciso verificar visualmente fontes, colisões intermediárias, LaTeX e exportação. Não há novos MP4 no ZIP.

