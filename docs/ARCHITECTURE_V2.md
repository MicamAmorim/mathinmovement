# Arquitetura v2 — Math in Movement

> Branch de evolução: `engine-v2`  
> A branch `main` permanece como referência histórica/estável e não será reescrita.

## 1. Problema atual

O repositório possui hoje dois pipelines paralelos:

- **demonstrações matemáticas** na raiz (`videos/`, `common.py`, `render_all.py`);
- **resoluções ENEM** em `enem/`, com outro `common.py`, outro runner, banco em `questions.json` + `specs.py`, `visuals.py`, narração, TTS e áudio.

Isso gera duplicação de responsabilidades e faz com que adicionar um conteúdo novo exija alterar vários arquivos Python, listas hardcoded e estruturas diferentes.

## 2. Objetivo

Transformar o projeto em:

1. **um único engine** de renderização, narração, layout e áudio;
2. **um registry dinâmico** de conteúdos;
3. **conteúdo declarativo** separado do código do engine;
4. formatos de intercâmbio `.qenem` e `.demo`;
5. CLI única para validar, listar, importar e renderizar;
6. compatibilidade com os conteúdos atuais durante a migração.

## 3. Princípio central

> Python é o motor. Conteúdo não deve ser cadastrado editando Python.

Questões, demonstrações, roteiros, respostas, metadados e instruções visuais ficam em documentos de conteúdo. O engine lê esses documentos e escolhe os renderers adequados.

## 4. Estrutura alvo

```text
mathinmovement/
├── pyproject.toml
├── README.md
├── src/
│   └── mathinmovement/
│       ├── cli.py
│       ├── config.py
│       ├── registry.py
│       ├── models/
│       │   ├── base.py
│       │   ├── qenem.py
│       │   └── demo.py
│       ├── engine/
│       │   ├── renderer.py
│       │   ├── scene.py
│       │   ├── layout.py
│       │   ├── timing.py
│       │   ├── narration.py
│       │   ├── tts.py
│       │   └── audio.py
│       ├── visuals/
│       │   ├── registry.py
│       │   ├── primitives.py
│       │   ├── geometry.py
│       │   ├── graphs.py
│       │   └── custom/
│       └── validators/
│           ├── qenem.py
│           └── demo.py
├── content/
│   ├── enem/
│   │   └── ENEM-2021-MT-11/
│   │       ├── manifest.yaml
│   │       └── assets/
│   └── demos/
│       └── area-triangulo/
│           ├── manifest.yaml
│           └── assets/
├── schemas/
│   ├── qenem.schema.json
│   └── demo.schema.json
├── cache/
│   ├── registry.sqlite
│   └── audio/
└── media/
    ├── vertical/
    └── horizontal/
```

## 5. Source of truth

O conteúdo em `content/` será o **source of truth versionável no Git**.

Um SQLite gerado em `cache/registry.sqlite` pode ser usado para busca, filtros e performance, mas será reconstruível a qualquer momento e não será a fonte autoritativa.

Isso evita transformar o Git em um dump de banco binário e permite revisar alterações de conteúdo por diff.

## 6. Formatos .qenem e .demo

Os formatos serão pacotes de intercâmbio, pensados para que uma única entrega possa conter tudo de que o conteúdo precisa.

### 6.1 Formato físico

`.qenem` e `.demo` serão containers ZIP com extensão própria.

Exemplo:

```text
ENEM-2026-MT-17.qenem
├── manifest.yaml
├── assets/
│   ├── figure.svg
│   └── source.png
└── README.md              # opcional
```

```text
area-triangulo.demo
├── manifest.yaml
├── assets/
└── README.md              # opcional
```

O comando `import` valida e expande o pacote para `content/`.

### 6.2 Por que container e não um único JSON

- suporta figuras e assets sem caminhos externos;
- continua sendo um único arquivo para compartilhar;
- pode ser gerado/validado automaticamente;
- permite evolução do schema;
- mantém o manifesto legível em YAML;
- não exige colocar código Python dentro do pacote para os casos comuns.

## 7. Manifesto comum

Todo conteúdo terá campos básicos:

```yaml
schema_version: 1
id: enem-2021-mt-11
type: qenem
title: "ENEM 2021 — Q146"
tags:
  - geometria
  - triangulo-equilatero

render:
  formats: [vertical, horizontal]
  default_format: vertical

narration:
  enabled: true
  language: pt-BR
  voice: pt-BR-AntonioNeural
```

## 8. Manifesto .qenem

Além dos campos comuns:

```yaml
exam:
  name: ENEM
  year: 2021
  canonical_id: ENEM-2021-MT-11
  question_number: 146
  booklet: "Caderno 5 Amarelo"

question:
  stem: |
    ...
  options:
    A: ...
    B: ...
    C: ...
    D: ...
    E: ...
  answer: D

solution:
  data:
    - ...
  goal: ...
  hook: ...
  strategy:
    - ...
  steps:
    - label: ...
      math: ...
  final_answer: D

visuals:
  statement:
    renderer: triangle_instrument
  concept:
    renderer: equilateral
    note: ...
```

