"""Gera uma amostra curta de voz para escolher o narrador antes dos 30 vídeos."""
import argparse, asyncio
from pathlib import Path
import edge_tts

TEXT=('Hoje vamos resolver uma questão do ENEM de forma visual. '
      'Primeiro identificamos os dados, depois construímos a ideia geométrica e, por fim, fazemos a conta passo a passo.')

async def run(voice,rate,out):
    await edge_tts.Communicate(TEXT,voice=voice,rate=rate).save(str(out))
    print(out)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--voice',default='pt-BR-AntonioNeural'); p.add_argument('--rate',default='+4%'); p.add_argument('--out',default='voice_preview.mp3')
    a=p.parse_args(); asyncio.run(run(a.voice,a.rate,Path(a.out)))
if __name__=='__main__': main()
