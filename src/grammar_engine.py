#!/usr/bin/env python3
from __future__ import annotations
import csv, json, random, re
from pathlib import Path

VOWELS=set('aeiouy')
PERSONS=['1sg','2sg','3sg','1pl','2pl','3pl']
ALL_CASES=['nominative','accusative','genitive','dative','instrumental','locative','ablative','vocative']

FAMILIES={
'naturalistic': {'base':['romance','germanic','slavic','arabic','semitic','turkic','uralic','japanese','celtic','latin','greek','indic','dravidian','iranian','bantu','austronesian','polynesian','kartvelian','caucasian','sino-tibetan','berber','quechuan','analytic','agglutinative','fusional','isolating']},
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
'semitic': {'orders':{'VSO':50,'SVO':45,'SOV':5},'adj':{'after':90,'before':10},'adp':{'preposition':98,'postposition':2},'poss':{'after':90,'before':10},'gender':[2],'cases':[0,2,3],'articles':['definite','both'],'agreement':['subject','subject-object'],'tense':['minimal','standard'],'aspect':['rich'],'mood':['standard','rich'],'morphology':['fusional','mixed'],'questions':['particle','mixed'],'negation':['particle','mixed'],'plural':['mixed'],'comparison':['mixed','particle']},
'uralic': {'orders':{'SOV':60,'SVO':35,'VSO':5},'adj':{'before':90,'after':10},'adp':{'postposition':95,'preposition':5},'poss':{'before':90,'after':10},'gender':[0],'cases':[6,7,8],'articles':['none','definite'],'agreement':['subject'],'tense':['standard','rich'],'aspect':['standard'],'mood':['rich'],'morphology':['agglutinative'],'questions':['particle'],'negation':['affix','mixed'],'plural':['suffix'],'comparison':['affix','particle']},
'kartvelian': {'orders':{'SOV':55,'SVO':40,'VSO':5},'adj':{'before':65,'after':35},'adp':{'postposition':90,'preposition':10},'poss':{'before':85,'after':15},'gender':[0],'cases':[6,7],'articles':['none'],'agreement':['subject-object'],'tense':['rich'],'aspect':['rich'],'mood':['rich'],'morphology':['agglutinative','mixed'],'questions':['particle','mixed'],'negation':['particle','affix'],'plural':['suffix'],'comparison':['particle','affix']},
'caucasian': {'orders':{'SOV':75,'SVO':20,'VSO':5},'adj':{'before':75,'after':25},'adp':{'postposition':90,'preposition':10},'poss':{'before':90,'after':10},'gender':[0,'classes'],'cases':[7,8],'articles':['none'],'agreement':['subject-object','subject'],'tense':['standard','rich'],'aspect':['rich'],'mood':['rich'],'morphology':['agglutinative','mixed'],'questions':['particle'],'negation':['affix','particle'],'plural':['suffix'],'comparison':['particle','affix']},
'austronesian': {'orders':{'VSO':35,'VOS':30,'SVO':30,'SOV':5},'adj':{'after':70,'before':30},'adp':{'preposition':90,'postposition':10},'poss':{'after':65,'before':35},'gender':[0],'cases':[0,2],'articles':['both','definite','none'],'agreement':['none','subject'],'tense':['minimal'],'aspect':['standard','rich'],'mood':['standard'],'morphology':['agglutinative','analytic','mixed'],'questions':['particle'],'negation':['particle'],'plural':['none','mixed','prefix'],'comparison':['particle']},
'dravidian': {'orders':{'SOV':98,'SVO':2},'adj':{'before':95,'after':5},'adp':{'postposition':99,'preposition':1},'poss':{'before':98,'after':2},'gender':[0,2,3],'cases':[6,7,8],'articles':['none'],'agreement':['subject'],'tense':['standard','rich'],'aspect':['standard'],'mood':['rich'],'morphology':['agglutinative'],'questions':['particle'],'negation':['affix','mixed'],'plural':['suffix'],'comparison':['particle','affix']},
'iranian': {'orders':{'SOV':90,'SVO':10},'adj':{'after':75,'before':25},'adp':{'preposition':75,'postposition':25},'poss':{'after':80,'before':20},'gender':[0,2],'cases':[0,2,3],'articles':['none','both'],'agreement':['subject'],'tense':['standard','rich'],'aspect':['standard','rich'],'mood':['standard','rich'],'morphology':['fusional','mixed'],'questions':['particle','mixed'],'negation':['affix','particle'],'plural':['suffix','mixed'],'comparison':['affix','particle']},
'sino-tibetan': {'orders':{'SVO':55,'SOV':40,'VSO':5},'adj':{'before':75,'after':25},'adp':{'preposition':55,'postposition':45},'poss':{'before':85,'after':15},'gender':[0],'cases':[0,2],'articles':['none'],'agreement':['none'],'tense':['minimal'],'aspect':['standard','rich'],'mood':['minimal','standard'],'morphology':['isolating','analytic'],'questions':['particle','word-order'],'negation':['particle'],'plural':['none','mixed'],'comparison':['particle']},
'berber': {'orders':{'VSO':45,'SVO':45,'SOV':10},'adj':{'after':85,'before':15},'adp':{'preposition':95,'postposition':5},'poss':{'after':80,'before':20},'gender':[2],'cases':[2,3],'articles':['none','definite'],'agreement':['subject'],'tense':['minimal','standard'],'aspect':['rich'],'mood':['standard'],'morphology':['fusional','mixed'],'questions':['particle','mixed'],'negation':['particle','affix'],'plural':['mixed'],'comparison':['particle']},
'quechuan': {'orders':{'SOV':99,'SVO':1},'adj':{'before':90,'after':10},'adp':{'postposition':99,'preposition':1},'poss':{'before':98,'after':2},'gender':[0],'cases':[7,8],'articles':['none'],'agreement':['subject-object','subject'],'tense':['rich'],'aspect':['standard','rich'],'mood':['rich'],'morphology':['agglutinative'],'questions':['particle'],'negation':['affix'],'plural':['suffix'],'comparison':['affix','particle']},
'analytic': {'orders':{'SVO':80,'SOV':10,'VSO':10},'adj':{'before':50,'after':50},'adp':{'preposition':80,'postposition':20},'poss':{'before':60,'after':40},'gender':[0],'cases':[0],'articles':['both','none'],'agreement':['none'],'tense':['minimal'],'aspect':['standard'],'mood':['minimal','standard'],'morphology':['analytic'],'questions':['particle','word-order'],'negation':['particle'],'plural':['none','mixed'],'comparison':['particle']},
'agglutinative': {'orders':{'SOV':80,'SVO':15,'VSO':5},'adj':{'before':80,'after':20},'adp':{'postposition':85,'preposition':15},'poss':{'before':85,'after':15},'gender':[0,2],'cases':[4,5,6,7,8],'articles':['none'],'agreement':['subject','subject-object'],'tense':['standard','rich'],'aspect':['standard','rich'],'mood':['standard','rich'],'morphology':['agglutinative'],'questions':['particle'],'negation':['affix'],'plural':['suffix'],'comparison':['affix','particle']},
'fusional': {'orders':{'SVO':45,'SOV':40,'VSO':15},'adj':{'before':50,'after':50},'adp':{'preposition':90,'postposition':10},'poss':{'before':40,'after':60},'gender':[2,3],'cases':[3,4,5,6,7],'articles':['none','both'],'agreement':['subject'],'tense':['standard','rich'],'aspect':['standard','rich'],'mood':['standard','rich'],'morphology':['fusional'],'questions':['mixed','particle'],'negation':['particle'],'plural':['mixed'],'comparison':['affix','mixed']},
'isolating': {'orders':{'SVO':75,'SOV':15,'VSO':10},'adj':{'before':55,'after':45},'adp':{'preposition':85,'postposition':15},'poss':{'before':65,'after':35},'gender':[0],'cases':[0],'articles':['none','both'],'agreement':['none'],'tense':['minimal'],'aspect':['minimal','standard'],'mood':['minimal'],'morphology':['isolating'],'questions':['particle','word-order'],'negation':['particle'],'plural':['none'],'comparison':['particle']},
}


