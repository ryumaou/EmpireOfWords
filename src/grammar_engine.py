#!/usr/bin/env python3
from __future__ import annotations
import csv, json, random
from pathlib import Path

VOWELS=set('aeiouy')

def join(a,b):
    if not a:return b
    if not b:return a
    return a+b[1:] if a[-1:]==b[:1] else a+b

def make_morpheme(pool,rng,used,minlen=1,maxlen=3):
    for _ in range(20000):
        w=rng.choice(pool); n=rng.randint(minlen,min(maxlen,len(w))); x=w[:n]
        if x and x not in used: used.add(x); return x
    raise RuntimeError('cannot create unique grammar morpheme')

def affix(form,spec): return join(spec['form'],form) if spec['side']=='prefix' else join(form,spec['form'])

def generate_grammar(root_pool,rng,mode='naturalistic'):
    used=set(); morph={}
    def M(name,sides=('suffix',),minlen=1,maxlen=3):
        morph[name]={'form':make_morpheme(root_pool,rng,used,minlen,maxlen),'side':rng.choice(list(sides))}; return morph[name]
    order=rng.choices(['SOV','SVO','VSO'],weights=[45,45,10])[0]
    post=(order=='SOV' and rng.random()<.8) or (order!='SOV' and rng.random()<.15)
    g={'mode':mode,'word_order':order,'adposition_type':'postposition' if post else 'preposition',
       'adjective_position':rng.choice(['before','after']),'possessor_position':rng.choices(['before','after'],[7,3])[0],
       'articles':rng.random()<.7,'noun':{'numbers':['singular','plural'],'cases':['nominative','accusative','genitive','dative']},
       'verb':{'tenses':['present','past','future'],'aspects':['simple','progressive'],
               'moods':['indicative','imperative','subjunctive','conditional'],'agreement':'subject person/number','negation':'affix'},
       'comparison':{'degrees':['positive','comparative','superlative']},'questions':{},'morphemes':morph}
    for n in ['plural','accusative','genitive','dative']: M(n)
    for n in ['past','future','progressive','negative','subjunctive','conditional']: M(n,('prefix','suffix'))
    M('imperative',('prefix','suffix')); M('comparative',('prefix','suffix')); M('superlative',('prefix','suffix'))
    if g['articles']: M('definite_article',('prefix','suffix')); M('indefinite_article',('prefix','suffix'))
    for p in ['1sg','2sg','3sg','1pl','2pl','3pl']: M('agr_'+p,('suffix',))
    available=[x for x in root_pool if len(x)>=2]; rng.shuffle(available)
    def word(): return available.pop()
    g['pronouns']={k:word() for k in ['1sg','2sg','3sg','1pl','2pl','3pl']}
    g['demonstratives']={'proximal_singular':word(),'distal_singular':word(),'proximal_plural':word(),'distal_plural':word()}
    g['interrogatives']={k:word() for k in ['who','what','where','when','why','how','which']}
    g['questions']={'yes_no_particle':word(),'particle_position':rng.choice(['initial','final']),
                    'wh_strategy':'in_situ' if rng.random()<.55 else 'fronted'}
    return g

def noun_form(word,g,number='singular',case='nominative'):
    if number=='plural': word=affix(word,g['morphemes']['plural'])
    if case!='nominative': word=affix(word,g['morphemes'][case])
    return word

def adjective_form(word,g,degree='positive'):
    return word if degree=='positive' else affix(word,g['morphemes'][degree])

def verb_form(word,g,person='3sg',tense='present',aspect='simple',mood='indicative',negative=False):
    m=g['morphemes']; x=word
    if tense!='present': x=affix(x,m[tense])
    if aspect=='progressive': x=affix(x,m['progressive'])
    if mood!='indicative': x=affix(x,m[mood])
    if negative: x=affix(x,m['negative'])
    x=affix(x,m['agr_'+person]); return x

def possessive_phrase(possessor, possessed, g):
    p=noun_form(possessor,g,case='genitive')
    return f'{p} {possessed}' if g['possessor_position']=='before' else f'{possessed} {p}'

def order_clause(s,v,o,g):
    return ' '.join({'SOV':[s,o,v],'SVO':[s,v,o],'VSO':[v,s,o]}[g['word_order']])

