# Auditoria e limpeza do legado

## Contexto

Após a validação visual e estrutural dos 60 conteúdos, o engine unificado passou a ser a implementação de produção.

O sistema anterior está preservado integralmente na branch `backup` no commit `4dfd345e2a12a29d3970f0ce97d4bb7b6edde22e`.

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
- `enem/audio/`;
- logs e backup local de código.

### Camada transitória v2

- comando `parity`;
- comando `migrate legacy-*`;
- renderer `compatibility`;
- metadados `render.compatibility` nos 60 manifests;
- módulos `src/mathinmovement/migrations/`;
- testes dedicados à migração/compatibilidade.

## Migração dos assets de áudio

Os 422 MP3s de narração foram movidos, sem regravação ou recompressão, de:

```text
enem/audio/<id>/<segmento>.mp3
```

para:

```text
content/enem/<id>/assets/audio/<segmento>.mp3
```

Os manifests foram atualizados para os novos caminhos. Dois arquivos auxiliares antigos de `enem/audio/` foram removidos.

## Estado final

A linha principal não possui mais o diretório `enem/` na raiz.

Tudo que é necessário para reconstruir, validar, empacotar e renderizar os conteúdos atuais está em:

- `content/`;
- `src/mathinmovement/`;
- `schemas/`;
- `tests/`;
- configuração de projeto.

O histórico anterior permanece acessível na branch `backup`.