MORPHOPHONEMIC_DEFAULTS={
 'romance':['elision','consonant_assimilation'], 'germanic':['ablaut','consonant_assimilation'],
 'slavic':['palatalization','consonant_assimilation'], 'arabic':['templatic_light','vowel_elision'],
 'semitic':['templatic_light','vowel_elision'], 'turkic':['vowel_harmony','consonant_assimilation'],
 'uralic':['vowel_harmony','consonant_assimilation'], 'japanese':['epenthesis','consonant_assimilation'],
 'celtic':['initial_mutation','lenition'], 'latin':['vowel_elision','consonant_assimilation'],
 'greek':['vowel_elision','consonant_assimilation'], 'indic':['vowel_harmony_light','consonant_assimilation'],
 'dravidian':['vowel_harmony_light','consonant_assimilation'], 'iranian':['vowel_elision','lenition'],
 'bantu':['vowel_harmony_light','nasal_assimilation'], 'austronesian':['reduplication','nasal_assimilation'],
 'polynesian':['vowel_elision','epenthesis'], 'kartvelian':['consonant_assimilation','epenthesis'],
 'caucasian':['consonant_assimilation','epenthesis'], 'sino-tibetan':['tone_like_none'],
 'berber':['vowel_elision','consonant_assimilation'], 'quechuan':['vowel_harmony_light','consonant_assimilation'],
 'analytic':[], 'agglutinative':['consonant_assimilation'], 'fusional':['vowel_elision','consonant_assimilation'],
 'isolating':[]
}
MORPHOPHONEMIC_CHOICES=['none','auto','vowel_harmony','vowel_harmony_light','initial_mutation','lenition','elision','vowel_elision','palatalization','consonant_assimilation','nasal_assimilation','epenthesis','reduplication','ablaut','templatic_light']

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

