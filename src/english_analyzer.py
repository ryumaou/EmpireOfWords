#!/usr/bin/env python3
"""Shared deterministic English analysis for conlang translation.

This module deliberately analyzes before realization.  It never invents target-language
forms; it reports what it can normalize, classify, and account for.
"""
from __future__ import annotations
import re

IRREGULAR_VERBS = {
 'shone':('shine','past'),'went':('go','past'),'gone':('go','participle'),'came':('come','past'),
 'ran':('run','past'),'sat':('sit','past'),'stood':('stand','past'),'fell':('fall','past'),
 'fallen':('fall','participle'),'blew':('blow','past'),'blown':('blow','participle'),
 'grew':('grow','past'),'grown':('grow','participle'),'ate':('eat','past'),'eaten':('eat','participle'),
 'wore':('wear','past'),'worn':('wear','participle'),'heard':('hear','past'),'thought':('think','past'),
 'brought':('bring','past'),'caught':('catch','past'),'threw':('throw','past'),'thrown':('throw','participle'),
 'saw':('see','past'),'seen':('see','participle'),'met':('meet','past'),'said':('say','past'),
 'made':('make','past'),'lost':('lose','past'),'gave':('give','past'),'knew':('know','past'),
 'known':('know','participle'),'found':('find','past'),'built':('build','past'),'left':('leave','past'),
 'torn':('tear','participle'),'awoke':('awake','past'),'won':('win','past'),'born':('bear','participle'),
 'took':('take','past'),'taken':('take','participle'),'spoke':('speak','past'),'spoken':('speak','participle'),
 'wrote':('write','past'),'written':('write','participle'),'drove':('drive','past'),'driven':('drive','participle'),
 'began':('begin','past'),'begun':('begin','participle'),'sang':('sing','past'),'sung':('sing','participle'),
 'drew':('draw','past'),'drawn':('draw','participle'),'flew':('fly','past'),'flown':('fly','participle'),
}
IRREGULAR_NOUNS={'children':'child','men':'man','women':'woman','people':'person','feet':'foot','teeth':'tooth','mice':'mouse','geese':'goose','leaves':'leaf'}
IRREGULAR_DEGREES={'better':'good','best':'good','worse':'bad','worst':'bad','farther':'far','farthest':'far','further':'far','furthest':'far'}
FUNCTION_WORDS=set('the a an of to in at on by for from with as and or but if when while because than that who whose where which what why how is are am was were be been being do does did have has had will shall can could should would must may might not no this these those my your his her our their its me him us them it i you he she we they there all every each some many much more less very too enough ever never often once twice again now soon today tomorrow yesterday here away together about around down up out over under through upon toward towards after before during between among except near until'.split())
AUX=set('is are am was were be been being do does did have has had will shall can could should would must may might'.split())
MODALS=set('can could should would must may might will shall'.split())
REFLEXIVES={'myself':'1sg','yourself':'2sg','himself':'3sg','herself':'3sg','itself':'3sg','ourselves':'1pl','yourselves':'2pl','themselves':'3pl'}
WH={'who','what','where','when','why','how','which'}
COMPLEMENT_HEADS={'think','know','believe','say','tell','hope','sure','opinion','fact','idea','claim','report','hear','see'}

CAPABILITIES={
 'simple_clause':'supported','copular_clause':'supported','existential':'supported','imperative':'supported',
 'yes_no_question':'limited','wh_question':'limited','coordination':'limited','modal':'limited','perfect':'limited',
 'progressive':'supported','negation':'supported','possessive':'limited','reflexive':'limited','comparison':'limited',
 'relative_clause':'diagnosed','complement_clause':'diagnosed','conditional_clause':'diagnosed','subordinate_clause':'diagnosed',
 'passive':'diagnosed','quotation':'diagnosed','appositive':'diagnosed','phrasal_verb':'limited','weather':'limited',
 'proper_name':'limited'
}

def tokens(text:str):
    t=text.replace('’',"'")
    t=re.sub(r"\b[Ii]t's\b", 'it is', t)
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+",t)

