from __future__ import annotations
from pathlib import Path
import json, re, math
from specs import SPECS

ROOT=Path(__file__).resolve().parent
QUESTIONS={q['canonical_id']:q for q in json.loads((ROOT/'data/questions.json').read_text(encoding='utf8'))}

VISUAL_OPTION_IDS={'ENEM-2023-MT-29'}

NUM_WORDS={
    '0':'zero','1':'um','2':'dois','3':'três','4':'quatro','5':'cinco','6':'seis','7':'sete','8':'oito','9':'nove'
}

def normalize_spaces(text:str)->str:
    return re.sub(r'\s+',' ',text).strip()


def prose_to_speech(text:str)->str:
    s=str(text)
    reps=[
        ('cm³',' centímetros cúbicos'),('cm²',' centímetros quadrados'),('m³',' metros cúbicos'),('m²',' metros quadrados'),
        ('√3','raiz de três'),('√2','raiz de dois'),('π','pi'),('ℓ','L'),('α','alfa'),('Δ','variação de '),
        ('≈',' aproximadamente '),('⇒',' portanto '),('→',' para '),('×',' vezes '),('²',' ao quadrado'),('³',' ao cubo'),('°',' graus'),
    ]
    # Units typed without superscript in some OCR stems.
    s=re.sub(r'(?<=\d)\s*cm3\b',' centímetros cúbicos',s,flags=re.I)
    s=re.sub(r'(?<=\d)\s*mL\b',' mililitros',s,flags=re.I)
    for a,b in reps: s=s.replace(a,b)
    s=re.sub(r'(?<=\d)\s*cm\b',' centímetros',s,flags=re.I)
    s=re.sub(r'(?<=\d)\s*km\b',' quilômetros',s,flags=re.I)
    s=re.sub(r'(?<=\d)\s*m\b',' metros',s,flags=re.I)
    s=s.replace('mL',' mililitros').replace('sen ', 'seno de ').replace('=', ' é igual a ').replace('/', ' dividido por ')
    s=re.sub(r'\b1\s+mililitros\b','1 mililitro',s)
    return normalize_spaces(s)

def strip_accessibility_descriptions(text:str)->str:
    # ENEM digital inserts accessibility descriptions directly in the parsed stem.
    text=re.sub(r'Descri[cç][aã]o\s+(?:da|do|das|dos)\s+[^:]+:.*?\(Fim da descri[cç][aã]o\)', ' ', text, flags=re.I|re.S)
    text=re.sub(r'Descri[cç][aã]o\s+[^:]+:.*?\(Fim da descri[cç][aã]o\)', ' ', text, flags=re.I|re.S)
    return normalize_spaces(text)

def spoken_stem(q:dict)->str:
    text=strip_accessibility_descriptions(q['stem'])
    cid=q['canonical_id']
    if cid=='ENEM-2021-MT-11':
        text=text.replace('Considere 1,7 como valor aproximado para .','Considere 1,7 como valor aproximado para raiz de três.')
    if cid=='ENEM-2022-MT-10':
        text=('O governo de um estado pretende realizar uma obra para integrar duas cidades e facilitar o escoamento da produção agrícola. '
              'O projeto interliga diretamente as cidades A e B à Rodovia 003 por duas rodovias retas, 001 e 002, que devem chegar ao mesmo ponto da Rodovia 003. '
              'A figura indica as posições das cidades e cinco localizações sugeridas, de I a V, para esse ponto de conexão. '
              'Pretende-se que a distância percorrida entre as duas cidades, passando pelo ponto de conexão, seja a menor possível. '
              'Qual das localizações sugeridas deve ser escolhida?')
    if cid in VISUAL_OPTION_IDS and 'Descrição das alternativas:' in text:
        text=text.split('Descrição das alternativas:',1)[0].strip()
    return normalize_spaces(text)

