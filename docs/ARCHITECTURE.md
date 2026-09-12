# Arquitetura atual — Math in Movement

## Estado

O Math in Movement usa um único engine nativo para demonstrações e questões ENEM.

Não há runtime de compatibilidade na linha principal. O sistema legado completo permanece disponível apenas na branch `backup`.

## Fonte de verdade

```text
content/
├── demos/<id>/
│   ├── manifest.yaml
│   └── assets/
└── enem/<id>/
    ├── manifest.yaml
    └── assets/
        └── audio/
```

Os manifests e seus assets são versionáveis e autoritativos. `cache/registry.sqlite` é um índice derivado e pode ser reconstruído a qualquer momento.

## Engine

```text
src/mathinmovement/
├── cli.py
├── registry.py
├── database.py
├── package_io.py
├── engine/
│   ├── renderer.py
│   └── scene.py
├── visuals/
└── models/
```

`UnifiedContentScene` interpreta os manifests e seleciona o perfil apropriado para `demo` ou `qenem`.

## Renderização

`production` e `native` usam o mesmo engine aprovado. A diferença é apenas o destino:

- `production` → `media/`;
- `native` → `media_native/`, útil para inspeção isolada.

Não existe renderer `compatibility`.

## Formatos de conteúdo

`.demo` e `.qenem` são containers ZIP com `manifest.yaml` e assets opcionais.

Como os assets ficam dentro do diretório do conteúdo, exportar um qENEM inclui também seus arquivos de narração.

O fluxo esperado para conteúdo novo é:

```powershell
python -m mathinmovement import novo.demo
python -m mathinmovement validate
python -m mathinmovement render <id>
```

ou:

```powershell
python -m mathinmovement import nova.qenem
python -m mathinmovement validate
python -m mathinmovement render <id>
```

## Visuais

Há dois níveis:

1. renderers/primitivas reutilizáveis no engine;
2. conteúdo declarativo nos manifests.

O próximo marco arquitetural é ampliar uma DSL/timeline visual para reduzir ainda mais a necessidade de novos métodos Python específicos por vídeo.

## Áudio

A narração qENEM é segmentada no manifest.

Cada segmento referencia um MP3 pertencente ao próprio conteúdo:

```text
content/enem/<id>/assets/audio/<segmento>.mp3
```

Isso mantém manifesto e assets juntos e torna os pacotes `.qenem` autocontidos.

## Branches

- `main`: linha estável do engine unificado;
- `backup`: snapshot integral do sistema anterior.

Branches de migração/limpeza podem ser mantidas temporariamente para auditoria, mas não fazem parte do runtime.

## Critério atual de integridade

- 60 conteúdos registrados;
- 30 demos + 30 qENEM;
- todos `production`;
- todos com `production_engine: native`;
- áudio qENEM colocalizado com os próprios conteúdos;
- SQLite totalmente reconstruível a partir de `content/`.
