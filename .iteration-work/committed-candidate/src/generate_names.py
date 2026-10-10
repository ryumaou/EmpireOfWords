#!/usr/bin/env python3
"""Generate proper names for an existing conlang package.

Personal names follow Christopher Pound's prop.pl idea: create a pool of
language-shaped forms, classify them as short/long by vowel count, and combine
one of each in randomized order. Family/clan names are semantic compounds from
NamingVocabulary-style formulas such as black+bear or dragon+hunter+castle.
"""
from __future__ import annotations
import argparse, csv, random, re, tempfile
from pathlib import Path
from language_io import resolve_project_path, resolve_language_path, load_language
from build_language import generate_unique_roots, load_lc_module, read_text
from grammar_engine import morphophonemic_join

VOWELS = set('aeiou')

def cap(s:str)->str:
    return s[:1].upper()+s[1:] if s else s

def vowel_count(s:str)->int:
    return sum(1 for ch in s.lower() if ch in VOWELS)

def load_formulas(path:Path)->list[tuple[str,list[str]]]:
    out=[]
    for no,raw in enumerate(read_text(path).splitlines(),1):
        line=raw.split('#',1)[0].strip()
        if not line: continue
        parts=[x.strip().lower() for x in line.split('+') if x.strip()]
        if len(parts)<2:
            raise ValueError(f'line {no}: expected a formula such as black+bear')
        out.append((line,parts))
    if not out: raise ValueError('naming vocabulary contains no usable formulas')
    return out

def gloss_index(data:dict)->dict[str,list[dict]]:
    idx={}
    for x in data.get('lexicon',[]):
        if not isinstance(x,dict): continue
        g=str(x.get('gloss','')).strip().lower(); f=str(x.get('form','')).strip()
        if g and f: idx.setdefault(g,[]).append(x)
    return idx

def find_form(term:str,idx:dict[str,list[dict]])->str|None:
    # Exact gloss first; then first parenthetical sense in vocabulary order.
    if term in idx: return str(idx[term][0].get('form','')).strip()
    for gloss,items in idx.items():
        base=re.sub(r'\s*\([^)]*\)\s*$','',gloss).strip()
        if base==term and items: return str(items[0].get('form','')).strip()
    return None

def compound(parts:list[str], idx:dict[str,list[dict]], grammar:dict)->tuple[str,list[str]]|None:
    forms=[]
    for p in parts:
        f=find_form(p,idx)
        if not f: return None
        forms.append(f)
    rules=grammar.get('morphophonemics',{}).get('rules',[])
    result=forms[0]
    # Treat later roots like suffixal compound members so boundary rules can
    # give family names the same phonological character as the language.
    for f in forms[1:]: result=morphophonemic_join(result,f,'suffix',rules)
    return result,forms

def personal_names(data:dict,count:int,rng:random.Random,cutoff:int,lc_path:Path)->list[dict]:
    roots=[str(x.get('form','')).strip().lower() for x in data.get('lexicon',[]) if isinstance(x,dict) and not x.get('derivation') and str(x.get('form','')).strip()]
    if not roots: raise ValueError('language contains no root forms for personal-name generation')
    with tempfile.TemporaryDirectory() as td:
        corpus=Path(td)/'roots.txt'; corpus.write_text(' '.join(roots),encoding='utf-8')
        lc=load_lc_module(lc_path)
        # prop.pl can discard excess short/long forms. Generate a generous pool,
        # then balance the two classes exactly as the original approach does.
        pool=[]; short=[]; long=[]; rounds=0
        while len(short)<count or len(long)<count:
            rounds+=1
            if rounds>12: break
            batch=generate_unique_roots(lc,corpus,max(count*8,40),rng,3,9)
            pool.extend(batch)
            short=[x for x in pool if vowel_count(x)<cutoff]
            long=[x for x in pool if vowel_count(x)>=cutoff]
        if len(short)<count or len(long)<count:
            raise ValueError(f'could not create enough short/long name elements with vowel cutoff {cutoff}; try --vowel-cutoff 2')
        rng.shuffle(short); rng.shuffle(long)
        rows=[]
        for a,b in zip(short[:count],long[:count]):
            first,last=(a,b) if rng.randrange(2) else (b,a)
            rows.append({'personal':f'{cap(first)} {cap(last)}','personal_parts':f'{first}+{last}'})
        return rows

