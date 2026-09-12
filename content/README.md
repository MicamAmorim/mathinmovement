# Conteúdo

Este diretório é a fonte de verdade declarativa do Math in Movement.

- `content/enem/<id>/manifest.yaml`: questões e resoluções ENEM;
- `content/demos/<id>/manifest.yaml`: demonstrações matemáticas.

O registry percorre esses manifests, valida os schemas e reconstrói `cache/registry.sqlite`.

Nenhum conteúdo de produção depende de scripts Python antigos, listas hardcoded ou arquivos de compatibilidade.