def chunk_text(text:str,max_chars:int=430)->list[str]:
    sentences=re.split(r'(?<=[.!?])\s+',normalize_spaces(text))
    chunks=[]; cur=''
    for sent in sentences:
        if not sent: continue
        if len(cur)+len(sent)+1<=max_chars:
            cur=(cur+' '+sent).strip()
        else:
            if cur: chunks.append(cur)
            if len(sent)<=max_chars: cur=sent
            else:
                words=sent.split(); cur=''
                for w in words:
                    if len(cur)+len(w)+1>max_chars:
                        if cur: chunks.append(cur)
                        cur=w
                    else: cur=(cur+' '+w).strip()
    if cur: chunks.append(cur)
    return chunks

def math_to_speech(tex:str)->str:
    s=tex
    # textual LaTeX fragments
    s=re.sub(r'\\text\{([^{}]*)\}',r'\1',s)
    s=re.sub(r'\\mathrm\{([^{}]*)\}',r'\1',s)
    s=s.replace('{,}',',').replace('\\,',' ')
    # common roots before removing braces
    s=re.sub(r'\\sqrt\[3\]\{([^{}]+)\}',r'raiz cúbica de \1',s)
    s=re.sub(r'\\sqrt\{([^{}]+)\}',r'raiz quadrada de \1',s)
    s=re.sub(r'\\sqrt\s*([0-9a-zA-Z]+)',r'raiz quadrada de \1',s)
    replacements=[
        ('\\Rightarrow','; portanto, '),('\\longrightarrow',' gera '),('\\approx',' aproximadamente '),
        ('\\cdot',' vezes '),('\\times',' vezes '),('\\pi',' pi '),('\\ell',' L '),
        ('\\Delta',' variação de '),('\\theta',' teta '),('\\omega',' ômega '),('\\alpha',' alfa '),('\\sin',' seno de '),('\\cos',' cosseno de '),
        ('\\ne',' diferente de '),('\\le',' menor ou igual a '),('\\ge',' maior ou igual a '),
        ('\\quad',', '),('\\over',' dividido por '),('\\circ',' graus '),
    ]
    for a,b in replacements: s=s.replace(a,b)
    s=s.replace('^2',' ao quadrado').replace('^3',' ao cubo')
    s=re.sub(r'\^\{?(-?\d+)\}?',r' elevado a \1',s)
    s=s.replace('_',' índice ')
    s=s.replace('\\',' ')
    s=s.replace('{',' ').replace('}',' ')
    s=s.replace('=',' é igual a ').replace('>',' é maior que ').replace('<',' é menor que ')
    s=s.replace('+',' mais ').replace('−',' menos ').replace('-', ' menos ')
    # slashes left after simple expressions
    s=s.replace('/',' dividido por ')
    s=re.sub(r'(?<=\d)(?=raiz)', ' ', s)
    s=re.sub(r'\s+',' ',s).strip(' ,;')
    s=s.replace(', ; portanto, ,', '; portanto,').replace('; ; portanto,', '; portanto,').replace('^ graus',' graus')
    # Make a few units friendlier.
    s=s.replace('cm ao cubo','centímetros cúbicos').replace('m ao cubo','metros cúbicos')
    s=s.replace('cm ao quadrado','centímetros quadrados').replace('m ao quadrado','metros quadrados')
    s=s.replace('cm','centímetros').replace('km','quilômetros')
    return s

def options_speech(q:dict)->str:
    if q['canonical_id'] in VISUAL_OPTION_IDS:
        return ('As alternativas são cinco gráficos. Observe que todos começam na altura máxima, mas têm formas diferentes. '
                'A alternativa A é uma cossenoide; as demais são formadas por segmentos de reta ou arcos de parábola.')
    bits=[]
    for letter,value in q.get('options',{}).items():
        value=normalize_spaces(value).strip(' /')
        bits.append(f'{letter}: {value}')
    return 'As alternativas são: '+ '; '.join(bits)+'.' if bits else ''

