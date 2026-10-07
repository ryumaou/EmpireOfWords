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
    # Productive lexical conversion lets one semantic root participate in another POS
    # without inventing an unrelated root. Languages vary between zero conversion and derivational affixes.
    lexical_conversion={}
    for conv in ('noun_to_verb','adjective_to_verb','noun_to_adjective'):
        strategy=rng.choice(['zero','affix']) if morphology not in ('isolating','analytic') else 'zero'
        lexical_conversion[conv]={'strategy':strategy}
        if strategy=='affix':
            key='convert_'+conv; M(key,affix_sides); lexical_conversion[conv]['morpheme']=key
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
    # Clause-level strategies are generated explicitly so the translator realizes
    # semantic features through the target grammar instead of English word order.
    particles['and']=word(); particles['or']=word(); particles['but']=word()
    particles['ability']=word(); particles['obligation']=word(); particles['possibility']=word()
    # Translation-ready analytic fallbacks. These do not force a language to use
    # analytic grammar when it has morphology; they guarantee every advertised
    # feature has a deterministic realization path.
    particles['future']=word(); particles['progressive']=word(); particles['perfect']=word(); particles['imperative']=word()
    # Independent grammar words used when the generated language chooses analytic
    # possession/complement/relative strategies.
    particles['possessive']=word(); particles['complementizer']=word(); particles['relative']=word()
    particles['conditional']=word(); particles['subordinate']=word(); particles['passive']=word(); particles['quotative']=word(); particles['appositive']=word()
    # Non-finite strategies are part of the language at creation time. They are not
    # copied from English: each language chooses bound morphology or an analytic marker.
    if morphology in ('agglutinative','fusional','mixed') and rng.random()<0.7:
        M('participle',affix_sides); participial={'strategy':'affix','morpheme':'participle','position':adj}
    else:
        particles['participle']=word(); participial={'strategy':'particle','particle':'participle','position':adj}
    if morphology in ('agglutinative','fusional','mixed') and rng.random()<0.6:
        M('infinitive',affix_sides); infinitive={'strategy':'affix','morpheme':'infinitive','position':'after_head'}
    else:
        particles['infinitive']=word(); infinitive={'strategy':'particle','particle':'infinitive','position':'before_verb'}
    g={'family':family,'requested_family':requested,'word_order':order,'adposition_type':adp,'adjective_position':adj,'possessor_position':poss,
       'articles':articles,'gender':gender,'morphology_type':morphology,
       'morphophonemics':{'mode':mp_override or 'auto','rules':mp_rules},
       'noun':{'numbers':['singular']+([] if plural=='none' else ['plural']),'plural_strategy':plural,'cases':cases},
       'verb':{'tenses':tenses,'tense_level':tense_level,'aspects':aspects,'aspect_level':aspect_level,'moods':moods,'mood_level':mood_level,'agreement':agreement,'negation':negation},
       'comparison':{'degrees':['positive','comparative','superlative'],'strategy':comparison,'marker_position':rng.choice(['before','after'])},
       'questions':{'strategy':qtype,'particle_position':rng.choice(['initial','final']),'wh_strategy':'in_situ' if rng.random()<.55 else 'fronted','structural_operation':'verb_fronting' if qtype in ('word-order','verb','mixed') else None},
       'coordination':{
           'np':{'strategy':rng.choice(['particle','particle','juxtaposition']),'position':'between'},
           'predicate':{'strategy':rng.choice(['particle','particle','juxtaposition']),'position':'between','shared_subject':True},
           'clause':{'strategy':rng.choice(['particle','particle','juxtaposition']),'position':'between'},
       },
       'possession':{'strategy':'genitive' if 'genitive' in cases else rng.choice(['juxtaposition','particle']),'position':poss},
       'modality':{'strategy':'particle','particle_position':rng.choice(['before_verb','after_verb'])},
       'tense_realization':{'future':'affix' if 'future' in morph else 'particle'},
       'aspect_realization':{'progressive':'affix' if 'progressive' in morph else 'particle','perfect':'affix' if 'perfect' in morph else 'particle'},
       'mood_realization':{'imperative':'affix' if 'imperative' in morph else 'particle'},
       'perfect':{'strategy':'affix' if 'perfect' in morph else 'particle'},
       'adverbs':{'position':rng.choice(['before_verb','after_verb','clause_final']),'derivation':'zero'},
       'copular':{'adjective_complement':True,'nominal_complement':True,'copula_position':'verb'},
       'lexical_conversion':lexical_conversion,
       'nonfinite':{'participial_modifier':participial,'infinitive_complement':infinitive},
       'relative_clause':{'strategy':'relative_particle','position':rng.choice(['before','after'])},
       'complement_clause':{'strategy':rng.choice(['juxtaposition','particle']),'position':rng.choice(['before','after'])},
       'conditional_clause':{'strategy':'particle','position':rng.choice(['initial','medial'])},
       'subordinate_clause':{'strategy':'particle','position':rng.choice(['before','after'])},
       'passive':{'strategy':rng.choice(['particle','morphological']),'agent_position':rng.choice(['before','after'])},
       'quotation':{'strategy':'quotative_particle','position':rng.choice(['before','after'])},
       'apposition':{'strategy':rng.choice(['juxtaposition','particle']),'position':'adjacent'},
       'realization_profile':{
           'word_order':order,'adposition_type':adp,'adjective_position':adj,'possessor_position':poss,
           'plural_strategy':plural,'comparison_strategy':comparison,'question_strategy':qtype,
           'negation_strategy':negation,'morphology_type':morphology,
           'noun_behavior':{'number':plural,'cases':cases,'possessor_position':poss,'compound_order':'modifier-head' if poss=='before' else 'head-modifier'},
           'noun_compound_order':'modifier-head' if poss=='before' else 'head-modifier',
           'adjective_behavior':{'position':adj,'comparison':comparison,'adverb_derivation':'zero'},
           'verb_behavior':{'agreement':agreement,'negation':negation,'tenses':tenses,'aspects':aspects,'moods':moods},
           'lexical_conversion':lexical_conversion,
           'nonfinite':{'participial_modifier':participial,'infinitive_complement':infinitive},
           'future':'affix' if 'future' in morph else 'particle',
           'progressive':'affix' if 'progressive' in morph else 'particle',
           'perfect':'affix' if 'perfect' in morph else 'particle',
           'imperative':'affix' if 'imperative' in morph else 'particle',
       },
       'translation_readiness':{'contract_version':5,'analytic_fallbacks':['future','progressive','perfect','imperative'],'adverb_fallback':'zero'},
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
    spec=g.get('possession',{})
    if spec.get('strategy')=='particle' and g.get('particles',{}).get('possessive'):
        mark=g['particles']['possessive']
        p=f'{p} {mark}' if spec.get('position',g.get('possessor_position'))=='before' else f'{mark} {p}'
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
    """Lemma-aware deterministic English NP realizer."""
    det=None; demo=None; number='singular'; adjectives=[]; noun=None; noun_gloss=None
    nums={'two':2,'three':3,'four':4,'five':5,'six':6,'seven':7,'eight':8,'nine':9,'ten':10}
    cleaned=[w.lower().strip(".,;:!?") for w in words if w.strip(".,;:!?")]
    # English possessive NP: baby's ball / Henry's dog.
    if len(cleaned)>=2 and cleaned[0].endswith("'s"):
        poss_lemma=_lexical_match(by,cleaned[0][:-2]) or cleaned[0][:-2]
        poss=_lookup(by,poss_lemma,('n',))
        head,hg=_np(cleaned[1:],g,by,case)
        if head and poss:
            return possessive_phrase(poss,head,g), f'{poss_lemma.upper()}-GEN {hg}'
    poss_det=None
    for lw in cleaned:
        if lw in ('the','a','an'): det=lw; continue
        if lw in ('my','your','his','her','our','their','its'):
            poss_det=lw; continue
        if lw in ('this','that','these','those'):
            demo=lw; number='plural' if lw in ('these','those') else number; continue
        if lw in nums:
            number='plural'; nf=_lookup(by,lw,('num',))
            if nf: adjectives.append((nf,lw.upper()))
            continue
        lemma=_lexical_match(by,lw) or lw
        vals=by.get(lemma,[])
        n=next((form for pos,form in vals if pos=='n' or pos.startswith('n')),None)
        if n and noun is None:
            noun=n; noun_gloss=lemma
            if lw!=lemma or lw in _IRREGULAR_NOUNS: number='plural'
            continue
        a=next((form for pos,form in vals if pos=='adj' or pos.startswith('adj')),None)
        if a: adjectives.append((a,lemma)); continue
    if not noun: return None,None
    core=noun_form(noun,g,number,case); ng=(noun_gloss or 'noun') + ('.PL' if number=='plural' else '') + ('.'+case[:3].upper() if case!='nominative' else '.NOM')
    parts=[core]; gps=[ng]
    for a,ag in adjectives:
        if g['adjective_position']=='before': parts.insert(0,a); gps.insert(0,ag)
        else: parts.append(a); gps.append(ag)
    if demo:
        key=('proximal_' if demo in ('this','these') else 'distal_')+('plural' if number=='plural' else 'singular')
        d=g['demonstratives'].get(key)
        if d: parts.insert(0,d); gps.insert(0,demo.upper())
    if det in ('the','a','an'):
        mk='definite_article' if det=='the' else 'indefinite_article'
        if mk in g['morphemes']:
            idx=parts.index(core); parts[idx]=affix(parts[idx],g['morphemes'][mk],g); gps[idx]+='-'+('DEF' if det=='the' else 'INDF')
    if poss_det:
        pm={'my':'1sg','your':'2sg','his':'3sg','her':'3sg','our':'1pl','their':'3pl','its':'3sg'}
        pf=g['pronouns'][pm[poss_det]]
        phrase=possessive_phrase(pf,' '.join(parts),g)
        return phrase, f'{pm[poss_det].upper()}-GEN '+' '.join(gps)
    return ' '.join(parts),' '.join(gps)

def _legacy_translate_sentence(sentence,g,entries,forms):
    """Legacy constrained English example translator.
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
            # Commands frequently end in particles/adverbials rather than an object
            # (go away, sit here, come with us).  Realize those conservatively.
            obj=None; og=''; tail_s=[]; tail_g=[]
            particle_words={'away','up','down','here','there','around','back','out','off','on','over','through','together','again','now','soon','tomorrow','today','yesterday'}
            prep_words={'with','by','to','in','at','on','from','for','into','onto','under','over','near','beside','across','through','upon','toward','towards','after','before','until','about'}
            if obj_words:
                if obj_words[0] in particle_words:
                    adv=_lookup(by,obj_words[0],('adv','prep','p')) or obj_words[0]
                    tail_s.append(adv); tail_g.append(obj_words[0].upper())
                    obj_words=obj_words[1:]
                elif obj_words[0] in prep_words:
                    prep=obj_words[0]; pobj,pg=_np(obj_words[1:],g,by,'dative' if prep in ('to','for') else 'locative')
                    ad=_lookup(by,prep,('prep','p')) or prep
                    if pobj:
                        tail_s.append(ad+' '+pobj if g['adposition_type']=='preposition' else pobj+' '+ad)
                        tail_g.append(prep.upper()+' '+pg)
                        obj_words=[]
            if obj_words:
                obj,og=_np(obj_words,g,by,'accusative')
            if obj or not obj_words:
                v=verb_form(verb,g,'2sg',mood='imperative' if 'imperative' in g['verb']['moods'] else 'indicative')
                surf=' '.join(x for x in (v,io,obj,*tail_s) if x)
                gloss=' '.join(x for x in (f'{toks[0]}-IMP',(('1SG.DAT') if io else ''),(og or ''),*tail_g) if x)
                return ('Translation',raw,surf,gloss,'ok')
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
    # Copular adjective/nominal predicates: I am happy; Sugar tastes sweet;
    # Their voices sound happy.  These are predicates, not missing objects.
    cm=re.fullmatch(r'(.+?)\s+(am|is|are|was|were|seem|seems|seemed|feel|feels|felt|sound|sounds|sounded|taste|tastes|tasted|grow|grows|grew)\s+(?:very\s+)?([a-z]+)',low)
    if cm:
        sw,cv,pred=cm.groups(); subj,sg=_np(sw.split(),g,by)
        if not subj and sw in ('i','you','he','she','we','they'):
            pmc={'i':'1sg','you':'2sg','he':'3sg','she':'3sg','we':'1pl','they':'3pl'}; subj=g['pronouns'][pmc[sw]]; sg=pmc[sw].upper()
        pl=_lexical_match(by,pred) or pred
        adj=_lookup(by,pl,('adj','adv'))
        noun=_lookup(by,pl,('n',))
        if subj and (adj or noun):
            person='3pl' if sw in ('we','they') else '1sg' if sw=='i' else '2sg' if sw=='you' else '3sg'
            past=cv in ('was','were','seemed','felt','sounded','tasted','grew')
            # Pure BE uses the generated copular verb if present; lexical linking verbs
            # retain their own lexeme when the dictionary provides one.
            if cv in ('am','is','are','was','were'):
                cop=_lookup(by,'be',('v',)) or _lookup(by,'exist',('v',))
            else:
                cop=_lookup(by,_lexical_match(by,cv) or cv,('v',))
            predsurf=adj or noun
            if cop:
                vf=verb_form(cop,g,person,'past' if past and 'past' in g['verb']['tenses'] else 'present')
                surf=order_clause(subj,vf,predsurf,g); gloss=order_clause(sg or 'SUBJ','COP-PST' if past else 'COP',pl.upper(),g)
            else:
                surf=f'{subj} {predsurf}'; gloss=f'{sg or "SUBJ"} {pl.upper()}'
            return ('Translation',raw,surf,gloss,'ok')

    # Generic simple clauses: subject + auxiliaries + verb + object/PP.
    toks=low.split(); subj_person=None; subj=None; subj_gloss=None; idx=0
    pm={'i':'1sg','you':'2sg','he':'3sg','she':'3sg','we':'1pl','they':'3pl'}
    if toks and toks[0] in pm:
        subj_person=pm[toks[0]]; subj=g['pronouns'][subj_person]; subj_gloss=subj_person.upper(); idx=1
    else:
        # find first verb boundary and treat preceding words as NP
        verb_words=set(k for k,v in by.items() if any(p=='v' for p,_ in v))
        vi=next((i for i,w in enumerate(toks) if w in verb_words or (w.endswith('ed') and (w[:-2] in verb_words or w[:-1] in verb_words)) or (w.endswith('ing') and (w[:-3] in verb_words or w[:-3]+'e' in verb_words)) or w in ('is','are','am','was','were','will','do','does','did')),None)
        if vi is not None:
            subj,sg=_np(toks[:vi],g,by); subj_gloss=sg; subj_person='3pl' if any(w.endswith('s') or w in ('children','men','women') for w in toks[:vi]) else '3sg'; idx=vi
    if subj:
        tense='present'; aspect='simple'; negative=False; perfect=False; modal=None
        while idx<len(toks) and toks[idx] in ('will','shall','can','could','should','would','must','may','might','do','does','did','not','is','are','am','was','were','has','have','had','been','being'):
            x=toks[idx]
            if x in ('will','shall'): tense='future'
            elif x in ('did','was','were','had'): tense='past'
            if x in ('can','could','should','would','must','may','might'): modal=x
            if x in ('has','have','had'): perfect=True
            if x in ('is','are','am','was','were','being') and idx+1<len(toks) and toks[idx+1].endswith('ing'): aspect='progressive'
            if x=='been' and idx+1<len(toks) and toks[idx+1].endswith('ing'): aspect='progressive'; perfect=True
            negative=negative or x=='not'; idx+=1
        if idx<len(toks) and toks[idx]=='not': negative=True; idx+=1
        if idx<len(toks):
            vw=toks[idx]; vg=_lexical_match(by,vw) or vw
            verb=_lookup(by,vg,('v',))
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
                        if n1 and n2: subj=f'{n1} {conj} {n2}'; subj_gloss=f'{g1} AND {g2}'; subj_person='3pl'
                obj=None; og=None
                # prepositional tail
                prep_i=next((i for i,x in enumerate(rest) if x in ('to','in','at','on','with','by','from','for','into','onto','under','over','near','beside','across','through','upon','toward','towards','after','before','until','about')),None)
                pp=''; ppg=''
                obj_words=rest if prep_i is None else rest[:prep_i]
                if obj_words:
                    # indirect-object pronoun then object NP: give him water
                    if obj_words[0] in ('me','him','her','us','them','you'):
                        im={'me':'1sg','you':'2sg','him':'3sg','her':'3sg','us':'1pl','them':'3pl'}; pp=g['pronouns'][im[obj_words[0]]]+' '; ppg=im[obj_words[0]].upper()+'.DAT '; obj_words=obj_words[1:]
                    obj,og=_np(obj_words,g,by,'accusative')
                if prep_i is not None:
                    prep=rest[prep_i]; pobj,pg=_np(rest[prep_i+1:],g,by,'dative' if prep in ('to','for') else 'locative')
                    ad=_lookup(by,prep,('prep','p')) or prep
                    if pobj: pp += (ad+' '+pobj if g['adposition_type']=='preposition' else pobj+' '+ad); ppg += prep.upper()+' '+pg
                v=verb_form(verb,g,subj_person,tense if tense in g['verb']['tenses'] else 'present',aspect if aspect in g['verb']['aspects'] else 'simple',negative=negative)
                vgl=vg.upper()+('-FUT' if tense=='future' else '-PST' if tense=='past' else '')+('-PROG' if aspect=='progressive' else '')+('-NEG' if negative else '')
                if perfect:
                    v=affix(v,g['morphemes']['perfect'],g) if 'perfect' in g['morphemes'] else v
                    vgl+='-PERF'
                if modal:
                    key='ability' if modal in ('can','could') else 'obligation' if modal in ('should','must') else 'possibility'
                    mp=g.get('particles',{}).get(key)
                    if mp: v=mp+' '+v
                    vgl+='-MOD'
                surf=order_clause(subj,v,obj or '',g).replace('  ',' ').strip(); surf=' '.join(x for x in [surf,pp,*tail] if x)
                gloss=order_clause(subj_gloss or 'SUBJ',vgl,og or '',g).replace('  ',' ').strip(); gloss=' '.join(x for x in [gloss,ppg] if x)
                if question:
                    q=g.get('particles',{}).get('yes_no')
                    if q:
                        surf=(q+' '+surf) if g['questions']['particle_position']=='initial' else (surf+' '+q)
                    elif g.get('questions',{}).get('strategy') in ('word-order','verb','mixed'):
                        # The target grammar marks interrogation structurally; the
                        # surface is already in target clause order, so no English
                        # auxiliary is copied.  The structured receipt records Q.
                        pass
                    gloss+=' Q'
                return ('Translation',raw,surf,gloss,'ok')
    return ('Translation',raw,'[UNRESOLVED]','[UNRESOLVED]','unsupported vocabulary or construction')


# Translation analysis is shared by build-time examples and standalone translation.
from structured_realizer import parse_clause as _parse_structured_clause, realize as _realize_structured_clause

from english_analyzer import (
    CAPABILITIES as TRANSLATION_CAPABILITIES,
    IRREGULAR_VERBS as _IRREGULAR_VERBS,
    IRREGULAR_NOUNS as _IRREGULAR_NOUNS,
    FUNCTION_WORDS as _FUNCTION_WORDS,
    AUX as _AUX,
    tokens as _english_tokens,
    lemma_candidates as _lemma_candidates,
    lexical_match as _lexical_match,
    analyze as _analyze_english,
)


def _normalize_for_legacy(raw,by):
    """Conservative English normalization used only when it preserves features."""
    tokens=_english_tokens(raw); changed=False
    # Normalize 3sg present lexical verbs when their lemma is in the lexicon.
    for i,w in enumerate(tokens):
        if w in _FUNCTION_WORDS: continue
        match=_lexical_match(by,w)
        if match and match!=w and w.endswith('s') and not w.endswith('ss'):
            tokens[i]=match; changed=True
    # Irregular simple past -> did + lemma. Avoid participles after HAVE/BE.
    for i,w in enumerate(list(tokens)):
        if w in _IRREGULAR_VERBS and _IRREGULAR_VERBS[w][1]=='past' and w not in ('was','were','had'):
            if i and tokens[i-1] in ('has','have','had','is','are','was','were'): continue
            lemma=_IRREGULAR_VERBS[w][0]
            if lemma in by:
                tokens[i:i+1]=['did',lemma]; changed=True; break
    if not changed: return raw
    punct='?' if raw.rstrip().endswith('?') else '!' if raw.rstrip().endswith('!') else '.'
    return ' '.join(tokens)+punct


def _prepare_for_legacy(raw, constructions, by):
    """Map English surface syntax into a neutral clause order for realization."""
    t=raw.strip()
    if 'imperative' in constructions and not t.endswith(('!','?')):
        t=t.rstrip('.')+'!'
    if 'yes_no_question' in constructions:
        qt=[x.lower() for x in _english_tokens(t)]
        if len(qt)>=2 and qt[0] in ('do','does','did','is','are','am','was','were','has','have','had','will','shall','can','could','should','would','must','may','might'):
            aux=qt[0]
            # Find the lexical predicate after the fronted auxiliary. Everything
            # before it is the subject NP; preserve the auxiliary for tense/modal/aspect.
            vi=None
            for i,w in enumerate(qt[1:],1):
                lm=_lexical_match(by,w) or w
                if any(p=='v' or p.startswith('v') for p,_ in by.get(lm,[])):
                    vi=i; break
                if w.endswith(('ing','ed','en')) and _lexical_match(by,w): vi=i; break
            if vi is not None:
                subj=qt[1:vi]; pred=qt[vi:]
                if aux in ('do','does','did'):
                    pred=([aux] if aux=='did' else [])+pred
                else:
                    pred=[aux]+pred
                t=' '.join(subj+pred)+'?'
    return t

def analyze_translation(sentence,g,entries,forms):
    """Return a structured deterministic analysis plus translation result."""
    by=_lexicon(entries,forms); raw=sentence.strip()
    base_ir=_analyze_english(raw,by)
    tokens=base_ir['tokens']; constructions=base_ir['constructions']
    lexical=base_ir['lexical_items']; missing=base_ir['missing_lexemes']
    normalized=_normalize_for_legacy(raw,by)
    prepared=_prepare_for_legacy(normalized,constructions,by)

    # v6.3 structured realization.  Parse semantic roles/features first and realize
    # them through the generated target grammar.  If this conservative first-pass
    # parser cannot represent the sentence, retain the proven legacy path below.
    structured_ir=_parse_structured_clause(raw,by,_lexical_match,_english_tokens,_lemma_candidates,constructions,g)
    structured=None
    if structured_ir is not None:
        structured=_realize_structured_clause(structured_ir,g,by,verb_form,noun_form,possessive_phrase,order_clause,affix,adjective_form)
    if structured:
        surface=structured['surface']; gloss=structured['gloss']; legacy_status='ok'
    else:
        legacy=_legacy_translate_sentence(prepared,g,entries,forms)
        _,_,surface,gloss,legacy_status=legacy

    # Constructions that the current deterministic realizer can identify but not
    # yet safely realize must never be silently flattened into a simple clause.
    diagnosed=[c for c in constructions if TRANSLATION_CAPABILITIES.get(c)=='diagnosed']
    if diagnosed:
        status='unsupported-grammar'; surface='[UNRESOLVED]'; gloss='[UNRESOLVED]'
        reason='unsupported construction: '+', '.join(diagnosed)
    elif legacy_status!='ok':
        if missing:
            status='unresolved-vocabulary'; reason='missing vocabulary: '+', '.join(dict.fromkeys(missing))
        else:
            # A failed surface-realizer pattern is not proof that the grammar is
            # unsupported.  Only positively diagnosed constructions above receive
            # unsupported-grammar.  Preserve the no-false-success rule by withholding
            # a surface form and reporting this as a partial realization.
            status='partial'; surface='[PARTIAL]'; gloss='[PARTIAL]'
            reason='recognized construction not yet fully realized'
    else:
        # Completeness guard: every recognized lexical concept must leave a receipt
        # in the gloss.  v5.5 exempted subject nouns/adjectives because the legacy
        # gloss said only SUBJ; generic clauses now retain the NP gloss, so that
        # exemption would hide lost adjectives and coordinated subjects.
        gu=gloss.lower(); dropped=[]
        receipts=set(structured.get('receipts',())) if structured else set()
        for item in lexical:
            lemma=item['lemma'].lower()
            if structured:
                if lemma not in receipts and item['token'].lower() not in receipts:
                    dropped.append(item['token'])
            elif lemma not in gu and item['token'].lower() not in gu:
                dropped.append(item['token'])
        # Grammatical features need receipts too. A sentence is not complete merely
        # because all dictionary roots appeared somewhere in the output.
        gl=gloss.upper()
        if 'progressive' in constructions and not (structured and 'progressive' in receipts) and 'PROG' not in gl: dropped.append('progressive aspect')
        if 'perfect' in constructions and not (structured and 'perfect' in receipts) and 'PERF' not in gl: dropped.append('perfect aspect')
        if 'negation' in constructions and not (structured and 'negation' in receipts) and 'NEG' not in gl: dropped.append('negation')
        if 'yes_no_question' in constructions and not (structured and 'question' in receipts) and ' Q' not in (' '+gl): dropped.append('question marking')
        if 'imperative' in constructions and not (structured and 'imperative' in receipts) and 'IMP' not in gl: dropped.append('imperative mood')
        if 'possessive' in constructions and not (structured and 'possessive' in receipts) and 'GEN' not in gl: dropped.append('possessive relation')
        if 'comparison' in constructions and not (structured and 'comparison' in receipts) and not any(x in gl for x in ('COMP','SUPER','MORE','LESS','THAN')): dropped.append('comparison')
        if 'modal' in constructions:
            low_tokens=set(base_ir['tokens'])
            if low_tokens & {'will','shall'}:
                if 'FUT' not in gl: dropped.append('future/modal')
            elif low_tokens & {'can','could','should','would','must','may','might'} and 'MOD' not in gl:
                dropped.append('modal meaning')
        # Explicit coordination with multiple lexical verbs is unsafe in legacy path.
        verb_count=sum(1 for item in lexical if any(p=='v' for p,_ in by.get(item['lemma'],[])))
        if 'coordination' in constructions and verb_count>1 and not (structured and 'coordination' in receipts): dropped.append('coordinated clause/predicate')
        if missing or dropped:
            status='unresolved-vocabulary' if missing else 'partial'
            surface='[UNRESOLVED]' if missing else '[PARTIAL]'
            gloss='[UNRESOLVED]' if missing else gloss
            reason_parts=[]
            if missing: reason_parts.append('missing vocabulary: '+', '.join(dict.fromkeys(missing)))
            if dropped: reason_parts.append('not realized: '+', '.join(dict.fromkeys(dropped)))
            reason='; '.join(reason_parts)
        else:
            status='ok'; reason='complete'
    ir=dict(base_ir)
    ir['normalized_english']=normalized if normalized!=raw else None
    ir['realizer_input']=prepared if prepared!=normalized else None
    ir['structured_clause']=structured.get('ir') if structured else (structured_ir.to_dict() if structured_ir is not None else None)
    ir['realization_receipts']=sorted(structured.get('receipts',())) if structured else []
    ir['realization_strategies']=structured.get('strategies',{}) if structured else {}
    return {'type':'Translation','english':raw,'surface':surface,'gloss':gloss,'status':status,'reason':reason,'ir':ir}


def translate_sentence(sentence,g,entries,forms):
    d=analyze_translation(sentence,g,entries,forms)
    return (d['type'],d['english'],d['surface'],d['gloss'],d['status'])

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
    data={'schema_version':2,'tool_version':'6.8','name':language_name,'seed':seed,'grammar':grammar,'translation_capabilities':TRANSLATION_CAPABILITIES,'derivational_morphology':{k:{'side':v.side,'form':v.form,'source_rule':v.source_rule} for k,v in deriv_affixes.items()},'lexicon':[{'gloss':e.key.gloss,'pos':e.key.pos,'form':forms.get(e.key,''),'derivation':e.expr} for e in entries],'translation_source':str(translation_source) if translation_source else None,'examples':[{'type':t,'english':en,'surface':s,'gloss':gl,'status':status} for t,en,s,gl,status in examples]}
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
