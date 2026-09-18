# Template — questão desafio

Este diretório é o modelo oficial de **questão desafio curta** do Math in Movement.

A referência nasceu do vídeo **“89% erram essa”** e foi preservada em dois níveis:

- `roteiro-desafio-89-v2.md`: referência editorial integral, com timing, narração, retenção e decisões estéticas;
- `manifest.yaml`: referência técnica renderizável em DSL v1.

## Estrutura padrão do formato

O padrão visual/editorial é:

1. a questão aparece no primeiro quadro, sem saudação;
2. gancho curto acima da questão;
3. contagem regressiva visual de 5 segundos;
4. resolução em etapas, uma operação/ideia por vez;
5. resposta final grande e isolada;
6. CTA curto perguntando se o espectador acertou.

A duração de **24 s** é a referência deste modelo, não uma obrigação. Preserve o ritmo e ajuste a timeline quando a questão exigir mais ou menos etapas.

## Convenções visuais

Quando houver esses operadores, use a paleta:

- `+` → amarelo;
- `×` → azul;
- `÷` → verde;
- `−` → vermelho.

A cor deve ser aplicada ao **operador**, não aos números adjacentes. No manifest, faça isso com `tex_to_color_map`; não use `\color{...}` dentro do TeX.

Priorize leitura em celular:

- expressão principal em torno de 72 pt ou maior quando couber;
- equações centrais em torno de 76–86 pt;
- expressões auxiliares em torno de 48 pt;
- resposta final muito destacada;
- margens generosas e nenhuma informação importante próxima da borda.

## Ao criar um novo desafio

Copie o `manifest.yaml` e altere, no mínimo:

- `id`;
- `title`;
- `tags`;
- `lesson.objective`, `lesson.steps` e `result`;
- expressão inicial e equações intermediárias;
- títulos das etapas;
- resposta final;
- hook e CTA, quando necessário;
- timeline, caso a quantidade de etapas mude.

Sempre valide a matemática antes de adaptar a animação.

O texto “89% erram essa” é apenas a referência editorial do vídeo original. Não trate percentuais desse tipo como dado estatístico sem fonte.

## Narração

A referência original usa somente duas falas:

- abertura;
- encerramento.

O miolo da resolução é visual. Esse padrão deve ser preservado por default para desafios curtos, salvo pedido diferente.

Os MP3/WAV gerados **não são versionados neste template**. O Git mantém o roteiro e o manifest como fonte de verdade; os assets de voz podem ser gerados no pacote final.

## Validação

Depois de copiar e adaptar:

```powershell
python -m mathinmovement validate
python -m mathinmovement dsl validate <id>
python -m mathinmovement produce <pacote.demo> --dry-run
```

Para reproduzir o timing de 24 s desta referência, use `MANIM_PACE=1.0`.