def figure_speech(q:dict,s:dict)->str:
    desc=normalize_spaces(q.get('visual_description',''))
    if not desc: return ''
    prefix='Observe a reconstrução esquemática da figura da questão. '
    return prefix+desc

def data_speech(s:dict)->str:
    return 'Separe os dados que realmente entram na conta: '+ '; '.join(s['data'])+'.'

def strategy_speech(s:dict)->str:
    return s.get('hook','')+' O plano é: '+' '.join(f'{i+1}, {x}' for i,x in enumerate(s['plan']))

def step_speech(label:str,tex:str)->str:
    spoken=math_to_speech(tex)
    label=label.rstrip('.')
    return f'{label}. Na tela, {spoken}.'

def answer_speech(q:dict)->str:
    opt=normalize_spaces(q.get('options',{}).get(q['answer'],''))
    if opt:
        return f'Logo, a resposta é a alternativa {q["answer"]}: {opt}'
    return f'Logo, a resposta é a alternativa {q["answer"]}.'

def build_for(spec:dict)->dict:
    q=QUESTIONS[spec['id']]
    segments=[]
    def add(key,kind,text,screen):
        text=prose_to_speech(text)
        if not text: return
        segments.append({'key':key,'kind':kind,'screen':screen,'text':text,'estimated_seconds':round(max(1.4,len(text.split())/2.55),2)})
    add('source','source',f'ENEM {q["year"]}, questão {q["question_number"]}. Vamos ler, interpretar e resolver visualmente.','source')
    for i,ch in enumerate(chunk_text(spoken_stem(q)),1):
        add(f'statement_{i:02d}','statement',ch,'statement')
    if spec.get('statement_visual'):
        add('figure','figure',figure_speech(q,spec),'figure')
    add('options','options',options_speech(q),'options')
    add('data','data',data_speech(spec),'data')
    add('strategy','strategy',strategy_speech(spec),'goal')
    add('visual','visual',spec['visual_note'],'visual')
    for i,(label,tex,*rest) in enumerate(spec['steps'],1):
        add(f'step_{i:02d}','step',step_speech(label,tex),'solution')
    add('answer','answer',answer_speech(q),'answer')
    return {
        'id':spec['id'],'year':q['year'],'question_number':q['question_number'],'answer':q['answer'],
        'has_statement_visual':bool(spec.get('statement_visual')),'statement_visual':spec.get('statement_visual'),
        'segments':segments,
        'estimated_total_seconds':round(sum(x['estimated_seconds'] for x in segments),1)
    }

def build_all()->dict:
    return {spec['id']:build_for(spec) for spec in SPECS}

def write_outputs()->None:
    outdir=ROOT/'narrations'; outdir.mkdir(exist_ok=True)
    all_data=build_all()
    (outdir/'narrations.json').write_text(json.dumps(all_data,ensure_ascii=False,indent=2),encoding='utf8')
    master=['# Narrações — 30 resoluções ENEM','',
            'Os blocos abaixo usam as mesmas chaves consumidas pelo `common.py` e pelo `generate_voice.py`. '+
            'Você pode editar qualquer fala e regenerar apenas os áudios correspondentes.','']
    for idx,spec in enumerate(SPECS,1):
        item=all_data[spec['id']]
        lines=[f'# {idx:02d} · {item["id"]} — Q{item["question_number"]}','',
               f'Tempo estimado de narração: **{item["estimated_total_seconds"]:.1f} s**','']
        for seg in item['segments']:
            lines += [f'## `{seg["key"]}` · {seg["kind"]}',seg['text'],'']
        fname=f'{idx:02d}_{item["id"].lower().replace("enem-","").replace("-","_")}.md'
        (outdir/fname).write_text('\n'.join(lines),encoding='utf8')
        master += lines + ['---','']
    (outdir/'NARRATION_ALL.md').write_text('\n'.join(master),encoding='utf8')
    print(f'Wrote {len(all_data)} narration scripts to {outdir}')

if __name__=='__main__':
    write_outputs()
