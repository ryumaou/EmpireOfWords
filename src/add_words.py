#!/usr/bin/env python3
"""Add independent lexical roots to an existing generated language package.

Existing forms are never regenerated. New forms are generated from a Pound-style
transition model learned from the language's existing root lexicon.
"""
from __future__ import annotations
import argparse, csv, json, random, re, sys, tempfile
from pathlib import Path
from language_io import resolve_project_path, resolve_language_path, load_language, validate_package
from build_language import EntryKey, generate_unique_roots, load_lc_module, read_text
from grammar_engine import noun_form, verb_form, adjective_form, PERSONS

def parse_additions(path:Path):
    out=[]
    for no,raw in enumerate(read_text(path).splitlines(),1):
        line=raw.split('#',1)[0].strip()
        if not line: continue
        if '=' in line:
            raise ValueError(f'line {no}: add_words currently accepts independent roots only (no derivation expression)')
        if ':' not in line: raise ValueError(f'line {no}: expected gloss:pos')
        gloss,pos=(x.strip() for x in line.rsplit(':',1))
        if not gloss or not pos: raise ValueError(f'line {no}: expected gloss:pos')
        out.append((gloss,pos))
    return out

def rewrite_dictionary(pkg:Path, lexicon:list[dict], daughter:bool=False):
    path=pkg/'dictionary.csv'
    if daughter:
        lineage={}
        lp=pkg/'lineage.csv'
        if lp.exists():
            with lp.open(encoding='utf-8',newline='') as f:
                for row in csv.DictReader(f): lineage[(row.get('English',''),row.get('POS',''))]=row
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f); w.writerow(['English','POS','Generated','Type','Derivation','Parent Form','Inheritance','Sound Changes','Origin Language'])
            for x in lexicon:
                row=lineage.get((x.get('gloss',''),x.get('pos','')),{})
                w.writerow([x.get('gloss',''),x.get('pos',''),x.get('form',''),'derived' if x.get('derivation') else 'root',x.get('derivation') or '',row.get('Parent Form',''),row.get('Status',''),row.get('Changes',''),row.get('Origin Language','')])
    else:
        with path.open('w',encoding='utf-8',newline='') as f:
            w=csv.writer(f); w.writerow(['English','POS','Generated','Type','Derivation'])
            for x in lexicon: w.writerow([x.get('gloss',''),x.get('pos',''),x.get('form',''),'derived' if x.get('derivation') else 'root',x.get('derivation') or ''])

def update_daughter_lineage(pkg:Path, additions:list[dict], language_name:str):
    path=pkg/'lineage.csv'; rows=[]
    if path.exists():
        with path.open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    # Normalize older daughter packages to the new origin-aware schema.
    fields=['English','POS','Parent Form','Daughter Form','Status','Changes','Origin Language']
    existing={(r.get('English',''),r.get('POS','')) for r in rows}
    parent_origin=''
    try:
        data=json.loads((pkg/'language.json').read_text(encoding='utf-8'))
        parent_origin=str(data.get('lineage',{}).get('parent_name',''))
    except Exception: pass
    for r in rows:
        r.setdefault('Origin Language', parent_origin if r.get('Status')=='inherited' else language_name)
    for x in additions:
        key=(x['gloss'],x['pos'])
        if key not in existing:
            rows.append({'English':x['gloss'],'POS':x['pos'],'Parent Form':'','Daughter Form':x['form'],'Status':'innovated-here','Changes':'local lexical addition','Origin Language':language_name})
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in fields})
    md=pkg/'lineage.md'
    if md.exists() and additions:
        with md.open('a',encoding='utf-8') as f:
            f.write('\n## Local lexical innovations\n')
            for x in additions: f.write(f"- `{x['gloss']}:{x['pos']}` → `{x['form']}` (origin: {language_name})\n")

