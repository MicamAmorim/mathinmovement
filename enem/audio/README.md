# Áudio gerado

Execute `python generate_voice.py --from 1 --to 30 --check-voice`.

A estrutura criada será `audio/ENEM-AAAA-MT-NN/<segmento>.mp3` e `audio/manifest.json`.
O arquivo `common.py` detecta o manifesto automaticamente e usa a duração real de cada MP3 para sincronizar as animações.
