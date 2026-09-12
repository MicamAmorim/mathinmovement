# Auditoria e limpeza do legado

## Contexto

Após a validação visual e estrutural dos 60 conteúdos, o engine unificado passou a ser a implementação de produção.

O sistema anterior já está preservado integralmente na branch `backup` no commit `4dfd345e2a12a29d3970f0ce97d4bb7b6edde22e`.

## Removido da linha principal

### Pipeline antigo de demos

- `videos/`;
- `common.py`;
- `render_all.py/.bat/.sh`;
- `validate.py`;
- logs de render;
- requirements e documentos de planejamento históricos da raiz.

### Pipeline antigo ENEM

- `enem/videos/`;
- `enem/common.py`;
- `enem/specs.py`;
- `enem/visuals.py`;
- `enem/pipeline.py`;
- runners e validadores antigos;
- `enem/data/`;
- `enem/narrations/`;
- logs e backup local de código.

### Camada transitória v2

- comando `parity`;
- comando `migrate legacy-*`;
- renderer `compatibility`;
- metadados `render.compatibility` nos 60 manifests;
- módulos `src/mathinmovement/migrations/`;
- testes dedicados à migração/compatibilidade.

## Mantido

- `content/`: fonte canônica;
- `src/mathinmovement/`: engine;
- `schemas/`;
- `tests/`;
- `manim.cfg`;
- `enem/audio/`: temporariamente, porque é referenciado pelos manifests.

## Próxima dívida técnica

Migrar `enem/audio/<id>/...` para assets pertencentes a cada item em `content/enem/<id>/assets/audio/`.

Depois disso, o diretório `enem/` poderá desaparecer por completo.