def append_paradigms(pkg:Path, additions:list[dict], grammar:dict):
    path=pkg/'paradigms.csv'; exists=path.exists()
    with path.open('a',encoding='utf-8',newline='') as f:
        w=csv.writer(f)
        if not exists: w.writerow(['English','POS','Lemma','Feature','Form'])
        for x in additions:
            gloss,pos,base=x['gloss'],x['pos'],x['form']
            if pos.startswith('n'):
                for num in grammar['noun']['numbers']:
                    for case in grammar['noun']['cases']: w.writerow([gloss,pos,base,f'{num}.{case}',noun_form(base,grammar,num,case)])
            elif pos=='v':
                people=PERSONS if grammar['verb']['agreement']!='none' else ['3sg']
                for mood in grammar['verb']['moods']:
                    for person in people:
                        if mood=='imperative' and person not in ('2sg','2pl','3sg'): continue
                        for tense in (grammar['verb']['tenses'] if mood=='indicative' else ['present']): w.writerow([gloss,pos,base,f'{mood}.{tense}.{person}',verb_form(base,grammar,person,tense,mood=mood)])
            elif pos=='adj':
                for degree in grammar['comparison']['degrees']: w.writerow([gloss,pos,base,degree,adjective_form(base,grammar,degree)])

def main(argv=None):
    root=Path(__file__).resolve().parent.parent
    p=argparse.ArgumentParser(description='Add new independent vocabulary roots to an existing language without regenerating it')
    p.add_argument('--language',required=True,type=Path,help='language.json or output/<Language> directory')
    p.add_argument('--words',required=True,type=Path,help='file containing gloss:pos entries, one per line')
    p.add_argument('--seed',type=int,default=None,help='seed for only the newly generated forms')
    p.add_argument('--project-root',type=Path,default=root)
    args=p.parse_args(argv); project=args.project_root.resolve()
    lang=resolve_language_path(project,args.language); words=resolve_project_path(project,args.words)
    if not lang.is_file(): p.error(f'language file not found: {lang}')
    if not words.is_file(): p.error(f'words file not found: {words}')
    try: data,grammar,entries,forms=load_language(lang); requested=parse_additions(words)
    except Exception as exc: p.error(str(exc))
    issues,_=validate_package(data,entries,forms)
    if issues: p.error('invalid language package: '+'; '.join(issues[:5]))
    existing={(str(x.get('gloss','')).strip(),str(x.get('pos','')).strip()) for x in data['lexicon']}
    seen=set(); todo=[]
    for item in requested:
        if item in existing:
            print(f'Skip existing: {item[0]}:{item[1]}')
        elif item in seen:
            print(f'Skip duplicate request: {item[0]}:{item[1]}')
        else: seen.add(item); todo.append(item)
    if not todo:
        print('No new words to add.'); return 0
    roots=[str(x.get('form','')).strip() for x in data['lexicon'] if not x.get('derivation') and str(x.get('form','')).strip()]
    if not roots: p.error('language contains no root forms from which to learn new word shapes')
    # Relearn the same two-character transition style from the existing language roots.
    corpus=' '.join(roots)
    with tempfile.TemporaryDirectory() as td:
        cp=Path(td)/'existing_roots.txt'; cp.write_text(corpus,encoding='utf-8')
        lc=load_lc_module(Path(__file__).with_name('lc.py')); rng=random.Random(args.seed)
        generated=[]; occupied={str(x.get('form','')).strip() for x in data['lexicon']}
        # Generate extra candidates because some may collide with existing forms.
        while len(generated)<len(todo):
            batch=generate_unique_roots(lc,cp,max(len(todo)*2,10),rng,3,7)
            for form in batch:
                if form not in occupied:
                    occupied.add(form); generated.append(form)
                    if len(generated)==len(todo): break
    additions=[]
    for (gloss,pos),form in zip(todo,generated):
        x={'gloss':gloss,'pos':pos,'form':form,'derivation':None}; data['lexicon'].append(x); additions.append(x)
    data['tool_version']='6.1'
    history=data.setdefault('lexicon_extensions',[])
    history.append({'source':str(words),'seed':args.seed,'count':len(additions),'origin_language':str(data.get('name',lang.parent.name)),'entries':[f"{x['gloss']}:{x['pos']}" for x in additions]})
    # Back up language.json before changing the package.
    backup=lang.with_suffix('.json.bak'); backup.write_bytes(lang.read_bytes())
    lang.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    pkg=lang.parent; is_daughter=bool(data.get('lineage'));
    if is_daughter: update_daughter_lineage(pkg,additions,str(data.get('name',pkg.name)))
    rewrite_dictionary(pkg,data['lexicon'],daughter=is_daughter); append_paradigms(pkg,additions,grammar)
    print(f'Language: {data.get("name",pkg.name)}'); print(f'Added: {len(additions)}')
    for x in additions: print(f"  {x['gloss']}:{x['pos']} = {x['form']}")
    print(f'Backup: {backup}'); print(f'Updated: {lang}'); return 0
if __name__=='__main__': raise SystemExit(main())