def _last_vowel(text):
    for ch in reversed(text.lower()):
        if ch in 'aeiou': return ch
    return ''

def _harmonize(aff, stem, strong=True):
    v=_last_vowel(stem)
    if not v: return aff
    target = ('a' if v in 'aou' else 'e') if strong else ('a' if v in 'ao' else 'e')
    for i,ch in enumerate(aff):
        if ch.lower() in 'aeiou': return aff[:i]+target+aff[i+1:]
    return aff

def _initial_mutate(text):
    pairs={'p':'b','t':'d','k':'g','b':'v','d':'dh','g':'gh','m':'v','f':'v','s':'h'}
    if not text: return text
    lo=text.lower()
    for a,b in sorted(pairs.items(),key=lambda x:-len(x[0])):
        if lo.startswith(a): return b+text[len(a):]
    return text

def _lenite_boundary(left,right):
    if not left or not right:return left,right
    m={'p':'b','t':'d','k':'g','b':'v','d':'dh','g':'gh','s':'h'}
    if right[0].lower() in m: right=m[right[0].lower()]+right[1:]
    return left,right

def morphophonemic_join(stem, aff, side, rules):
    if not aff:return stem
    if not rules:return join(aff,stem) if side=='prefix' else join(stem,aff)
    rules=set(rules)
    if 'vowel_harmony' in rules: aff=_harmonize(aff,stem,True)
    elif 'vowel_harmony_light' in rules: aff=_harmonize(aff,stem,False)
    if side=='prefix': left,right=aff,stem
    else: left,right=stem,aff
    if 'initial_mutation' in rules and side=='prefix': right=_initial_mutate(right)
    if 'lenition' in rules: left,right=_lenite_boundary(left,right)
    if ('elision' in rules or 'vowel_elision' in rules) and left and right and left[-1:].lower() in 'aeiou' and right[:1].lower() in 'aeiou':
        left=left[:-1]
    if 'palatalization' in rules and left and right and right[:1].lower() in 'ie':
        repl={'k':'ch','g':'j','t':'ch','d':'j'}
        if left[-1:].lower() in repl:left=left[:-1]+repl[left[-1:].lower()]
    if 'nasal_assimilation' in rules and left and right and left[-1:].lower()=='n':
        if right[:1].lower() in 'pbm': left=left[:-1]+'m'
        elif right[:1].lower() in 'kg': left=left[:-1]+'ng'
    if 'consonant_assimilation' in rules and left and right and left[-1:].lower() not in 'aeiou' and right[:1].lower()==left[-1:].lower():
        right=right[1:]
    if 'epenthesis' in rules and left and right and left[-1:].lower() not in 'aeiou' and right[:1].lower() not in 'aeiou':
        left += 'a'
    result=join(left,right)
    if 'reduplication' in rules and side=='prefix' and stem:
        # Productive light reduplication: repeat the first CV (or first two letters).
        unit=stem[:2]
        for i,ch in enumerate(stem):
            if ch.lower() in 'aeiou': unit=stem[:i+1]; break
        result=unit+result
    # Lightweight family-flavored stem alternations. These are intentionally not full historical reconstructions.
    if 'ablaut' in rules and side=='suffix' and aff:
        for a,b in [('a','e'),('e','i'),('i','a'),('o','u'),('u','o')]:
            pos=result.lower().find(a)
            if 0<=pos<len(stem): result=result[:pos]+b+result[pos+1:]; break
    if 'templatic_light' in rules and side=='prefix' and len(stem)>=3:
        # Conservative internal-vowel alternation; keeps the generated lexical root recognizable.
        chars=list(result); changed=0
        for i,ch in enumerate(chars):
            if i>=len(aff) and ch.lower() in 'aeiou': chars[i]='a' if changed==0 else 'i'; changed+=1
            if changed>=2: break
        result=''.join(chars)
    return result

