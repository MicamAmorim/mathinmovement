from pathlib import Path
import argparse, subprocess, sys
ROOT=Path(__file__).resolve().parent

def run(cmd):
    print('>', ' '.join(map(str,cmd)))
    subprocess.run(cmd,cwd=ROOT,check=True)

def main():
    p=argparse.ArgumentParser(description='Narração + TTS + renderização das resoluções ENEM.')
    p.add_argument('--from',dest='start',type=int,default=1)
    p.add_argument('--to',dest='end',type=int,default=30)
    p.add_argument('--voice',default='pt-BR-AntonioNeural')
    p.add_argument('--rate',default='+4%')
    p.add_argument('--quality',choices=['draft','final'],default='final')
    p.add_argument('--format',dest='video_format',choices=['vertical','horizontal'],default='vertical',
                   help='vertical=9:16 (padrão atual), horizontal=16:9')
    p.add_argument('--skip-voice',action='store_true')
    p.add_argument('--skip-render',action='store_true')
    p.add_argument('--keep-going',action='store_true')
    a=p.parse_args()
    run([sys.executable,'narration_builder.py'])
    if not a.skip_voice:
        run([sys.executable,'generate_voice.py','--from',str(a.start),'--to',str(a.end),'--voice',a.voice,f'--rate={a.rate}','--check-voice'])
    if not a.skip_render:
        cmd=[sys.executable,'render_all.py','--from',str(a.start),'--to',str(a.end),'--quality',a.quality,'--format',a.video_format]
        if a.keep_going: cmd.append('--keep-going')
        run(cmd)
if __name__=='__main__': main()
