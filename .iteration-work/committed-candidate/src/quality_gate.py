#!/usr/bin/env python3
"""Fail CI when sentence-level translation coverage regresses across languages.

This gate checks diagnostic classifications, not semantic correctness. Pair files by
language header and reject mismatched corpora, missing languages, and new failures.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path
from compare_diagnostics import parse, compare

def load(paths):
    result={}
    for path in paths:
        data=parse(path)
        text=Path(path).read_text(encoding='utf-8-sig')
        match=re.search(r'^Translation diagnostics: (.+)$',text,re.M)
        if not match: raise ValueError(f'language header missing: {path}')
        name=match.group(1).strip()
        if name in result: raise ValueError(f'duplicate language: {name}')
        result[name]=data
    return result

def corpus_identity(path):
    """Stable corpus identity: sentence order and content, ignoring CRLF vs LF."""
    from grammar_engine import load_translation_sentences
    sentences=load_translation_sentences(path)
    return {'count':len(sentences),'sha256':hashlib.sha256(json.dumps(sentences,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()}

def evaluate(before,after,allow_regressions=0):
    if set(before)!=set(after): raise ValueError(f'language sets differ: before={sorted(before)} after={sorted(after)}')
    rows={name:compare(before[name],after[name]) for name in sorted(before)}
    # A changed sentence at the same ID is not a recovery/regression comparison.
    for name in before:
        for sid in set(before[name]['records']) & set(after[name]['records']):
            a=before[name]['records'][sid]['sentence']
            b=after[name]['records'][sid]['sentence']
            if a!=b: raise ValueError(f'{name}: sentence #{sid} changed between runs')
    new=sum(len(v['newly_noncomplete']) for v in rows.values())
    recovered=sum(len(v['newly_complete']) for v in rows.values())
    return {'pass':new<=allow_regressions,'newly_noncomplete':new,'newly_complete':recovered,'languages':rows}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--before',nargs='+',required=True,help='Baseline diagnostics, one file per language')
    p.add_argument('--after',nargs='+',required=True,help='Candidate diagnostics, one file per language')
    p.add_argument('--before-corpus',type=Path,help='Original English corpus; strongly recommended')
    p.add_argument('--after-corpus',type=Path,help='Candidate English corpus; strongly recommended')
    p.add_argument('--allow-regressions',type=int,default=0)
    p.add_argument('--json-output',type=Path)
    args=p.parse_args(argv)
    try:
        if args.allow_regressions<0: raise ValueError('allow-regressions must be nonnegative')
        if bool(args.before_corpus)!=bool(args.after_corpus):
            raise ValueError('provide both --before-corpus and --after-corpus')
        before=load(args.before); after=load(args.after)
        result=evaluate(before,after,args.allow_regressions)
        if args.before_corpus:
            b=corpus_identity(args.before_corpus); a=corpus_identity(args.after_corpus)
            if b!=a: raise ValueError(f'English corpus changed: before={b} after={a}')
            for name in before:
                if before[name]['total']!=b['count']: raise ValueError(f'{name}: diagnostics/corpus sentence count mismatch')
            result['corpus']=b
        else:
            result['warning']='No corpus files provided; changes to complete sentences cannot be detected'
    except (ValueError,OSError) as exc:
        print(f'QUALITY GATE ERROR: {exc}',file=sys.stderr);return 2
    if result.get('warning'): print('WARNING:',result['warning'])
    for name,row in result['languages'].items():
        print(f'{name}: complete {row["before"].get("Complete",0)} -> {row["after"].get("Complete",0)}; regressions {len(row["newly_noncomplete"])}; recoveries {len(row["newly_complete"])}')
        for item in row['newly_noncomplete']:
            print(f'  REGRESSION #{item["id"]}: {item["sentence"]} ({item["after_reason"]})')
    print(f'QUALITY GATE: {"PASS" if result["pass"] else "FAIL"} ({result["newly_noncomplete"]} regressions; {result["newly_complete"]} recoveries)')
    if args.json_output: args.json_output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return 0 if result['pass'] else 1
if __name__=='__main__':raise SystemExit(main())
