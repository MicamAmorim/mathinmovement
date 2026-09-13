# API interna e fila de jobs

Esta camada prepara o Math in Movement Studio sem acoplar Manim/FFmpeg ao servidor HTTP.

## Arquitetura

```text
Studio / cliente HTTP
        ↓
FastAPI
        ↓
cache/jobs.sqlite
        ↓
worker separado
        ↓
produce()
   ├── TTS
   ├── Manim
   └── FFmpeg
```

A API nunca chama Manim diretamente. `POST /jobs` apenas persiste um job com status `queued`. Um processo worker separado faz o claim atômico e executa `produce()`.

## Instalação

A API é opcional:

```powershell
python -m pip install -e ".[api]"
```

O engine local continua funcionando sem FastAPI/Uvicorn.

## Iniciar a API

Terminal 1:

```powershell
python -m mathinmovement serve
```

Padrão:

```text
http://127.0.0.1:8000
```

O Studio local fica em:

```text
http://127.0.0.1:8000/studio
```

O OpenAPI interativo do FastAPI fica em:

```text
http://127.0.0.1:8000/docs
```

## Iniciar o worker

Terminal 2:

```powershell
python -m mathinmovement worker
```

Para processar no máximo um job:

```powershell
python -m mathinmovement worker --once
```

## Enfileirar por PowerShell

Teste sem render real:

```powershell
$body = @{
    target = "ENEM-2021-MT-11"
    quality = "draft"
    dry_run = $true
} | ConvertTo-Json

$job = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/jobs" `
    -ContentType "application/json" `
    -Body $body

$job
```

Depois:

```powershell
python -m mathinmovement worker --once
```

E consulte:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/jobs/$($job.id)"
```

## Jobs com trilha

O payload aceita os mesmos parâmetros essenciais de `produce`:

```json
{
  "target": "ENEM-2021-MT-11",
  "format": "vertical",
  "quality": "draft",
  "music": "C:\\music\\bach.mp3",
  "music_volume": 0.1,
  "fade_in": 1.5,
  "fade_out": 2.5
}
```

## Estados

- `queued`: aguardando worker;
- `running`: claim realizado por um worker;
- `succeeded`: produção concluída;
- `failed`: produção terminou com erro;
- `canceled`: cancelado antes de iniciar.

Somente jobs `queued` podem ser cancelados nesta primeira versão.

## CLI da fila

```powershell
python -m mathinmovement jobs list
python -m mathinmovement jobs list --status queued
python -m mathinmovement jobs list --json
python -m mathinmovement jobs show <job-id>
python -m mathinmovement jobs cancel <job-id>
```

## Endpoints iniciais

```text
GET  /health
GET  /contents
POST /jobs
GET  /jobs
GET  /jobs/{job_id}
POST /jobs/{job_id}/cancel
```

## Limites atuais

Esta é a primeira camada interna para o Studio. Ainda não há autenticação, upload HTTP de pacotes/assets, streaming de logs, progresso percentual, heartbeat do worker ou recuperação automática de jobs que ficaram `running` após interrupção abrupta. Esses itens entram antes de uma implantação multiusuário.
