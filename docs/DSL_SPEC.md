# DSL visual v1

## Objetivo

Descrever animações matemáticas sem Python arbitrário no conteúdo. O engine traduz objetos e ações declarativas para Manim.

## Autoria canônica

Para conteúdo novo:

- demos usam `visual_program` na raiz do manifest;
- qENEM usam `visuals.<nome>.program`;
- `render.production_engine` deve ser `dsl`;
- `dsl_shadow` é um campo legado de compatibilidade com o catálogo migrado e não deve ser emitido por novas ferramentas de autoria.

O renderer nativo é um fallback apenas para conteúdos que declaram explicitamente `native_ready: true`.

## Programa mínimo

```yaml
visual_program:
  dsl_version: '1.0'
  objects:
    - id: tri
      type: polygon
      points: [[-2, -1], [2, -1], [0, 2]]
      color: cyan
      fill_opacity: 0.15
    - id: eq
      type: math
      tex: 'A=\\frac{bh}{2}'
      at: [0, -4.5]
  timeline:
    - op: create
      target: tri
      run_time: 1.5
    - op: write
      target: eq
    - op: highlight
      target: eq
```

Tipos podem usar o nome curto ou o namespace canônico. Ex.: `circle` equivale a `2d.circle`.

## Objetos 2D da v1

line, dashed_line, polygon, regular_polygon, rectangle, rounded_rectangle, square, circle, ellipse, arc, sector, arc_between_points, dot, arrow, double_arrow, curved_arrow, brace, angle, axes, polyline, graph, text, math e group.

## Ações da v1

create, fade_in, fade_out, write, translate, rotate, scale, opacity, stretch, highlight, style, copy, transform, transform_from_copy, replacement_transform, rigid_motion, lagged, parallel, wait, add, remove, move_to, next_to, arrange e animate_value.

## Dinâmica segura

Trackers são objetos `tracker`. Um objeto com `dynamic: true` é reconstruído via always_redraw. Valores iniciados por `=` são expressões numéricas restritas.

```yaml
objects:
  - id: t
    type: tracker
    value: 0
  - id: p
    type: dot
    point: ['=2*cos(t)', '=2*sin(t)']
    dynamic: true
timeline:
  - op: create
    target: p
  - op: animate_value
    target: t
    value: '=tau'
    run_time: 4
    rate_func: linear
```

Funções permitidas: sin, cos, tan, sqrt, abs, min e max. Constantes: pi, tau e e. Não há eval, exec, imports ou acesso a atributos.

## qENEM

Uma figura qENEM pode usar um programa DSL estático no lugar de renderer registrado:

```yaml
visuals:
  statement:
    description: 'reconstrução vetorial'
    program:
      dsl_version: '1.0'
      objects:
        - id: c
          type: circle
          radius: 2
          color: cyan
      timeline: []
```

## Evolução

O parser central não enumera tipos. Novas capacidades entram pelo registry. Uma futura camada 3D poderá registrar `3d.*` sem alterar programas 1.x existentes.
