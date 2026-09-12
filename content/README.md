# Conteúdo

Este diretório é a fonte de verdade declarativa do Math in Movement.

- `content/enem/<id>/manifest.yaml`: questões e resoluções ENEM;
- `content/demos/<id>/manifest.yaml`: demonstrações matemáticas;
- `content/<tipo>/<id>/assets/`: arquivos pertencentes ao próprio conteúdo.

As narrações qENEM ficam em `content/enem/<id>/assets/audio/` e são referenciadas pelo respectivo manifest.

O registry percorre os manifests, valida os schemas e reconstrói `cache/registry.sqlite`.

Nenhum conteúdo de produção depende de scripts Python antigos, listas hardcoded, arquivos de compatibilidade ou diretórios legados externos.
