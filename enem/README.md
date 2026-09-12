# Assets de áudio ENEM

Este diretório não contém mais um pipeline ENEM separado.

Ele permanece temporariamente apenas porque os manifests de qENEM ainda referenciam arquivos como:

```text
enem/audio/<canonical_id>/<segmento>.mp3
```

O código de renderização é inteiramente fornecido por `src/mathinmovement/`.

Próxima etapa prevista: mover esses MP3s para assets pertencentes aos próprios conteúdos (por exemplo, `content/enem/<id>/assets/audio/`) e então remover este diretório residual.
