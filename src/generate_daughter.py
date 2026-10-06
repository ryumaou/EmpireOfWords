#!/usr/bin/env python3
"""Generate a historically descended daughter language from an Empire Of Words language package."""
from __future__ import annotations
import argparse, copy, csv, json, random, re, tempfile
from pathlib import Path
from types import SimpleNamespace

from language_io import resolve_language_path, resolve_project_path, load_language, validate_package, EntryKey
from build_language import generate_unique_roots, load_lc_module
from grammar_engine import write_package

PROFILES={
    'conservative': {'sound_rules':3,'lexical_replacement':0.02,'grammar_drift':0.10},
    'balanced': {'sound_rules':6,'lexical_replacement':0.06,'grammar_drift':0.25},
    'divergent': {'sound_rules':10,'lexical_replacement':0.12,'grammar_drift':0.45},
}

# Ordered, deliberately modest sound changes. A rule is eligible only when its source occurs.
RULES=[
 ('ai > e', r'ai', 'e'), ('au > o', r'au', 'o'), ('ei > i', r'ei', 'i'), ('ou > u', r'ou', 'u'),
 ('aa > a', r'aa', 'a'), ('ee > e', r'ee', 'e'), ('ii > i', r'ii', 'i'), ('oo > o', r'oo', 'o'), ('uu > u', r'uu', 'u'),
 ('ph > f', r'ph', 'f'), ('th > t', r'th', 't'), ('kh > k', r'kh', 'k'), ('gh > g', r'gh', 'g'),
 ('sh > s', r'sh', 's'), ('ch > sh', r'ch', 'sh'),
 ('intervocalic p > b', r'(?<=[aeiou])p(?=[aeiou])', 'b'),
 ('intervocalic t > d', r'(?<=[aeiou])t(?=[aeiou])', 'd'),
 ('intervocalic k > g', r'(?<=[aeiou])k(?=[aeiou])', 'g'),
 ('intervocalic s > z', r'(?<=[aeiou])s(?=[aeiou])', 'z'),
 ('initial w > v', r'^w', 'v'), ('initial y > j', r'^y', 'j'),
 ('final d > t', r'd$', 't'), ('final b > p', r'b$', 'p'), ('final g > k', r'g$', 'k'),
 ('final e loss', r'e$', ''), ('final a loss', r'a$', ''),
 ('unstressed-like medial vowel loss', r'(?<=[bcdfghjklmnpqrstvwxyz])[aeiou](?=[bcdfghjklmnpqrstvwxyz])', ''),
 ('nn > n', r'nn', 'n'), ('mm > m', r'mm', 'm'), ('ll > l', r'll', 'l'), ('rr > r', r'rr', 'r'),
]

def latin_letters(s): return ''.join(c for c in s.lower() if 'a'<=c<='z')

def choose_rules(forms,rng,count):
    candidates=[]
    sample=' '.join(forms)
    for rule in RULES:
        if re.search(rule[1],sample,re.I): candidates.append(rule)
    rng.shuffle(candidates)
    return candidates[:min(count,len(candidates))]

def evolve(form,rules,minimum=1):
    cur=form; applied=[]
    for label,pat,repl in rules:
        new=re.sub(pat,repl,cur,flags=re.I)
        if new!=cur:
            # Independent lexical words remain at least two visible Latin letters.
            if len(latin_letters(new))>=minimum:
                cur=new; applied.append(label)
    return cur,applied

def evolve_grammar(g,rules):
    g=copy.deepcopy(g)
    for spec in g.get('morphemes',{}).values():
        spec['form']=evolve(str(spec.get('form','')),rules,1)[0]
    for section in ('particles','pronouns','demonstratives','interrogatives'):
        for k,v in list(g.get(section,{}).items()): g[section][k]=evolve(str(v),rules,2)[0]
    return g

def drift_grammar(g,rng,chance):
    g=copy.deepcopy(g); changes=[]
    options=[
      ('word_order',['SVO','SOV','VSO','VOS','OVS','OSV']),
      ('adjective_position',['before','after']),
      ('possessor_position',['before','after']),
      ('adposition_type',['preposition','postposition']),
    ]
    for key,vals in options:
        if rng.random()<chance:
            old=g.get(key); choices=[x for x in vals if x!=old]
            if choices:
                new=rng.choice(choices); g[key]=new; changes.append(f'{key}: {old} > {new}')
    q=g.get('questions',{})
    if rng.random()<chance/2:
        old=q.get('wh_strategy'); new='fronted' if old=='in_situ' else 'in_situ'; q['wh_strategy']=new; changes.append(f'wh_strategy: {old} > {new}')
    if rng.random()<chance/2:
        old=q.get('particle_position'); new='final' if old=='initial' else 'initial'; q['particle_position']=new; changes.append(f'question particle position: {old} > {new}')
    return g,changes

