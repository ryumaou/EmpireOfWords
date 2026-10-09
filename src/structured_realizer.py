#!/usr/bin/env python3
"""Conservative structured English -> generated-language realization.

v6.6 expands the first structured pass without weakening completeness: a parse is
accepted only when every represented lexical/grammatical feature receives a receipt.
"""
from __future__ import annotations
import re
import copy
from english_analyzer import IRREGULAR_VERBS
from ir import NPIR, PPIR, PredicateIR, ClauseIR, ModifierIR, ComparisonIR, ParticipialModifierIR

PRON={'i':'1sg','me':'1sg','you':'2sg','he':'3sg','him':'3sg','she':'3sg','her':'3sg','we':'1pl','us':'1pl','they':'3pl','them':'3pl','it':'3sg'}
DET={'the','a','an','this','that','these','those'}
QUANT={'some','many','several','all','every','each','few','both'}
POSS={'my':'1sg','your':'2sg','his':'3sg','her':'3sg','our':'1pl','their':'3pl','its':'3sg'}
PREP={'with','by','to','in','at','on','from','for','into','onto','under','over','near','beside','across','through','upon','toward','towards','after','before','about','of','like','during','until'}
PARTICLES={'away','up','down','around','back','out','off','over','through'}
AUX={'will','shall','can','could','should','would','must','may','might','do','does','did','is','are','am','was','were','has','have','had','been','being','be'}
MODALS={'can','could','should','would','must','may','might'}
COPULA={'be','is','are','am','was','were','been','being'}
LINKING={'seem','feel','taste','sound','look','grow','become'}
ADV_COMMON={'here','there','now','soon','today','tomorrow','yesterday','again','together','probably','usually','often','always','ever','never','then','indeed','enough','first','slowly','sharply','patiently','hastily','early','twice','once'}
FREQ={'usually','often','always','ever','never','once','twice'}
TEMP={'now','soon','today','tomorrow','yesterday','then','early'}
DEGREE={'very','too','much','more','less','quite'}
CONJ={'and','or','but'}


def _pos(by,lemma,prefix):
    def ok(p):
        if prefix=='n' and p in ('dim','aug'): return True
        return p==prefix or p.startswith(prefix)
    return any(ok(p) for p,_ in by.get(lemma,[]))
def _form(by,lemma,prefixes):
    for p,f in by.get(lemma,[]):
        if any((x=='n' and p in ('dim','aug')) or p==x or p.startswith(x) for x in prefixes): return f
    return None

def _convert_form(by,lemma,target,g):
    direct=_form(by,lemma,(target,))
    if direct:return direct
    source=None; conv=None
    if target=='v':
        if _form(by,lemma,('n',)): source=_form(by,lemma,('n',)); conv='noun_to_verb'
        elif _form(by,lemma,('adj',)): source=_form(by,lemma,('adj',)); conv='adjective_to_verb'
    elif target=='adj' and _form(by,lemma,('n',)):
        source=_form(by,lemma,('n',)); conv='noun_to_adjective'
    if not source or not conv:return None
    spec=g.get('lexical_conversion',{}).get(conv,{})
    if spec.get('strategy')=='zero': return source
    if spec.get('strategy')=='affix':
        mm=g.get('morphemes',{}).get(spec.get('morpheme',''))
        if mm:return (mm['form']+source) if mm.get('side')=='prefix' else (source+mm['form'])
    return None

def _lemma_for_pos(word,by,lemma_candidates,target,g):
    candidates=lemma_candidates(word)
    if target=='v' and (word.endswith(('ed','ing','es')) or word in IRREGULAR_VERBS):
        # Prefer canonical verbal stems over preflight-created surface lexemes.
        candidates=[x for x in candidates if x!=word]+[word]
    for cand in candidates:
        if _convert_form(by,cand,target,g): return cand
    return None

def _lemma(word, by, lexical_match): return lexical_match(by,word) or word

def _copula_lemma(by):
    for x in ('be','be (copula)','be (temporary state)','be (age)','be (located)'):
        if _pos(by,x,'v'): return x
    return None

def _split_once(words, choices):
    for i,w in enumerate(words):
        if w in choices: return words[:i],w,words[i+1:]
    return words,None,[]

def _degree_for(raw, lemma, by):
    if raw in ('more','less'): return 'comparative'
    if raw in ('most','least'): return 'superlative'
    if raw in ('better','worse'): return 'comparative'
    if raw in ('best','worst'): return 'superlative'
    if raw.endswith('est') and lemma!=raw and (_pos(by,lemma,'adj') or _pos(by,lemma,'adv')): return 'superlative'
    if raw.endswith('er') and lemma!=raw and (_pos(by,lemma,'adj') or _pos(by,lemma,'adv')): return 'comparative'
    return 'positive'

