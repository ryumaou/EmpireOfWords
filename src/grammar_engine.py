#!/usr/bin/env python3
from __future__ import annotations
import csv, json, random
from pathlib import Path

VOWELS=set('aeiouy')
PERSONS=['1sg','2sg','3sg','1pl','2pl','3pl']
ALL_CASES=['nominative','accusative','genitive','dative','instrumental','locative','ablative','vocative']

FAMILIES={
'naturalistic': {'base':['romance','germanic','slavic','arabic','turkic','japanese','celtic','latin','greek','indic','bantu','polynesian','analytic','agglutinative','fusional','isolating']},
'random': {},
'romance': {'orders':{'SVO':90,'SOV':5,'VSO':5},'adj':{'after':75,'before':25},'adp':{'preposition':95,'postposition':5},'poss':{'after':75,'before':25},'gender':[2,3],'cases':[0,0,0,2,3],'articles':['both'],'agreement':['subject'],'tense':['standard','rich'],'aspect':['standard'],'mood':['standard','rich'],'morphology':['fusional','mixed'],'questions':['word-order','mixed'],'negation':['particle'],'plural':['suffix','mixed'],'comparison':['affix','mixed']},
'germanic': {'orders':{'SVO':85,'SOV':15},'adj':{'before':85,'after':15},'adp':{'preposition':95,'postposition':5},'poss':{'before':70,'after':30},'gender':[0,2,3],'cases':[0,2,4],'articles':['both'],'agreement':['subject'],'tense':['standard'],'aspect':['minimal','standard'],'mood':['standard'],'morphology':['fusional','mixed'],'questions':['word-order','verb','mixed'],'negation':['particle'],'plural':['suffix','mixed'],'comparison':['affix','mixed']},
'slavic': {'orders':{'SVO':60,'SOV':25,'VSO':15},'adj':{'before':80,'after':20},'adp':{'preposition':95,'postposition':5},'poss':{'before':65,'after':35},'gender':[3],'cases':[6,7],'articles':['none'],'agreement':['subject'],'tense':['standard'],'aspect':['rich'],'mood':['standard'],'morphology':['fusional'],'questions':['mixed','word-order'],'negation':['particle'],'plural':['suffix','mixed'],'comparison':['affix','mixed']},
'arabic': {'orders':{'VSO':55,'SVO':40,'SOV':5},'adj':{'after':95,'before':5},'adp':{'preposition':98,'postposition':2},'poss':{'after':90,'before':10},'gender':[2],'cases':[0,3],'articles':['definite'],'agreement':['subject'],'tense':['minimal','standard'],'aspect':['rich'],'mood':['standard','rich'],'morphology':['fusional','mixed'],'questions':['particle','mixed'],'negation':['particle','mixed'],'plural':['mixed'],'comparison':['mixed']},
'turkic': {'orders':{'SOV':98,'SVO':2},'adj':{'before':95,'after':5},'adp':{'postposition':98,'preposition':2},'poss':{'before':95,'after':5},'gender':[0],'cases':[6,7,8],'articles':['none'],'agreement':['subject'],'tense':['rich'],'aspect':['standard','rich'],'mood':['rich'],'morphology':['agglutinative'],'questions':['particle'],'negation':['affix'],'plural':['suffix'],'comparison':['affix','particle']},
'japanese': {'orders':{'SOV':99,'SVO':1},'adj':{'before':98,'after':2},'adp':{'postposition':100},'poss':{'before':100},'gender':[0],'cases':[4,5,6],'articles':['none'],'agreement':['none'],'tense':['minimal','standard'],'aspect':['standard'],'mood':['standard'],'morphology':['agglutinative','mixed'],'questions':['particle'],'negation':['affix'],'plural':['none','suffix'],'comparison':['particle']},
'celtic': {'orders':{'VSO':85,'SVO':15},'adj':{'after':85,'before':15},'adp':{'preposition':95,'postposition':5},'poss':{'before':55,'after':45},'gender':[2],'cases':[0,2,3],'articles':['definite','both'],'agreement':['subject'],'tense':['standard'],'aspect':['standard'],'mood':['standard'],'morphology':['fusional','mixed'],'questions':['particle','verb'],'negation':['particle'],'plural':['mixed','suffix'],'comparison':['particle','mixed']},
'latin': {'orders':{'SOV':65,'SVO':25,'VSO':10},'adj':{'after':60,'before':40},'adp':{'preposition':95,'postposition':5},'poss':{'after':70,'before':30},'gender':[3],'cases':[6,7],'articles':['none'],'agreement':['subject'],'tense':['rich'],'aspect':['rich'],'mood':['rich'],'morphology':['fusional'],'questions':['particle','mixed'],'negation':['particle'],'plural':['mixed'],'comparison':['affix']},
'greek': {'orders':{'SVO':65,'SOV':20,'VSO':15},'adj':{'before':60,'after':40},'adp':{'preposition':98,'postposition':2},'poss':{'after':70,'before':30},'gender':[3],'cases':[4,5],'articles':['definite','both'],'agreement':['subject'],'tense':['rich'],'aspect':['rich'],'mood':['rich'],'morphology':['fusional'],'questions':['particle','mixed'],'negation':['particle'],'plural':['mixed'],'comparison':['affix','mixed']},
'indic': {'orders':{'SOV':95,'SVO':5},'adj':{'before':85,'after':15},'adp':{'postposition':98,'preposition':2},'poss':{'before':90,'after':10},'gender':[0,2,3],'cases':[3,4,5],'articles':['none','both'],'agreement':['subject'],'tense':['standard'],'aspect':['rich'],'mood':['standard'],'morphology':['fusional','mixed'],'questions':['particle','mixed'],'negation':['particle'],'plural':['suffix','mixed'],'comparison':['particle','mixed']},
'bantu': {'orders':{'SVO':98,'SOV':2},'adj':{'after':85,'before':15},'adp':{'preposition':85,'postposition':15},'poss':{'after':80,'before':20},'gender':['classes'],'cases':[0],'articles':['none'],'agreement':['subject-object'],'tense':['rich'],'aspect':['rich'],'mood':['rich'],'morphology':['agglutinative'],'questions':['particle','mixed'],'negation':['affix','mixed'],'plural':['prefix','mixed'],'comparison':['particle']},
'polynesian': {'orders':{'VSO':60,'VOS':30,'SVO':10},'adj':{'after':90,'before':10},'adp':{'preposition':95,'postposition':5},'poss':{'after':65,'before':35},'gender':[0],'cases':[0],'articles':['both','definite'],'agreement':['none'],'tense':['minimal'],'aspect':['standard'],'mood':['standard'],'morphology':['analytic','isolating'],'questions':['particle'],'negation':['particle'],'plural':['none','mixed'],'comparison':['particle']},
'analytic': {'orders':{'SVO':80,'SOV':10,'VSO':10},'adj':{'before':50,'after':50},'adp':{'preposition':80,'postposition':20},'poss':{'before':60,'after':40},'gender':[0],'cases':[0],'articles':['both','none'],'agreement':['none'],'tense':['minimal'],'aspect':['standard'],'mood':['minimal','standard'],'morphology':['analytic'],'questions':['particle','word-order'],'negation':['particle'],'plural':['none','mixed'],'comparison':['particle']},
'agglutinative': {'orders':{'SOV':80,'SVO':15,'VSO':5},'adj':{'before':80,'after':20},'adp':{'postposition':85,'preposition':15},'poss':{'before':85,'after':15},'gender':[0,2],'cases':[4,5,6,7,8],'articles':['none'],'agreement':['subject','subject-object'],'tense':['standard','rich'],'aspect':['standard','rich'],'mood':['standard','rich'],'morphology':['agglutinative'],'questions':['particle'],'negation':['affix'],'plural':['suffix'],'comparison':['affix','particle']},
'fusional': {'orders':{'SVO':45,'SOV':40,'VSO':15},'adj':{'before':50,'after':50},'adp':{'preposition':90,'postposition':10},'poss':{'before':40,'after':60},'gender':[2,3],'cases':[3,4,5,6,7],'articles':['none','both'],'agreement':['subject'],'tense':['standard','rich'],'aspect':['standard','rich'],'mood':['standard','rich'],'morphology':['fusional'],'questions':['mixed','particle'],'negation':['particle'],'plural':['mixed'],'comparison':['affix','mixed']},
'isolating': {'orders':{'SVO':75,'SOV':15,'VSO':10},'adj':{'before':55,'after':45},'adp':{'preposition':85,'postposition':15},'poss':{'before':65,'after':35},'gender':[0],'cases':[0],'articles':['none','both'],'agreement':['none'],'tense':['minimal'],'aspect':['minimal','standard'],'mood':['minimal'],'morphology':['isolating'],'questions':['particle','word-order'],'negation':['particle'],'plural':['none'],'comparison':['particle']},
}

