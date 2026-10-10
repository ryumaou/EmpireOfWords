#!/usr/bin/env python3
"""Translate English sentences with an existing generated conlang package.

This tool never generates or modifies a language. It loads output/<Language>/language.json
and reuses grammar_engine.translate_sentence() for deterministic translation.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import json
import sys
from pathlib import Path

from grammar_engine import load_translation_sentences, analyze_translation, TRANSLATION_CAPABILITIES
from english_analyzer import lemma_candidates, lexical_match, IRREGULAR_VERBS, IRREGULAR_NOUNS
from language_io import resolve_project_path, resolve_language_path, load_language, validate_package, TOOL_VERSION


def format_result(result) -> str:
    return (
        f"[{result['type']}]\n"
        f"English: {result['english']}\n"
        f"Language: {result['surface']}\n"
        f"Gloss: {result['gloss']}\n"
        f"Status: {result['status']}\n"
        f"Reason: {result['reason']}\n"
    )



def infer_missing_entry(word: str, sentences: list[str], by_pos: dict):
    """Return (lemma, pos) when a missing English token can be safely normalized.

    This is deliberately conservative: uncertain words are left for review rather than
    written into an add_words.py input file with a fabricated part of speech.
    """
    w=word.lower().strip("'\"")
    possessive_source=w.endswith("'s")
    if possessive_source: w=w[:-2]
    lemma=(IRREGULAR_VERBS.get(w) or (None,None))[0] if w in IRREGULAR_VERBS else IRREGULAR_NOUNS.get(w)
    if not lemma:
        cands=lemma_candidates(w)
        # Prefer transparent inflectional normalizations; otherwise keep the surface lemma.
        if w.endswith('ies') and len(w)>3: lemma=w[:-3]+'y'
        elif w.endswith('ves') and len(w)>3: lemma=cands[0] if cands else w
        elif w.endswith('ing') and len(w)>4: lemma=cands[1] if len(cands)>1 and cands[1].endswith('e') else cands[0]
        elif w.endswith('ed') and len(w)>3: lemma=cands[1] if len(cands)>1 and cands[1].endswith('e') else cands[0]
        elif w.endswith('es') and len(w)>3:
            if w.endswith('ies'): lemma=w[:-3]+'y'
            elif w.endswith(('ches','shes','xes','zes','ses')): lemma=w[:-2]
            else: lemma=w[:-1]
        elif w.endswith('s') and len(w)>2 and not w.endswith('ss'): lemma=w[:-1]
        elif w.endswith('ly') and len(w)>3: lemma=cands[-1] if cands else w[:-2]
        else: lemma=w
    # Collect local contexts in which the token occurred.
    contexts=[]
    import re
    for sent in sentences:
        toks=[x.lower() for x in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+",sent.replace('’',"'"))]
        contexts += [(toks,i) for i,t in enumerate(toks) if t==w]
    # Strong morphology and closed-class lexical cues first.
    if w in IRREGULAR_VERBS or w.endswith(('ed','ing')): return lemma,'v'
    if w.endswith('ly') or w in {'everywhere','somewhere','nowhere','here','there'}: return lemma,'adv'
    if w in {'dear','alas','oh','hello','goodbye'}: return lemma,'interj'
    # Strong syntactic cues.
    for toks,i in contexts:
        prev=toks[i-1] if i else '' ; prev2=toks[i-2] if i>1 else '' ; nxt=toks[i+1] if i+1<len(toks) else ''
        if prev in {'a','an','the','this','that','these','those','my','your','his','her','our','their','its','some','many','three','two','one'}:
            # If the following token is a known noun, this missing item is very likely an adjective (the wild dog).
            nm=lexical_match(by_pos,nxt) if nxt else None
            if nm and any(pos.startswith('n') for pos,_ in by_pos.get(nm,())): return lemma,'adj'
            return lemma,'n'
        nm=lexical_match(by_pos,nxt) if nxt else None
        if nm and any(pos.startswith('n') for pos,_ in by_pos.get(nm,())):
            # Bare prenominal modifier: wild animals, yellow candlelight, friendly caress.
            return lemma,'adj'
        if prev in {'to','will','shall','can','could','should','would','must','may','might','do','does','did'}: return lemma,'v'
        if prev in {'then'}: return lemma,'v'
        if prev.endswith(('ed','ing')): return lemma,'n'
        if prev in {'very','too','more','less','quite'}: return lemma,'adj'
        if prev in {'is','are','am','was','were','be','been','seem','seems','seemed','feel','feels','felt','look','looks','looked','sound','sounds','sounded','grow','grows','grew','become','became','prove','proved'} and nxt not in {'a','an','the'}: return lemma,'adj'
        if prev in {'myself','yourself','himself','herself','itself','ourselves','yourselves','themselves'} and prev2 in {'prove','proved','consider','considered','make','made'}: return lemma,'adj'
        if any(x in {'is','are','am','was','were','be','been','seem','seems','seemed','feel','feels','felt','look','looks','looked','sound','sounds','sounded','grow','grows','grew','become','became'} for x in toks[max(0,i-4):i]):
            if prev not in {'a','an','the'}: return lemma,'adj'
        if prev in {'in','on','at','by','with','from','for','into','onto','under','over','near','beside','across','through','upon','toward','towards','after','before','about','of','like','during'}: return lemma,'n'
        if prev in {'and','or','but'}:
            # Coordinate with the adjacent known adjective/noun when possible.
            pm=lexical_match(by_pos,prev2) if prev2 else None
            if pm:
                poses=[p for p,_ in by_pos.get(pm,())]
                if any(p.startswith('adj') for p in poses): return lemma,'adj'
                if any(p.startswith('n') for p in poses): return lemma,'n'
        # Object-like position after a known lexical verb is safely nominal for the
        # missing-word queue; this does not affect parsing until the user applies it.
        pm=lexical_match(by_pos,prev) if prev else None
        if pm and any(p.startswith('v') for p,_ in by_pos.get(pm,())): return lemma,'n'
        if pm and any(p.startswith('adj') for p,_ in by_pos.get(pm,())): return lemma,'n'
        if prev.endswith("'s"): return lemma,'n'
        nm=lexical_match(by_pos,nxt) if nxt else None
        if nm and any(p.startswith('v') for p,_ in by_pos.get(nm,())): return lemma,'n'
    if possessive_source: return lemma,'n'
    # Transparent plural morphology is safe enough to classify as a noun.
    if w in IRREGULAR_NOUNS or (w.endswith('s') and not w.endswith(('ss','us','is'))): return lemma,'n'
    return None

def write_missing_additions(output_path: Path, results: list[dict], sentences: list[str], language_name: str, entries):
    from collections import Counter
    missing=Counter()
    for r in results:
        missing.update(r.get('ir',{}).get('missing_lexemes',[]))
    path=output_path.with_name(output_path.stem+'_missing_words.txt')
    if not missing:
        if path.exists(): path.unlink()
        return None, [], []
    by_pos={}
    for e in entries: by_pos.setdefault(e.key.gloss,[]).append((e.key.pos,None))
    additions=[]; uncertain=[]; seen=set()
    for word,count in missing.most_common():
        inferred=infer_missing_entry(word,sentences,by_pos)
        if inferred:
            lemma,pos=inferred; key=(lemma,pos)
            if key not in seen:
                seen.add(key); additions.append((lemma,pos,word,count))
        else: uncertain.append((word,count))
    lines=[
        '# Empire Of Words - missing vocabulary required by this translation',
        f'# Language: {language_name}',
        '# This file is directly compatible with src/add_words.py.',
        '# Review before applying. Comments and uncertain items are ignored by add_words.py.',
        ''
    ]
    for lemma,pos,source,count in additions:
        note=f'  # {count} occurrence' + ('s' if count!=1 else '')
        if source!=lemma: note += f'; from {source}'
        lines.append(f'{lemma}:{pos}{note}')
    if uncertain:
        lines += ['', '# REVIEW REQUIRED - POS could not be inferred safely; not active add_words entries.']
        for word,count in uncertain: lines.append(f'# {word}  ({count})')
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return path, additions, uncertain

def main(argv=None) -> int:
    root_default = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(
        description="Translate English sentences using an existing generated language.json"
    )
    p.add_argument("--version", action="version", version=f"Empire Of Words translator {TOOL_VERSION} | {Path(__file__).resolve()}")
    p.add_argument(
        "--language", required=True, type=Path,
        help="existing language.json or its output/<Language> directory"
    )
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--input", type=Path,
        help="sentence file; blank lines and # comments are ignored"
    )
    source.add_argument(
        "--sentence",
        help="translate one English sentence"
    )
    p.add_argument(
        "--output", type=Path,
        help="output text file; for --input defaults to <language-dir>/translations/<input-stem>.txt"
    )
    p.add_argument(
        "--diagnostics", action="store_true",
        help="write a diagnostic report with status counts, constructions, missing lexemes, and intermediate analyses"
    )
    p.add_argument("--project-root", type=Path, default=root_default)
    args = p.parse_args(argv)

    project = args.project_root.resolve()
    language_path = resolve_language_path(project, args.language)
    if not language_path.is_file():
        p.error(f"language file not found: {language_path}")

    try:
        data, grammar, entries, forms = load_language(language_path)
    except (OSError, ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        p.error(f"cannot load language: {exc}")
    package_issues, package_warnings = validate_package(data, entries, forms)
    if package_issues:
        p.error("invalid language package: " + "; ".join(package_issues[:5]))
    for warning in package_warnings[:5]:
        print(f"Warning: {warning}", file=sys.stderr)

    if args.input is not None:
        input_path = resolve_project_path(project, args.input)
        if not input_path.is_file():
            p.error(f"translation input file not found: {input_path}")
        sentences = load_translation_sentences(input_path)
        if not sentences:
            p.error(f"translation input contains no usable sentences: {input_path}")
    else:
        input_path = None
        sentence = (args.sentence or "").strip()
        if not sentence:
            p.error("--sentence cannot be empty")
        sentences = [sentence]

    results = [analyze_translation(s, grammar, entries, forms) for s in sentences]
    text = "\n".join(format_result(r).rstrip() for r in results) + "\n"
    counts = {}
    for r in results: counts[r['status']] = counts.get(r['status'],0)+1
    unresolved = len(results) - counts.get('ok',0)
    name = str(data.get("name") or language_path.parent.name)

    package_sha = hashlib.sha256(language_path.read_bytes()).hexdigest()
    translator_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    grammar_sha = hashlib.sha256(json.dumps(grammar, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
    manifest_path = language_path.parent / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    package_version = manifest.get('tool_version', data.get('tool_version', 'unknown'))
    contract_version = grammar.get('translation_readiness', {}).get('contract_version', 'unknown')
    if args.output is not None:
        output_path = resolve_project_path(project, args.output)
    elif input_path is not None:
        output_path = language_path.parent / "translations" / f"{input_path.stem}.txt"
    else:
        output_path = None

    if output_path is None:
        sys.stdout.write(text)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        missing_path, addable_missing, uncertain_missing = write_missing_additions(output_path, results, sentences, name, entries)
        try:
            shown = output_path.relative_to(project)
        except ValueError:
            shown = output_path
        print(f"Language: {name}")
        print(f"Sentences: {len(results)}")
        print(f"Complete: {counts.get('ok',0)}")
        print(f"Partial: {counts.get('partial',0)}")
        print(f"Missing vocabulary: {counts.get('unresolved-vocabulary',0)}")
        print(f"Unsupported grammar: {counts.get('unsupported-grammar',0)}")
        print(f"Output: {shown}")
        if missing_path is not None:
            try: mshown=missing_path.relative_to(project)
            except ValueError: mshown=missing_path
            print(f"Missing-word additions: {mshown}")
            print(f"Addable missing concepts: {len(addable_missing)}")
            if uncertain_missing: print(f"Missing words requiring POS review: {len(uncertain_missing)}")

        if args.diagnostics:
            from collections import Counter
            construction_counts=Counter()
            missing_counts=Counter()
            for r in results:
                if r['status']!='ok':
                    construction_counts.update(r['ir'].get('constructions',[]))
                    missing_counts.update(r['ir'].get('missing_lexemes',[]))
            diag_path=output_path.with_name(output_path.stem+'_diagnostics.txt')
            lines=[f"Translation diagnostics: {name}","="*60,"",
                   f"Translator version: {TOOL_VERSION}",
                   f"Language build version: {package_version}",
                   f"Language schema version: {data.get('schema_version', 'unknown')}",
                   f"Grammar contract version: {contract_version}",
                   f"Language package SHA256: {package_sha}",
                   f"Grammar SHA256: {grammar_sha}",
                   f"Translator SHA256: {translator_sha}", "",
                   f"Sentences: {len(results)}",f"Complete: {counts.get('ok',0)}",
                   f"Partial: {counts.get('partial',0)}",
                   f"Missing vocabulary: {counts.get('unresolved-vocabulary',0)}",
                   f"Unsupported grammar: {counts.get('unsupported-grammar',0)}","",
                   "Target language realization profile:"]
            rp=grammar.get('realization_profile',{})
            for k in ('word_order','adposition_type','adjective_position','possessor_position','plural_strategy','comparison_strategy','question_strategy','negation_strategy','morphology_type','future','progressive','perfect','imperative'):
                if k in rp: lines.append(f"  {k}: {rp[k]}")
            coord=grammar.get('coordination',{})
            for k in ('np','predicate','clause'):
                if isinstance(coord.get(k),dict): lines.append(f"  {k}_coordination: {coord[k].get('strategy')}")
            lines += ["", "Construction inventory:"]
            for k,v in TRANSLATION_CAPABILITIES.items(): lines.append(f"  {k}: {v}")
            lines += ["","Most common constructions in non-complete sentences:"]
            for k,n in construction_counts.most_common(): lines.append(f"  {k}: {n}")
            lines += ["","Most common missing/unrecognized English lexemes:"]
            for k,n in missing_counts.most_common(50): lines.append(f"  {k}: {n}")
            lines += ["","Per-sentence diagnostics:","-"]
            for i,r in enumerate(results,1):
                if r['status']=='ok': continue
                lines += [f"#{i} {r['english']}",f"  Status: {r['status']}",f"  Reason: {r['reason']}",
                          f"  Constructions: {', '.join(r['ir'].get('constructions',[])) or 'simple'}",
                          f"  Normalized: {r['ir'].get('normalized_english') or '(unchanged)'}"]
                rs=r['ir'].get('realization_strategies',{})
                if rs:
                    compact=', '.join(f"{k}={v}" for k,v in rs.items() if v not in (None,{},[]))
                    lines.append(f"  Target strategies: {compact}")
                lines.append("")
            diag_path.write_text("\n".join(lines)+"\n",encoding="utf-8")
            json_path=output_path.with_name(output_path.stem+'_analysis.json')
            json_path.write_text(json.dumps({
                'language':name, 'summary':counts, 'provenance': {'translator_version': TOOL_VERSION, 'language_build_version': package_version, 'package_sha256': package_sha, 'grammar_sha256': grammar_sha, 'translator_sha256': translator_sha, 'contract_version': contract_version},
                'capabilities':TRANSLATION_CAPABILITIES, 'sentences':results
            },ensure_ascii=False,indent=2),encoding='utf-8')
            try: dshown=diag_path.relative_to(project)
            except ValueError: dshown=diag_path
            print(f"Diagnostics: {dshown}")
            try: jshown=json_path.relative_to(project)
            except ValueError: jshown=json_path
            print(f"Analysis JSON: {jshown}")

    return 2 if unresolved else 0


if __name__ == "__main__":
    raise SystemExit(main())
