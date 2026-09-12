# ENEM em Movimento — 30 resoluções em Manim + narração neural

Pacote vertical (9:16) com 30 resoluções comentadas do ENEM Matemática 2021–2025.
A versão v2 separa **leitura do problema**, **figura original reconstruída**, **extração de dados**, **estratégia**, **modelo visual**, **resolução passo a passo** e **resposta**. A narração usa exatamente os mesmos segmentos das cenas, portanto áudio e animação permanecem sincronizados.

## O que mudou na v2

- roteiro de cada questão revisto para evitar saltos algébricos;
- correção matemática da Q146/2021: a altura indicada na figura é **8 cm**;
- correção da Q145/2022: **A=(20,40)**, **B=(50,20)** e o ponto ótimo é **IV, x=40**;
- auditoria de figuras: 18 das 30 questões têm figura/tabela/gráfico relevante no enunciado;
- a Q164/2023 mostra as **cinco alternativas gráficas**, em vez de convertê-las em texto;
- reconstruções vetoriais das figuras necessárias antes da solução;
- 30 roteiros de narração em Markdown e um `narrations.json` consumido pelo motor;
- suporte a TTS neural gratuito com `edge-tts`;
- duração de cada animação passa a usar a duração real do MP3 quando o áudio existe;
- modo de prévia rápida sem esperar a narração inteira.

## Estrutura

- `videos/`: 30 cenas independentes (`Resolucao01` ... `Resolucao30`);
- `common.py`: fluxo didático, sincronização e áudio;
- `visuals.py`: reconstruções das figuras e diagramas conceituais;
- `specs.py`: dados, estratégia e passos matemáticos;
- `data/questions.json`: as 30 questões e gabaritos;
- `narrations/`: um `.md` por questão, `NARRATION_ALL.md` e `narrations.json`;
- `narration_builder.py`: recompõe os textos de narração a partir do banco e dos roteiros;
- `generate_voice.py`: gera os MP3s neurais por segmento;
- `voice_preview.py`: gera uma amostra curta para escolher a voz;
- `audio/manifest.json`: criado automaticamente após a síntese, com duração real de cada segmento;
- `AUDITORIA_ROTEIROS.md`: relatório da revisão;
- `validate.py`: auditoria estrutural automatizada;
- `render_all.py`: renderização em lote.

## Instalação

Python 3.11 ou 3.12 recomendado.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Manim também precisa de FFmpeg, LaTeX e `dvisvgm`. No Windows, MiKTeX costuma resolver a parte LaTeX.

## Narração: voz neural gratuita

O caminho padrão é `edge-tts`, porque entrega vozes neurais pt-BR muito naturais, não exige chave de API e é simples de automatizar. O padrão do projeto é `pt-BR-AntonioNeural`. Como ele usa o serviço on-line do Microsoft Edge, é preciso internet e o endpoint pode mudar no futuro.

### 1. Listar as vozes pt-BR disponíveis

```powershell
python generate_voice.py --list-voices
```

### 2. Ouvir uma amostra

```powershell
python voice_preview.py --voice pt-BR-AntonioNeural --rate=+4%
```

Algumas alternativas pt-BR normalmente disponíveis são `pt-BR-FranciscaNeural`, `pt-BR-BrendaNeural` e `pt-BR-DonatoNeural`.

### 3. Gerar a voz apenas da primeira questão

```powershell
python generate_voice.py --from 1 --to 1 --voice pt-BR-AntonioNeural --rate=+4% --check-voice
```

### 4. Gerar as 30 questões

```powershell
python generate_voice.py --from 1 --to 30 --voice pt-BR-AntonioNeural --rate=+4% --check-voice
```

O gerador cria um MP3 para cada bloco (`statement_01`, `figure`, `step_03`, etc.) e grava a duração real em `audio/manifest.json`. Ele também mantém cache: se texto, voz e prosódia não mudarem, o áudio existente não é refeito.

> Alternativa realmente local/open source: o Kokoro-82M tem licença Apache-2.0 e vozes brasileiras (`pf_dora`, `pm_alex`, `pm_santa`). Ele é interessante para um pipeline 100% offline, mas o `edge-tts` ficou como padrão por ser mais simples para este repositório e por exigir menos dependências.

## Editar a narração

