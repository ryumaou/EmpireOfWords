#!/usr/bin/env python3
"""Inspect structured meaning independently of conlang surface realization.

This is a development probe, not a substitute for human translation assessment.
A strict fixture defines expected clause roles and flags dropped relationships.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from english_analyzer import analyze, lexical_match, tokens, lemma_candidates
from structured_realizer import parse_clause, realize
from grammar_engine import verb_form, noun_form, possessive_phrase, order_clause, affix, adjective_form

def roles(clause):
    if clause is None: return []
    result=[]
    cur=clause
    while cur:
        p=cur.predicate
        result.append({'subject': cur.subject.head if cur.subject else None,
                       'predicate': p.lemma,
                       'object': p.object.head if p.object else None,
                       'tense':p.tense})
        for child in p.coordinated:
            result.append({'subject':cur.subject.head if cur.subject else None,
                           'predicate':child.lemma,
                           'object':child.object.head if child.object else None,
                           'tense':child.tense})
        cur=cur.coordinated
    return result

def attachments(np, owner='subject'):
    if np is None:return []
    out=[]
    for pp in np.attached_pps:
        out.append({'owner':np.head,'adposition':pp.adposition,'object':pp.object.head})
        out.extend(attachments(pp.object,owner))
    if np.possessor:out.extend(attachments(np.possessor,owner))
    for child in np.coordinated:out.extend(attachments(child,owner))
    return out

def all_attachments(clause):
    out=[]
    while clause:
        out.extend(attachments(clause.subject))
        predicates=[clause.predicate]+clause.predicate.coordinated
        for p in predicates:
            out.extend(attachments(p.object))
            for pp in p.pps:out.extend(attachments(pp.object))
        clause=clause.coordinated
    return out

def realization_probe(sentence,by,g):
    result=inspect(sentence,by,g)
    c=analyze(sentence,by)['constructions']
    ir=parse_clause(sentence,by,lexical_match,tokens,lemma_candidates,c,g)
    try:
        output=realize(ir,g,by,verb_form,noun_form,possessive_phrase,order_clause,affix,adjective_form) if ir else None
    except (KeyError, TypeError, ValueError):
        output=None  # incomplete grammar fixture, not a successful realization
    expected=[]
    for role in result['roles']:
        if role['predicate']:expected.append(role['predicate'])
    receipts=set(output['receipts']) if output else set()
    return {'parsed':ir is not None,'realized':output is not None,
            'expected_predicates':expected,'missing_predicates':[x for x in expected if x not in receipts],
            'surface':output['surface'] if output else None,
            'gloss':output['gloss'] if output else None,
            'receipts':sorted(receipts)}

def inspect(sentence,by,g=None):
    c=analyze(sentence,by)['constructions']
    ir=parse_clause(sentence,by,lexical_match,tokens,lemma_candidates,c,g or {})
    return {'sentence':sentence,'constructions':c,'roles':roles(ir),
            'parsed':ir is not None,'attachments':all_attachments(ir) if ir else [],
            'question':{'type':ir.clause_type,'word':ir.wh_word} if ir else None,
            'degree_question':ir.wh_degree if ir else None,
            'subordination':{'relation':ir.subordinate_relation,'roles':roles(ir.subordinate)} if ir and ir.subordinate else None}

def check(expected,actual):
    return {'passed':expected==actual,'expected':expected,'actual':actual}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fixtures',default=str(Path(__file__).resolve().parent.parent/'translations'/'semantic_fixtures_v1.json'))
    args=ap.parse_args()
    fixtures=json.loads(Path(args.fixtures).read_text(encoding='utf-8'))
    failures=0
    for case in fixtures:
        by={lemma:[(pos,lemma+'x')] for lemma,pos in case['lexicon'].items()}
        result=inspect(case['sentence'],by)
        verdict=check(case['expected_roles'],result['roles'])
        if 'expected_attachments' in case:
            verdict['passed']=verdict['passed'] and case['expected_attachments']==result['attachments']
        if 'expected_question' in case:
            verdict['passed']=verdict['passed'] and case['expected_question']==result['question']
        if 'expected_degree_question' in case:
            verdict['passed']=verdict['passed'] and case['expected_degree_question']==result['degree_question']
        if 'expected_subordination' in case:
            verdict['passed']=verdict['passed'] and case['expected_subordination']==result['subordination']
        print(('PASS' if verdict['passed'] else 'FAIL')+' '+case['id'])
        if not verdict['passed']:
            failures+=1
            print('  expected:',json.dumps(verdict['expected']))
            print('  actual:  ',json.dumps(verdict['actual']))
            if 'expected_attachments' in case:
                print('  expected attachments:',json.dumps(case['expected_attachments']))
                print('  actual attachments:  ',json.dumps(result['attachments']))
    print(f'{len(fixtures)-failures}/{len(fixtures)} semantic fixtures passed')
    return 1 if failures else 0

if __name__=='__main__': sys.exit(main())
