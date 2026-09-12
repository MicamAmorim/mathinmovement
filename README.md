# Math in Movement

Engine unificado em Python/Manim para demonstrações matemáticas e resoluções comentadas do ENEM.

O projeto possui hoje **60 conteúdos de produção**:

- 30 demonstrações matemáticas;
- 30 questões ENEM comentadas;
- todos renderizados pelo engine nativo unificado.

## Instalação

Python 3.11 ou 3.12:

```powershell
python -m pip install -e .
python -m pip install -e ".[render]"
```

Para renderização também são necessários os requisitos de sistema do Manim, incluindo FFmpeg e uma instalação LaTeX compatível.

## Validação

```powershell
python -m unittest discover -s tests -v
python -m mathinmovement validate
python -m mathinmovement db rebuild
python -m mathinmovement db status
```

## Listar conteúdo

```powershell
python -m mathinmovement list --type demo
python -m mathinmovement list --type qenem
```

## Renderização

Um conteúdo:

```powershell
python -m mathinmovement render area-triangulo
python -m mathinmovement render ENEM-2021-MT-11
```

Formato horizontal:

```powershell
python -m mathinmovement render ENEM-2021-MT-11 --format horizontal
```

Lotes:

```powershell
python -m mathinmovement render --all --type demo --status production --keep-going
python -m mathinmovement render --all --type qenem --status production --format vertical --keep-going
python -m mathinmovement render --all --type qenem --status production --format horizontal --keep-going
```

Simular sem executar o Manim:

```powershell
python -m mathinmovement render --all --type qenem --dry-run
```

## Conteúdo declarativo

A fonte canônica está em:

```text
content/
├── demos/
└── enem/
```

Cada item possui um `manifest.yaml`. Assets pertencentes ao conteúdo ficam dentro do próprio diretório, por exemplo:

```text
content/enem/ENEM-2021-MT-11/
├── manifest.yaml
└── assets/
    └── audio/
        ├── source.mp3
        ├── statement_01.mp3
        └── ...
```

O SQLite em `cache/registry.sqlite` é apenas um índice reconstruível.

Pacotes podem ser importados e exportados:

```powershell
python -m mathinmovement import arquivo.demo
python -m mathinmovement import arquivo.qenem
python -m mathinmovement export area-triangulo
python -m mathinmovement export ENEM-2021-MT-11
```

Como os assets ficam junto do conteúdo, um pacote `.qenem` exportado leva consigo também sua narração disponível.

## Produção em uma etapa

Para um conteúdo já cadastrado:

```powershell
python -m mathinmovement produce ENEM-2021-MT-11
```

Para importar um pacote e produzir o vídeo:

```powershell
python -m mathinmovement produce minha-questao.qenem
python -m mathinmovement produce minha-demo.demo
```

O comando `produce` executa o fluxo `import → TTS/cache → render`. Para qENEM com `narration.segments`, os MP3s ausentes são gerados com Edge TTS e a duração real é registrada no manifest.

Comandos úteis:

```powershell
python -m mathinmovement voice ENEM-2021-MT-11
python -m mathinmovement produce ENEM-2021-MT-11 --format horizontal
python -m mathinmovement produce nova.qenem --voice pt-BR-AntonioNeural
python -m mathinmovement produce nova.qenem --skip-voice
python -m mathinmovement produce nova.qenem --dry-run
```

Dentro de um pacote novo, assets podem ser referenciados de forma portátil, por exemplo `assets/audio/source.mp3`.

## DSL visual v1

A DSL visual é versionada e usa um registry extensível de capacidades.

```powershell
python -m mathinmovement dsl ops
python -m mathinmovement dsl audit
python -m mathinmovement dsl validate <id>
python -m mathinmovement dsl regress --dry-run
python -m mathinmovement dsl regress --quality draft
```

Um demo novo pode declarar `visual_program` com `dsl_version`, `objects` e `timeline`.
qENEM podem declarar programas DSL estáticos em `visuals.statement.program` e `visuals.concept.program`.

A v1 cobre o vocabulário gráfico já usado nos 60 vídeos aprovados. O conjunto mínimo de regressão possui 8 demos e 6 qENEM. Veja `docs/DSL_COVERAGE.md` e `docs/DSL_SPEC.md`.

## Roadmap

O planejamento de evolução do projeto está em [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Estrutura principal

```text
content/                 conteúdo canônico + assets
src/mathinmovement/      engine, CLI, registry e renderers
schemas/                 contratos dos manifests
tests/                   testes automatizados
cache/                   SQLite reconstruível
media/                   saída de produção
media_native/            saída isolada para inspeção do engine
```

O código legado foi removido da linha principal após a migração para o engine unificado. O snapshot histórico completo permanece preservado na branch `backup`.
