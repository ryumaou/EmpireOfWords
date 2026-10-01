#!/usr/bin/env python3
from __future__ import annotations
import json, random, re
from pathlib import Path

VOWELS=set('aeiouy')

def join(a,b):
    if not a:return b
    if not b:return a
    return a+b[1:] if a[-1:]==b[:1] else a+b

def make_morpheme(pool,rng,used):
    for _ in range(10000):
        w=rng.choice(pool)
        n=rng.choices([1,2,3],weights=[2,6,2],k=1)[0]
        x=w[:n]
        if x and x not in used:
            used.add(x); return x
    raise RuntimeError('cannot create unique grammar morpheme')

def affix(form, spec):
    return join(spec['form'],form) if spec['side']=='prefix' else join(form,spec['form'])

def generate_grammar(root_pool,rng,mode='naturalistic'):
    used=set(); morph={}
    def M(name, sides=('suffix',)):
        morph[name]={'form':make_morpheme(root_pool,rng,used),'side':rng.choice(list(sides))}
        return morph[name]
    # Weighted bundles avoid purely independent typological roulette.
    order=rng.choices(['SOV','SVO','VSO'],weights=[45,45,10])[0]
    post=(order=='SOV' and rng.random()<.8) or (order!='SOV' and rng.random()<.15)
    adj_after=rng.random() < (.35 if order=='SOV' else .65)
    grammar={
      'mode':mode,'word_order':order,
      'adposition_type':'postposition' if post else 'preposition',
      'adjective_position':'after' if adj_after else 'before',
      'possessor_position':'before' if rng.random()<.7 else 'after',
      'articles':rng.random()<.7,
      'noun':{'numbers':['singular','plural'],'cases':['nominative','accusative','genitive','dative']},
      'verb':{'tenses':['present','past','future'],'aspects':['simple','progressive'],'negation':'affix'},
      'morphemes':morph
    }
    M('plural'); M('accusative'); M('genitive'); M('dative')
    M('past',('prefix','suffix')); M('future',('prefix','suffix')); M('progressive',('prefix','suffix')); M('negative',('prefix','suffix'))
    if grammar['articles']:
        M('definite_article',('prefix','suffix')); M('indefinite_article',('prefix','suffix'))
    # pronouns are independent words: take full >=2-letter roots.
    available=[x for x in root_pool if len(x)>=2]
    rng.shuffle(available)
    grammar['pronouns']={k:available.pop() for k in ['1sg','2sg','3sg','1pl','2pl','3pl']}
    return grammar

def noun_forms(word,g):
    m=g['morphemes']; out={'singular':word,'plural':affix(word,m['plural'])}
    for c in ('accusative','genitive','dative'): out[c]=affix(word,m[c])
    return out

def verb_forms(word,g):
    m=g['morphemes']; return {'present':word,'past':affix(word,m['past']),'future':affix(word,m['future']),
      'progressive':affix(word,m['progressive']),'negative':affix(word,m['negative'])}

def write_package(outdir, language_name, grammar, entries, forms, deriv_affixes, seed):
    outdir.mkdir(parents=True,exist_ok=True)
    data={'name':language_name,'seed':seed,'grammar':grammar,
          'derivational_morphology':{k:{'side':v.side,'form':v.form,'source_rule':v.source_rule} for k,v in deriv_affixes.items()},
          'lexicon':[{'gloss':e.key.gloss,'pos':e.key.pos,'form':forms.get(e.key,''),'derivation':e.expr} for e in entries]}
    (outdir/'language.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (outdir/'grammar.json').write_text(json.dumps(grammar,ensure_ascii=False,indent=2),encoding='utf-8')
    with (outdir/'paradigms.csv').open('w',encoding='utf-8',newline='') as f:
        import csv
        w=csv.writer(f); w.writerow(['English','POS','Lemma','Feature','Form'])
        for e in entries:
            base=forms.get(e.key)
            if not base: continue
            table=noun_forms(base,grammar) if e.key.pos.startswith('n') else verb_forms(base,grammar) if e.key.pos=='v' else None
            if table:
                for feat,form in table.items(): w.writerow([e.key.gloss,e.key.pos,base,feat,form])
    ref=[]
    ref += [f'# {language_name}', '', f'Generation seed: `{seed}`', '', '## Syntax',
            f"- Basic word order: **{grammar['word_order']}**",
            f"- Adpositions: **{grammar['adposition_type']}s**",
            f"- Adjectives occur **{grammar['adjective_position']}** the noun.",
            f"- Possessors occur **{grammar['possessor_position']}** the possessed noun.",
            f"- Articles: **{'yes' if grammar['articles'] else 'no'}**", '', '## Nouns',
            '- Number: singular and plural.', '- Cases: nominative (unmarked), accusative, genitive, dative.', '', '## Verbs',
            '- Tense: present (unmarked), past, future.', '- Aspect: simple and progressive.', '- Negation is morphological.', '', '## Pronouns']
    for k,v in grammar['pronouns'].items(): ref.append(f'- {k}: **{v}**')
    ref += ['', '## Inflectional Morphemes']
    for k,v in grammar['morphemes'].items(): ref.append(f"- {k}: **{v['form']+'-' if v['side']=='prefix' else '-'+v['form']}**")
    (outdir/'reference.md').write_text('\n'.join(ref)+'\n',encoding='utf-8')
