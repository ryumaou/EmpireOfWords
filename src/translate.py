#!/usr/bin/env python3
"""Translate English sentences with an existing generated conlang package.

This tool never generates or modifies a language. It loads output/<Language>/language.json
and reuses grammar_engine.translate_sentence() for deterministic translation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from grammar_engine import load_translation_sentences, analyze_translation, TRANSLATION_CAPABILITIES
from language_io import resolve_project_path, resolve_language_path, load_language, validate_package


def format_result(result) -> str:
    return (
        f"[{result['type']}]\n"
        f"English: {result['english']}\n"
        f"Language: {result['surface']}\n"
        f"Gloss: {result['gloss']}\n"
        f"Status: {result['status']}\n"
        f"Reason: {result['reason']}\n"
    )


def main(argv=None) -> int:
    root_default = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(
        description="Translate English sentences using an existing generated language.json"
    )
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
                   f"Sentences: {len(results)}",f"Complete: {counts.get('ok',0)}",
                   f"Partial: {counts.get('partial',0)}",
                   f"Missing vocabulary: {counts.get('unresolved-vocabulary',0)}",
                   f"Unsupported grammar: {counts.get('unsupported-grammar',0)}","",
                   "Construction inventory:"]
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
                          f"  Normalized: {r['ir'].get('normalized_english') or '(unchanged)'}",""]
            diag_path.write_text("\n".join(lines)+"\n",encoding="utf-8")
            missing_path=output_path.with_name(output_path.stem+'_missing_words.txt')
            missing_lines=["# Missing/unrecognized English words from translation diagnostics",
                           "# Review these and add desired entries to a supplemental vocabulary file as gloss:pos.",
                           "# Counts are shown after #; this file is intentionally POS-neutral.", ""]
            for word,n in missing_counts.most_common(): missing_lines.append(f"{word}  # {n}")
            missing_path.write_text("\n".join(missing_lines)+"\n",encoding="utf-8")
            json_path=output_path.with_name(output_path.stem+'_analysis.json')
            json_path.write_text(json.dumps({
                'language':name, 'summary':counts,
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
