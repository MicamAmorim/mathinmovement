# Roadmap — Math in Movement

Atualizado em: 2026-09-12

Este roadmap acompanha a evolução do Math in Movement de engine declarativo em Python/Manim para uma plataforma completa de autoria, validação, renderização e distribuição de conteúdos matemáticos.

## Estado atual

- [x] Engine nativo unificado para `demo` e `qenem`.
- [x] 60 conteúdos de produção registrados: 30 demos + 30 qENEM.
- [x] Pacotes portáveis `.demo` e `.qenem` com `manifest.yaml` e assets.
- [x] Importação, exportação, validação e registry SQLite reconstruível.
- [x] Pipeline `produce`: import → TTS/cache → render.
- [x] TTS segmentado e cacheado por fingerprint.
- [x] Renderização vertical e horizontal.
- [x] DSL visual v1 e runtime extensível.
- [x] Testes automatizados e regressão DSL.
- [x] Validação local como quality gate canônico enquanto CI remota estiver indisponível (`mim verify`).
- [x] Concluir migração do catálogo para programas DSL declarativos.
  - Estado em 2026-09-12 na branch `feature-dsl-catalog-migration`: 30/30 demos e 30/30 qENEM possuem shadow ports DSL.
  - Regressão renderizada vertical dos 60 conteúdos aprovada visualmente.
  - Os 60 manifests agora usam `production_engine: dsl`; a produção usa apenas formatos listados em `dsl_shadow.approved_formats` e aplica fallback nativo nos demais.
  - Demos: DSL suportada e aprovada em vertical; horizontal permanece protegido pelo renderer nativo.
  - qENEM: DSL suportada em vertical e horizontal; apenas vertical está promovida até a regressão visual 16:9.

## M1 — Fechar a migração DSL

Prioridade imediata.

- [x] Migrar os 9 demos restantes para DSL.
- [x] Migrar os qENEM restantes para DSL quando aplicável. Estado atual: 30/30.
- [x] Executar regressão visual dos shadow ports em vertical.
- [x] Validar layout, TeX, timing e composição da regressão vertical.
- [x] Promover os programas validados e reduzir dependência de renderers específicos.
- [x] Consolidar a branch de migração na `main`.

Critério de saída: catálogo completo reproduzível pelo contrato declarativo aprovado, com testes de regressão e sem perda visual relevante. **Concluído em 2026-09-12.** A validação não depende de GitHub Actions: `mim verify` é o quality gate canônico local, e `mim verify --render-dsl --keep-going` executa a regressão renderizada.

## M2 — Kit de autoria para LLMs e usuários

Objetivo: permitir que um usuário entregue uma questão do ENEM ou uma fórmula/teorema a uma LLM e receba um pacote válido do Math in Movement. A autoria nova usa DSL canônica (`visual_program` / `visuals.*.program`); `dsl_shadow` fica apenas como compatibilidade de migração.

- [x] Criar `docs/AUTHORING_WITH_LLM.md`.
- [x] Documentar claramente que `.demo` e `.qenem` são containers ZIP autocontidos.
- [x] Fornecer template mínimo e template completo de `manifest.yaml` para cada tipo.
- [x] Fornecer um prompt oficial para geração de `.demo`.
- [x] Fornecer um prompt oficial para geração de `.qenem`.
- [x] Incluir regras de narrativa, sincronização visual, TeX, assets, formatos e DSL.
- [x] Exigir no prompt que a LLM produza conteúdo compatível com a versão da DSL declarada.
- [x] Incluir checklist de validação e comandos:
  - `mim import`
  - `mim validate`
  - `mim dsl validate`
  - `mim produce --dry-run`
- [x] Adicionar exemplos prontos em `examples/templates/`.
- [x] Adicionar `mim scaffold demo|qenem` para gerar a estrutura-base localmente, com opção `--package`.

Critério de saída: um usuário sem conhecer Python consegue pedir a uma LLM um conteúdo novo, importar o pacote e validá-lo. **Concluído e validado localmente em 2026-09-12.**

## M3 — Math in Movement Studio (Web App)

Objetivo: transformar o engine em uma aplicação visual de gerenciamento e renderização.

### Catálogo

- [ ] Listar todos os `.demo` e `.qenem` cadastrados.
- [ ] Busca por texto.
- [ ] Filtros por tipo, ano, tags, status, formato e disponibilidade de narração.
- [ ] Ordenação por nome, data, tipo e última renderização.
- [ ] Cards com título, tipo, tags, thumbnail e status de validação.

### Upload e importação

- [ ] Upload individual de `.demo` ou `.qenem`.
- [ ] Upload múltiplo.
- [ ] Upload de `.zip` contendo vários pacotes.
- [ ] Validação antes da importação definitiva.
- [ ] Relatório amigável de erros de schema/DSL/assets.
- [ ] Proteções contra ZIP malformado, zip-slip, arquivos excessivamente grandes e extensões não permitidas.
- [ ] Opção de substituir conteúdo existente mediante confirmação.

### Renderização