def generate_examples(g, entries, forms):
    by={}
    for e in entries:
        if e.key in forms: by.setdefault(e.key.gloss,forms[e.key])
    def L(*names):
        for n in names:
            if n in by:return by[n],n
        return None,None
    examples=[]
    warrior,wg=L('warrior'); dragon,dg=L('dragon'); kill,kg=L('kill')
    if warrior and dragon and kill:
        s=noun_form(warrior,g); o=noun_form(dragon,g,case='accusative'); v=verb_form(kill,g,'3sg','past')
        surface=order_clause(s,v,o,g); gloss=order_clause('warrior.NOM','kill-PST-3SG','dragon-ACC',g)
        examples.append(('Declarative','The warrior killed the dragon.',surface,gloss))
        q=g['questions']['yes_no_particle']; surface=(q+' '+surface) if g['questions']['particle_position']=='initial' else (surface+' '+q)
        examples.append(('Yes/no question','Did the warrior kill the dragon?',surface,gloss+' Q'))
    hunter,hg=L('hunter'); house,houseg=L('house');
    if hunter and house:
        examples.append(('Possession',"the hunter's house",possessive_phrase(hunter,house,g),'hunter-GEN house' if g['possessor_position']=='before' else 'house hunter-GEN'))
    big,bg=L('big');
    if big:
        examples.append(('Comparison','bigger / biggest',f"{adjective_form(big,g,'comparative')} / {adjective_form(big,g,'superlative')}",'big-CMPR / big-SUP'))
    see,sg=L('see'); who=g['interrogatives']['who']
    if see:
        v=verb_form(see,g,'2sg'); clause=f'{g["pronouns"]["2sg"]} {v} {who}'
        if g['questions']['wh_strategy']=='fronted': clause=f'{who} {g["pronouns"]["2sg"]} {v}'
        examples.append(('Wh-question','Who do you see?',clause,'who 2SG see-2SG'))
    go,gg=L('go')
    if go:
        for mood,eng in [('imperative','Go!'),('subjunctive','that he go'),('conditional','he would go')]:
            examples.append((mood.title(),eng,verb_form(go,g,'3sg' if mood!='imperative' else '2sg',mood=mood),f'go-{mood[:4].upper()}'))
    return examples

def write_package(outdir, language_name, grammar, entries, forms, deriv_affixes, seed):
    outdir.mkdir(parents=True,exist_ok=True)
    examples=generate_examples(grammar,entries,forms)
    data={'name':language_name,'seed':seed,'grammar':grammar,
      'derivational_morphology':{k:{'side':v.side,'form':v.form,'source_rule':v.source_rule} for k,v in deriv_affixes.items()},
      'lexicon':[{'gloss':e.key.gloss,'pos':e.key.pos,'form':forms.get(e.key,''),'derivation':e.expr} for e in entries],
      'examples':[{'type':t,'english':en,'surface':s,'gloss':gl} for t,en,s,gl in examples]}
    (outdir/'language.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    (outdir/'grammar.json').write_text(json.dumps(grammar,ensure_ascii=False,indent=2),encoding='utf-8')
    with (outdir/'paradigms.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['English','POS','Lemma','Feature','Form'])
        for e in entries:
            base=forms.get(e.key)
            if not base: continue
            if e.key.pos.startswith('n'):
                for num in grammar['noun']['numbers']:
                    for case in grammar['noun']['cases']: w.writerow([e.key.gloss,e.key.pos,base,f'{num}.{case}',noun_form(base,grammar,num,case)])
            elif e.key.pos=='v':
                for mood in grammar['verb']['moods']:
                    for person in ['1sg','2sg','3sg','1pl','2pl','3pl']:
                        if mood=='imperative' and person not in ('2sg','2pl'): continue
                        for tense in (grammar['verb']['tenses'] if mood=='indicative' else ['present']):
                            w.writerow([e.key.gloss,e.key.pos,base,f'{mood}.{tense}.{person}',verb_form(base,grammar,person,tense,mood=mood)])
            elif e.key.pos=='adj':
                for degree in grammar['comparison']['degrees']: w.writerow([e.key.gloss,e.key.pos,base,degree,adjective_form(base,grammar,degree)])
    with (outdir/'examples.txt').open('w',encoding='utf-8') as f:
        for t,en,s,gl in examples: f.write(f'[{t}]\nEnglish: {en}\nLanguage: {s}\nGloss: {gl}\n\n')
    ref=[f'# {language_name}','',f'Generation seed: `{seed}`','','## Syntax',f"- Basic word order: **{grammar['word_order']}**",f"- Adpositions: **{grammar['adposition_type']}s**",f"- Adjectives occur **{grammar['adjective_position']}** the noun.",f"- Possessors occur **{grammar['possessor_position']}** the possessed noun.",f"- Articles: **{'yes' if grammar['articles'] else 'no'}**",'', '## Nouns','- Number: singular and plural.','- Cases: nominative (unmarked), accusative, genitive, dative.','- Possession marks the possessor with genitive case.','', '## Verbs','- Subject agreement: 1st/2nd/3rd person × singular/plural.','- Tense: present, past, future.','- Aspect: simple and progressive.','- Moods: indicative, imperative, subjunctive, conditional.','- Negation is morphological.','', '## Comparison','- Positive, comparative, and superlative adjective forms.','', '## Questions',f"- Yes/no particle: **{grammar['questions']['yes_no_particle']}**, {grammar['questions']['particle_position']}-position.",f"- Wh-words: **{grammar['questions']['wh_strategy']}**.",'','## Demonstratives']
    for k,v in grammar['demonstratives'].items(): ref.append(f'- {k}: **{v}**')
    ref += ['', '## Interrogatives']
    for k,v in grammar['interrogatives'].items(): ref.append(f'- {k}: **{v}**')
    ref += ['', '## Pronouns']
    for k,v in grammar['pronouns'].items(): ref.append(f'- {k}: **{v}**')
    ref += ['', '## Inflectional Morphemes']
    for k,v in grammar['morphemes'].items(): ref.append(f"- {k}: **{v['form']+'-' if v['side']=='prefix' else '-'+v['form']}**")
    ref += ['', '## Generated Examples']
    for t,en,s,gl in examples: ref += [f'### {t}',f'- English: {en}',f'- Language: **{s}**',f'- Gloss: `{gl}`','']
    (outdir/'reference.md').write_text('\n'.join(ref)+'\n',encoding='utf-8')