def parse_np(words,by,lexical_match):
    words=[w for w in words if w]
    if not words:return None
    # NP coordination, recursively represented rather than flattened.
    left,cj,right=_split_once(words,CONJ)
    if cj and left and right:
        a=parse_np(left,by,lexical_match); b=parse_np(right,by,lexical_match)
        if a and b:
            a.conjunction=cj; a.coordinated=[b]; return a
    if len(words)==1 and words[0] in PRON: return NPIR(words,person=PRON[words[0]],head=words[0])
    poss=None
    if words and words[0] in POSS:
        poss=NPIR([words[0]],person=POSS[words[0]],head=words[0]); words=words[1:]
    det=None
    if words and words[0] in DET: det=words.pop(0)
    # Productive English participial NP modifier: tiger wearing a bell. Preserve it
    # as a non-finite predicate rather than letting the object noun become the NP head.
    participial=[]
    ing_i=next((i for i,w in enumerate(words[1:],1) if w.endswith('ing') and lexical_match(by,w)),None)
    if ing_i is not None:
        vl=_lemma(words[ing_i],by,lexical_match)
        if _pos(by,vl,'v'):
            pobj=parse_np(words[ing_i+1:],by,lexical_match) if words[ing_i+1:] else None
            participial=[ParticipialModifierIR(vl,pobj)]
            words=words[:ing_i]
    # Preserve recursive PP attachments inside noun phrases: man WITH a stick,
    # girls WITH wreaths OF flowers. These belong to the NP, not the predicate.
    attached_pps=[]
    prep_i=next((i for i,w in enumerate(words) if w in PREP),None)
    if prep_i is not None:
        remaining=words[prep_i:]
        words=words[:prep_i]
        while remaining:
            ad=remaining[0]
            if ad not in PREP:return None
            # The entire tail belongs to the next NP; recursion handles OF flowers.
            obj=parse_np(remaining[1:],by,lexical_match)
            if obj is None:return None
            attached_pps.append(PPIR(ad,obj))
            remaining=[]
    # English genitive can itself be a multiword NP: the little girl's doll.
    poss_i=next((i for i,w in enumerate(words[:-1]) if w.endswith("'s") or w.endswith('’s')),None)
    if poss_i is not None:
        poss_words=words[:poss_i+1]; poss_words[-1]=poss_words[-1][:-2]
        poss=parse_np(poss_words,by,lexical_match)
        words=words[poss_i+1:]
    candidates=[]
    for i,w in enumerate(words):
        lm=_lemma(w,by,lexical_match)
        if _pos(by,lm,'n'): candidates.append((i,lm,w))
    if not candidates:return None
    hi,head,raw=candidates[-1]
    adjectives=[]; noun_modifiers=[]; numeral=None; quantifier=None; comparison=None
    prefix=words[:hi]
    skip=False
    for i,w in enumerate(prefix):
        if skip: skip=False; continue
        lm=_lemma(w,by,lexical_match)
        if _pos(by,lm,'num'): numeral=lm; continue
        if w in QUANT or _pos(by,lm,'det'):
            quantifier=lm; continue
        if w in ('more','less','most','least') and i+1<len(prefix):
            al=_lemma(prefix[i+1],by,lexical_match)
            if _pos(by,al,'adj'):
                adjectives.append(al); comparison=ComparisonIR('superlative' if w in ('most','least') else 'comparative',marker=w); skip=True; continue
        if _pos(by,lm,'adj'):
            adjectives.append(lm)
            d=_degree_for(w,lm,by)
            if d!='positive': comparison=ComparisonIR(d,marker=w)
        elif _pos(by,lm,'n'):
            # English productive noun adjunct: sea water, apple tree, spring sun.
            noun_modifiers.append(lm)
    plural=(raw.endswith('s') and not raw.endswith(('ss','us','is'))) or raw in ('children','men','women','people') or numeral not in (None,'one') or quantifier in ('many','several','all','both','few')
    return NPIR(words,head=head,determiner=det,number='plural' if plural else 'singular',adjectives=adjectives,noun_modifiers=noun_modifiers,participial_modifiers=participial,attached_pps=attached_pps,numeral=numeral,quantifier=quantifier,possessor=poss,comparison=comparison)

def _modifier(word,by,lexical_match):
    lm=_lemma(word,by,lexical_match)
    if word in DEGREE: kind='degree'
    elif word in FREQ: kind='frequency'
    elif word in TEMP: kind='temporal'
    else: kind='manner'
    if word in ADV_COMMON or word.endswith('ly') or _pos(by,lm,'adv') or (word.endswith('ly') and _pos(by,lm,'adj')):
        return ModifierIR(lm,kind,word)
    return None

