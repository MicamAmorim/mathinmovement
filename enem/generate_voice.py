from __future__ import annotations
import argparse, asyncio, hashlib, json
from pathlib import Path
from mutagen.mp3 import MP3
import edge_tts
from specs import SPECS

ROOT=Path(__file__).resolve().parent
NARR_PATH=ROOT/'narrations'/'narrations.json'
AUDIO_DIR=ROOT/'audio'
MANIFEST_PATH=AUDIO_DIR/'manifest.json'
DEFAULT_VOICE='pt-BR-AntonioNeural'
FALLBACK_VOICES=['pt-BR-AntonioNeural','pt-BR-FranciscaNeural','pt-BR-DonatoNeural','pt-BR-BrendaNeural']


def load_json(path,default):
    return json.loads(path.read_text(encoding='utf8')) if path.exists() else default

def fingerprint(text,voice,rate,volume,pitch):
    raw='\0'.join([text,voice,rate,volume,pitch]).encode('utf8')
    return hashlib.sha256(raw).hexdigest()[:20]

async def ptbr_voices():
    voices=await edge_tts.list_voices()
    return [v for v in voices if v.get('Locale')=='pt-BR' or str(v.get('ShortName','')).startswith('pt-BR-')]

async def list_ptbr():
    voices=await ptbr_voices()
    print('Vozes pt-BR disponíveis no endpoint atual:')
    for v in voices:
        print(f"- {v.get('ShortName')} · {v.get('Gender','?')}")

async def resolve_voice(requested,check=False):
    if not check: return requested
    voices=await ptbr_voices(); names={v.get('ShortName') for v in voices}
    if requested in names: return requested
    for v in FALLBACK_VOICES:
        if v in names:
            print(f'[voz] {requested} indisponível; usando {v}')
            return v
    if names:
        v=sorted(names)[0]; print(f'[voz] usando fallback {v}'); return v
    raise RuntimeError('Nenhuma voz pt-BR foi encontrada pelo edge-tts.')

async def synthesize_one(text,out,voice,rate,volume,pitch):
    out.parent.mkdir(parents=True,exist_ok=True)
    communicate=edge_tts.Communicate(text=text,voice=voice,rate=rate,volume=volume,pitch=pitch)
    await communicate.save(str(out))
    return round(float(MP3(out).info.length),3)

async def main_async(args):
    if args.list_voices:
        await list_ptbr(); return
    narr=load_json(NARR_PATH,{})
    if not narr: raise SystemExit('Narrações ausentes. Execute: python narration_builder.py')
    AUDIO_DIR.mkdir(exist_ok=True)
    manifest=load_json(MANIFEST_PATH,{})
    voice=await resolve_voice(args.voice,args.check_voice)
    selected=SPECS[max(0,args.start-1):min(len(SPECS),args.end)]
    total=sum(len(narr[s['id']]['segments']) for s in selected)
    done=0
    for spec in selected:
        cid=spec['id']; manifest.setdefault(cid,{})
        print(f'\n[{cid}]')
        for seg in narr[cid]['segments']:
            done+=1; key=seg['key']; text=seg['text']; out=AUDIO_DIR/cid/f'{key}.mp3'
            fp=fingerprint(text,voice,args.rate,args.volume,args.pitch)
            old=manifest[cid].get(key,{})
            if out.exists() and old.get('fingerprint')==fp and not args.force:
                print(f'  {done:03d}/{total:03d} {key}: cache')
                continue
            print(f'  {done:03d}/{total:03d} {key}: sintetizando')
            duration=await synthesize_one(text,out,voice,args.rate,args.volume,args.pitch)
            manifest[cid][key]={
                'file':str(out.relative_to(ROOT)).replace('\\','/'),
                'duration':duration,'voice':voice,'rate':args.rate,'volume':args.volume,
                'pitch':args.pitch,'fingerprint':fp,'text':text,
            }
            MANIFEST_PATH.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    MANIFEST_PATH.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(f'\nConcluído. Manifesto: {MANIFEST_PATH.relative_to(ROOT)}')
    print('Agora renderize normalmente; common.py usa os MP3 automaticamente.')

def main():
    p=argparse.ArgumentParser(description='Gera narração neural pt-BR por segmento com edge-tts.')
    p.add_argument('--from',dest='start',type=int,default=1,help='primeiro vídeo (1-30)')
    p.add_argument('--to',dest='end',type=int,default=30,help='último vídeo (1-30)')
    p.add_argument('--voice',default=DEFAULT_VOICE)
    p.add_argument('--rate',default='+4%',help='ex.: +4%%, -8%%')
    p.add_argument('--volume',default='+0%')
    p.add_argument('--pitch',default='+0Hz')
    p.add_argument('--force',action='store_true',help='regenera mesmo quando o texto não mudou')
    p.add_argument('--check-voice',action='store_true',help='consulta as vozes atuais e aplica fallback pt-BR')
    p.add_argument('--list-voices',action='store_true',help='lista vozes pt-BR e sai')
    args=p.parse_args()
    if args.start<1 or args.end>30 or args.start>args.end: p.error('intervalo deve estar entre 1 e 30')
    asyncio.run(main_async(args))

if __name__=='__main__': main()