- [ ] Renderizar um item.
- [ ] Selecionar vários itens e renderizar em lote.
- [ ] Presets: vertical 9:16 e horizontal 16:9.
- [ ] Qualidade draft/final.
- [ ] Gerar/ignorar/forçar narração.
- [ ] Selecionar voz TTS quando aplicável.
- [ ] Fila de jobs com progresso, logs, cancelar, repetir e retry.
- [ ] Preview do vídeo pronto no próprio navegador.
- [ ] Download do MP4.
- [ ] Download em ZIP quando houver renderização em lote.
- [ ] Histórico de renders por conteúdo.

### Trilha sonora

- [ ] Campo para upload de trilha sonora de fundo por job.
- [ ] Biblioteca opcional de trilhas reutilizáveis.
- [ ] Controle de volume.
- [ ] Fade in/fade out.
- [ ] Loop ou corte automático para a duração do vídeo.
- [ ] Ducking automático durante a narração.
- [ ] Normalização de loudness.
- [ ] Preview da mistura antes do render final, quando viável.

### Exportação

- [ ] Exportar novamente o conteúdo como `.demo` ou `.qenem`.
- [ ] Exportar vídeo + pacote-fonte + metadados em um bundle ZIP.

Critério de saída: todo o fluxo cotidiano pode ser feito pela interface sem usar terminal.

## M4 — Pipeline de pós-produção

Implementação concluída e validada localmente em 2026-09-12: módulo FFmpeg, `media_raw/`, fingerprint de raw, troca de trilha sem rerenderizar Manim, ducking, fades, volume e loudness.

Criar uma etapa explícita depois do Manim:

```text
package/content
    ↓
validate
    ↓
TTS/cache
    ↓
render Manim
    ↓
post-process
    ├── narration
    ├── background music
    ├── ducking
    ├── fades
    └── loudness normalization
    ↓
final MP4
```

- [x] Criar módulo de pós-processamento baseado em FFmpeg.
- [x] Separar vídeo renderizado de master final.
- [x] Cachear o render bruto por fingerprint de conteúdo + assets + parâmetros de render; parâmetros de música refazem apenas o master.
- [x] Preservar render bruto para não rerenderizar Manim quando apenas a trilha mudar.

## M5 — Editor e experiência de autoria

- [ ] Editor web de manifest/DSL com syntax highlighting.
- [ ] Validação em tempo real.
- [ ] Autocomplete baseado nos schemas e registry de capacidades DSL.
- [ ] Preview draft de baixa resolução.
- [ ] Storyboard/timeline visual dos segmentos.
- [ ] Preview de voz por segmento.
- [ ] Editor de texto da narração com regeneração apenas do trecho alterado.
- [ ] Thumbnail automática.
- [ ] Duplicar conteúdo como ponto de partida.
- [ ] Versionamento/revisões do manifest.
- [ ] Diff entre versões.
- [ ] Coleções/playlists de vídeos.
- [ ] Tags e favoritos.

## M6 — Escala e publicação

Primeira fundação do Studio em `feature-api-jobs`: API interna, JobStore SQLite e worker separado implementados; aguardam quality gate local antes da consolidação.

- [x] API HTTP interna inicial sobre o core Python, sem duplicar regras de negócio (`serve`, `/contents`, `/jobs`).
- [x] Worker de renderização separado da aplicação web (`worker` / `worker --once`).
- [x] Fila persistente local de jobs em SQLite com claim atômico e estados de lifecycle.
- [ ] Armazenamento externo para pacotes, assets e MP4s em instalações hospedadas.
- [ ] Banco persistente para usuários/jobs/histórico; manter o SQLite atual como índice local reconstruível.
- [ ] Autenticação e permissões se houver uso multiusuário.
- [ ] Links compartilháveis de preview/download.
- [ ] Presets de publicação para Instagram/Reels, TikTok/Shorts e YouTube.
- [ ] Integração futura com LLM dentro do próprio Studio: colar questão/fórmula → gerar rascunho `.qenem`/`.demo` → validar → editar → renderizar.

## Sugestões de alta prioridade

1. **Render cache por fingerprint** — evita rerenderizar Manim quando nada visual mudou.
2. **Fila de jobs** — indispensável para lote e para uma versão hospedada.
3. **Validação antes de importar** — impede que uploads ruins contaminem o catálogo.
4. **Preview draft rápido** — reduz muito o ciclo de edição.
5. **Pós-produção desacoplada** — permite trocar música/volume sem refazer a animação.
6. **Editor de narração por segmentos** — aproveita o cache TTS já existente.
7. **Presets de publicação** — transforma vertical/horizontal em perfis reutilizáveis.
8. **Histórico e versionamento** — importante quando o catálogo começar a crescer.
9. **Thumbnails automáticas** — melhora muito a navegação no catálogo web.
10. **LLM como autora de pacote, não de Python arbitrário** — mantém segurança e portabilidade usando a DSL como contrato.

## Ordem recomendada

1. Fechar a migração DSL.
2. Publicar o kit de autoria + prompts oficiais.
3. Criar a camada de pós-produção de áudio.
4. Expor o core por uma API interna.
5. Construir o Studio web com catálogo/upload/render.
6. Adicionar editor DSL, histórico e recursos avançados.
7. Só depois integrar geração por LLM diretamente no Studio.