def parse_clause(raw,by,lexical_match,english_tokens,lemma_candidates,constructions,g=None):
    toks=[x.lower() for x in english_tokens(raw)]
    if not toks:return None
    # Causal subordination is preserved in the IR, but deliberately remains
    # diagnosed/unsupported until a licensed target-language linker is available.
    # Do not flatten the reason clause into a single predicate.
    if 'subordinate_clause' in constructions and re.search(r'\bbecause\b',raw,re.I):
        left,right=re.split(r'\bbecause\b',raw,maxsplit=1,flags=re.I)
        limited=[c for c in constructions if c!='subordinate_clause']
        main=parse_clause(left.strip()+'.',by,lexical_match,english_tokens,lemma_candidates,limited,g)
        reason=parse_clause(right.strip(' .!?')+'.',by,lexical_match,english_tokens,lemma_candidates,[],g)
        if main and reason:
            main.subordinate=reason
            main.subordinate_relation='cause'
            main.source_tokens=english_tokens(raw)
            return main
        return None
    if any(c in constructions for c in ('relative_clause','appositive','conditional_clause','passive','quotation','complement_clause')): return None
    # Degree questions are not ordinary WHERE/WHEN adjunct questions. Preserve
    # both HOW and its adjective; reconstruct the uninverted copular clause.
    degree_match=re.match(r'^\s*how\s+([a-z]+)\s+(is|are|was|were)\s+(.+?)\s*\?\s*$',raw,re.I)
    if degree_match:
        adjective,aux,subject=degree_match.groups()
        lemma=_lemma(adjective,by,lexical_match)
        if not _pos(by,lemma,'adj'):return None
        statement=subject+' '+aux+' '+adjective+'.'
        base=parse_clause(statement,by,lexical_match,english_tokens,lemma_candidates,[],g)
        if not base or base.predicate.complement_kind!='adjective' or base.predicate.complement.head!=lemma:
            return None
        base.clause_type='wh_question';base.wh_word='how';base.wh_degree=lemma
        base.source_tokens=english_tokens(raw)
        return base
    # Let's is a hortative, not possessive; keep it outside structured pass until a
    # dedicated inclusive imperative strategy exists.
    if toks[:2]==['let','s'] or (toks and toks[0] in ("let's",'lets')):
        # Inclusive hortative: represent as first-person-plural imperative.
        rest=toks[1:] if toks and toks[0] in ("let's",'lets') else toks[2:]
        if rest:
            lm=_lemma_for_pos(rest[0],by,lemma_candidates,'v',g or {}) or _lemma(rest[0],by,lexical_match)
            if _convert_form(by,lm,'v',g or {}):
                return ClauseIR(NPIR(['we'],head='we',person='1pl'),PredicateIR(lm,mood='imperative'),'hortative',source_tokens=english_tokens(raw))
        return None
    # Comma-separated action series: retain each finite predicate, rather than
    # silently reducing an A, B, and C series to its first and last verbs.
    # Only enter this branch when the initial segment and EVERY subsequent
    # segment can be parsed as a predicate; ordinary comma modifiers fall back.
    if ',' in raw and re.search(r'\b(?:and|or|but)\b', raw, re.I):
        segments=[part.strip(' ,;.!?') for part in raw.split(',')]
        if len(segments)>=3:
            last=segments[-1]
            match=re.match(r'^(and|or|but)\s+(.+)$',last,re.I)
            if match:
                conjunction=match.group(1).lower()
                segments[-1]=match.group(2)
                subcons=[c for c in constructions if c!='coordination']
                first=parse_clause(segments[0]+'.',by,lexical_match,english_tokens,lemma_candidates,subcons,g)
                if first and first.predicate and first.predicate.lemma:
                    parsed=[]
                    for segment in segments[1:]:
                        # This construction shares its subject across the series.
                        # The synthetic subject is discarded after parsing.
                        child=parse_clause('They '+segment+'.',by,lexical_match,english_tokens,lemma_candidates,subcons,g)
                        if not child or not child.predicate or not child.predicate.lemma:
                            parsed=[]; break
                        parsed.append(child.predicate)
                    if len(parsed)==len(segments)-1:
                        first.predicate.conjunction=conjunction
                        first.predicate.coordinated.extend(parsed)
                        first.source_tokens=english_tokens(raw)
                        return first
    # Predicate/clause coordination: parse both predicates and preserve the conjunction.
    # Preserve sentence-level interrogative scope across the coordinated predicate.
    # A question about A OR B must mark the entire construction, not just a child.
    # Right-hand predicate may omit the shared English subject; supply a temporary
    # pronoun only for analysis, then discard it and inherit the real subject.
    for cj in ('and','but','or'):
        m=re.search(r'\b'+cj+r'\b', raw, flags=re.I)
        if not m: continue
        left_raw=raw[:m.start()].strip(' ,;'); right_raw=raw[m.end():].strip(' ,;.!?')
        if not left_raw or not right_raw: continue
        # Only split here when both sides actually contain predicates. NP and
        # adjective coordination belong inside their containing constituent.
        lt=[x.lower() for x in english_tokens(left_raw)]; rt=[x.lower() for x in english_tokens(right_raw)]
        def has_pred(xs):
            return any(x in AUX or any(_form(by,c,('v',)) for c in lemma_candidates(x)) for x in xs)
        if not (has_pred(lt) and has_pred(rt)): continue
        subcons=[c for c in constructions if c!='coordination']
        left=parse_clause(left_raw+('?' if raw.rstrip().endswith('?') else '.'),by,lexical_match,english_tokens,lemma_candidates,subcons,g)
        if left:
            # A complete right-hand clause must retain its OWN subject. The old
            # synthetic "They" silently replaced explicit subjects such as BIRD.
            explicit=parse_clause(right_raw+'.',by,lexical_match,english_tokens,lemma_candidates,subcons,g)
            if explicit and explicit.subject and explicit.predicate and explicit.predicate.lemma:
                # Reject a bare predicate misread as a nominal subject.
                right_first=rt[0] if rt else ''
                if right_first in DET or right_first in PRON or right_first in POSS or right_raw[:1].isupper():
                    left.conjunction=cj; left.coordinated=explicit
                    left.source_tokens=english_tokens(raw)
                    if raw.rstrip().endswith('?'):
                        left.clause_type='yes_no_question'
                    return left
            # Shared-subject coordination is a distinct grammatical operation.
            right=parse_clause('They '+right_raw+'.',by,lexical_match,english_tokens,lemma_candidates,subcons,g)
            if right and right.predicate and right.predicate.lemma:
                left.predicate.conjunction=cj; left.predicate.coordinated=[right.predicate]
                left.source_tokens=english_tokens(raw)
                if raw.rstrip().endswith('?'):
                    left.clause_type='yes_no_question'
                return left
    q=raw.rstrip().endswith('?'); imp='imperative' in constructions
    # WH-fronting is represented as an interrogative feature, not a subject.
    # Restrict to adjunct questions whose missing constituent can be realized
    # without inventing an object or a copular predicate.
    wh_word=None
    if q and toks and toks[0] in ('where','when'):
        wh_word=toks.pop(0)
        if not toks:return None
    front_aux=None
    if q and toks and toks[0] in AUX: front_aux=toks.pop(0)
    # leading sentence adverbs are modifiers, not subject material
    leading=[]
    while toks:
        if front_aux in COPULA and toks[0] in ('today','tomorrow','yesterday'):
            break
        m=_modifier(toks[0],by,lexical_match)
        if not m: break
        leading.append(m); toks.pop(0)
    # Copular BE with adjective/nominal complement has no English lexical verb after
    # the auxiliary. Represent BE explicitly when possible.
    cop_i=next((i for i,w in enumerate(toks) if w in COPULA),None)
    vi=None; verb_lemma=None; copular=False
    if imp and toks:
        if toks[0]=='be':
            lm=_copula_lemma(by)
        else:
            lm=_lemma_for_pos(toks[0],by,lemma_candidates,'v',g or {}) or _lemma(toks[0],by,lexical_match)
        if lm and (_convert_form(by,lm,'v',g or {}) or toks[0]=='be'):
            vi=0; verb_lemma=lm; copular=toks[0]=='be'
    if vi is None:
        # When a modal/future auxiliary is present, the lexical predicate after it
        # outranks an earlier participial modifier (A tiger wearing ... will starve).
        modal_i=next((i for i,w in enumerate(toks) if w in MODALS or w in ('will','shall','did','do','does')),None)
        if modal_i is not None:
            for i in range(modal_i+1,len(toks)):
                lm=_lemma_for_pos(toks[i],by,lemma_candidates,'v',g or {})
                if lm: vi=i; verb_lemma=lm; copular=lm in LINKING; break
    if vi is None:
        verb_candidates=[]
        for i,w in enumerate(toks):
            if w in AUX: continue
            if w in LINKING or any(w.startswith(x) for x in ('seem','feel','sound')):
                lm=_lemma_for_pos(w,by,lemma_candidates,'v',g or {})
            else:
                lm=next((c for c in ([x for x in lemma_candidates(w) if x!=w]+[w] if w.endswith(('ed','ing','es')) else lemma_candidates(w)) if _form(by,c,('v',))),None)
            if lm: verb_candidates.append((i,w,lm))
        # Prefer a verb whose left edge forms a plausible subject NP. This prevents
        # homographs such as FIRE in 'the fire feels hot' from stealing the predicate slot.
        # Prefer overtly inflected lexical predicates over homographic bare
        # nouns (the west wind BLEW; WIND can also be a verb).
        def verb_score(item):
            i,w,lm=item
            explicit=(w in IRREGULAR_VERBS or
                      (w.endswith(('ed','ing','es')) and lm!=w))
            return (int(explicit), i)
        eligible=[item for item in verb_candidates if item[0]>0 and
                  parse_np([x for x in toks[:item[0]] if x not in AUX],by,lexical_match)]
        chosen=max(eligible,key=verb_score) if any(verb_score(item)[0] for item in eligible) else (eligible[0] if eligible else None)
        if chosen is None and verb_candidates: chosen=verb_candidates[0]
        if chosen:
            vi,w,verb_lemma=chosen; copular=verb_lemma in LINKING or w.rstrip('s') in LINKING
    # Fronted copula question: Are you hungry? / Is today Monday?
    if vi is None and front_aux in COPULA:
        # first NP/pronoun is subject; remainder is handled as complement below
        for cut in range(1,len(toks)+1):
            cand=parse_np(toks[:cut],by,lexical_match)
            if cand or (cut==1 and toks[0] in ('today','tomorrow','yesterday') and _form(by,toks[0],('adv','n'))):
                vi=cut; verb_lemma=_copula_lemma(by); copular=True; break
        if not verb_lemma or not _pos(by,verb_lemma,'v'): return None
    if vi is None and cop_i is not None:
        vi=cop_i; verb_lemma=_copula_lemma(by); copular=True
        if not verb_lemma or not _pos(by,verb_lemma,'v'): return None
    if vi is None:return None
    front_copula=bool(front_aux in COPULA and copular and vi is not None and (vi>=len(toks) or toks[vi] not in COPULA))
    subject_words=[]; premods=[]
    for w in toks[:vi]:
        if w in AUX: continue
        m=None if front_aux in COPULA and w in ('today','tomorrow','yesterday') else _modifier(w,by,lexical_match)
        if m: premods.append(m)
        else: subject_words.append(w)
    subject=None if imp else parse_np(subject_words,by,lexical_match)
    if not imp and subject is None and front_aux in COPULA and len(subject_words)==1 and subject_words[0] in ('today','tomorrow','yesterday'):
        subject=NPIR(subject_words,head=subject_words[0])
    if not imp and subject is None:return None
    pred=PredicateIR(verb_lemma,mood='imperative' if imp else 'indicative',modifiers=leading+premods)
    auxiliaries=[]
    if front_aux: auxiliaries.append(front_aux)
    auxiliaries += [w for w in toks[:vi] if w in AUX]
    if vi < len(toks) and toks[vi] in AUX: auxiliaries.append(toks[vi])
    # A lexical English past form must carry tense even when it has not been
    # normalized to an auxiliary construction.
    if vi<len(toks):
        verb_token=toks[vi]
        if verb_token in IRREGULAR_VERBS and IRREGULAR_VERBS[verb_token][1]=='past':
            pred.tense='past'
        elif verb_token.endswith('ed') and verb_lemma!=verb_token:
            pred.tense='past'
    for a in auxiliaries:
        if a in ('will','shall'): pred.tense='future'
        elif a in ('did','was','were','had'): pred.tense='past'
        if a in MODALS: pred.modal=a
        if a in ('has','have','had') and verb_lemma!='have' and 'perfect' in constructions and 'perfect' not in pred.aspect: pred.aspect.append('perfect')
        if a in ('is','are','am','was','were','been','being') and 'progressive' in constructions and 'progressive' not in pred.aspect: pred.aspect.append('progressive')
    if vi < len(toks) and toks[vi].endswith('ing') and 'progressive' in constructions and 'progressive' not in pred.aspect: pred.aspect.append('progressive')
    rest=toks[vi:] if front_copula else toks[vi+1:]
    if 'not' in rest or 'negation' in constructions: pred.negative=True; rest=[x for x in rest if x!='not']
    # comparison standard: keep 'than NP' out of ordinary PP processing.
    if 'than' in rest:
        ti=rest.index('than'); std=parse_np(rest[ti+1:],by,lexical_match); rest=rest[:ti]
        pred.comparison=ComparisonIR('comparative',standard=std,marker='than')
    pi=next((i for i,w in enumerate(rest) if w in PREP),None)
    core=rest if pi is None else rest[:pi]; ppwords=[] if pi is None else rest[pi:]
    npwords=[]
    if any(w in ('more','less') for w in core):
        pred.comparison=pred.comparison or ComparisonIR('comparative',marker=next(w for w in core if w in ('more','less')))
    for i,w in enumerate(core):
        lm=_lemma(w,by,lexical_match)
        if w in PARTICLES: pred.particles.append(w)
        else:
            m=_modifier(w,by,lexical_match)
            if m: pred.modifiers.append(m)
            else: npwords.append(w)
    if npwords:
        # Coordinated predicative adjectives: small but strong; blue or gray.
        cidx=next((i for i,w in enumerate(npwords) if w in CONJ),None)
        if cidx is not None and cidx>0 and cidx+1<len(npwords):
            leftv=[x for x in npwords[:cidx] if x not in DEGREE]; rightv=[x for x in npwords[cidx+1:] if x not in DEGREE]
            if len(leftv)==1 and len(rightv)==1:
                la=_lemma(leftv[0],by,lexical_match); ra=_lemma(rightv[0],by,lexical_match)
                if _pos(by,la,'adj') and _pos(by,ra,'adj'):
                    pred.complement=NPIR(leftv,head=la); pred.complement_kind='adjective'; copular=True
                    pred.complement_conjunction=npwords[cidx]; pred.coordinated_complements=[NPIR(rightv,head=ra)]
                    npwords=[]
        # Predicate/adjective comparison: more slowly is handled as modifiers; taller etc as complement.
        # A definite superlative is an adjective predicate, not a noun object:
        # "the dog is the biggest" must not silently drop THE/BIGGEST.
        # Only consume the article here when an overt superlative is present.
        superlative_adj=None
        if copular and len(npwords)==2 and npwords[0]=='the':
            candidate=_lemma(npwords[1],by,lexical_match)
            if _pos(by,candidate,'adj') and _degree_for(npwords[1],candidate,by)=='superlative':
                superlative_adj=candidate
        if superlative_adj:
            pred.complement=NPIR(npwords,head=superlative_adj)
            pred.complement_kind='adjective'
            pred.comparison=ComparisonIR('superlative',marker=npwords[1])
            npwords=[]
        np=parse_np(npwords,by,lexical_match) if npwords else None
        if np: pred.object=np
        elif not superlative_adj:
            # remove degree marker before adjective complement
            vals=[x for x in npwords if x not in DEGREE]
            if len(vals)==1:
                lm=_lemma(vals[0],by,lexical_match)
                if _pos(by,lm,'adj'):
                    pred.complement=NPIR(vals,head=lm); pred.complement_kind='adjective'; copular=True
                    d='comparative' if any(x in ('more','less') for x in npwords) else _degree_for(vals[0],lm,by)
                    if d!='positive': pred.comparison=pred.comparison or ComparisonIR(d,marker=vals[0])
                elif _pos(by,lm,'n'):
                    pred.complement=NPIR(vals,head=lm); pred.complement_kind='nominal'; copular=True
    while ppwords:
        ad=ppwords.pop(0); nxt=next((i for i,w in enumerate(ppwords) if w in PREP),len(ppwords))
        obj=parse_np(ppwords[:nxt],by,lexical_match)
        if obj: pred.pps.append(PPIR(ad,obj))
        else: return None
        ppwords=ppwords[nxt:]
    return ClauseIR(subject,pred,'wh_question' if wh_word else 'yes_no_question' if q else 'imperative' if imp else 'declarative',source_tokens=english_tokens(raw),wh_word=wh_word)

