# Matemática em Movimento — planejamento dos 30 vídeos

## Padrão geral da série

- **Formato:** vertical 9:16, 1080 × 1920, 30 fps.
- **Duração alvo:** aproximadamente 25–40 s por episódio; ajuste os `wait()` conforme a narração/ritmo desejado.
- **Identidade:** fundo `#0B1020`; turquesa para objeto principal; dourado para construção auxiliar; branco para estrutura; cores extras apenas quando ajudam a distinguir peças.
- **Tipografia:** `DejaVu Sans` para texto e LaTeX vetorial para fórmulas.
- **Estrutura narrativa:** fórmula-alvo → objeto geométrico surge gradualmente → construção/recorte/rearranjo → equações intermediárias → fórmula final destacada.
- **Regra visual:** quando uma demonstração usa recorte, são as **próprias peças** que se movem. Só há cópia quando a prova matematicamente exige uma segunda cópia.
- **Zonas fixas:** título/fórmula no topo, prova no centro, legenda em `y≈-3.3`, dedução em `y≈-4.75`, assinatura no rodapé.

---

## 01 — Área do triângulo
**Fórmula:** `A = bh/2`  
**Prova visual:** duplicar o triângulo e girar/transladar a cópia para completar um paralelogramo.  
**Sequência:** base e altura → segunda cópia → paralelogramo de área `bh` → cada triângulo é metade.

## 02 — Área do paralelogramo
**Fórmula:** `A = bh`  
**Prova visual:** cortar o triângulo de uma ponta e transladá-lo para a outra ponta, transformando o paralelogramo em retângulo.  
**Sequência:** mostrar altura perpendicular → corte → deslocamento da própria peça → retângulo `b × h`.

## 03 — Área do trapézio
**Fórmula:** `A = (B+b)h/2`  
**Prova visual:** uma cópia girada do trapézio completa um paralelogramo.  
**Sequência:** bases `B` e `b` → copiar/girar → base total `B+b` → dividir por 2.

## 04 — Área do losango
**Fórmula:** `A = Dd/2`  
**Prova visual:** diagonais dividem o losango em quatro triângulos; as próprias peças são rearranjadas num retângulo `D × d/2`.  
**Sequência:** diagonais → quatro peças → rearranjo → área do retângulo.

## 05 — Área do triângulo equilátero
**Fórmula:** `A = (√3/4)ℓ²`  
**Prova visual:** altura divide o lado ao meio; Pitágoras obtém `h = (√3/2)ℓ`.  
**Sequência:** equilátero → altura/mediana → triângulo retângulo → Pitágoras → substituir em `A=ℓh/2`.

## 06 — Área de polígonos regulares
**Fórmula:** `A = Pa/2`  
**Prova visual:** ligar centro aos vértices cria `n` triângulos congruentes; alinhá-los evidencia soma das bases `P=nℓ`.  
**Sequência:** triangulação → apótema → abrir/alinha triângulos → substituir `P=nℓ`.

## 07 — Comprimento da circunferência e significado de π
**Fórmula:** `C = πd = 2πr`  
**Prova visual:** desenrolar a circunferência e comparar seu comprimento com sucessivos diâmetros.  
**Sequência:** círculo/diâmetro → desenrolar em reta → pouco mais de 3 diâmetros → definir `π=C/d`.

## 08 — Área do círculo
**Fórmula:** `A = πr²`  
**Prova visual:** dividir o círculo em setores e alterná-los até aproximar um retângulo de base `πr` e altura `r`.  
**Sequência:** setores → alternância → retângulo limite → `A=(πr)r`.

## 09 — Comprimento de arco
**Fórmula:** `L = (θ/360°)2πr` ou `L=rθ` em radianos  
**Prova visual:** o arco ocupa a mesma fração da circunferência que `θ` ocupa de uma volta completa.  
**Sequência:** destacar arco/ângulo → proporção → fórmula em graus → versão em radianos.

## 10 — Área do setor circular
**Fórmula:** `A_s = (θ/360°)πr²`  
**Prova visual:** setor como fração angular do círculo.  
**Sequência:** setor destacado → proporção de áreas → fórmula → forma `A_s=r²θ/2` em radianos.

## 11 — Área da coroa circular
**Fórmula:** `A = π(R²-r²)`  
**Prova visual:** retirar o disco interno do disco externo.  
**Sequência:** dois raios → diferença `πR²-πr²` → fatorar `π`.

## 12 — Teorema de Pitágoras
**Fórmula:** `a²+b²=c²`  
**Prova visual:** quatro triângulos retângulos idênticos dentro de um quadrado de lado `a+b`; a região central tem área `c²`.  
**Sequência:** quadrado externo → quatro triângulos → área central → expansão/cancelamento.

## 13 — Relações métricas no triângulo retângulo
**Fórmulas:** `h²=mn`, `a²=cn`, `b²=cm`  
**Prova visual:** altura à hipotenusa cria três triângulos semelhantes.  
**Sequência:** altura → dois subtriângulos → proporção `h/m=n/h` → demais relações.

## 14 — Razões trigonométricas por semelhança
**Fórmulas:** `senθ=op/hip`, `cosθ=adj/hip`, `tgθ=op/adj`  
**Prova visual:** dois triângulos retângulos semelhantes com mesmo `θ`; lados escalam pelo mesmo fator e as razões permanecem invariantes.  
**Sequência:** triângulo pequeno → ampliar → comparar razões → definir seno/cosseno/tangente.

