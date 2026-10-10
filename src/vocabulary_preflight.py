#!/usr/bin/env python3
"""Read-only corpus vocabulary and realization preflight for existing languages."""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
from language_io import load_language, resolve_language_path, resolve_project_path
from grammar_engine import analyze_translation, load_translation_sentences
from english_analyzer import lemma_candidates


def inspect_corpus(sentences, grammar, entries, forms):
    results=[analyze_translation(s,grammar,entries,forms) for s in sentences]
    counts=Counter(r['status'] for r in results)
    missing=Counter()
    stages=Counter()
    for r in results:
        missing.update(r['ir'].get('missing_lexemes',()))
        if r['status']!='ok': stages[r['ir']['diagnostic_stage']]+=1
    return {'total':len(results),'statuses':dict(sorted(counts.items())),
            'stages':dict(sorted(stages.items())),
            'missing_tokens':[{'token':w,'count':n,'lemma_candidates':lemma_candidates(w)} for w,n in sorted(missing.items())],
            'sentences':[{'sentence':r['english'],'status':r['status'],'stage':r['ir']['diagnostic_stage'],
                          'reason':r['reason']} for r in results]}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--language',required=True,type=Path)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',type=Path,help='optional JSON report path')
    p.add_argument('--project-root',type=Path,default=Path(__file__).resolve().parent.parent)
    a=p.parse_args(argv)
    root=a.project_root.resolve()
    _,g,entries,forms=load_language(resolve_language_path(root,a.language))
    sentences=load_translation_sentences(resolve_project_path(root,a.input))
    report=inspect_corpus(sentences,g,entries,forms)
    payload=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
    if a.output:
        target=resolve_project_path(root,a.output)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(payload,encoding='utf-8')
        print(f'Report: {target}')
    print('Sentences:',report['total'])
    print('Statuses:',report['statuses'])
    print('Failure stages:',report['stages'])
    print('Missing tokens:',', '.join(f"{r['token']} ({r['count']})" for r in report['missing_tokens']) or 'none')
    return 0

if __name__=='__main__': raise SystemExit(main())
