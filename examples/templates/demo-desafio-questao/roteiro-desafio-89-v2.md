# Desafio de operações — roteiro e narração

**Formato:** vertical 9:16, 1080 × 1920, 30 fps. **Duração:** 24 segundos.

**Expressão:** 6 ÷ 2 × (1 + 2).

## Narração — somente duas falas

| Janela | Fala |
|---|---|
| 00:00,000–00:02,568 | “89% erram essa.” |
| 00:21,000–00:22,872 | “Você conseguiu?” |

Pronúncia da primeira fala: “Oitenta e nove por cento erram essa.”
Do segundo 3 ao 21 não há narração, nem leitura dos números da contagem.

## Roteiro visual

| Tempo | O que aparece e acontece |
|---|---|
| 00:00–00:03 | A expressão já aparece no primeiro quadro. Acima, “89% ERRAM ESSA”, com o percentual em dourado. Abaixo: “VOCÊ TEM 5 SEGUNDOS”. Primeira fala. |
| 00:03–00:08 | A expressão permanece imóvel e legível. Contagem visual: 5, 4, 3, 2, 1, cada número durante exatamente um segundo. |
| 00:08–00:12 | “01 / PARÊNTESES”. Mostrar 1 + 2 = 3 em dourado; transformar a expressão em 6 ÷ 2 × 3. Texto: “Primeiro, resolva dentro deles.” |
| 00:12–00:17 | “02 / DA ESQUERDA PARA A DIREITA”. Texto: “× e ÷ têm a mesma prioridade.” Destacar 6 ÷ 2 = 3 e transformar a expressão em 3 × 3. |
| 00:17–00:20 | “03 / MULTIPLICAÇÃO”. Transformar 3 × 3 em 3 × 3 = 9. Texto: “Agora, basta multiplicar.” |
| 00:20–00:21 | O resultado 9 cresce e fica verde. Acima: “RESPOSTA”. |
| 00:21–00:24 | Manter o 9 visível. Aparecem “Você conseguiu?” e “QUAL FOI O SEU RESULTADO?”. Segunda e última fala. |

## Validação matemática

6 ÷ 2 × (1 + 2) = 6 ÷ 2 × 3 = 3 × 3 = **9**.

Primeiro resolvemos os parênteses. Em seguida, divisão e multiplicação têm a mesma prioridade e são efetuadas da esquerda para a direita. O sinal × explícito evita a ambiguidade de uma multiplicação por justaposição.

## Retenção e direção

- Desafio legível já no primeiro quadro, sem saudação ou apresentação.
- Cinco segundos completos para o espectador formar seu palpite.
- Uma operação por etapa; cores orientam a leitura.
- A resposta aparece somente depois do raciocínio.
- Pergunta final convida a comentar o resultado que o espectador encontrou.
- Fundo escuro, fórmulas serifadas e textos curtos com margens para leitura em celular.

## Nota editorial

“89%” é o gancho solicitado pelo autor, não um percentual comprovado por pesquisa. Não deve ser citado como dado estatístico. O relatório de referência recomenda não inventar percentuais de erro. Não há garantia de viralização.

## Reprodução no Math in Movement

Pacote: \`desafio-89-operacoes.demo\`, com DSL canônica 1.0, sem código executável.

A timeline foi calculada para \`MANIM_PACE=1.0\`; esse valor mantém os timestamps indicados. A configuração padrão 1.15 prolonga as animações, mas não as pausas da contagem.

O pacote inclui as duas falas em MP3 e a faixa de 24 s sincronizada. A renderização visual DSL não injeta as falas automaticamente; a faixa sincronizada é aplicada na pós-produção. Para reproduzir pelo CLI, use \`--music assets/audio/narracao-desafio-89.wav --music-volume 1 --fade-in 0 --fade-out 0 --no-ducking\`.

## Ajustes estéticos — versão 2

- Paleta dos operadores: **+ amarelo**, **× azul/ciano**, **÷ verde** e **− vermelho**.
- A cor é aplicada ao **símbolo do operador**, mantendo números e demais elementos em branco para maximizar contraste.
- Expressão principal ampliada para **72 pt**.
- Equações das etapas ampliadas para **76–86 pt**; expressões auxiliares para **48 pt**.
- Resultado final ampliado para **155 pt**.
- Textos auxiliares menores também receberam pequenos aumentos para leitura confortável em celular.
- Timeline, narração, contagem e solução matemática permanecem inalteradas.