def lemma_candidates(word:str):
    w=word.lower().strip("'\""); out=[]
    if w.endswith("'s") and len(w)>2: out.append(w[:-2])
    if w in REFLEXIVES: out.append(w)
    if w in IRREGULAR_VERBS: out.append(IRREGULAR_VERBS[w][0])
    if w in IRREGULAR_NOUNS: out.append(IRREGULAR_NOUNS[w])
    if w in IRREGULAR_DEGREES: out.append(IRREGULAR_DEGREES[w])
    out.append(w)
    if w.endswith('iest') and len(w)>4: out.append(w[:-4]+'y')
    if w.endswith('ier') and len(w)>3: out.append(w[:-3]+'y')
    if w.endswith('est') and len(w)>4: out.extend([w[:-3],w[:-3]+'e'])
    if w.endswith('er') and len(w)>3: out.extend([w[:-2],w[:-2]+'e'])
    if w.endswith('ies') and len(w)>3: out.append(w[:-3]+'y')
    if w.endswith('ves') and len(w)>3: out.extend([w[:-3]+'f',w[:-3]+'fe'])
    if w.endswith('es') and len(w)>3:
        out.extend([w[:-2],w[:-1]])
        # freezes -> freeze; dances -> dance; fixes -> fix
        if w.endswith('zes'): out.append(w[:-1])
    if w.endswith('ied') and len(w)>4: out.append(w[:-3]+'y')
    if w.endswith('s') and len(w)>2 and not w.endswith('ss'): out.append(w[:-1])
    if w.endswith('ing') and len(w)>4:
        b=w[:-3]; out.extend([b,b+'e'])
        if len(b)>2 and b[-1]==b[-2]: out.append(b[:-1])
    if w.endswith('ed') and len(w)>3:
        b=w[:-2]; out.extend([b,b+'e'])
        # danced -> dance, dressed -> dress (already covered), carried -> carry
        if b.endswith('c'): out.append(b+'e')
        if b.endswith('i'): out.append(b[:-1]+'y')
        if len(b)>2 and b[-1]==b[-2]: out.append(b[:-1])
    if w.endswith('ly') and len(w)>3:
        b=w[:-2]; out.append(b)
        if b.endswith('i'): out.append(b[:-1]+'y')
    seen=[]
    for x in out:
        if x and x not in seen: seen.append(x)
    return seen

def lexical_match(by,word,preferred_pos=None):
    """Resolve an English token without allowing an unrelated homograph to
    override an inflected verb. A context-free lookup retains its old behavior.
    """
    candidates=lemma_candidates(word)
    if preferred_pos:
        matches=[c for c in candidates if any(pos==preferred_pos or pos.startswith(preferred_pos) for pos,_ in by.get(c,()))]
        if matches:
            # For explicit inflections, prefer a dictionary lemma over a spurious
            # separately seeded surface form (danced:v vs dance:v).
            w=word.lower()
            if w.endswith(('ed','ing','es')) or w in IRREGULAR_VERBS:
                derived=[c for c in matches if c!=w]
                if derived:return derived[0]
            return matches[0]
    for c in candidates:
        if c in by:return c
    return None

def _is_proper(raw_token, index):
    bare=raw_token.rstrip("'s").rstrip("’s")
    return bare[:1].isupper() and bare.lower() not in FUNCTION_WORDS|{'i'}