def _weighted(rng,d):
    return rng.choices(list(d),weights=list(d.values()))[0]
def _pick(rng,x): return rng.choice(x)
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

def _feature_levels(level, minimal, standard, rich): return {'minimal':minimal,'standard':standard,'rich':rich}[level]

def generate_grammar(root_pool,rng,family='naturalistic',overrides=None):
    overrides=overrides or {}
    requested=family
    if family=='naturalistic': family=rng.choice(FAMILIES['naturalistic']['base'])
    if family not in FAMILIES: raise ValueError(f'unknown grammar family: {family}')
    p=FAMILIES[family]
    if family=='random':
        p={'orders':{x:1 for x in ['SVO','SOV','VSO','VOS','OVS','OSV']},'adj':{'before':1,'after':1},'adp':{'preposition':1,'postposition':1},'poss':{'before':1,'after':1},'gender':[0,2,3,'classes'],'cases':list(range(9)),'articles':['none','definite','indefinite','both'],'agreement':['none','subject','subject-object'],'tense':['minimal','standard','rich'],'aspect':['minimal','standard','rich'],'mood':['minimal','standard','rich'],'morphology':['analytic','agglutinative','fusional','mixed','isolating'],'questions':['particle','word-order','verb','mixed'],'negation':['particle','affix','mixed'],'plural':['none','suffix','prefix','mixed'],'comparison':['particle','affix','mixed']}
    val=lambda key, chooser: overrides.get(key,chooser())
    order=val('word_order',lambda:_weighted(rng,p['orders']))
    adj=val('adjective_position',lambda:_weighted(rng,p['adj']))
    adp=val('adposition',lambda:_weighted(rng,p['adp']))
    poss=val('possession',lambda:_weighted(rng,p['poss']))
    gender=val('gender',lambda:_pick(rng,p['gender']))
    case_count=int(val('cases',lambda:_pick(rng,p['cases'])))
    articles=val('articles',lambda:_pick(rng,p['articles']))
    agreement=val('agreement',lambda:_pick(rng,p['agreement']))
    tense_level=val('tense',lambda:_pick(rng,p['tense']))
    aspect_level=val('aspect',lambda:_pick(rng,p['aspect']))
    mood_level=val('mood',lambda:_pick(rng,p['mood']))
    morphology=val('morphology',lambda:_pick(rng,p['morphology']))
    qtype=val('questions',lambda:_pick(rng,p['questions']))
    negation=val('negation',lambda:_pick(rng,p['negation']))
    plural=val('plural',lambda:_pick(rng,p['plural']))
    comparison=val('comparison',lambda:_pick(rng,p['comparison']))
    cases=ALL_CASES[:case_count] if case_count else ['nominative']
    tenses=_feature_levels(tense_level,['present'],['present','past','future'],['present','past','future','remote_past'])
    aspects=_feature_levels(aspect_level,['simple'],['simple','progressive'],['simple','progressive','perfect'])
    moods=_feature_levels(mood_level,['indicative','imperative'],['indicative','imperative','subjunctive','conditional'],['indicative','imperative','subjunctive','conditional','optative'])
    used=set(); morph={}
    def M(name,sides=('suffix',),minlen=1,maxlen=3):
        morph[name]={'form':make_morpheme(root_pool,rng,used,minlen,maxlen),'side':rng.choice(list(sides))}; return morph[name]
    affix_sides=('suffix',) if morphology=='agglutinative' else ('prefix','suffix')
    if plural!='none': M('plural',('prefix',) if plural=='prefix' else affix_sides)
    for c in cases:
        if c!='nominative': M(c,affix_sides)
    for x in tenses:
        if x!='present': M(x,affix_sides)
    for x in aspects:
        if x!='simple': M(x,affix_sides)
    for x in moods:
        if x!='indicative': M(x,affix_sides)
    if negation!='particle': M('negative',affix_sides)
    if comparison!='particle': M('comparative',affix_sides); M('superlative',affix_sides)
    if articles in ('definite','both'): M('definite_article',('prefix','suffix'))
    if articles in ('indefinite','both'): M('indefinite_article',('prefix','suffix'))
    if agreement!='none':
        for person in PERSONS: M('agr_'+person,('suffix',))
    available=[x for x in root_pool if len(x)>=2]; rng.shuffle(available)
    def word():
        if not available: raise RuntimeError('not enough grammar words in root pool')
        return available.pop()
    pronouns={k:word() for k in PERSONS}
    demonstratives={k:word() for k in ['proximal_singular','distal_singular','proximal_plural','distal_plural']}
    interrogatives={k:word() for k in ['who','what','where','when','why','how','which']}
    particles={}
    if qtype in ('particle','mixed'): particles['yes_no']=word()
    if negation in ('particle','mixed'): particles['negative']=word()
    if comparison in ('particle','mixed'): particles['comparative']=word(); particles['superlative']=word()
    g={'family':family,'requested_family':requested,'word_order':order,'adposition_type':adp,'adjective_position':adj,'possessor_position':poss,
       'articles':articles,'gender':gender,'morphology_type':morphology,
       'noun':{'numbers':['singular']+([] if plural=='none' else ['plural']),'plural_strategy':plural,'cases':cases},
       'verb':{'tenses':tenses,'tense_level':tense_level,'aspects':aspects,'aspect_level':aspect_level,'moods':moods,'mood_level':mood_level,'agreement':agreement,'negation':negation},
       'comparison':{'degrees':['positive','comparative','superlative'],'strategy':comparison},
       'questions':{'strategy':qtype,'particle_position':rng.choice(['initial','final']),'wh_strategy':'in_situ' if rng.random()<.55 else 'fronted'},
       'morphemes':morph,'particles':particles,'pronouns':pronouns,'demonstratives':demonstratives,'interrogatives':interrogatives}
    return g