def affix(form,spec,g=None):
    rules=(g or {}).get('morphophonemics',{}).get('rules',[])
    return morphophonemic_join(form,spec['form'],spec['side'],rules)

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
    mp_override=overrides.get('morphophonemics')
    if mp_override in (None,'auto'):
        mp_rules=list(MORPHOPHONEMIC_DEFAULTS.get(family,[]))
    elif mp_override=='none': mp_rules=[]
    else: mp_rules=[x.strip() for x in str(mp_override).split(',') if x.strip()]
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
       'morphophonemics':{'mode':mp_override or 'auto','rules':mp_rules},
       'noun':{'numbers':['singular']+([] if plural=='none' else ['plural']),'plural_strategy':plural,'cases':cases},
       'verb':{'tenses':tenses,'tense_level':tense_level,'aspects':aspects,'aspect_level':aspect_level,'moods':moods,'mood_level':mood_level,'agreement':agreement,'negation':negation},
       'comparison':{'degrees':['positive','comparative','superlative'],'strategy':comparison},
       'questions':{'strategy':qtype,'particle_position':rng.choice(['initial','final']),'wh_strategy':'in_situ' if rng.random()<.55 else 'fronted'},
       'morphemes':morph,'particles':particles,'pronouns':pronouns,'demonstratives':demonstratives,'interrogatives':interrogatives}
    return g

def load_grammar(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def noun_form(word,g,number='singular',case='nominative'):
    if number=='plural' and 'plural' in g['morphemes']: word=affix(word,g['morphemes']['plural'],g)
    if case!='nominative' and case in g['morphemes']: word=affix(word,g['morphemes'][case],g)
    return word

def adjective_form(word,g,degree='positive'):
    if degree=='positive': return word
    if degree in g['morphemes']: return affix(word,g['morphemes'][degree],g)
    particle=g.get('particles',{}).get(degree); return f'{particle} {word}' if particle else word

def verb_form(word,g,person='3sg',tense='present',aspect='simple',mood='indicative',negative=False):
    m=g['morphemes']; x=word
    for feature in (tense,aspect,mood):
        if feature not in ('present','simple','indicative') and feature in m: x=affix(x,m[feature],g)
    if negative:
        if 'negative' in m: x=affix(x,m['negative'],g)
        elif g.get('particles',{}).get('negative'): x=g['particles']['negative']+' '+x
    if 'agr_'+person in m: x=affix(x,m['agr_'+person],g)
    return x

def possessive_phrase(possessor, possessed, g):
    p=noun_form(possessor,g,case='genitive') if 'genitive' in g['noun']['cases'] else possessor
    return f'{p} {possessed}' if g['possessor_position']=='before' else f'{possessed} {p}'

def order_clause(s,v,o,g):
    return ' '.join({'SOV':[s,o,v],'SVO':[s,v,o],'VSO':[v,s,o],'VOS':[v,o,s],'OVS':[o,v,s],'OSV':[o,s,v]}[g['word_order']])

def load_translation_sentences(path):
    """Read one English sentence per line. Blank lines and # comments are ignored."""
    raw=Path(path).read_bytes()
    if raw.startswith(b'\xef\xbb\xbf'):
        text=raw.decode('utf-8-sig')
    else:
        try: text=raw.decode('utf-8')
        except UnicodeDecodeError: text=raw.decode('cp1252')
    return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith('#')]

def _lexicon(entries,forms):
    by={}
    for e in entries:
        if e.key in forms:
            by.setdefault(e.key.gloss.lower(),[]).append((e.key.pos,forms[e.key]))
    return by

def _lookup(by, gloss, poses=()):
    vals=by.get(gloss.lower(),[])
    if poses:
        for pos,form in vals:
            if any(pos==p or pos.startswith(p) for p in poses): return form
    return vals[0][1] if vals else None