## 9. Manifesto .demo

```yaml
schema_version: 1
id: area-triangulo
type: demo
title: "Área do triângulo"

lesson:
  objective: "Demonstrar visualmente A = bh/2."
  hook: "Por que aparece o 1/2?"
  steps:
    - narration: ...
      visual:
        action: create
        target: triangle
    - narration: ...
      visual:
        action: duplicate
        target: triangle
    - narration: ...
      visual:
        action: transform
        target: parallelogram

result:
  math: "A=\\frac{bh}{2}"
```

## 10. Visuais

Há dois níveis:

### 10.1 DSL declarativa

A maior parte das cenas deve usar primitives reutilizáveis:

- ponto, linha, seta;
- polígono, círculo, arco;
- eixos e gráficos;
- texto e MathTex;
- grupos;
- transformações;
- destaque, corte, translação, rotação;
- disposição em grid/colunas.

Isso permite que uma nova questão ou demo seja adicionada apenas pelo manifesto.

### 10.2 Renderer customizado

Quando a cena realmente exigir lógica especial, o manifesto referencia um renderer registrado no engine:

```yaml
visual:
  renderer: ferris_wheel_choices
```

Os renderers customizados pertencem ao engine, são reutilizáveis e testáveis. O conteúdo não deve carregar Python arbitrário.

## 11. Registry

O registry:

1. percorre `content/enem` e `content/demos`;
2. valida cada manifesto;
3. indexa por `id`, tipo, ano e tags;
4. detecta IDs duplicados;
5. expõe consultas para CLI e engine.

Nenhum número total de conteúdos fica hardcoded.

## 12. CLI alvo

```powershell
# diagnóstico
python -m mathinmovement doctor

# validar tudo
python -m mathinmovement validate

# listar
python -m mathinmovement list
python -m mathinmovement list --type qenem
python -m mathinmovement list --type demo

# importar pacote
python -m mathinmovement import arquivo.qenem
python -m mathinmovement import arquivo.demo

# renderizar um item
python -m mathinmovement render ENEM-2021-MT-11
python -m mathinmovement render area-triangulo

# formato
python -m mathinmovement render ENEM-2021-MT-11 --format horizontal

# voz
python -m mathinmovement render ENEM-2021-MT-11 --voice pt-BR-AntonioNeural

# sem refazer voz já cacheada
python -m mathinmovement render ENEM-2021-MT-11 --skip-voice

# lote
python -m mathinmovement render --all --type qenem
python -m mathinmovement render --all --type demo
```

## 13. Áudio e narração

A camada atual de segmentos e duração real dos MP3 será preservada conceitualmente:

- narração segmentada;
- cache por fingerprint de texto + voz + prosódia;
- duração real do MP3 controla a animação;
- áudio reutilizado entre vertical e horizontal;
- TTS desacoplado do renderer.

## 14. Layout

O layout será uma responsabilidade compartilhada do engine, não de cada conteúdo.

Perfis iniciais:

- `vertical`: 9:16;
- `horizontal`: 16:9.

O conteúdo pode fornecer preferências, mas não deve codificar posições absolutas específicas de um único formato sempre que puder usar anchors e regiões.

## 15. Estratégia de migração

A migração será incremental.

### Fase A — infraestrutura

- criar package `mathinmovement`;
- models;
- registry;
- schemas;
- CLI;
- layout compartilhado;
- testes.

### Fase B — migrar demos

Converter as 30 demonstrações atuais para `.demo`/manifestos sem apagar os arquivos antigos ainda.

Critério: o novo engine deve reproduzir os conteúdos existentes.

### Fase C — migrar ENEM

Converter `questions.json` + `specs.py` + referências de `visuals.py` para conteúdos declarativos.

Critérios de regressão:

- mesmos IDs;
- mesmos gabaritos;
- mesmos passos;
- mesmas correções já auditadas;
- mesmos 18 casos de figura relevantes;
- narração preservada.

### Fase D — unificação dos runners

Substituir gradualmente:

- `render_all.py` da raiz;
- `enem/render_all.py`;
- `enem/pipeline.py`;
- listas hardcoded de cenas.

### Fase E — compatibilidade

Enquanto a migração não estiver completa, comandos antigos continuam disponíveis ou apontam para wrappers compatíveis.

Somente depois da equivalência validada o código legado pode ser marcado como deprecated.

## 16. Política de branch

- `main`: snapshot original preservado;
- `engine-v2`: nova linha principal de desenvolvimento;
- mudanças grandes em `engine-v2` devem ser feitas em commits pequenos e semanticamente separados;
- não reescrever o histórico da `main`.

## 17. Critério de sucesso

Adicionar uma nova questão comum deve se resumir a:

```powershell
python -m mathinmovement import nova_questao.qenem
python -m mathinmovement validate
python -m mathinmovement render <id>
```

Adicionar uma nova demonstração comum:

```powershell
python -m mathinmovement import nova_demo.demo
python -m mathinmovement validate
python -m mathinmovement render <id>
```

Sem editar listas de cenas, limites numéricos, `specs.py`, `questions.json` ou runners.