def _conj_form(g,cj,by): return g.get('particles',{}).get(cj) or _form(by,cj,('conj',))

def realize_np(np,g,by,noun_form,possessive_phrase,adjective_form=None,case='nominative'):
    if np is None:return None,None,set()
    if np.person:
        f=g.get('pronouns',{}).get(np.person); return (f,np.person.upper(),{np.head or np.person}) if f else (None,None,set())
    nf=_form(by,np.head,('n',)) if np.head else None
    if not nf and np.head in ('today','tomorrow','yesterday') and np.tokens==[np.head]:
        adv=_form(by,np.head,('adv',))
        if adv:return adv,np.head.upper(),{np.head}
    if not nf:return None,None,set()
    surf=noun_form(nf,g,np.number,case if case in g.get('noun',{}).get('cases',[]) else 'nominative'); gloss=np.head.upper()+('.PL' if np.number=='plural' else '')+(':'+case.upper() if case!='nominative' and case in g.get('noun',{}).get('cases',[]) else ''); receipts={np.head}
    # Articles/demonstratives are target-grammar morphology, not discarded English scaffolding.
    if np.determiner in ('the','a','an'):
        key='definite_article' if np.determiner=='the' else 'indefinite_article'
        if key in g.get('morphemes',{}):
            mm=g['morphemes'][key]; surf=(mm['form']+surf) if mm.get('side')=='prefix' else (surf+mm['form']); gloss += '-DEF' if key=='definite_article' else '-INDEF'
    elif np.determiner in ('this','that','these','those'):
        dk={'this':'proximal_singular','that':'distal_singular','these':'proximal_plural','those':'distal_plural'}[np.determiner]
        df=g.get('demonstratives',{}).get(dk)
        if df: surf=df+' '+surf; gloss=dk.upper()+' '+gloss
    # Productive noun compounds are language-specific but do not require a fake adjective sense.
    for nm in np.noun_modifiers:
        mf=_form(by,nm,('n',))
        if not mf:return None,None,set()
        if g.get('realization_profile',{}).get('noun_compound_order','modifier-head')=='modifier-head':
            surf=mf+' '+surf; gloss=nm.upper()+' '+gloss
        else:
            surf=surf+' '+mf; gloss=gloss+' '+nm.upper()
        receipts.add(nm)
    if np.quantifier:
        qf=_form(by,np.quantifier,('det','num','adj'))
        if not qf:return None,None,set()
        surf=qf+' '+surf; gloss=np.quantifier.upper()+' '+gloss; receipts.add(np.quantifier)
    for a in np.adjectives:
        af=_form(by,a,('adj',))
        if not af:return None,None,set()
        degree=np.comparison.degree if np.comparison and a==np.adjectives[-1] else 'positive'
        if adjective_form: af=adjective_form(af,g,degree)
        if degree!='positive': receipts.add('comparison')
        if g.get('adjective_position')=='before': surf=af+' '+surf; gloss=a.upper()+('-COMP ' if degree=='comparative' else '-SUPER ' if degree=='superlative' else ' ')+gloss
        else: surf=surf+' '+af; gloss=gloss+' '+a.upper()+('-COMP' if degree=='comparative' else '-SUPER' if degree=='superlative' else '')
        receipts.add(a)
    if np.numeral:
        numf=_form(by,np.numeral,('num',))
        if not numf:return None,None,set()
        surf=numf+' '+surf; gloss=np.numeral.upper()+' '+gloss; receipts.add(np.numeral)
    # Non-finite/participial modifiers use a strategy generated with the language.
    for pm in np.participial_modifiers:
        vf=_convert_form(by,pm.lemma,'v',g)
        if not vf:return None,None,set()
        spec=g.get('nonfinite',{}).get('participial_modifier',{})
        strategy=spec.get('strategy','particle')
        if strategy=='affix':
            mm=g.get('morphemes',{}).get(spec.get('morpheme',''))
            if not mm:return None,None,set()
            vf=(mm['form']+vf) if mm.get('side')=='prefix' else (vf+mm['form'])
        elif strategy=='particle':
            mark=g.get('particles',{}).get(spec.get('particle','participle'))
            if not mark:return None,None,set()
            vf=mark+' '+vf
        po=pg=''; pr=set()
        if pm.object:
            po,pg,pr=realize_np(pm.object,g,by,noun_form,possessive_phrase,adjective_form,'accusative')
            if not po:return None,None,set()
        chunk=' '.join(x for x in (vf,po) if x); cgl=' '.join(x for x in (pm.lemma.upper()+'-PTCP',pg) if x)
        if spec.get('position','after')=='before': surf=chunk+' '+surf; gloss=cgl+' '+gloss
        else: surf=surf+' '+chunk; gloss=gloss+' '+cgl
        receipts.add(pm.lemma); receipts.add('participial modifier'); receipts|=pr
    for pp in np.attached_pps:
        pf,pg,pr=realize_np(pp.object,g,by,noun_form,possessive_phrase,adjective_form,'locative')
        ad=_form(by,pp.adposition,('prep','p'))
        if not pf or not ad:return None,None,set()
        chunk=ad+' '+pf if g.get('adposition_type')=='preposition' else pf+' '+ad
        surf=surf+' '+chunk
        gloss=gloss+' '+pp.adposition.upper()+' '+pg
        receipts|=pr; receipts.add(pp.adposition); receipts.add('np attachment')
    if np.possessor:
        pf,pg,pr=realize_np(np.possessor,g,by,noun_form,possessive_phrase,adjective_form,'genitive')
        if not pf:return None,None,set()
        surf=possessive_phrase(pf,surf,g); gloss=pg+'-GEN '+gloss; receipts|=pr; receipts.add('possessive')
    if np.coordinated:
        cs=g.get('coordination',{}).get('np',g.get('coordination',{}))
        strategy=cs.get('strategy','particle')
        cj=_conj_form(g,np.conjunction or 'and',by) if strategy=='particle' else ''
        if strategy=='particle' and not cj:return None,None,set()
        for other in np.coordinated:
            of,og,orr=realize_np(other,g,by,noun_form,possessive_phrase,adjective_form,case)
            if not of:return None,None,set()
            surf=f'{surf} {cj} {of}'.replace('  ',' ').strip(); gloss=f'{gloss} {(np.conjunction or "and").upper()} {og}'; receipts|=orr
        receipts.add('coordination')
    return surf,gloss,receipts