O texto completo está em:

```text
narrations/NARRATION_ALL.md
```

Há também um arquivo separado por questão. O arquivo efetivamente lido pelo renderizador e pelo TTS é:

```text
narrations/narrations.json
```

Se você alterar `specs.py` ou `data/questions.json`, rode:

```powershell
python narration_builder.py
```

Depois gere novamente apenas o intervalo afetado. O cache do TTS identifica os segmentos cujo texto mudou.

## Pipeline em um comando

Depois de instalar as dependências, você pode reconstruir as narrações, gerar a voz e renderizar um intervalo inteiro:

```powershell
python pipeline.py --from 1 --to 30 --voice pt-BR-AntonioNeural --rate=+4% --quality final --keep-going
```

Para reconstruir os textos e renderizar usando áudios já existentes, acrescente `--skip-voice`. Para gerar apenas os áudios, use `--skip-render`.

## Validar

```powershell
python validate.py
```

A validação confere 30 IDs, gabaritos, figuras, segmentos de narração e presença de todos os passos.

## Renderizar

Primeira questão, rascunho:

```powershell
python render_all.py --from 1 --to 1 --quality draft
```

Todas em 1080 × 1920 / 30 fps:

```powershell
python render_all.py --quality final --keep-going
```

Se a pasta `audio/` contiver os MP3s, eles entram **automaticamente** na cena. Se não houver MP3, o vídeo ainda renderiza usando o tempo estimado da narração.

### Prévia rápida durante desenvolvimento

PowerShell:

```powershell
$env:ENEM_FAST_PREVIEW="1"
python render_all.py --from 1 --to 1 --quality draft
Remove-Item Env:ENEM_FAST_PREVIEW
```

Nesse modo, a cena usa apenas cerca de 16% dos tempos de narração e não adiciona os MP3s.

## Uma cena isolada

```powershell
python -m manim --format mp4 --disable_caching -r 1080,1920 --fps 30 videos/01_2021_q146_triangulo_equilatero.py Resolucao01
```

## Filosofia visual

A figura que pertence à questão aparece **antes** das alternativas e é identificada como “reconstrução vetorial esquemática”. Depois vem um segundo visual, agora didático, que destaca a ideia matemática usada na solução. Isso evita misturar “o que o ENEM mostrou” com “o que estamos construindo para explicar”.

As reconstruções são vetoriais e não pretendem reproduzir pixel a pixel a diagramação do caderno; preservam os elementos geométricos e valores necessários à resolução.

## Diagnóstico antes de renderizar

Antes de tentar as 30 cenas, rode:

```powershell
python enem/doctor.py
```

O `render_all.py` também executa esse diagnóstico automaticamente. Ele verifica o mesmo Python/venv usado pelo runner, importação do Manim/PyAV, `latex`, `dvisvgm`, fonte DejaVu Sans e faz um smoke test real com `Text` + `MathTex`. Se algo falhar, a renderização é interrompida antes de repetir o mesmo erro nas 30 cenas.

Para testar apenas a primeira resolução:

```powershell
python enem/render_all.py --from 1 --to 1 --quality draft
```

Se uma cena falhar, as últimas linhas do log agora aparecem diretamente no terminal. O log completo continua em `enem/logs/NN.log`. Para pular o diagnóstico deliberadamente, use `--no-preflight`.


## Hotfix v2.2 — Manim 0.19 / `Scene.duration`

Se a cena falhar em `common.py` com:

```text
TypeError: 'NoneType' object is not callable
...
duration=self.duration(key)
```

isso é uma colisão de nome com o ciclo de vida de `Scene` no Manim. A v2.2 renomeia o método do projeto para `segment_duration()` e torna a leitura da duração tolerante a valores ausentes no manifesto de áudio.

A v2.2 também deixa de exigir `DejaVu Sans`. O arquivo `font_utils.py` escolhe automaticamente uma fonte instalada (`DejaVu Sans`, `Segoe UI`, `Aptos`, `Arial`, `Liberation Sans`, `Noto Sans` ou `Sans`). Você pode forçar uma família com a variável de ambiente `ENEM_FONT`.

Teste recomendado:

```powershell
python enem/doctor.py
python enem/render_all.py --from 1 --to 1 --quality draft
```
