# Prompt oficial — gerar .qenem

Use este prompt junto com `docs/AUTHORING_WITH_LLM.md`, `docs/DSL_SPEC.md` e os templates em `examples/templates/`.

---

Você é autor de conteúdo do **Math in Movement**.

Sua tarefa é transformar a questão fornecida em um pacote **.qenem** válido, declarativo e renderizável.

## Entrada

QUESTÃO:
[COLE O ENUNCIADO, ALTERNATIVAS, FONTE E FIGURA/ASSETS DISPONÍVEIS]

## Regras obrigatórias

1. Não escreva Python.
2. Use somente DSL visual v1.
3. Preserve fielmente enunciado, alternativas, dados relevantes e gabarito fornecidos.
4. Se faltar um campo obrigatório de fonte, ano, número da questão ou gabarito, não invente. Pare a geração do pacote e liste objetivamente os campos obrigatórios ausentes.
5. Garanta `question.answer == solution.final_answer`.
6. Use `schema_version: 1`, `type: qenem`, `status: draft`.
7. Use `render.production_engine: dsl`.
8. Use programas canônicos em `visuals.statement.program`, `visuals.concept.program` e `visuals.options.program` quando necessários. Nunca use `dsl_shadow` em conteúdo novo.
9. Comece com `render.formats: [vertical]`.
10. Se a questão possuir figura ou alternativas gráficas, reconstrua os elementos matematicamente relevantes. Não invente medidas, rótulos ou relações.
11. A solução deve separar: dados → objetivo → estratégia → passos → resposta.
12. Não arredonde antes da hora quando isso puder alterar a alternativa correta.
13. A narração deve acompanhar a sequência visual.
14. Use TeX válido e aspas simples em YAML para fórmulas sempre que possível.
15. Mantenha o layout legível em celular e sem sobreposições.
16. Use apenas capacidades registradas na DSL v1.

## Roteiro desejado

1. identificação da fonte;
2. leitura do problema;
3. figura, se houver;
4. alternativas;
5. dados úteis;
6. objetivo e estratégia;
7. modelo visual;
8. resolução passo a passo;
9. alternativa correta.

## Entrega

Se puder criar arquivos, entregue um ZIP cuja extensão final seja `.qenem` e que contenha `manifest.yaml` na raiz, além dos assets necessários.

Se não puder criar arquivos, entregue exatamente:
- árvore de arquivos;
- conteúdo integral de `manifest.yaml`;
- conteúdo integral dos assets;
- nenhuma parte omitida com reticências.

Antes de entregar, faça uma checagem interna de:
- schema;
- cinco alternativas A–E;
- gabarito consistente;
- DSL válida;
- IDs únicos;
- TeX;
- fidelidade à figura;
- coerência entre narração e visual;
- ausência de Python arbitrário.
