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

def rewrite_dictionary(pkg:Path, lexicon:list[dict]):
    with (pkg/'dictionary.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['English','POS','Generated','Type','Derivation'])
        for x in lexicon: w.writerow([x.get('gloss',''),x.get('pos',''),x.get('form',''),'derived' if x.get('derivation') else 'root',x.get('derivation') or ''])

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
    data['tool_version']='5.7'
    history=data.setdefault('lexicon_extensions',[])
    history.append({'source':str(words),'seed':args.seed,'count':len(additions),'entries':[f"{x['gloss']}:{x['pos']}" for x in additions]})
    # Back up language.json before changing the package.
    backup=lang.with_suffix('.json.bak'); backup.write_bytes(lang.read_bytes())
    lang.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    pkg=lang.parent; rewrite_dictionary(pkg,data['lexicon']); append_paradigms(pkg,additions,grammar)
    print(f'Language: {data.get("name",pkg.name)}'); print(f'Added: {len(additions)}')
    for x in additions: print(f"  {x['gloss']}:{x['pos']} = {x['form']}")
    print(f'Backup: {backup}'); print(f'Updated: {lang}'); return 0
if __name__=='__main__': raise SystemExit(main())
