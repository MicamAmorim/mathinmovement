# Autoria com LLM — Math in Movement

Este guia define o contrato oficial para uma LLM criar conteúdo novo do Math in Movement sem escrever Python arbitrário.

## Princípio

A LLM produz conteúdo declarativo. O engine Python/Manim permanece confiável e separado do conteúdo.

Para conteúdo novo, use a DSL canônica:

- `demo`: `visual_program`;
- `qenem`: `visuals.statement.program`, `visuals.concept.program` e, quando necessário, `visuals.options.program`.

`dsl_shadow` existe apenas para compatibilidade com o catálogo migrado e não deve ser usado em conteúdo novo.

## Pacotes

`.demo` e `.qenem` são containers ZIP. O `manifest.yaml` deve ficar na raiz do ZIP.

```text
meu-conteudo.demo
├── manifest.yaml
└── assets/
    ├── images/
    └── audio/
```

Uma LLM capaz de gerar arquivos deve entregar o ZIP com a extensão correta. Se só puder responder em texto, deve entregar a árvore de arquivos e o conteúdo integral de cada arquivo, sem omissões.

## Regras gerais

1. `schema_version: 1`.
2. Conteúdo novo começa com `status: draft`.
3. `render.production_engine: dsl`.
4. Comece com `render.formats: [vertical]`. Adicione `horizontal` somente após inspeção visual.
5. Use apenas capacidades da DSL v1 documentadas em `docs/DSL_SPEC.md`.
6. Não inclua Python, imports, `eval`, `exec` ou código executável.
7. IDs de objetos DSL devem ser únicos dentro do programa.
8. Em YAML, prefira aspas simples para TeX, por exemplo `'A=\frac{bh}{2}'`.
9. Preserve a correção matemática antes da estética.
10. Evite sobreposição: mantenha textos curtos e deixe margens generosas.
11. Use transformações visuais graduais quando houver demonstração geométrica.
12. Não invente informação ausente da questão-fonte. Se uma figura original não puder ser reconstruída fielmente, declare a limitação e use um esquema matematicamente equivalente somente quando isso não alterar o problema.

## Estilo visual recomendado

- fundo escuro e alto contraste;
- `cyan` para objeto principal;
- `gold` para medida, destaque ou elemento em transformação;
- `white` para texto/fórmula principal;
- `muted` para observações secundárias;
- animações progressivas em vez de aparições abruptas;
- uma ideia visual por vez;
- fórmula final apenas depois da justificativa visual.

## Demo

Campos mínimos:

- `schema_version`, `id`, `type`, `title`;
- `lesson.objective` e ao menos um item em `lesson.steps`;
- `result`;
- `render`;
- `visual_program`.

O programa deve conter `dsl_version`, `objects` e `timeline`.

Veja:
- `examples/templates/demo-minimal/manifest.yaml`;
- `examples/templates/demo-complete/manifest.yaml`.

## qENEM

Campos mínimos:

- metadados de `exam`;
- `question.stem`, cinco alternativas e `answer`;
- `solution.goal`, `strategy`, `steps` e `final_answer`;
- `render`.

Sempre confira que:

```text
question.answer == solution.final_answer
```

Use programas declarativos em `visuals.*.program` quando a questão possuir figura, gráfico, alternativas gráficas ou quando uma representação conceitual ajudar a solução.

Veja:
- `examples/templates/qenem-minimal/manifest.yaml`;
- `examples/templates/qenem-complete/manifest.yaml`.

## Narração

Para rascunhos, `narration.enabled: false` é suficiente.

Quando habilitada, a narração deve acompanhar exatamente a ordem visual. Para qENEM, os segmentos usuais são:

`source`, `statement_01`, `figure`, `options`, `data`, `strategy`, `visual`, `step_01` ... `answer`.

Não é necessário embutir MP3 no pacote quando o pipeline TTS irá gerá-los.

## Criar uma base local

O CLI pode gerar um conteúdo mínimo válido antes da edição pela LLM:

```powershell
python -m mathinmovement scaffold demo meu-demo
python -m mathinmovement scaffold qenem minha-questao --year 2026 --question-number 146
```

Para também gerar imediatamente o container ZIP com a extensão correta:

```powershell
python -m mathinmovement scaffold demo meu-demo --package
python -m mathinmovement scaffold qenem minha-questao --year 2026 --question-number 146 --package
```

O diretório gerado contém `manifest.yaml` e `assets/`. Use `--force` somente quando quiser substituir um scaffold já existente.

## Fluxo de validação

Depois de gerar o pacote:

```powershell
python -m mathinmovement import meu-conteudo.demo
python -m mathinmovement validate
python -m mathinmovement dsl validate meu-conteudo
python -m mathinmovement produce meu-conteudo --dry-run
python -m mathinmovement produce meu-conteudo --quality draft
```

Para qENEM, troque a extensão e o ID conforme o manifest.

## Critérios de aprovação visual

- nada cortado fora do frame;
- nenhuma fórmula ou legenda sobreposta;
- labels associados ao objeto correto;
- transformações geometricamente válidas;
- figura da questão preserva os dados relevantes;
- solução visual concorda com a solução algébrica;
- leitura confortável em celular;
- nenhuma etapa importante aparece antes de ser explicada.

## Prompts oficiais

- `prompts/llm-demo.md`;
- `prompts/llm-qenem.md`.

Esses prompts devem ser usados junto com `docs/DSL_SPEC.md` e os templates oficiais.