def replace_roots(data, forms, rng, rate, srcdir):
    roots=[x for x in data['lexicon'] if not x.get('derivation') and x.get('form')]
    n=min(len(roots),round(len(roots)*rate))
    if n<=0:return set(),{}
    chosen=set(rng.sample(range(len(roots)),n)); corpus=' '.join(forms)
    lc=load_lc_module(srcdir/'lc.py'); replacements={}; occupied=set(forms)
    with tempfile.TemporaryDirectory() as td:
        cp=Path(td)/'daughter_roots.txt'; cp.write_text(corpus,encoding='utf-8')
        while len(replacements)<n:
            batch=generate_unique_roots(lc,cp,max(10,(n-len(replacements))*2),rng,3,7)
            for w in batch:
                if w not in occupied:
                    occupied.add(w); replacements[len(replacements)]=w
                    if len(replacements)==n:break
    return chosen,replacements

def main(argv=None):
    root=Path(__file__).resolve().parent.parent
    p=argparse.ArgumentParser(description='Generate a historically descended daughter language from an existing language package')
    p.add_argument('--parent',required=True,type=Path,help='parent language.json or output/<Parent> directory')
    p.add_argument('--language-name',required=True)
    p.add_argument('--profile',choices=PROFILES,default='balanced')
    p.add_argument('--seed',type=int,default=None)
    p.add_argument('--sound-rules',type=int,default=None,help='number of regular sound changes; overrides profile')
    p.add_argument('--lexical-replacement',type=float,default=None,help='fraction 0..1 of inherited root lexemes replaced by innovations')
    p.add_argument('--grammar-drift',type=float,default=None,help='probability 0..1 for each supported syntax drift')
    p.add_argument('--output',type=Path,default=None,help='daughter output directory; default output/<LanguageName>')
    p.add_argument('--project-root',type=Path,default=root)
    args=p.parse_args(argv); project=args.project_root.resolve(); rng=random.Random(args.seed)
    parent_path=resolve_language_path(project,args.parent)
    if not parent_path.is_file(): p.error(f'parent language not found: {parent_path}')
    data,grammar,entries,forms=load_language(parent_path); issues,_=validate_package(data,entries,forms)
    if issues:p.error('invalid parent language: '+'; '.join(issues[:5]))
    parent_origin={}
    parent_lineage=parent_path.parent/'lineage.csv'
    if parent_lineage.exists():
        with parent_lineage.open(encoding='utf-8',newline='') as f:
            for row in csv.DictReader(f):
                parent_origin[(row.get('English',''),row.get('POS',''))]=row.get('Origin Language','') or data.get('name',parent_path.parent.name)
    prof=PROFILES[args.profile]; nrules=args.sound_rules if args.sound_rules is not None else prof['sound_rules']
    repl=args.lexical_replacement if args.lexical_replacement is not None else prof['lexical_replacement']
    drift=args.grammar_drift if args.grammar_drift is not None else prof['grammar_drift']
    if nrules<0:p.error('--sound-rules must be >= 0')
    if not 0<=repl<=1:p.error('--lexical-replacement must be between 0 and 1')
    if not 0<=drift<=1:p.error('--grammar-drift must be between 0 and 1')
    parent_forms=[x.get('form','') for x in data['lexicon'] if x.get('form')]
    rules=choose_rules(parent_forms,rng,nrules)
    daughter_forms={}; history=[]
    for e in entries:
        old=forms.get(e.key,''); new,applied=evolve(old,rules,2); daughter_forms[e.key]=new
        history.append({'gloss':e.key.gloss,'pos':e.key.pos,'parent':old,'daughter':new,'changes':applied,'status':'inherited','origin_language':parent_origin.get((e.key.gloss,e.key.pos),data.get('name',parent_path.parent.name))})
    root_indices,replacements=replace_roots(data,list(daughter_forms.values()),rng,repl,Path(__file__).resolve().parent)
    roots=[x for x in data['lexicon'] if not x.get('derivation') and x.get('form')]
    root_key_order=[EntryKey(str(x['gloss']),str(x['pos'])) for x in roots]
    for j,idx in enumerate(sorted(root_indices)):
        key=root_key_order[idx]; old=daughter_forms[key]; daughter_forms[key]=replacements[j]
        for h in history:
            if h['gloss']==key.gloss and h['pos']==key.pos:
                h['pre_replacement']=old; h['daughter']=replacements[j]; h['status']='innovated'; h['origin_language']=args.language_name; h['changes'].append('lexical replacement'); break
    dgrammar=evolve_grammar(grammar,rules); dgrammar,grammar_changes=drift_grammar(dgrammar,rng,drift)
    # Evolve derivational affixes too, preserving their rule definitions.
    daff={}
    for name,spec in data.get('derivational_morphology',{}).items():
        daff[name]=SimpleNamespace(side=spec.get('side','suffix'),form=evolve(str(spec.get('form','')),rules,1)[0],source_rule=spec.get('source_rule',''))
    out=resolve_project_path(project,args.output) if args.output else project/'output'/args.language_name
    write_package(out,args.language_name,dgrammar,entries,daughter_forms,daff,args.seed)
    # Add lineage metadata to canonical package.
    lp=out/'language.json'; child=json.loads(lp.read_text(encoding='utf-8'))
    child['tool_version']='6.1'
    child['lineage']={'parent_name':data.get('name',parent_path.parent.name),'parent_path':str(parent_path),'parent_seed':data.get('seed'),'daughter_seed':args.seed,'profile':args.profile,'sound_changes':[r[0] for r in rules],'grammar_changes':grammar_changes,'lexical_replacement_rate':repl,'innovated_roots':len(root_indices)}
    lp.write_text(json.dumps(child,ensure_ascii=False,indent=2),encoding='utf-8')
    # Rewrite dictionary with ancestry columns.
    hist={(h['gloss'],h['pos']):h for h in history}
    with (out/'dictionary.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['English','POS','Generated','Type','Derivation','Parent Form','Inheritance','Sound Changes','Origin Language'])
        for e in entries:
            h=hist[(e.key.gloss,e.key.pos)]; w.writerow([e.key.gloss,e.key.pos,daughter_forms.get(e.key,''),'derived' if e.expr else 'root',e.expr or '',h['parent'],h['status'],'; '.join(h['changes']),h.get('origin_language','')])
    with (out/'lineage.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['English','POS','Parent Form','Daughter Form','Status','Changes','Origin Language'])
        for h in history:w.writerow([h['gloss'],h['pos'],h['parent'],h['daughter'],h['status'],'; '.join(h['changes']),h.get('origin_language','')])
    report=[f'# {args.language_name} — Lineage', '', f"Parent: **{data.get('name',parent_path.parent.name)}**",f'Profile: **{args.profile}**',f'Seed: `{args.seed}`','', '## Ordered sound changes']
    report += [f'{i}. {r[0]}' for i,r in enumerate(rules,1)] or ['No regular sound changes selected.']
    report += ['', '## Grammar changes'] + ([f'- {x}' for x in grammar_changes] or ['- No grammar drift selected.'])
    report += ['', '## Lexical inheritance',f'- Lexical replacement rate: {repl:.1%}',f'- Innovated root lexemes: {len(root_indices)}',f'- Total lexical entries: {len(entries)}','', 'See `lineage.csv` for word-by-word ancestry.','']
    (out/'lineage.md').write_text('\n'.join(report),encoding='utf-8')
    manifest={'language':args.language_name,'kind':'daughter','parent':str(parent_path),'parent_name':data.get('name'),'seed':args.seed,'profile':args.profile,'sound_changes':[r[0] for r in rules],'grammar_changes':grammar_changes,'lexical_replacement_rate':repl,'counts':{'entries':len(entries),'innovated_roots':len(root_indices)}}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Parent: {data.get("name",parent_path.parent.name)}'); print(f'Daughter: {args.language_name}'); print(f'Profile: {args.profile}'); print(f'Sound changes: {len(rules)}'); print(f'Grammar changes: {len(grammar_changes)}'); print(f'Innovated roots: {len(root_indices)}'); print(f'Output: {out}'); return 0

if __name__=='__main__': raise SystemExit(main())
