# Template — questão desafio curta

Este diretório é a fonte canônica para vídeos curtos no formato **pergunta → palpite → resolução → resposta → comentário**.

## Estrutura recomendada

1. expressão e hook já no primeiro frame;
2. cinco segundos para o espectador formar um palpite;
3. uma transformação matemática por etapa;
4. resposta grande e isolada;
5. encerramento: **“Você conseguiu resolver? Coloque nos comentários.”**

A duração em torno de 24 segundos é a referência, não uma obrigação. Ajuste o início da resolução de acordo com a duração da abertura narrada.

## Áudio padrão da contagem

Marque o primeiro passo visual da contagem com:

```yaml
- op: add
  target: n5
  tags: [countdown-5s]
```

A tag deve ficar no passo em que o número `5` aparece. O runtime registra o timestamp exato dessa etapa e **não** envia o bipe ao Manim. O FFmpeg usa diretamente o arquivo original versionado em:

```text
assets/audio/countdown-5s-original.mp3
```

O arquivo original tem cerca de 11,02 s; o trecho usado pelo countdown começa em 4,832653 s e vai até o fim. O FFmpeg recorta essa janela diretamente do MP3, zera o timestamp do recorte e então aplica `atempo=0.9` (90% da velocidade original). O runtime também sincroniza automaticamente a permanência visual de `n5 → n4 → n3 → n2 → n1` com o intervalo efetivo do áudio, levando em conta `MANIM_PACE`. Na mixagem final, um limiter evita clipping entre narração e bipe.

## Convenções visuais

Quando houver esses operadores, use a paleta:

- `+` → amarelo;
- `×` → azul;
- `÷` → verde;
- `−` → vermelho.

Aplique a cor ao operador por meio de `tex_to_color_map`; não use `\color{...}` dentro do TeX.

Priorize leitura em celular:

- expressão principal em torno de 72 pt ou maior quando couber;
- equações centrais em torno de 76–86 pt;
- expressões auxiliares em torno de 48 pt;
- resposta final muito destacada;
- margens generosas.

## Títulos

Varie a engenharia de atenção, em vez de repetir percentuais ou “só gênios”:

- escolha binária: `9 ou 1?`;
- desafio direto: `Você acertaria?`;
- pressão temporal: `Você tem 5 segundos`;
- conflito de regra: `Multiplica ou divide primeiro?`;
- erro provável: `Onde está a pegadinha?`;
- expressão nua: `6 ÷ 2 × (1 + 2) = ?`.

Percentuais como “89% erram” não devem ser tratados como estatística sem fonte.

## Narração

Por padrão, use somente duas falas:

- abertura: o hook do vídeo;
- encerramento: `Você conseguiu resolver? Coloque nos comentários.`

O miolo da resolução permanece visual para preservar o compromisso mental do espectador.

Os assets de voz de cada conteúdo devem ficar dentro do respectivo `.demo`. O áudio da contagem é o MP3 original compartilhado em `assets/audio/countdown-5s-original.mp3`; sua inserção ocorre no pós-processamento com FFmpeg, a 90% da velocidade original.

## Validação

Depois de copiar e adaptar:

```powershell
python -m mathinmovement validate
python -m mathinmovement dsl validate <id>
python -m mathinmovement produce <pacote.demo> --dry-run
```

Para reproduzir o ritmo desta referência, use `MANIM_PACE=1.0`.
