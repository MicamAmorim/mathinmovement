# DSL visual - auditoria de cobertura v1

A DSL foi extraída dos 60 vídeos já aprovados, e não de uma lista abstrata.

A auditoria separa objetos gráficos, ações, ações compostas, dinâmica e layout.

## Estado da migração

Em 2026-09-12, **30/30 demos** possuem `dsl_shadow.visual_program` e **30/30 qENEM** possuem `dsl_shadow.visuals`.
Assim, os **60/60 conteúdos de produção** já têm uma representação shadow declarativa.

A regressão renderizada vertical dos 60 conteúdos foi aprovada em 2026-09-12 e o catálogo foi promovido para `production_engine: dsl`. A produção usa DSL quando o formato está declarado em `dsl_shadow.formats` e cai para o renderer nativo quando aquele formato ainda não foi aprovado na DSL. Atualmente os 30 demos têm shadow aprovado em vertical; as 30 qENEM declaram vertical e horizontal. O conjunto mínimo de capacidade das qENEM permanece com 6 questões.

Cobertura mínima das demos: 31 capacidades semânticas usadas pelas 30 demos.
Set cover mínimo de 8 demos:
- area-triangulo
- area-losango
- comprimento-circunferencia-pi
- relacoes-metricas-triangulo-retangulo
- area-prismas-planificacao
- volume-prismas
- volume-piramide
- area-cone

Cobertura mínima das qENEM: 6 questões:
- ENEM-2021-MT-11
- ENEM-2023-MT-06
- ENEM-2023-MT-07
- ENEM-2023-MT-29
- ENEM-2023-MT-44
- ENEM-2024-MT-30

Esses 14 vídeos são a suíte de regressão visual de capacidade da DSL.

Extensibilidade:
- namespace 2d.* para objetos;
- layout.* para composição;
- anim.* para animações;
- dynamic.* para trackers e redraw;
- futuramente 3d.* sem alterar programas dsl_version 1.0.
