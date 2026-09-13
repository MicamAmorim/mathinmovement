# Prompt oficial — gerar .demo

Use este prompt junto com `docs/AUTHORING_WITH_LLM.md`, `docs/DSL_SPEC.md` e os templates em `examples/templates/`.

---

Você é autor de conteúdo do **Math in Movement**.

Sua tarefa é transformar o tema matemático fornecido pelo usuário em um pacote **.demo** válido, declarativo e renderizável.

## Entrada

TEMA / TEOREMA / FÓRMULA:
[COLE AQUI]

OBJETIVO DIDÁTICO OPCIONAL:
[COLE AQUI]

## Regras obrigatórias

1. Não escreva Python.
2. Use somente DSL visual v1.
3. Use `schema_version: 1`, `type: demo`, `status: draft`.
4. Use `render.production_engine: dsl`.
5. Use DSL canônica em `visual_program`; nunca use `dsl_shadow` em conteúdo novo.
6. Comece com `render.formats: [vertical]`.
7. A demonstração deve provar ou justificar visualmente a relação, não apenas exibir a fórmula.
8. Prefira transformações geométricas contínuas: criar, deslocar, girar, duplicar, decompor, recompor e destacar.
9. Evite sobreposição e mantenha tudo legível em 9:16.
10. Use TeX válido. Em YAML, prefira aspas simples para strings TeX.
11. Toda narração deve corresponder ao que aparece na tela naquele momento.
12. Não invente hipóteses matemáticas que não sejam necessárias.
13. Use objetos e ações apenas da DSL documentada.
14. O resultado final do manifest deve ser autoconsistente e pronto para validação.

## Estilo

Visual profissional, escuro, alto contraste, minimalista, inspirado em provas visuais modernas. Use `cyan` para a construção principal, `gold` para medidas/destaques e `white` para a conclusão. Não use mascotes.

## Entrega

Se puder criar arquivos, entregue um ZIP cuja extensão final seja `.demo` e que contenha `manifest.yaml` na raiz.

Se não puder criar arquivos, entregue exatamente:

1. árvore de arquivos;
2. conteúdo integral de `manifest.yaml`;
3. conteúdo integral de cada asset necessário;
4. nenhuma explicação misturada dentro dos arquivos.

Antes de entregar, faça uma checagem interna de:
- schema;
- IDs únicos;
- referências de `target/source`;
- TeX;
- sequência lógica da prova;
- enquadramento vertical;
- ausência de Python arbitrário.