## 15 — Lei dos senos
**Fórmula:** `a/senA = b/senB = c/senC`  
**Prova visual:** uma mesma altura escrita como `b senA` e `a senB`.  
**Sequência:** triângulo geral → altura → duas expressões de `h` → igualdade → repetir ciclicamente.

## 16 — Lei dos cossenos
**Fórmula:** `a²=b²+c²−2bc cosA`  
**Prova visual:** projetar `b` sobre `c` e aplicar Pitágoras ao triângulo retângulo resultante.  
**Sequência:** altura/projeção → `b cosA` → Pitágoras → expandir → identidade trigonométrica.

## 17 — Área do triângulo usando seno
**Fórmula:** `A = bc senA / 2`  
**Prova visual:** a altura é `h=b senA`.  
**Sequência:** área comum `ch/2` → seno no triângulo retângulo → substituir `h`.

## 18 — Escalas: comprimentos, áreas e volumes
**Relações:** `L→kL`, `A→k²A`, `V→k³V`  
**Prova visual:** ampliar quadrado e cubo; cada dimensão recebe o fator `k`.  
**Sequência:** lado ×2 → área ×4 → extensão ao cubo → regra por dimensão.

## 19 — Relação de Euler em poliedros convexos
**Fórmula:** `V−E+F=2`  
**Prova visual:** contar vértices, arestas e faces de um cubo como exemplo estável.  
**Sequência:** desenhar cubo → marcar 8 vértices → `E=12`, `F=6` → `8−12+6=2` → enunciar generalidade convexa.

## 20 — Diagonal do paralelepípedo
**Fórmula:** `D = √(a²+b²+c²)`  
**Prova visual:** Pitágoras em duas etapas: diagonal da base e depois diagonal espacial.  
**Sequência:** caixa → diagonal da base → `d_b²=a²+b²` → triângulo espacial → substituir.

## 21 — Área de prismas retos por planificação
**Fórmula:** `A_T=2A_b+P_bh`  
**Prova visual:** faces laterais abertas formam retângulo de base `P_b` e altura `h`; acrescentar duas bases.  
**Sequência:** prisma → abrir lateral → `A_L=P_bh` → somar bases.

## 22 — Volume de prismas
**Fórmula:** `V=A_bh`  
**Prova visual:** empilhar seções congruentes de área constante `A_b`.  
**Sequência:** base → camadas → `ΔV≈A_bΔh` → soma ao longo de `h`.

## 23 — Área do cilindro
**Fórmula:** `A_T=2πr²+2πrh`  
**Prova visual:** abrir a lateral em um retângulo `2πr × h`; somar dois círculos.  
**Sequência:** cilindro → planificação lateral → `A_L=2πrh` → duas bases.

## 24 — Volume do cilindro
**Fórmula:** `V=πr²h`  
**Prova visual:** cilindro como prisma de base circular/empilhamento de discos iguais.  
**Sequência:** disco → pilha → `A_b=πr²` → `V=A_bh`.

## 25 — Área de pirâmides regulares
**Fórmula:** `A_T=A_b+P_bg/2`  
**Prova visual:** planificar as faces laterais triangulares; soma das bases dos triângulos é o perímetro da base.  
**Sequência:** pirâmide → faces abertas → `n(ℓg/2)` → `P_b=nℓ` → somar base.

## 26 — Volume da pirâmide
**Fórmula:** `V=A_bh/3`  
**Prova visual:** um cubo pode ser particionado em três pirâmides congruentes; Cavalieri estende o fator `1/3` a bases gerais.  
**Sequência:** cubo → três regiões → `V_cubo=3V_pir` → fórmula quadrada → generalização.

## 27 — Área do cone
**Fórmula:** `A_T=πrg+πr²`  
**Prova visual:** superfície lateral aberta é setor de raio `g`; seu arco mede `2πr`.  
**Sequência:** cone → setor → área do setor como `arco×raio/2` → lateral `πrg` → somar base.

## 28 — Volume do cone
**Fórmula:** `V=πr²h/3`  
**Prova visual:** cone como limite de pirâmides regulares de número crescente de lados.  
**Sequência:** pirâmide quadrangular → hexagonal → muitos lados → `A_b→πr²` mantendo fator `1/3`.

## 29 — Volume da esfera
**Fórmula:** `V=4πR³/3`  
**Prova visual:** princípio de Cavalieri entre uma semiesfera e `cilindro − cone`. Na altura `y`, ambas as seções valem `π(R²−y²)`.  
**Sequência:** comparação → seções horizontais → Cavalieri → volume da semiesfera → duplicar.

## 30 — Área da esfera
**Fórmula:** `A=4πR²`  
**Prova visual:** teorema de Arquimedes das zonas: cada faixa da esfera tem a mesma área da faixa correspondente do cilindro circunscrito.  
**Sequência:** esfera/cilindro → destacar faixas → `ΔA=2πRΔh` → integrar/somar sobre altura `2R` → `4πR²`.

---

## Observações de produção

1. Os roteiros foram feitos **sem narração e sem trilha**, para você poder adicionar voz depois.
2. Os tempos podem ser ajustados diretamente em `run_time=` e `wait()`.
3. Para mudar a identidade visual de toda a série, edite `common.py`.
4. Para vídeos mais longos, aumente apenas as pausas; evite desacelerar demais as transformações principais.
5. Para Instagram/Reels, preserve a região inferior livre de elementos críticos porque a interface da plataforma cobre parte da tela.
6. Nos vídeos 26, 28, 29 e 30, a prova é conceitualmente mais avançada; vale narrar explicitamente o papel do **Princípio de Cavalieri**, do **limite de polígonos/pirâmides** e do **teorema das zonas de Arquimedes**.
