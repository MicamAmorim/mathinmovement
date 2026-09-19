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

### Cores por trecho em fórmulas

O objeto `math` aceita `tex_to_color_map` para colorir substrings sem inserir comandos de cor dentro do LaTeX:

```yaml
- id: expr
  type: math
  tex: '6\div2\times(1+2)=?'
  color: white
  tex_to_color_map:
    '+': yellow
    '\times': blue
    '\div': green
    '-': red
```

Também é possível declarar `substrings_to_isolate` como lista. Prefira `tex_to_color_map` a comandos como `\color{...}` dentro de `tex`, pois mantém o TeX portátil entre instalações do Manim.

Por compatibilidade, o runtime reconhece padrões legados simples como `{\color{green}\div}` e `\textcolor{red}{-}`, converte-os para `tex_to_color_map` e remove o comando de cor antes da compilação LaTeX. Conteúdo novo não deve depender dessa conversão.

## Objetos 2D da v1

line, dashed_line, polygon, regular_polygon, rectangle, rounded_rectangle, square, circle, ellipse, arc, sector, arc_between_points, dot, arrow, double_arrow, curved_arrow, brace, angle, axes, polyline, graph, text, math e group.

## Objetos 3D da v1

A DSL também aceita geometria tridimensional real, renderizada com `ThreeDScene`/`ThreeDCamera` do Manim:

- `3d.axes`: eixos cartesianos tridimensionais;
- `3d.cube`: cubo;
- `3d.prism`: prisma retangular com `dimensions: [x, y, z]`;
- `3d.dot`: ponto esférico 3D;
- `3d.line`: segmento 3D;
- `3d.arrow`: seta 3D;
- `3d.plane`: plano retangular orientável no espaço.

Objetos 3D aceitam `at`, `shift`, `scale`, `opacity`, `rotate_x`, `rotate_y`, `rotate_z` e também:

```yaml
rotate:
  angle: '=pi/2'
  axis: [0, 1, 0]
  about_point: [0, 0, 0]
```

Exemplo:

```yaml
objects:
  - id: axes
    type: 3d.axes
    x_range: [-4, 4, 1]
    y_range: [-3, 3, 1]
    z_range: [-2, 6, 1]

  - id: cube
    type: 3d.cube
    side: 1.4
    at: [1, 0, 3]
    color: cyan
    fill_opacity: 0.18

  - id: ray
    type: 3d.line
    start: [-2, 0, 0]
    end: [1, 0, 3]
    color: gold
```

## Câmera 3D

A timeline pode controlar a câmera:

```yaml
timeline:
  - op: camera.set_orientation
    phi: '=65*pi/180'
    theta: '=-55*pi/180'
    zoom: 0.9

  - op: camera.move
    phi: '=75*pi/180'
    theta: '=-25*pi/180'
    zoom: 1.05
    run_time: 2.0

  - op: camera.begin_ambient_rotation
    rate: 0.05
    about: theta

  - op: wait
    duration: 2

  - op: camera.stop_ambient_rotation
    about: theta
```

Para textos e fórmulas que devem permanecer como HUD durante movimentos da câmera, use `fixed_in_frame`; para labels que permanecem no espaço mas sempre voltados ao observador, use `fixed_orientation`. As ações inversas são `unfix_in_frame` e `unfix_orientation`.

## Ações da v1

create, fade_in, fade_out, write, translate, rotate, scale, opacity, stretch, highlight, style, copy, transform, transform_from_copy, replacement_transform, rigid_motion, lagged, parallel, wait, add, remove, move_to, next_to, arrange, animate_value, camera.set_orientation, camera.move, camera.begin_ambient_rotation, camera.stop_ambient_rotation, fixed_in_frame, fixed_orientation, unfix_in_frame e unfix_orientation.

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

O parser central não enumera tipos. Novas capacidades entram pelo registry. A camada 3D segue esse princípio: `3d.*` e `camera.*` foram adicionados sem alterar a semântica dos programas 2D existentes.
