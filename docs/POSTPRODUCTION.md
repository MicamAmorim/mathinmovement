# Pós-produção com FFmpeg

O Math in Movement separa o render Manim do master final quando uma trilha sonora é usada.

## Fluxo

```text
conteúdo + TTS
    ↓
Manim
    ↓
media_raw/<tipo>/<formato>/<id>-<fingerprint>.mp4
    ↓
FFmpeg
    ├── trilha em loop
    ├── volume
    ├── fade in/out
    ├── ducking pela narração já presente no render
    └── loudness normalization
    ↓
media/<tipo>/<formato>/<id>.mp4
```

O fingerprint do vídeo bruto inclui o conteúdo, seus assets, formato e qualidade. Trocar somente a música, volume, fades ou ducking reutiliza o raw existente.

## Produção com trilha

```powershell
python -m mathinmovement produce ENEM-2021-MT-11 `
    --music "music/bach.mp3" `
    --music-volume 0.12 `
    --fade-in 1.5 `
    --fade-out 2.5
```

Por padrão:

- a trilha é repetida até cobrir o vídeo;
- o volume musical é `0.12`;
- ducking é ativado;
- loudness normalization é ativada;
- o raw compatível é reutilizado.

Controles:

```text
--no-ducking
--no-normalize
--no-reuse-raw
```

Use `--no-reuse-raw` para forçar um novo render Manim.

## Trocar música sem Manim

Depois de um raw existir, a trilha pode ser trocada diretamente:

```powershell
python -m mathinmovement postprocess `
    "media_raw/qenem/vertical/ENEM-2021-MT-11-<fingerprint>.mp4" `
    --music "music/chopin.mp3" `
    -o "media/qenem/vertical/ENEM-2021-MT-11.mp4"
```

Esse comando não executa Manim.

## Ducking

Quando o vídeo bruto possui áudio, o FFmpeg usa esse áudio como sidechain para reduzir a música automaticamente durante a narração. Se o raw não possui áudio, a trilha é usada sem sidechain.

## Loudness

Quando habilitada, a mistura final usa `loudnorm` com alvo aproximado de:

- integrated loudness: -16 LUFS;
- true peak: -1.5 dBTP;
- LRA: 11.

## Observação arquitetural

Nesta primeira versão, a narração continua sincronizada dentro do render Manim. A pós-produção trata esse áudio como a faixa principal e adiciona a música por cima. Uma evolução futura poderá exportar a timeline de narração e mixá-la integralmente no estágio FFmpeg sem mudar o formato dos pacotes.