def _np(words,g,by,case='nominative'):
    # Deterministic small English NP realizer used by translation-file examples.
    det=None; demo=None; number='singular'; adjectives=[]; noun=None; gloss=[]
    nums={'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10}
    for w in words:
        lw=w.lower()
        if lw in ('the','a','an'): det=lw; continue
        if lw in ('this','that','these','those'): demo=lw; number='plural' if lw in ('these','those') else number; continue
        if lw in nums:
            number='plural'; nf=_lookup(by,lw,('num',));
            if nf: adjectives.append((nf,lw.upper()))
            continue
        # common English plural fallback
        candidates=[lw]
        if lw.endswith('ren'): candidates.append(lw[:-3])
        if lw.endswith('ies'): candidates.append(lw[:-3]+'y')
        if lw.endswith('s'): candidates.append(lw[:-1])
        found_n=None
        for c in candidates:
            found_n=_lookup(by,c,('n',))
            if found_n: noun=found_n; gloss.append(c); number='plural' if c!=lw or lw.endswith('s') else number; break
        if found_n: continue
        a=_lookup(by,lw,('adj',))
        if a: adjectives.append((a,lw)); continue
    if not noun: return None,None
    core=noun_form(noun,g,number,case); ng=(gloss[-1] if gloss else 'noun') + ('.PL' if number=='plural' else '') + ('.'+case[:3].upper() if case!='nominative' else '.NOM')
    parts=[core]; gps=[ng]
    for a,ag in adjectives:
        if g['adjective_position']=='before': parts.insert(0,a); gps.insert(0,ag)
        else: parts.append(a); gps.append(ag)
    if demo:
        key=('proximal_' if demo in ('this','these') else 'distal_')+('plural' if number=='plural' else 'singular')
        d=g['demonstratives'].get(key)
        if d: parts.insert(0,d); gps.insert(0,demo.upper())
    # Articles are represented by generated bound morphemes where available.
    if det in ('the','a','an'):
        mk='definite_article' if det=='the' else 'indefinite_article'
        if mk in g['morphemes']:
            # attach to the noun-bearing word
            idx=parts.index(core); parts[idx]=affix(parts[idx],g['morphemes'][mk],g); gps[idx]+='-'+('DEF' if det=='the' else 'INDF')
    return ' '.join(parts),' '.join(gps)

def translate_sentence(sentence,g,entries,forms):
    """Translate a deliberately constrained English example sentence.
    Unsupported constructions return an explanatory status rather than invented language.
    """
    by=_lexicon(entries,forms)
    raw=sentence.strip(); low=re.sub(r'[.!?]+$','',raw.lower()).strip()
    question=raw.rstrip().endswith('?'); imperative=raw.rstrip().endswith('!')
    # copular existential: There is a black mountain.
    m=re.fullmatch(r'there (?:is|are) (.+)',low)
    if m:
        np,ng=_np(m.group(1).split(),g,by)
        exist=_lookup(by,'be (exist)',('v',)) or _lookup(by,'exist',('v',)) or _lookup(by,'be',('v',))
        if np and exist:
            v=verb_form(exist,g,'3sg'); return ('Translation',raw,order_clause(np,v,'',g).replace('  ',' ').strip(),order_clause(ng,'exist-3SG','',g).replace('  ',' ').strip(),'ok')
    # yes/no adjective predicate: Are you hungry?
    m=re.fullmatch(r'(?:are|is|am) (you|he|she|i|we|they) ([a-z -]+)',low)
    if m:
        pm={'i':'1sg','you':'2sg','he':'3sg','she':'3sg','we':'1pl','they':'3pl'}; person=pm[m.group(1)]
        adj=_lookup(by,m.group(2),('adj',)); cop=_lookup(by,'be',('v',)) or _lookup(by,'be (copula)',('v',))
        if adj:
            surf=f"{g['pronouns'][person]} {adj}" + (f" {verb_form(cop,g,person)}" if cop else '')
            q=g.get('particles',{}).get('yes_no')
            if q: surf=(q+' '+surf) if g['questions']['particle_position']=='initial' else (surf+' '+q)
            return ('Translation',raw,surf,f'{person.upper()} {m.group(2)}'+(' COP' if cop else '')+(' Q' if q else ''),'ok')
    # wh copular possession/location: Where is my book?
    m=re.fullmatch(r'where is my ([a-z -]+)',low)
    if m:
        noun=_lookup(by,m.group(1),('n',)); where=g['interrogatives']['where']; cop=_lookup(by,'be',('v',)) or _lookup(by,'be (copula)',('v',))
        if noun:
            poss=possessive_phrase(g['pronouns']['1sg'],noun,g); surf=f'{where} {poss}' + (f' {verb_form(cop,g,"3sg")}' if cop else '')
            return ('Translation',raw,surf,f'WHERE 1SG-GEN {m.group(1)}'+(' COP' if cop else ''),'ok')
    # imperative: Give me the red bird!
    if imperative:
        toks=low.split(); verb=_lookup(by,toks[0],('v',))
        if verb:
            rest=toks[1:]; obj_words=rest
            io=None
            if rest and rest[0] in ('me','him','her','us','them','you'):
                mp={'me':'1sg','you':'2sg','him':'3sg','her':'3sg','us':'1pl','them':'3pl'}; io=g['pronouns'][mp[rest[0]]]; obj_words=rest[1:]
            obj,og=_np(obj_words,g,by,'accusative')
            if obj:
                v=verb_form(verb,g,'2sg',mood='imperative' if 'imperative' in g['verb']['moods'] else 'indicative')
                surf=' '.join(x for x in (v,io,obj) if x); return ('Translation',raw,surf,f'{toks[0]}-IMP '+(('1SG.DAT ') if io else '')+og,'ok')
    # Subject with a present-participial modifier: A tiger wearing a bell will starve.
    m=re.fullmatch(r'(the |a |an )?([a-z -]+?) ([a-z]+ing) (the |a |an )?([a-z -]+?) will ([a-z]+)',low)
    if m:
        head_words=((m.group(1) or '')+m.group(2)).split(); subj,sg=_np(head_words,g,by)
        part=m.group(3); stem=part[:-3]; pv=_lookup(by,stem,('v',)) or _lookup(by,stem+'e',('v',))
        pobj,pg=_np(((m.group(4) or '')+m.group(5)).split(),g,by,'accusative')
        main=_lookup(by,m.group(6),('v',))
        if subj and pv and pobj and main:
            rel=order_clause(subj,verb_form(pv,g,'3sg',aspect='progressive' if 'progressive' in g['verb']['aspects'] else 'simple'),pobj,g)
            mv=verb_form(main,g,'3sg','future' if 'future' in g['verb']['tenses'] else 'present')
            return ('Translation',raw,f'{rel} {mv}',f'SUBJ {stem.upper()}-PART {pg} {m.group(6).upper()}-FUT','ok')
    # Generic simple clauses: subject + auxiliaries + verb + object/PP.
    toks=low.split(); subj_person=None; subj=None; idx=0
    pm={'i':'1sg','you':'2sg','he':'3sg','she':'3sg','we':'1pl','they':'3pl'}
    if toks and toks[0] in pm:
        subj_person=pm[toks[0]]; subj=g['pronouns'][subj_person]; idx=1
    else:
        # find first verb boundary and treat preceding words as NP
        verb_words=set(k for k,v in by.items() if any(p=='v' for p,_ in v))
        vi=next((i for i,w in enumerate(toks) if w in verb_words or (w.endswith('ed') and (w[:-2] in verb_words or w[:-1] in verb_words)) or (w.endswith('ing') and (w[:-3] in verb_words or w[:-3]+'e' in verb_words)) or w in ('is','are','am','was','were','will','do','does','did')),None)
        if vi is not None:
            subj,sg=_np(toks[:vi],g,by); subj_person='3pl' if any(w.endswith('s') or w in ('children','men','women') for w in toks[:vi]) else '3sg'; idx=vi
    if subj:
        tense='present'; aspect='simple'; negative=False
        while idx<len(toks) and toks[idx] in ('will','do','does','did','not','is','are','am','was','were'):
            x=toks[idx]; tense='future' if x=='will' else ('past' if x in ('did','was','were') else tense); negative=negative or x=='not'; aspect='progressive' if x in ('is','are','am','was','were') else aspect; idx+=1
        if idx<len(toks) and toks[idx]=='not': negative=True; idx+=1
        if idx<len(toks):
            vw=toks[idx]; basevw=vw[:-3] if vw.endswith('ing') else (vw[:-2] if vw.endswith('ed') else vw)
            candidates=[vw,basevw, (vw[:-1] if vw.endswith('ed') else ''), (basevw+'e' if vw.endswith('ing') else '')]
            if basevw.endswith('k') and vw.endswith('ked'): candidates.append(basevw+'e')
            verb=None; vg=None
            for c in candidates:
                verb=_lookup(by,c,('v',))
                if verb: vg=c; break
            if verb:
                idx+=1; rest=toks[idx:]
                # strip common temporal adverb when lexicalized separately
                tail=[]
                if rest and rest[-1] in ('yesterday','today','tomorrow'):
                    adv=_lookup(by,rest[-1],('adv',));
                    if adv: tail=[adv]; rest=rest[:-1]
                # conjunction subject pattern: The woman and the man are talking.
                if ' and ' in low and low.find(' and ') < low.find(vw):
                    left,right=re.split(r' and ',low,1); right_words=right.split(); auxi=next((i for i,x in enumerate(right_words) if x in ('is','are','am','was','were','will') or _lookup(by,x,('v',))),None)
                    if auxi is not None:
                        n1,g1=_np(left.split(),g,by); n2,g2=_np(right_words[:auxi],g,by); conj=_lookup(by,'and',('conj',)) or 'and'
                        if n1 and n2: subj=f'{n1} {conj} {n2}'; subj_person='3pl'
                obj=None; og=None
                # prepositional tail
                prep_i=next((i for i,x in enumerate(rest) if x in ('to','in','at','on')),None)
                pp=''; ppg=''
                obj_words=rest if prep_i is None else rest[:prep_i]
                if obj_words:
                    # indirect-object pronoun then object NP: give him water
                    if obj_words[0] in ('me','him','her','us','them','you'):
                        im={'me':'1sg','you':'2sg','him':'3sg','her':'3sg','us':'1pl','them':'3pl'}; pp=g['pronouns'][im[obj_words[0]]]+' '; ppg=im[obj_words[0]].upper()+'.DAT '; obj_words=obj_words[1:]
                    obj,og=_np(obj_words,g,by,'accusative')
                if prep_i is not None:
                    prep=rest[prep_i]; pobj,pg=_np(rest[prep_i+1:],g,by,'dative' if prep=='to' else 'locative')
                    ad=_lookup(by,prep,('prep','p')) or prep
                    if pobj: pp += (ad+' '+pobj if g['adposition_type']=='preposition' else pobj+' '+ad); ppg += prep.upper()+' '+pg
                v=verb_form(verb,g,subj_person,tense if tense in g['verb']['tenses'] else 'present',aspect if aspect in g['verb']['aspects'] else 'simple',negative=negative)
                surf=order_clause(subj,v,obj or '',g).replace('  ',' ').strip(); surf=' '.join(x for x in [surf,pp,*tail] if x)
                gloss=order_clause('SUBJ',vg.upper()+('-FUT' if tense=='future' else '-PST' if tense=='past' else '')+('-PROG' if aspect=='progressive' else '')+('-NEG' if negative else ''),og or '',g).replace('  ',' ').strip(); gloss=' '.join(x for x in [gloss,ppg] if x)
                if question:
                    q=g.get('particles',{}).get('yes_no')
                    if q: surf=(q+' '+surf) if g['questions']['particle_position']=='initial' else (surf+' '+q); gloss+=' Q'
                return ('Translation',raw,surf,gloss,'ok')
    return ('Translation',raw,'[UNRESOLVED]','[UNRESOLVED]','unsupported vocabulary or construction')

def generate_examples(g, entries, forms, translation_sentences=None):
    if translation_sentences is not None:
        return [translate_sentence(s,g,entries,forms) for s in translation_sentences]
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
        examples.append(('Declarative','The warrior killed the dragon.',surface,gloss,'ok'))
        q=g.get('particles',{}).get('yes_no')
        if q: surface=(q+' '+surface) if g['questions']['particle_position']=='initial' else (surface+' '+q)
        examples.append(('Yes/no question','Did the warrior kill the dragon?',surface,gloss+(' Q' if q else ' ?'),'ok'))
    hunter,_=L('hunter'); house,_=L('house')
    if hunter and house: examples.append(('Possession',"the hunter's house",possessive_phrase(hunter,house,g),'hunter-GEN house' if g['possessor_position']=='before' else 'house hunter-GEN','ok'))
    big,_=L('big')
    if big: examples.append(('Comparison','bigger / biggest',f"{adjective_form(big,g,'comparative')} / {adjective_form(big,g,'superlative')}",'big-CMPR / big-SUP','ok'))
    see,_=L('see'); who=g['interrogatives']['who']
    if see:
        v=verb_form(see,g,'2sg'); clause=f'{g["pronouns"]["2sg"]} {v} {who}'
        if g['questions']['wh_strategy']=='fronted': clause=f'{who} {g["pronouns"]["2sg"]} {v}'
        examples.append(('Wh-question','Who do you see?',clause,'who 2SG see-2SG','ok'))
    go,_=L('go')
    if go:
        for mood,eng in [('imperative','Go!'),('subjunctive','that he go'),('conditional','he would go')]:
            if mood in g['verb']['moods']: examples.append((mood.title(),eng,verb_form(go,g,'3sg' if mood!='imperative' else '2sg',mood=mood),f'go-{mood[:4].upper()}','ok'))
    return examples

def write_package(outdir, language_name, grammar, entries, forms, deriv_affixes, seed, translation_sentences=None, translation_source=None):
    outdir.mkdir(parents=True,exist_ok=True); examples=generate_examples(grammar,entries,forms,translation_sentences)
    data={'name':language_name,'seed':seed,'grammar':grammar,'derivational_morphology':{k:{'side':v.side,'form':v.form,'source_rule':v.source_rule} for k,v in deriv_affixes.items()},'lexicon':[{'gloss':e.key.gloss,'pos':e.key.pos,'form':forms.get(e.key,''),'derivation':e.expr} for e in entries],'translation_source':str(translation_source) if translation_source else None,'examples':[{'type':t,'english':en,'surface':s,'gloss':gl,'status':status} for t,en,s,gl,status in examples]}
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
        for t,en,s,gl,status in examples: f.write(f'[{t}]\nEnglish: {en}\nLanguage: {s}\nGloss: {gl}\nStatus: {status}\n\n')
    ref=[f'# {language_name}','',f'Generation seed: `{seed}`',f"Grammar family: **{grammar['family']}**",f"Morphology type: **{grammar['morphology_type']}**",f"Morphophonemics: **{', '.join(grammar.get('morphophonemics',{}).get('rules',[])) or 'none'}**",'', '## Syntax',f"- Basic word order: **{grammar['word_order']}**",f"- Adpositions: **{grammar['adposition_type']}s**",f"- Adjectives occur **{grammar['adjective_position']}** the noun.",f"- Possessors occur **{grammar['possessor_position']}** the possessed noun.",f"- Articles: **{grammar['articles']}**",f"- Gender/classes: **{grammar['gender']}**",'', '## Nouns',f"- Number strategy: **{grammar['noun']['plural_strategy']}**.",f"- Cases: {', '.join(grammar['noun']['cases'])}.",'', '## Verbs',f"- Agreement: **{grammar['verb']['agreement']}**.",f"- Tense: {', '.join(grammar['verb']['tenses'])}.",f"- Aspect: {', '.join(grammar['verb']['aspects'])}.",f"- Moods: {', '.join(grammar['verb']['moods'])}.",f"- Negation: **{grammar['verb']['negation']}**.",'', '## Comparison',f"- Strategy: **{grammar['comparison']['strategy']}**.",'', '## Questions',f"- Strategy: **{grammar['questions']['strategy']}**.",f"- Wh-words: **{grammar['questions']['wh_strategy']}**.",'','## Demonstratives']
    for k,v in grammar['demonstratives'].items(): ref.append(f'- {k}: **{v}**')
    ref += ['', '## Interrogatives']; [ref.append(f'- {k}: **{v}**') for k,v in grammar['interrogatives'].items()]
    ref += ['', '## Pronouns']; [ref.append(f'- {k}: **{v}**') for k,v in grammar['pronouns'].items()]
    ref += ['', '## Inflectional Morphemes']; [ref.append(f"- {k}: **{v['form']+'-' if v['side']=='prefix' else '-'+v['form']}**") for k,v in grammar['morphemes'].items()]
    ref += ['', '## Particles']; [ref.append(f'- {k}: **{v}**') for k,v in grammar.get('particles',{}).items()]
    ref += ['', '## Generated Examples']
    for t,en,s,gl,status in examples: ref += [f'### {t}',f'- English: {en}',f'- Language: **{s}**',f'- Gloss: `{gl}`',f'- Status: `{status}`','']
    (outdir/'reference.md').write_text('\n'.join(ref)+'\n',encoding='utf-8')