def _realize_modifier(m,g,by):
    af=_form(by,m.lemma,('adv',))
    if not af and g.get('adverbs',{}).get('derivation','zero')=='zero': af=_form(by,m.lemma,('adj',))
    return af

def realize(clause,g,by,verb_form,noun_form,possessive_phrase,order_clause,affix,adjective_form=None):
    p=clause.predicate; receipts=set(); ss=sg=''; person='2sg' if clause.clause_type=='imperative' else '3sg'
    if clause.subject:
        ss,sg,sr=realize_np(clause.subject,g,by,noun_form,possessive_phrase,adjective_form)
        if not ss:return None
        receipts|=sr
        if clause.subject.person: person=clause.subject.person
        elif clause.subject.number=='plural': person='3pl'
    vf=_convert_form(by,p.lemma,'v',g)
    if not vf:return None
    # A feature counts as morphologically available only if its morpheme exists,
    # not merely because its label appears in the grammar inventory.
    morph=g.get('morphemes',{})
    native_tense=p.tense in g.get('verb',{}).get('tenses',[]) and (p.tense=='present' or p.tense in morph)
    tense=p.tense if native_tense else 'present'
    requested_aspects=[x for x in ('progressive','perfect') if x in p.aspect]
    primary_aspect=requested_aspects[0] if requested_aspects else 'simple'
    native_aspect=primary_aspect in g.get('verb',{}).get('aspects',[]) and (primary_aspect=='simple' or primary_aspect in morph)
    aspect=primary_aspect if native_aspect else 'simple'
    native_mood=p.mood in g.get('verb',{}).get('moods',[]) and (p.mood=='indicative' or p.mood in morph)
    mood=p.mood if native_mood else 'indicative'
    # Negation is realized once by the grammar engine. A gloss must describe
    # the single licensed operation, not add a second independent NOT token.
    v=verb_form(vf,g,person,tense,aspect,mood,p.negative); vg=p.lemma.upper(); receipts.add(p.lemma)
    if p.tense=='past' and not native_tense:
        mark=g.get('particles',{}).get('past')
        if not mark:return None
        v=mark+' '+v
    if p.tense=='past':
        receipts.add('past'); vg+='-PST'
    if p.tense=='future':
        if not native_tense:
            mark=g.get('particles',{}).get('future');
            if not mark:return None
            v=mark+' '+v
        receipts.add('future'); vg+='-FUT'
    for ai,requested_aspect in enumerate(requested_aspects):
        native=(requested_aspect in g.get('verb',{}).get('aspects',[]) and requested_aspect in morph)
        if ai==0 and requested_aspect==primary_aspect and native_aspect:
            pass
        elif native:
            mm=morph[requested_aspect]; v=affix(v,mm,g)
        else:
            mark=g.get('particles',{}).get(requested_aspect)
            if not mark:return None
            v=mark+' '+v
        receipts.add(requested_aspect); vg+='-'+('PERF' if requested_aspect=='perfect' else 'PROG')
    if p.mood=='imperative':
        if not native_mood:
            mark=g.get('particles',{}).get('imperative')
            if not mark:return None
            v=mark+' '+v
        receipts.add('imperative'); vg+='-IMP'
    if p.negative:
        receipts.add('negation'); vg+='-NEG'
    if p.modal:
        key='ability' if p.modal in ('can','could') else 'obligation' if p.modal in ('should','must') else 'possibility'
        mp=g.get('particles',{}).get(key)
        if not mp:return None
        v=(mp+' '+v) if g.get('modality',{}).get('particle_position','before_verb')=='before_verb' else (v+' '+mp)
        receipts.add('modal'); vg+='-MOD'
    os=og=''
    if p.object:
        os,og,orr=realize_np(p.object,g,by,noun_form,possessive_phrase,adjective_form,'accusative')
        if not os:return None
        receipts|=orr
    # adjective predicate/linking complement
    comp_s=comp_g=''
    if p.complement and p.complement_kind=='adjective':
        af=_form(by,p.complement.head,('adj',))
        if not af:return None
        degree=p.comparison.degree if p.comparison else 'positive'
        if adjective_form: af=adjective_form(af,g,degree)
        comp_s=af; comp_g=p.complement.head.upper()+('-COMP' if degree=='comparative' else '-SUPER' if degree=='superlative' else '')
        receipts.add(p.complement.head)
        if degree!='positive': receipts.add('comparison')
        os=comp_s if not os else os+' '+comp_s; og=comp_g if not og else og+' '+comp_g
        if p.coordinated_complements:
            cs=g.get('coordination',{}).get('predicate',{}); strategy=cs.get('strategy','particle')
            cj=_conj_form(g,p.complement_conjunction or 'and',by) if strategy=='particle' else ''
            if strategy=='particle' and not cj:return None
            for cc in p.coordinated_complements:
                caf=_form(by,cc.head,('adj',))
                if not caf:return None
                os=(os+' '+cj+' '+caf).replace('  ',' ').strip(); og=og+' '+(p.complement_conjunction or 'and').upper()+' '+cc.head.upper()
                receipts.add(cc.head)
            receipts.add('coordination')
    elif p.complement and p.complement_kind=='nominal':
        comp_s,comp_g,cr=realize_np(p.complement,g,by,noun_form,possessive_phrase,adjective_form,'nominative')
        if not comp_s:return None
        receipts|=cr
        os=comp_s if not os else os+' '+comp_s; og=comp_g if not og else og+' '+comp_g
    surf=order_clause(ss,v,os,g).strip() if ss else ' '.join(x for x in (v,os) if x)
    gloss=order_clause(sg,vg,og,g).strip() if sg else ' '.join(x for x in (vg,og) if x)
    # Modifiers are first-class receipts. -ly may use target adjective by explicit zero-adverb strategy.
    before=[]; after=[]; final=[]
    for m in p.modifiers:
        mf=_realize_modifier(m,g,by)
        if not mf:
            # English degree words more/less are grammatical when a comparison IR exists.
            if m.source in ('more','less') and p.comparison:
                continue
            return None
        if p.comparison and p.comparison.degree=='comparative' and m.kind=='manner':
            cp=g.get('particles',{}).get('comparative')
            if cp: mf=cp+' '+mf; receipts.add('comparison')
        receipts.add(m.lemma); receipts.add(m.source or m.lemma)
        pos=g.get('adverbs',{}).get('position','after_verb')
        (before if pos=='before_verb' else final if pos=='clause_final' else after).append((mf,m.lemma.upper()))
    if before: surf=' '.join(x[0] for x in before)+' '+surf; gloss=' '.join(x[1] for x in before)+' '+gloss
    if after: surf=surf+' '+' '.join(x[0] for x in after); gloss=gloss+' '+' '.join(x[1] for x in after)
    if final: surf=surf+' '+' '.join(x[0] for x in final); gloss=gloss+' '+' '.join(x[1] for x in final)
    # Lexical verb particles: require a lexical target form if available, otherwise
    # use a semantically neutral particle only when the same item exists as adv/prep.
    for part in p.particles:
        pf=_form(by,part,('adv','prep','p'))
        if not pf:return None
        surf += ' '+pf; gloss += ' '+part.upper(); receipts.add(part)
    for pp in p.pps:
        pf,pg,pr=realize_np(pp.object,g,by,noun_form,possessive_phrase,adjective_form,'locative')
        ad=_form(by,pp.adposition,('prep','p'))
        if not pf or not ad:return None
        chunk=ad+' '+pf if g.get('adposition_type')=='preposition' else pf+' '+ad
        surf+=' '+chunk; gloss+=' '+pp.adposition.upper()+' '+pg; receipts|=pr; receipts.add(pp.adposition)
    if p.comparison and p.comparison.standard:
        sf,sgl,sr=realize_np(p.comparison.standard,g,by,noun_form,possessive_phrase,adjective_form,'ablative')
        if not sf:return None
        cp=g.get('particles',{}).get('comparative')
        if not cp:return None
        surf += ' '+cp+' '+sf; gloss += ' COMP-STD '+sgl; receipts|=sr; receipts.add('comparison')
    if p.coordinated:
        cs=g.get('coordination',{}).get('predicate',g.get('coordination',{}))
        strategy=cs.get('strategy','particle')
        cj=_conj_form(g,p.conjunction or 'and',by) if strategy=='particle' else ''
        if strategy=='particle' and not cj:return None
        for child in p.coordinated:
            cc=ClauseIR(copy.deepcopy(clause.subject),copy.deepcopy(child),'declarative',source_tokens=clause.source_tokens)
            out=realize(cc,g,by,verb_form,noun_form,possessive_phrase,order_clause,affix,adjective_form)
            if not out:return None
            surf=(surf+' '+cj+' '+out['surface']).replace('  ',' ').strip()
            gloss=gloss+' '+(p.conjunction or 'and').upper()+' '+out['gloss']
            receipts.update(out['receipts'])
        receipts.add('coordination'); receipts.add('coordinated predicate')
    if clause.coordinated is not None:
        # Independent clauses use the target language's CLAUSE coordination
        # strategy, never predicate coordination or inherited subjects.
        cs=g.get('coordination',{}).get('clause',{})
        strategy=cs.get('strategy','juxtaposition')
        cj=_conj_form(g,clause.conjunction or 'and',by) if strategy=='particle' else ''
        if strategy=='particle' and not cj:return None
        out=realize(clause.coordinated,g,by,verb_form,noun_form,possessive_phrase,order_clause,affix,adjective_form)
        if not out:return None
        surf=' '.join(x for x in (surf,cj,out['surface']) if x)
        gloss+=' '+(clause.conjunction or 'and').upper()+' '+out['gloss']
        receipts.update(out['receipts'])
        receipts.add('coordination'); receipts.add('coordinated clause')
    if clause.clause_type=='hortative':
        mark=g.get('particles',{}).get('imperative')
        if mark and mark not in surf.split(): surf=mark+' '+surf
        receipts.add('imperative'); receipts.add('hortative'); gloss+=' HORT'
    if clause.subordinate is not None:
        # This semantic structure is available for auditing, not yet realized.
        # The causal connective requires a target grammar contract; refusing to
        # invent one is safer than claiming a faithful translation.
        return None
    if clause.clause_type=='wh_question':
        interrogative=g.get('interrogatives',{}).get(clause.wh_word)
        if not interrogative:return None
        if clause.wh_degree:
            # The adjective has already been realized as the predicate
            # complement. HOW scopes over its degree, not over the subject.
            if p.complement_kind!='adjective' or p.complement.head!=clause.wh_degree:
                return None
            receipts.add('degree_question');receipts.add('degree');receipts.add('how')
            gloss+=' DEG-'+clause.wh_degree.upper()
        if g.get('questions',{}).get('wh_strategy')=='fronted':
            surf=interrogative+' '+surf
        else:
            surf=surf+' '+interrogative
        receipts.add('question'); receipts.add('wh_question'); receipts.add(clause.wh_word)
        gloss+=' WH-'+clause.wh_word.upper()
    if clause.clause_type=='yes_no_question':
        q=g.get('particles',{}).get('yes_no')
        strategy=g.get('questions',{}).get('strategy')
        if q:
            surf=(q+' '+surf) if g.get('questions',{}).get('particle_position')=='initial' else (surf+' '+q)
        elif strategy in ('word-order','verb','mixed'):
            qop=g.get('questions',{}).get('structural_operation')
            if qop=='verb_fronting':
                # Clause is already assembled in target order; move the realized verb complex
                # to clause-initial position only when it is not already initial.
                if ss and surf.startswith(ss+' '):
                    tail=surf[len(ss):].strip(); surf=tail+' '+ss
            else:
                return None
        else: return None
        receipts.add('question'); gloss+=' Q'
    return {'surface':surf.strip(),'gloss':gloss.strip(),'receipts':sorted(receipts),'ir':clause.to_dict(),'strategies':{
        'word_order':g.get('word_order'),'adposition':g.get('adposition_type'),'adjective_position':g.get('adjective_position'),
        'possession':g.get('possession',{}).get('strategy'),'comparison':g.get('comparison',{}).get('strategy'),
        'question':g.get('questions',{}).get('strategy'),'coordination':g.get('coordination',{}),
        'tense':g.get('tense_realization',{}),'aspect':g.get('aspect_realization',{}),'mood':g.get('mood_realization',{})}}
