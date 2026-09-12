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