def detect_constructions(raw, low_tokens, by=None):
    low=' '.join(low_tokens); found=[]
    if 'if' in low_tokens: found.append('conditional_clause')
    if any(x in low_tokens for x in ('because','while')): found.append('subordinate_clause')
    if any(x in low_tokens for x in ('who','whose','which')): found.append('relative_clause')
    # "that" is relative only when it follows a nominal; after a cognition/reporting
    # head or copular predicate it is a complementizer. Demonstrative "that house" is neither.
    for i,w in enumerate(low_tokens):
        if w!='that': continue
        prev=low_tokens[i-1] if i else '' ; nxt=low_tokens[i+1] if i+1<len(low_tokens) else ''
        if prev in COMPLEMENT_HEADS or any(x in COMPLEMENT_HEADS for x in low_tokens[max(0,i-4):i]):
            found.append('complement_clause')
        elif i>0 and prev not in AUX|MODALS|{'to','and','or','but'} and nxt in {'i','you','he','she','we','they','it'}:
            found.append('relative_clause')
    if re.search(r'\b(?:is|are|was|were|be|been|being)\s+\w+(?:ed|en)\b',low) and ' by ' in ' '+low+' ': found.append('passive')
    comp=False
    if ' than ' in ' '+low+' ' or any(w in low_tokens for w in ('more','less','better','worse')): comp=True
    elif by:
        for w in low_tokens:
            if not w.endswith(('er','est')): continue
            # An exact lexical item such as 'together' is not comparative merely
            # because its spelling ends in -er. Only a derived candidate may
            # license comparative analysis.
            exact=by.get(w,[])
            if exact:
                continue
            for cand in lemma_candidates(w):
                if cand == w:
                    continue
                if any(pos.startswith('adj') or pos.startswith('adv') for pos,_ in by.get(cand,[])):
                    comp=True; break
            if comp: break
    if comp: found.append('comparison')
    if any(w in REFLEXIVES for w in low_tokens): found.append('reflexive')
    if any(w in MODALS for w in low_tokens): found.append('modal')
    # HAVE is perfect only when it auxiliates a participle/been; lexical HAVE (e.g.
    # 'Have some tea') is not perfect.
    for i,w in enumerate(low_tokens[:-1]):
        if w not in ('has','have','had'): continue
        nxt=low_tokens[i+1]
        if nxt=='been' or nxt in IRREGULAR_VERBS and IRREGULAR_VERBS[nxt][1]=='participle' or nxt.endswith(('ed','en')):
            found.append('perfect'); break
    # Progressive requires a BE auxiliary immediately licensing a verbal -ing form.
    # A noun such as STRING in 'This string is too short' is not progressive merely
    # because its spelling ends in -ing.
    for i,w in enumerate(low_tokens[:-1]):
        if w not in ('is','are','am','was','were','be','been','being'): continue
        nxt=low_tokens[i+1]
        if not nxt.endswith('ing'): continue
        lemma=lexical_match(by,nxt) if by else None
        vals=by.get(lemma,[]) if by and lemma else []
        if not vals or any(p=='v' for p,_ in vals):
            found.append('progressive'); break
    if 'not' in low_tokens or 'never' in low_tokens: found.append('negation')
    if any(w in low_tokens for w in ('and','or','but')): found.append('coordination')
    # Multiple commas often mark coordinated predicates or introductory phrases,
    # not apposition. Diagnose apposition only for a bounded nominal interruption.
    comma_parts=[x.strip() for x in raw.split(',')]
    if len(comma_parts)>=3:
        middle=comma_parts[1].lower()
        outer=(comma_parts[0]+' '+comma_parts[-1]).lower()
        # Conservative: vocative/appositive NP interruptions, not adverbial predicates.
        if middle and not any(w.endswith('ly') for w in middle.split()) and not any(v in middle.split() for v in ('dressed','went','watched','saw','sat','stood','looked')):
            if any(x in middle.split() for x in ('son','madam','girl','room','bedroom','kitchen','mite')):
                found.append('appositive')
    if any(q in raw for q in ('“','”','"')): found.append('quotation')
    if raw.rstrip().endswith('?'): found.append('wh_question' if low_tokens and low_tokens[0] in WH else 'yes_no_question')
    # Imperative requires imperative punctuation or an initial lexical verb; sentence
    # length alone is never evidence for imperative mood.
    first=low_tokens[0] if low_tokens else ''
    first_is_verb=bool(by and first in by and any(p=='v' or p.startswith('v') for p,_ in by[first]))
    aux_imperative = first in ('be','do','have') and not raw.rstrip().endswith('?') and 'perfect' not in found
    # Exclamation marks alone do not make a clause imperative (e.g. 'Alas!' or
    # 'This string is too short!').  Imperative force requires an initial verb.
    if (first_is_verb and first not in AUX) or aux_imperative or first in ("let's",'lets'): found.append('imperative')
    if low_tokens[:2] in (['it','is'],['it','was']) and any(w in low_tokens for w in ('rain','raining','snow','snowing')): found.append('weather')
    if any(w.endswith("'s") and w not in ("let's",) for w in low_tokens): found.append('possessive')
    return list(dict.fromkeys(found))

def analyze(raw, by):
    original=tokens(raw); low=[x.lower() for x in original]
    constructions=detect_constructions(raw,low,by)
    lexical=[]; missing=[]; grammatical=[]; proper=[]
    for i,(surface,w) in enumerate(zip(original,low)):
        if w in ("let's",'lets'):
            grammatical.append({'token':w,'role':'hortative'}); continue
        if w in REFLEXIVES:
            grammatical.append({'token':w,'role':'reflexive','person':REFLEXIVES[w]}); continue
        if w.endswith("'s") and w not in ("let's",):
            stem=w[:-2]; m=lexical_match(by,stem)
            if m: lexical.append({'token':w,'lemma':m,'feature':'possessive'})
            elif _is_proper(surface,i): proper.append(surface[:-2]); grammatical.append({'token':w,'role':'proper_possessive'})
            else: missing.append(w)
            continue
        if w in FUNCTION_WORDS or w.isdigit(): grammatical.append({'token':w,'role':'function'}); continue
        # Inflected predicates require a verbal lemma, not an accidental noun
        # homograph (freezes -> freeze, rather than freez:n).
        verbal_inflection=(w in IRREGULAR_VERBS or (w.endswith(('ed','ing','es')) and w not in IRREGULAR_NOUNS))
        verb=lexical_match(by,w,'v') if verbal_inflection else None
        m=verb or lexical_match(by,w)
        if m: lexical.append({'token':w,'lemma':m})
        elif _is_proper(surface,i): proper.append(surface); grammatical.append({'token':w,'role':'proper_name'})
        else: missing.append(w)
    return {'tokens':low,'original_tokens':original,'constructions':constructions,'lexical_items':lexical,
            'grammatical_items':grammatical,'proper_names':proper,'missing_lexemes':list(dict.fromkeys(missing))}
