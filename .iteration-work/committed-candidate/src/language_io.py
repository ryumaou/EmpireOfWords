#!/usr/bin/env python3
"""Shared language-package I/O and validation."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json

SCHEMA_VERSION=2
TOOL_VERSION='7.6.6'

@dataclass(frozen=True)
class EntryKey:
    gloss:str
    pos:str
@dataclass
class Entry:
    key:EntryKey
    expr:str|None=None
    line_no:int=0

def resolve_project_path(project:Path,value:Path)->Path:
    return value.resolve() if value.is_absolute() else (project/value).resolve()

def resolve_language_path(project:Path,value:Path)->Path:
    p=resolve_project_path(project,value)
    return p/'language.json' if p.is_dir() else p

def load_language(path:Path):
    raw=path.read_bytes()
    text=raw.decode('utf-8-sig') if raw.startswith(b'\xef\xbb\xbf') else raw.decode('utf-8')
    data=json.loads(text)
    if not isinstance(data,dict): raise ValueError('language.json must contain a JSON object')
    grammar=data.get('grammar'); lexicon=data.get('lexicon')
    if not isinstance(grammar,dict): raise ValueError("language.json does not contain a usable 'grammar' object")
    if not isinstance(lexicon,list): raise ValueError("language.json does not contain a usable 'lexicon' array")
    entries=[]; forms={}
    for i,item in enumerate(lexicon,1):
        if not isinstance(item,dict): continue
        gloss=str(item.get('gloss','')).strip(); pos=str(item.get('pos','')).strip(); form=str(item.get('form','')).strip()
        if not gloss or not pos: continue
        e=Entry(EntryKey(gloss,pos),item.get('derivation'),i); entries.append(e)
        if form: forms[e.key]=form
    if not entries: raise ValueError('language.json contains no usable lexical entries')
    return data,grammar,entries,forms

def validate_package(data,entries,forms):
    issues=[]; warnings=[]
    schema=data.get('schema_version',1)
    if not isinstance(schema,int): issues.append('schema_version must be an integer')
    elif schema>SCHEMA_VERSION: warnings.append(f'package schema {schema} is newer than this tool supports ({SCHEMA_VERSION})')
    seen_forms={}
    for e in entries:
        f=forms.get(e.key,'')
        if not f: issues.append(f'missing form: {e.key.gloss}:{e.key.pos}'); continue
        label=f'{e.key.gloss}:{e.key.pos}'
        if f in seen_forms and seen_forms[f]!=label: warnings.append(f'homophone: {label} = {seen_forms[f]} = {f}')
        else: seen_forms[f]=label
    for key in ('word_order','morphemes','pronouns','verb'):
        if key not in data.get('grammar',{}): issues.append(f'grammar missing required key: {key}')
    contract_issues,contract_warnings=validate_grammar_contract(data.get('grammar',{}))
    issues.extend(contract_issues); warnings.extend(contract_warnings)
    return issues,warnings


def validate_grammar_contract(grammar):
    """Validate that advertised grammar features have deterministic realizers."""
    issues=[]; warnings=[]
    morph=grammar.get('morphemes',{}); particles=grammar.get('particles',{})
    verb=grammar.get('verb',{})
    for tense in verb.get('tenses',[]):
        if tense!='present' and tense not in morph and tense not in particles:
            issues.append(f'grammar feature has no realization: tense {tense}')
    for aspect in verb.get('aspects',[]):
        if aspect!='simple' and aspect not in morph and aspect not in particles:
            issues.append(f'grammar feature has no realization: aspect {aspect}')
    for mood in verb.get('moods',[]):
        if mood!='indicative' and mood not in morph and mood not in particles:
            issues.append(f'grammar feature has no realization: mood {mood}')
    if grammar.get('questions',{}).get('strategy') in ('particle','mixed') and not particles.get('yes_no'):
        issues.append('question strategy requires a yes/no particle')
    if grammar.get('possession',{}).get('strategy')=='particle' and not particles.get('possessive'):
        issues.append('possession strategy requires possessive particle')
    coord=grammar.get('coordination',{})
    # v6.6 has separate NP/predicate/clause strategies; accept legacy flat contracts.
    strategies=[]
    if 'strategy' in coord: strategies.append(coord.get('strategy'))
    else: strategies.extend(coord.get(k,{}).get('strategy') for k in ('np','predicate','clause'))
    if 'particle' in strategies:
        for key in ('and','or','but'):
            if not particles.get(key): issues.append(f'coordination strategy requires particle: {key}')
    rp=grammar.get('realization_profile',{})
    if grammar.get('translation_readiness',{}).get('contract_version',0)>=3:
        for key in ('word_order','adposition_type','adjective_position','possessor_position','comparison_strategy','question_strategy'):
            if key not in rp: issues.append(f'realization profile missing: {key}')
    if grammar.get('translation_readiness',{}).get('contract_version',0)>=4:
        lc=grammar.get('lexical_conversion',{})
        for key in ('noun_to_verb','adjective_to_verb','noun_to_adjective'):
            spec=lc.get(key)
            if not spec: issues.append(f'lexical conversion missing: {key}'); continue
            if spec.get('strategy')=='affix' and spec.get('morpheme') not in morph:
                issues.append(f'lexical conversion affix missing: {key}')
        if 'noun_compound_order' not in rp: issues.append('realization profile missing: noun_compound_order')
    if grammar.get('translation_readiness',{}).get('contract_version',0)>=5:
        nf=grammar.get('nonfinite',{})
        for key in ('participial_modifier','infinitive_complement'):
            spec=nf.get(key)
            if not spec: issues.append(f'nonfinite strategy missing: {key}'); continue
            if spec.get('strategy')=='affix' and spec.get('morpheme') not in morph:
                issues.append(f'nonfinite affix missing: {key}')
            if spec.get('strategy')=='particle' and not particles.get(spec.get('particle')):
                issues.append(f'nonfinite particle missing: {key}')
        if grammar.get('questions',{}).get('strategy') in ('word-order','verb','mixed') and not grammar.get('questions',{}).get('structural_operation'):
            issues.append('structural question strategy missing operation')
    # Translation-ready fallbacks may be used even when a feature is not
    # grammaticalized in the typological profile.
    for key in ('future','progressive','perfect','imperative'):
        if not particles.get(key) and key not in morph:
            warnings.append(f'no analytic fallback for {key}; some English inputs may remain partial')
    if grammar.get('translation_readiness',{}).get('contract_version',0)>=6:
        caps=set(grammar.get('translation_readiness',{}).get('capabilities',[]))
        required={'stacked_aspect','constituent_coordination','copular_imperative','nominal_predicate','irregular_comparison'}
        missing=sorted(required-caps)
        if missing: issues.append('contract v6 capabilities missing: '+', '.join(missing))
    if grammar.get('translation_readiness',{}).get('contract_version',0)>=7:
        if 'past' not in morph and not particles.get('past'):
            issues.append('contract v7 requires past tense realization or analytic past marker')
        if grammar.get('verb',{}).get('negation') in ('affix','mixed') and 'negative' not in morph:
            issues.append('contract v7 requires a negative affix for affix/mixed negation')
    return issues,warnings