def family_names(data:dict,grammar:dict,formulas:list[tuple[str,list[str]]],count:int,rng:random.Random)->tuple[list[dict],int]:
    idx=gloss_index(data); available=[]; unavailable=0
    for raw,parts in formulas:
        c=compound(parts,idx,grammar)
        if c is None: unavailable+=1; continue
        form,source_forms=c
        available.append({'family':cap(form),'formula':raw,'meaning':' '.join(parts),'source_forms':'+'.join(source_forms)})
    if not available: raise ValueError('none of the naming formulas can be built from this language lexicon')
    rng.shuffle(available)
    if count<=len(available): return available[:count],unavailable
    # Allow repeated formula selection only after every available formula has
    # appeared once; generated family forms themselves remain deterministic.
    out=list(available)
    while len(out)<count: out.append(dict(rng.choice(available)))
    return out,unavailable

def write_outputs(path:Path,language:str,mode:str,rows:list[dict],unavailable:int):
    path.parent.mkdir(parents=True,exist_ok=True)
    csv_path=path.with_suffix('.csv')
    fields=['full_name','personal_name','family_name','meaning','formula','personal_generation','family_source_forms']
    with csv_path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    with path.open('w',encoding='utf-8') as f:
        f.write(f'Proper names: {language}\n')
        f.write('='*60+'\n\n')
        for i,r in enumerate(rows,1):
            f.write(f'{i}. {r["full_name"]}\n')
            if r['personal_name']: f.write(f'   Personal name: {r["personal_name"]}\n   Personal generation: {r["personal_generation"]}\n')
            if r['family_name']: f.write(f'   Family name: {r["family_name"]}\n   Meaning: {r["meaning"]}\n   Formula: {r["formula"]}\n   Language roots: {r["family_source_forms"]}\n')
            f.write('\n')
        if mode in ('family','full','all'): f.write(f'Unavailable formulas (missing one or more lexical roots): {unavailable}\n')
    return path,csv_path

def main(argv=None):
    root=Path(__file__).resolve().parent.parent
    p=argparse.ArgumentParser(description='Generate language-shaped personal names and meaningful family/clan names')
    p.add_argument('--language',required=True,type=Path,help='language.json or output/<Language> directory')
    p.add_argument('--naming-vocabulary',type=Path,default=Path('vocabulary/NamingVocabulary.txt'),help='family-name formula file')
    p.add_argument('--mode',choices=['personal','family','full','all'],default='full')
    p.add_argument('--count',type=int,default=25)
    p.add_argument('--seed',type=int,default=None)
    p.add_argument('--vowel-cutoff',type=int,default=3,help='prop.pl short/long boundary; default 3 vowels')
    p.add_argument('--output',type=Path,default=None,help='text output path; CSV is written beside it')
    p.add_argument('--project-root',type=Path,default=root)
    args=p.parse_args(argv)
    if args.count<1: p.error('--count must be at least 1')
    project=args.project_root.resolve(); lang=resolve_language_path(project,args.language)
    if not lang.is_file(): p.error(f'language file not found: {lang}')
    try: data,grammar,entries,forms=load_language(lang)
    except Exception as exc: p.error(str(exc))
    rng=random.Random(args.seed); lname=str(data.get('name') or lang.parent.name)
    formulas=[]
    if args.mode in ('family','full','all'):
        nv=resolve_project_path(project,args.naming_vocabulary)
        if not nv.is_file(): p.error(f'naming vocabulary not found: {nv}')
        try: formulas=load_formulas(nv)
        except Exception as exc: p.error(str(exc))
    personals=[]; families=[]; unavailable=0
    try:
        if args.mode in ('personal','full','all'): personals=personal_names(data,args.count,rng,args.vowel_cutoff,Path(__file__).with_name('lc.py'))
        if args.mode in ('family','full','all'): families,unavailable=family_names(data,grammar,formulas,args.count,rng)
    except Exception as exc: p.error(str(exc))
    rows=[]
    for i in range(args.count):
        pr=personals[i] if personals else {}; fr=families[i] if families else {}
        personal=pr.get('personal',''); family=fr.get('family','')
        full=' '.join(x for x in (personal,family) if x)
        rows.append({'full_name':full,'personal_name':personal,'family_name':family,'meaning':fr.get('meaning',''),'formula':fr.get('formula',''),'personal_generation':pr.get('personal_parts',''),'family_source_forms':fr.get('source_forms','')})
    out=resolve_project_path(project,args.output) if args.output else lang.parent/'names'/f'names_{args.mode}.txt'
    txt,csvp=write_outputs(out,lname,args.mode,rows,unavailable)
    print(f'Language: {lname}'); print(f'Mode: {args.mode}'); print(f'Names: {len(rows)}')
    if formulas: print(f'Naming formulas: {len(formulas)}; unavailable for this lexicon: {unavailable}')
    print(f'Text: {txt}'); print(f'CSV: {csvp}')
    return 0
if __name__=='__main__': raise SystemExit(main())
