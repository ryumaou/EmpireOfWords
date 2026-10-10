#!/usr/bin/env python3
"""Validate a generated language package and optionally audit a translation suite."""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path
from language_io import resolve_language_path, resolve_project_path, load_language, validate_package
from grammar_engine import load_translation_sentences, analyze_translation

def main(argv=None):
    root=Path(__file__).resolve().parent.parent
    p=argparse.ArgumentParser(description='Validate a generated conlang package')
    p.add_argument('--language',required=True,type=Path)
    p.add_argument('--translations',type=Path,help='optional sentence suite to audit')
    p.add_argument('--report',type=Path,help='optional JSON report path')
    p.add_argument('--project-root',type=Path,default=root)
    a=p.parse_args(argv); project=a.project_root.resolve(); lp=resolve_language_path(project,a.language)
    if not lp.is_file(): p.error(f'language file not found: {lp}')
    try: data,g,entries,forms=load_language(lp)
    except Exception as exc: p.error(f'cannot load language: {exc}')
    issues,warnings=validate_package(data,entries,forms)
    report={'language':data.get('name',lp.parent.name),'schema_version':data.get('schema_version',1),'entries':len(entries),'forms':len(forms),'issues':issues,'warnings':warnings}
    if a.translations:
        tp=resolve_project_path(project,a.translations)
        if not tp.is_file(): p.error(f'translation suite not found: {tp}')
        results=[analyze_translation(s,g,entries,forms) for s in load_translation_sentences(tp)]
        counts=Counter(r['status'] for r in results); constructions=Counter(); missing=Counter()
        for r in results:
            if r['status']!='ok': constructions.update(r['ir'].get('constructions',[])); missing.update(r['ir'].get('missing_lexemes',[]))
        report['translation_audit']={'sentences':len(results),'status_counts':dict(counts),'problem_constructions':dict(constructions.most_common()),'missing_lexemes':dict(missing.most_common())}
    print(f"Language: {report['language']}")
    print(f"Schema: {report['schema_version']}")
    print(f"Lexicon: {len(entries)} entries / {len(forms)} forms")
    print(f"Errors: {len(issues)}  Warnings: {len(warnings)}")
    if 'translation_audit' in report:
        a2=report['translation_audit']; print(f"Translation audit: {a2['sentences']} sentences")
        for k in ('ok','partial','unresolved-vocabulary','unsupported-grammar'): print(f"  {k}: {a2['status_counts'].get(k,0)}")
    if a.report:
        rp=resolve_project_path(project,a.report); rp.parent.mkdir(parents=True,exist_ok=True); rp.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8'); print(f'Report: {rp}')
    return 2 if issues else 0
if __name__=='__main__': raise SystemExit(main())