def load_grammar(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def noun_form(word,g,number='singular',case='nominative'):
    if number=='plural' and 'plural' in g['morphemes']: word=affix(word,g['morphemes']['plural'])
    if case!='nominative' and case in g['morphemes']: word=affix(word,g['morphemes'][case])
    return word

def adjective_form(word,g,degree='positive'):
    if degree=='positive': return word
    if degree in g['morphemes']: return affix(word,g['morphemes'][degree])
    particle=g.get('particles',{}).get(degree); return f'{particle} {word}' if particle else word

def verb_form(word,g,person='3sg',tense='present',aspect='simple',mood='indicative',negative=False):
    m=g['morphemes']; x=word
    for feature in (tense,aspect,mood):
        if feature not in ('present','simple','indicative') and feature in m: x=affix(x,m[feature])
    if negative:
        if 'negative' in m: x=affix(x,m['negative'])
        elif g.get('particles',{}).get('negative'): x=g['particles']['negative']+' '+x
    if 'agr_'+person in m: x=affix(x,m['agr_'+person])
    return x

def possessive_phrase(possessor, possessed, g):
    p=noun_form(possessor,g,case='genitive') if 'genitive' in g['noun']['cases'] else possessor
    return f'{p} {possessed}' if g['possessor_position']=='before' else f'{possessed} {p}'

def order_clause(s,v,o,g):
    return ' '.join({'SOV':[s,o,v],'SVO':[s,v,o],'VSO':[v,s,o],'VOS':[v,o,s],'OVS':[o,v,s],'OSV':[o,s,v]}[g['word_order']])

def generate_examples(g, entries, forms):
    by={}
    for e in entries:
        if e.key in forms: by.setdefault(e.key.gloss,forms[e.key])
    def L(*names):
        for n in names:
            if n in by:return by[n],n
        return None,None
    examples=[]; warrior,_=L('warrior'); dragon,_=L('dragon'); kill,_=L('kill')
    if warrior and dragon and kill:
        s=noun_form(warrior,g); o=noun_form(dragon,g,case='accusative'); v=verb_form(kill,g,'3sg','past' if 'past' in g['verb']['tenses'] else 'present')
        surface=order_clause(s,v,o,g); gloss=order_clause('warrior.NOM','kill-PST-3SG','dragon-ACC',g)
        examples.append(('Declarative','The warrior killed the dragon.',surface,gloss))
        q=g.get('particles',{}).get('yes_no')
        if q: surface=(q+' '+surface) if g['questions']['particle_position']=='initial' else (surface+' '+q)
        examples.append(('Yes/no question','Did the warrior kill the dragon?',surface,gloss+(' Q' if q else ' ?')))
    hunter,_=L('hunter'); house,_=L('house')
    if hunter and house: examples.append(('Possession',"the hunter's house",possessive_phrase(hunter,house,g),'hunter-GEN house' if g['possessor_position']=='before' else 'house hunter-GEN'))
    big,_=L('big')
    if big: examples.append(('Comparison','bigger / biggest',f"{adjective_form(big,g,'comparative')} / {adjective_form(big,g,'superlative')}",'big-CMPR / big-SUP'))
    see,_=L('see'); who=g['interrogatives']['who']
    if see:
        v=verb_form(see,g,'2sg'); clause=f'{g["pronouns"]["2sg"]} {v} {who}'
        if g['questions']['wh_strategy']=='fronted': clause=f'{who} {g["pronouns"]["2sg"]} {v}'
        examples.append(('Wh-question','Who do you see?',clause,'who 2SG see-2SG'))
    go,_=L('go')
    if go:
        for mood,eng in [('imperative','Go!'),('subjunctive','that he go'),('conditional','he would go')]:
            if mood in g['verb']['moods']: examples.append((mood.title(),eng,verb_form(go,g,'3sg' if mood!='imperative' else '2sg',mood=mood),f'go-{mood[:4].upper()}'))
    return examples

def write_package(outdir, language_name, grammar, entries, forms, deriv_affixes, seed):
    outdir.mkdir(parents=True,exist_ok=True); examples=generate_examples(grammar,entries,forms)
    data={'name':language_name,'seed':seed,'grammar':grammar,'derivational_morphology':{k:{'side':v.side,'form':v.form,'source_rule':v.source_rule} for k,v in deriv_affixes.items()},'lexicon':[{'gloss':e.key.gloss,'pos':e.key.pos,'form':forms.get(e.key,''),'derivation':e.expr} for e in entries],'examples':[{'type':t,'english':en,'surface':s,'gloss':gl} for t,en,s,gl in examples]}
    (outdir/'language.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); (outdir/'grammar.json').write_text(json.dumps(grammar,ensure_ascii=False,indent=2),encoding='utf-8')
    with (outdir/'paradigms.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f); w.writerow(['English','POS','Lemma','Feature','Form'])
        for e in entries:
            base=forms.get(e.key)
            if not base: continue
            if e.key.pos.startswith('n'):
                for num in grammar['noun']['numbers']:
                    for case in grammar['noun']['cases']: w.writerow([e.key.gloss,e.key.pos,base,f'{num}.{case}',noun_form(base,grammar,num,case)])
            elif e.key.pos=='v':
                people=PERSONS if grammar['verb']['agreement']!='none' else ['3sg']
                for mood in grammar['verb']['moods']:
                    for person in people:
                        if mood=='imperative' and person not in ('2sg','2pl','3sg'): continue
                        for tense in (grammar['verb']['tenses'] if mood=='indicative' else ['present']): w.writerow([e.key.gloss,e.key.pos,base,f'{mood}.{tense}.{person}',verb_form(base,grammar,person,tense,mood=mood)])
            elif e.key.pos=='adj':
                for degree in grammar['comparison']['degrees']: w.writerow([e.key.gloss,e.key.pos,base,degree,adjective_form(base,grammar,degree)])
    with (outdir/'examples.txt').open('w',encoding='utf-8') as f:
        for t,en,s,gl in examples: f.write(f'[{t}]\nEnglish: {en}\nLanguage: {s}\nGloss: {gl}\n\n')
    ref=[f'# {language_name}','',f'Generation seed: `{seed}`',f"Grammar family: **{grammar['family']}**",f"Morphology type: **{grammar['morphology_type']}**",'', '## Syntax',f"- Basic word order: **{grammar['word_order']}**",f"- Adpositions: **{grammar['adposition_type']}s**",f"- Adjectives occur **{grammar['adjective_position']}** the noun.",f"- Possessors occur **{grammar['possessor_position']}** the possessed noun.",f"- Articles: **{grammar['articles']}**",f"- Gender/classes: **{grammar['gender']}**",'', '## Nouns',f"- Number strategy: **{grammar['noun']['plural_strategy']}**.",f"- Cases: {', '.join(grammar['noun']['cases'])}.",'', '## Verbs',f"- Agreement: **{grammar['verb']['agreement']}**.",f"- Tense: {', '.join(grammar['verb']['tenses'])}.",f"- Aspect: {', '.join(grammar['verb']['aspects'])}.",f"- Moods: {', '.join(grammar['verb']['moods'])}.",f"- Negation: **{grammar['verb']['negation']}**.",'', '## Comparison',f"- Strategy: **{grammar['comparison']['strategy']}**.",'', '## Questions',f"- Strategy: **{grammar['questions']['strategy']}**.",f"- Wh-words: **{grammar['questions']['wh_strategy']}**.",'','## Demonstratives']
    for k,v in grammar['demonstratives'].items(): ref.append(f'- {k}: **{v}**')
    ref += ['', '## Interrogatives']; [ref.append(f'- {k}: **{v}**') for k,v in grammar['interrogatives'].items()]
    ref += ['', '## Pronouns']; [ref.append(f'- {k}: **{v}**') for k,v in grammar['pronouns'].items()]
    ref += ['', '## Inflectional Morphemes']; [ref.append(f"- {k}: **{v['form']+'-' if v['side']=='prefix' else '-'+v['form']}**") for k,v in grammar['morphemes'].items()]
    ref += ['', '## Particles']; [ref.append(f'- {k}: **{v}**') for k,v in grammar.get('particles',{}).items()]
    ref += ['', '## Generated Examples']
    for t,en,s,gl in examples: ref += [f'### {t}',f'- English: {en}',f'- Language: **{s}**',f'- Gloss: `{gl}`','']
    (outdir/'reference.md').write_text('\n'.join(ref)+'\n',encoding='utf-8')
