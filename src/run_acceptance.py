"""Run production acceptance without altering existing generated languages.

Exit 0 means ALL eight release criteria pass; 1 means incomplete/failed evidence;
2 means invalid runner configuration. Full semantic review is never inferred from
the translator's status, gloss, parser IR or realization receipts.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch
import venv

from acceptance_gate import (assess_diversity, assess_holdout, digest, file_digest,
                             load_suite, translation_identity, word_errors)

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('romance', 'germanic', 'slavic', 'arabic', 'turkic',
            'japanese', 'celtic', 'bantu', 'analytic', 'random')


def snapshot(path):
    return {p.relative_to(path).as_posix(): file_digest(p)
            for p in sorted(path.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def run_process(args, log, *, cwd=ROOT, environment=None, timeout=240):
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1', PYTHONIOENCODING='utf-8')
    env.update(environment or {})
    try:
        proc = subprocess.run([str(a) for a in args], cwd=cwd, env=env, capture_output=True,
                              text=True, encoding='utf-8', errors='replace', timeout=timeout)
        code, output = proc.returncode, proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        code, output = 124, 'Command exceeded acceptance timeout\n'
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(output, encoding='utf-8')
    return {'pass': code == 0, 'exit_code': code, 'log': str(log)}


def build_languages(destination):
    records, packages = [], []
    source = ROOT / 'data/magic.txt'
    vocabulary = ROOT / 'vocabulary/MagicVocabulary.txt'
    for index, family in enumerate(FAMILIES):
        name = f'Acceptance{index + 1:02}'
        seed = 21000 + index * 97
        print(f'Generating {name}: {family}, seed {seed}', flush=True)
        roots = [destination / 'builds/first', destination / 'builds/repeat']
        attempts = []
        for project, hash_seed in zip(roots, ('1', '987654')):
            project.mkdir(parents=True, exist_ok=True)
            attempts.append(run_process([
                sys.executable, '-B', ROOT / 'src/build_language.py', '--project-root', project,
                '--source', source, '--vocabulary', vocabulary, '--language-name', name,
                '--grammar-family', family, '--morphophonemics', 'none', '--seed', seed,
            ], destination / 'logs' / f'build_{project.name}_{name}.log',
                environment={'PYTHONHASHSEED': hash_seed}))
        left, right = (p / 'output' / name for p in roots)
        record = {'language': name, 'family': family, 'seed': seed, 'attempts': attempts,
                  'reproducible': all(a['pass'] for a in attempts) and snapshot(left) == snapshot(right)}
        if all(a['pass'] for a in attempts):
            data = json.loads((left / 'language.json').read_text(encoding='utf-8'))
            record['word_errors'] = word_errors(data)
            record['validation'] = run_process([
                sys.executable, '-B', ROOT / 'src/validate_language.py', '--language', left,
            ], destination / 'logs' / f'validate_{name}.log')
            packages.append((left, data))
        records.append(record)
    return records, packages


def observe_core_order(path, package):
    # Independent observation: locate real lexical stems in surface output, not
    # in the translator's gloss, IR, receipts or declared realization strategy.
    from grammar_engine import analyze_translation
    from language_io import load_language
    _, grammar, entries, forms = load_language(path / 'language.json')
    result = analyze_translation('The dog sees the cat.', grammar, entries, forms)
    lexicon = {(e['gloss'], e['pos']): e['form'] for e in package['lexicon']}
    positions = {}
    surface = result['surface']
    for role, key in (('S', ('dog', 'n')), ('V', ('see', 'v')), ('O', ('cat', 'n'))):
        form = lexicon.get(key)
        if form and surface.count(form) == 1:
            positions[role] = surface.index(form)
    observed = ''.join(sorted(positions, key=positions.get)) if len(positions) == 3 else None
    return {'language': package['name'], 'observed': observed, 'declared': grammar['word_order'],
            'surface': surface, 'pass': result['status'] == 'ok' and observed == grammar['word_order']}


def vocabulary_probe(destination, source):
    import add_words
    copies = [destination / 'vocabulary' / name for name in ('first', 'repeat', 'fault', 'publish_fault')]
    for target in copies:
        shutil.copytree(source, target)
    requested = destination / 'vocabulary/additions.txt'
    requested.write_text('frobnicator:n\nfrobnicator:n\nquuxling:n\ndog:n\n', encoding='utf-8')
    original = json.loads((source / 'language.json').read_text(encoding='utf-8'))
    before_source = snapshot(source)
    for target in copies[:2]:
        result = run_process([sys.executable, '-B', ROOT / 'src/add_words.py', '--language', target,
                              '--words', requested, '--seed', '4519'],
                             destination / 'logs' / f'expand_{target.name}.log')
        if not result['pass']:
            return {'pass': False, 'error': 'Vocabulary expansion CLI failed', 'command': result}
    changed = json.loads((copies[0] / 'language.json').read_text(encoding='utf-8'))
    lookup = {(x['gloss'], x['pos']): x for x in changed['lexicon']}
    preserved = (changed['lexicon'][:len(original['lexicon'])] == original['lexicon']
                 and all(changed.get(key) == value for key, value in original.items()
                         if key not in ('lexicon', 'lexicon_extensions'))
                 and len(changed['lexicon']) == len(original['lexicon']) + 2)
    repeatable = snapshot(copies[0]) == snapshot(copies[1])
    before_noop = snapshot(copies[0])
    noop = run_process([sys.executable, '-B', ROOT / 'src/add_words.py', '--language', copies[0],
                        '--words', requested, '--seed', '9999'], destination / 'logs/expand_noop.log')
    idempotent = noop['pass'] and before_noop == snapshot(copies[0])
    malformed = destination / 'vocabulary/invalid.txt'
    malformed.write_text('not a gloss and pos\n', encoding='utf-8')
    bad = run_process([sys.executable, '-B', ROOT / 'src/add_words.py', '--language', copies[0],
                       '--words', malformed, '--seed', '4519'], destination / 'logs/expand_invalid.log')
    invalid_safe = not bad['pass'] and before_noop == snapshot(copies[0])
    before_fault = snapshot(copies[2])
    caught = False
    buffer = io.StringIO()
    with patch('add_words.rewrite_dictionary', side_effect=OSError('acceptance-injected disk write failure')):
        with redirect_stdout(buffer), redirect_stderr(buffer):
            try:
                add_words.main(['--language', str(copies[2]), '--words', str(requested), '--seed', '4519'])
            except OSError:
                caught = True
    fault_safe = caught and before_fault == snapshot(copies[2])
    before_publish_fault = snapshot(copies[3])
    original_replace = add_words.os.replace
    replacements = 0
    def fail_second_replace(source_path, target_path):
        nonlocal replacements
        replacements += 1
        if replacements == 2:
            raise OSError('acceptance-injected publication failure')
        return original_replace(source_path, target_path)
    with patch('add_words.os.replace', side_effect=fail_second_replace):
        with redirect_stdout(buffer), redirect_stderr(buffer):
            try:
                add_words.main(['--language', str(copies[3]), '--words', str(requested), '--seed', '4519'])
            except OSError:
                pass
    publish_safe = replacements >= 2 and before_publish_fault == snapshot(copies[3])
    unchanged_source = before_source == snapshot(source)
    checks = {'existing_forms_and_grammar_preserved': preserved, 'same_seed_repeatable': repeatable,
              'duplicate_request_is_noop': idempotent, 'malformed_request_is_safe': invalid_safe,
              'failed_write_leaves_package_unchanged': fault_safe,
              'failed_publication_rolls_back': publish_safe,
              'original_package_unchanged': unchanged_source,
              'new_words_valid': not word_errors(changed)}
    return {'pass': all(checks.values()), 'checks': checks,
            'fault_changed_files': sorted(k for k in before_fault.keys() | snapshot(copies[2]).keys()
                                         if before_fault.get(k) != snapshot(copies[2]).get(k))}


def clean_install(destination):
    print('Checking isolated installation and documented CLI workflows', flush=True)
    with tempfile.TemporaryDirectory(prefix='eow-clean-') as temp:
        checkout = Path(temp) / 'project'
        checkout.mkdir()
        for name in ('src', 'tests', 'acceptance', 'translations', 'vocabulary', 'data'):
            shutil.copytree(ROOT / name, checkout / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        # Regression fixtures are versioned packages, not development outputs.
        for language in (ROOT / 'output').glob('*/language.json'):
            target = checkout / language.parent.relative_to(ROOT)
            target.mkdir(parents=True)
            for item in language.parent.iterdir():
                if item.is_file():
                    shutil.copy2(item, target / item.name)
        for name in ('README.md', 'verify_install.cmd'):
            shutil.copy2(ROOT / name, checkout / name)
        env_path = Path(temp) / 'venv'
        venv.EnvBuilder(with_pip=False).create(env_path)
        python = env_path / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        tests = run_process([python, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-q'],
                            destination / 'logs/clean_regression.log', cwd=checkout)
        cli = run_process([python, '-B', checkout / 'src/verify_install.py'],
                          destination / 'logs/clean_cli.log', cwd=checkout)
        demo = checkout / 'demo'
        build = run_process([python, '-B', checkout / 'src/build_language.py', '--project-root', demo,
                             '--source', checkout / 'data/magic.txt', '--vocabulary', checkout / 'vocabulary/MagicVocabulary.txt',
                             '--language-name', 'Smoke', '--seed', '7351'],
                            destination / 'logs/clean_documented_build.log', cwd=checkout)
        translation = run_process([python, '-B', checkout / 'src/translate.py', '--language', demo / 'output/Smoke',
                                   '--sentence', 'The dog sees the cat.'],
                                  destination / 'logs/clean_documented_translate.log', cwd=checkout)
        return {'pass': all(x['pass'] for x in (tests, cli, build, translation)),
                'regression': tests, 'cli': cli, 'documented_build': build, 'documented_translation': translation,
                'environment': 'Fresh stdlib-only venv, no pip, no user site packages or repository caches',
                'scope': 'Current operating system and Python version; other platforms require separate runs'}


def development_contrasts(destination):
    from grammar_engine import analyze_translation, load_translation_sentences
    from language_io import load_language
    results = {}
    for path in sorted((ROOT / 'output').glob('*/language.json')):
        _, g, entries, forms = load_language(path)
        results[path.parent.name] = {}
        for corpus in sorted((ROOT / 'translations').glob('*.txt')):
            rows = [analyze_translation(s, g, entries, forms) for s in load_translation_sentences(corpus)]
            results[path.parent.name][corpus.stem] = {
                'counts': dict(Counter(row['status'] for row in rows)),
                'sentences': [{k: row[k] for k in ('english', 'status', 'surface', 'gloss')} for row in rows],
            }
    (destination / 'development_results.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    return results


def write_status(path, report, destination):
    rows = ['# Empire Of Words — project status', '',
            'Production acceptance: **' + ('SATISFIED' if report['pass'] else 'NOT SATISFIED') + '**.', '',
            f"Evidence generated: {report['timestamp']}. Python {report['python']}; {report['platform']}.", '',
            '## Acceptance results', '', '| Criterion | Result | Evidence |', '|---|---|---|']
    for key, value in report['criteria'].items():
        rows.append(f"| {key} | {'PASS' if value['pass'] else 'FAIL / NOT VERIFIED'} | {value['summary']} |")
    rows += ['', '## Failures and regressions', '']
    rows += ['- ' + item for item in report['remaining_failures']]
    rows += ['', '## Iteration evidence', '',
             f"- Regression suite: {report['regression']['test_count']} tests passed; semantic fixtures: {report['semantic_fixtures']['fixture_count']} passed.",
             f"- Holdout translator completion: {min(r['translator_complete'] for r in report['holdout']['languages'].values())}–{max(r['translator_complete'] for r in report['holdout']['languages'].values())}/200 per language; independently reviewed: {sum(r['independently_reviewed'] for r in report['holdout']['languages'].values())}/2,000; independently correct: {sum(r['independently_correct'] for r in report['holdout']['languages'].values())}/2,000.",
             f"- Ten-language generation: {sum(r['reproducible'] for r in report['generation'])}/10 reproducible; {sum(p['pass'] for p in report['diversity']['pairs'])}/45 distinct pairs; {len({r['observed'] for r in report['diversity']['observed_orders'] if r['pass']})} observed core word orders.",
             f"- Vocabulary expansion: {sum(report['vocabulary'].get('checks', {}).values())}/{len(report['vocabulary'].get('checks', {}))} safety checks; existing packages: {report['existing_file_count']} files preserved.",
             f"- Clean-install workflow: {'passed' if report['clean_install']['pass'] else 'failed'} on {report['platform']} / Python {report['python']}.",
             f"- Regression comparison: {report['regressions']['summary']}"]
    if report.get('iteration_comparison'):
        comparison = report['iteration_comparison']
        rows.append(f"- Versus prior iteration: {', '.join(comparison['newly_passing_criteria']) or 'none'} newly passing; {', '.join(comparison['newly_failing_criteria']) or 'none'} newly failing; vocabulary safety {comparison['vocabulary_checks_before']} → {comparison['vocabulary_checks_after']} checks; translation completion {comparison['coverage_delta_min']} to {comparison['coverage_delta_max']} sentences per language.")
    rows += ['',
             'A translator completion flag is never an independent semantic correctness score.', '',
             '## Next priority and architectural decision', '',
             'The major parser revision is underway. Explicit two-clause conditionals now use separate',
             'condition and consequence IR nodes. Explicit finite passives now bind patient and agent',
             'roles and use the target passive strategy; new morphological packages include an affix.',
             'Existing language packages remain immutable; incomplete old strategies fail safely.',
             'Next: role-aware relative gaps, complement arguments, and complex passive clauses.',
             'These need a compositional source-span contract and an independent target-semantic oracle.', '',
             'Vocabulary expansion passes simulated writer and publication failures; power-loss',
             'recovery remains unverified and needs a durable transaction design.',
             'The new 200-case suite is a frozen candidate, not independently approved ground truth.',
             'Independent suite approval, per-output review and implementation-integrity review are pending.',
             'Do not tune translation rules on these cases; create a replacement blind holdout if exposed',
             'cases are used during implementation. No claim of 95% correctness is made.', '',
             '## Reproduce and inspect', '',
             f'- Full evidence: `{destination.relative_to(ROOT).as_posix() if destination.is_relative_to(ROOT) else destination}/report.json`',
             '- Command: `python -B src/run_acceptance.py --output acceptance-runs/next-iteration`',
             '- Add `--previous <prior-run>/report.json` to enforce sentence-level development status comparisons.',
             '- Policy and independent-review protocol: `acceptance/README.md`.',
             '- A clean-install pass applies only to the recorded OS/Python; it is not a cross-platform certificate.', '']
    path.write_text('\n'.join(rows), encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='new empty run directory, outside output/')
    parser.add_argument('--reviews', type=Path, default=ROOT / 'acceptance/semantic_reviews.json')
    parser.add_argument('--previous', type=Path, help='prior report.json for development-regression comparison')
    parser.add_argument('--status-file', type=Path, default=ROOT / 'PROJECT_STATUS.md')
    args = parser.parse_args(argv)
    destination = args.output.resolve()
    if destination.is_relative_to(ROOT / 'output') or (destination.exists() and any(destination.iterdir())):
        parser.error('Use a new empty run directory outside existing output packages')
    try:
        cases, manifest = load_suite(ROOT)
        reviews = json.loads(args.reviews.read_text(encoding='utf-8'))
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    destination.mkdir(parents=True, exist_ok=True)
    before = snapshot(ROOT / 'output')
    source_sha = digest({p.name: file_digest(p) for p in sorted((ROOT / 'src').glob('*.py'))})
    report = {'timestamp': datetime.now(timezone.utc).isoformat(), 'python': sys.version.split()[0],
              'platform': sys.platform, 'source_sha256': source_sha, 'suite_sha256': manifest['suite_sha256']}
    print('Running regression and semantic fixture suites', flush=True)
    report['regression'] = run_process([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'tests', '-q'],
                                       destination / 'logs/regression.log')
    report['semantic_fixtures'] = run_process([sys.executable, '-B', ROOT / 'src/semantic_audit.py'],
                                              destination / 'logs/semantic_fixtures.log')
    regression_log = Path(report['regression']['log']).read_text(encoding='utf-8')
    fixture_log = Path(report['semantic_fixtures']['log']).read_text(encoding='utf-8')
    import re
    report['regression']['test_count'] = int(re.search(r'Ran (\d+) tests?', regression_log).group(1)) if re.search(r'Ran (\d+) tests?', regression_log) else 0
    report['semantic_fixtures']['fixture_count'] = int(re.search(r'(\d+)\s+semantic fixture', fixture_log).group(1)) if re.search(r'(\d+)\s+semantic fixture', fixture_log) else 0
    builds, generated = build_languages(destination)
    report['generation'] = builds
    report['diversity'] = assess_diversity([p for _, p in generated],
                                         [observe_core_order(path, p) for path, p in generated])
    print('Evaluating frozen holdout candidates (coverage only until independent review)', flush=True)
    from grammar_engine import analyze_translation
    from language_io import load_language
    translations = []
    for path, package in generated:
        _, grammar, entries, forms = load_language(path / 'language.json')
        for case in cases:
            out = analyze_translation(case['english'], grammar, entries, forms)
            record = {'case_id': case['id'], 'english': case['english'], 'construction': case['construction'],
                      'language': package['name'], 'package_sha256': file_digest(path / 'language.json'),
                      'source_sha256': source_sha, 'surface': out['surface'], 'status': out['status']}
            record['output_sha256'] = translation_identity(record)
            translations.append(record)
    (destination / 'holdout_outputs.json').write_text(json.dumps(translations, indent=2), encoding='utf-8')
    report['holdout'] = assess_holdout(cases, manifest, translations, reviews)
    report['vocabulary'] = vocabulary_probe(destination, generated[0][0]) if generated else {'pass': False, 'error': 'no package generated'}
    report['clean_install'] = clean_install(destination)
    print('Checking all development corpora and existing-language contrast probes', flush=True)
    development = development_contrasts(destination)
    report['regressions'] = {'pass': True, 'summary': 'Baseline established; no prior-run comparison supplied.', 'new_failures': [], 'changed_complete': []}
    if args.previous:
        old_path = args.previous.resolve().parent / 'development_results.json'
        old = json.loads(old_path.read_text(encoding='utf-8'))
        if old.keys() != development.keys():
            raise ValueError('Development language set changed')
        for language in development:
            if old[language].keys() != development[language].keys():
                raise ValueError('Development corpus set changed')
            for corpus, data in development[language].items():
                left = old[language][corpus]['sentences']
                right = data['sentences']
                if [x['english'] for x in left] != [x['english'] for x in right]:
                    raise ValueError('Development corpus changed')
                for i, (a, b) in enumerate(zip(left, right), 1):
                    item = {'language': language, 'corpus': corpus, 'id': i}
                    if a['status'] == 'ok' and b['status'] != 'ok':
                        report['regressions']['new_failures'].append(item)
                    if a['status'] == b['status'] == 'ok' and (a['surface'], a['gloss']) != (b['surface'], b['gloss']):
                        report['regressions']['changed_complete'].append(item)
        failures = len(report['regressions']['new_failures'])
        changes = len(report['regressions']['changed_complete'])
        report['regressions']['pass'] = failures == changes == 0
        report['regressions']['summary'] = f'{failures} newly non-complete; {changes} changed complete outputs requiring semantic review.'
    language_paths = sorted(p.parent for p in (ROOT / 'output').glob('*/language.json'))
    audit = run_process([sys.executable, '-B', ROOT / 'src/audit_languages.py', '--languages', *language_paths,
                         '--output', destination / 'contrast_audit'], destination / 'logs/contrast_audit.log')
    audit_text = (destination / 'contrast_audit/language_audit.md').read_text(encoding='utf-8')
    audit['pass'] = audit['pass'] and ': FAIL' not in audit_text and ': INCONCLUSIVE' not in audit_text
    report['contrasts'] = audit
    report['existing_packages_preserved'] = before == snapshot(ROOT / 'output')
    report['existing_file_count'] = len(before)
    integrity = reviews.get('implementation_review') or {}
    integrity_pass = (integrity.get('source_sha256') == source_sha and integrity.get('approved') is True
                      and integrity.get('independent_of_implementation') is True
                      and bool(integrity.get('reviewer')) and integrity.get('reviewer') not in manifest['authors']
                      and bool(integrity.get('notes')) and report['holdout']['pass'])
    words_pass = (len(builds) == 10 and all(r['reproducible'] and not r.get('word_errors', ['missing build'])
                                         and r.get('validation', {}).get('pass') for r in builds))
    coverage = [r['translator_complete'] for r in report['holdout']['languages'].values()]
    def criterion(passed, summary): return {'pass': bool(passed), 'summary': summary}
    report['criteria'] = {
        '1. Regression tests': criterion(report['regression']['pass'] and report['semantic_fixtures']['pass']
                                         and report['regressions']['pass'] and audit['pass'], 'Regression, semantic fixtures, development comparison and contrast audit'),
        '2. Independent holdout >=95%': criterion(report['holdout']['pass'],
            f'Coverage only: {min(coverage, default=0)}–{max(coverage, default=0)}/200; independent semantic approval required'),
        '3. Construction support': criterion(report['holdout']['construction_support_pass'],
            'All 20 construction groups, including conditionals, relatives, complements and passive, require at least 9/10 independently correct examples in every language'),
        '4. Ten distinct languages': criterion(report['diversity']['pass'], '45 lexical/grammar comparisons plus independent surface-order observations'),
        '5. Safe vocabulary expansion': criterion(report['vocabulary']['pass'] and report['existing_packages_preserved'],
            'Preservation, repeatability, idempotency, malformed-input rejection and injected write failure'),
        '6. Word invariants and reproducibility': criterion(words_pass, 'All lexical/free grammatical forms [a-z]{2,}; ten repeat builds with different Python hash seeds'),
        '7. No inflated semantic metrics': criterion(integrity_pass, 'Independent source audit and hash-bound semantic judgments required; receipts never award credit'),
        '8. Clean installation': criterion(report['clean_install']['pass'], 'Fresh venv regression, CLI help/version and documented build/translate workflow'),
    }
    report['remaining_failures'] = [key + ': ' + value['summary'] for key, value in report['criteria'].items() if not value['pass']]
    report['pass'] = all(value['pass'] for value in report['criteria'].values()) and report['existing_packages_preserved']
    if args.previous:
        previous = json.loads(args.previous.read_text(encoding='utf-8'))
        current_coverage = {k: v['translator_complete'] for k, v in report['holdout']['languages'].items()}
        old_coverage = {k: v['translator_complete'] for k, v in previous['holdout']['languages'].items()}
        coverage_deltas = [current_coverage[k] - old_coverage[k] for k in current_coverage]
        report['iteration_comparison'] = {
            'newly_passing_criteria': [k for k, v in report['criteria'].items() if v['pass'] and not previous['criteria'][k]['pass']],
            'newly_failing_criteria': [k for k, v in report['criteria'].items() if not v['pass'] and previous['criteria'][k]['pass']],
            'vocabulary_checks_before': f"{sum(previous['vocabulary'].get('checks', {}).values())}/{len(previous['vocabulary'].get('checks', {}))}",
            'vocabulary_checks_after': f"{sum(report['vocabulary'].get('checks', {}).values())}/{len(report['vocabulary'].get('checks', {}))}",
            'coverage_delta_min': min(coverage_deltas), 'coverage_delta_max': max(coverage_deltas),
        }
    (destination / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    write_status(args.status_file.resolve(), report, destination)
    for key, value in report['criteria'].items():
        print(('PASS ' if value['pass'] else 'NOT SATISFIED ') + key, flush=True)
    print('Report:', destination / 'report.json')
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
