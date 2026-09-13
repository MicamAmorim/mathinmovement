# Math in Movement Studio — MVP

O Studio é a interface web local do Math in Movement. Ele usa a mesma API e a mesma fila de jobs do CLI; não duplica regras de renderização.

## Instalação

A interface é servida pela camada opcional de API:

```powershell
python -m pip install -e ".[api]"
```

## Executar

Terminal 1 — API + Studio:

```powershell
python -m mathinmovement serve
```

Terminal 2 — worker:

```powershell
python -m mathinmovement worker
```

Abra:

```text
http://127.0.0.1:8000/studio
```

A raiz `http://127.0.0.1:8000/` redireciona para o Studio.

## O que o MVP já faz

### Catálogo

- lista demos e qENEM;
- busca por título, ID, tag e ano;
- filtros por tipo, status, ano, tag, formato e disponibilidade de narração;
- mostra tags, status e metadados básicos;
- atualiza o catálogo sem recarregar a página.

### Configuração de render

Ao selecionar um conteúdo, o painel lateral permite definir:

- vertical 9:16 ou horizontal 16:9, respeitando os formatos declarados no manifest;
- qualidade draft/final;
- voz TTS ou voz padrão do manifest;
- pular TTS;
- forçar regeneração de TTS;
- dry-run;
- preview rápido;
- caminho opcional de trilha sonora;
- volume da música;
- fade in/out;
- ducking;
- normalização de loudness.

O Studio apenas cria um job. O worker executa `produce()`.

### Fila

A tabela de jobs:

- atualiza automaticamente;
- mostra queued/running/succeeded/failed/canceled;
- exibe conteúdo, configuração, horário e resultado;
- permite cancelar jobs ainda em fila.

## Arquitetura

```text
browser
  ↓
/studio
  ↓
FastAPI
  ├── GET /contents
  ├── POST /jobs
  └── GET /jobs
        ↓
cache/jobs.sqlite
        ↓
worker
        ↓
produce()
  ├── TTS
  ├── Manim
  └── FFmpeg
```

A interface não executa Manim nem FFmpeg dentro da requisição HTTP.

## Teste seguro

Com o worker rodando, selecione um conteúdo e marque **Dry run** antes de enfileirar. O job deve passar por:

```text
queued → running → succeeded
```

sem render real.

## Limites do MVP

Ainda não fazem parte desta primeira versão:

- upload de `.demo`/`.qenem` pela interface;
- thumbnails reais;
- preview do MP4 no navegador;
- download do vídeo;
- upload de música pelo navegador;
- progresso percentual;
- streaming de logs;
- retry por botão;
- histórico detalhado de renders;
- autenticação/multiusuário.

Esses recursos serão adicionados sobre a mesma API/job queue, sem trocar o core.
