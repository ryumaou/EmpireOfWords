"""Independent release-evidence validation; never trusts translator receipts."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

SEMANTIC_DIMENSIONS = (
    'roles', 'tense_aspect_mood', 'polarity', 'scope', 'reference',
    'lexical_content', 'target_grammar', 'no_english_fallback',
    'no_fabricated_receipts',
)
REQUIRED_CONSTRUCTIONS = {'conditional', 'relative_clause', 'complement_clause', 'passive'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized_sentence(text):
    return ' '.join(re.findall(r'[a-z]+', text.lower()))


def load_suite(root):
    root = Path(root)
    path = root / 'acceptance/holdout_v1.tsv'
    manifest = json.loads((root / 'acceptance/holdout_manifest.json').read_text(encoding='utf-8'))
    raw = path.read_text(encoding='utf-8')
    if hashlib.sha256(raw.encode('utf-8')).hexdigest() != manifest['suite_sha256']:
        raise ValueError('Holdout changed: create a new reviewed suite version, not a new score on edited cases')
    rows = list(csv.DictReader(raw.splitlines(), delimiter='\t'))
    if len(rows) != 200 or manifest['case_count'] != 200:
        raise ValueError('Exactly 200 cases are required')
    if {r['id'] for r in rows} != {f'H{i:03}' for i in range(1, 201)}:
        raise ValueError('Missing or duplicated case IDs')
    normalized = [normalized_sentence(r['english']) for r in rows]
    if len(set(normalized)) != 200:
        raise ValueError('Duplicate holdout sentences')
    counts = dict(Counter(r['construction'] for r in rows))
    if counts != manifest['construction_counts'] or not REQUIRED_CONSTRUCTIONS <= counts.keys():
        raise ValueError('Construction scope changed or required constructions missing')
    development = {normalized_sentence(s) for p in (root / 'translations').glob('*.txt')
                   for s in decode_corpus(p).splitlines()
                   if s.strip() and not s.lstrip().startswith('#')}
    overlap = set(normalized) & development
    if overlap:
        raise ValueError(f'Holdout overlaps development corpus: {sorted(overlap)}')
    return rows, manifest


def decode_corpus(path):
    raw = Path(path).read_bytes()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252')


def translation_identity(record):
    """Bind review to actual source and surface, not a self-reported success flag."""
    return digest({key: record[key] for key in
                   ('case_id', 'english', 'language', 'package_sha256', 'source_sha256', 'surface')})


def assess_holdout(rows, manifest, translations, reviews):
    languages = sorted({r['language'] for r in translations})
    errors = []
    expected = {(lang, row['id']) for lang in languages for row in rows}
    indexed = {}
    cases = {r['id']: r for r in rows}
    for record in translations:
        key = (record['language'], record['case_id'])
        if key in indexed:
            errors.append(f'Duplicate translation: {key}')
        indexed[key] = record
        if record['case_id'] not in cases or record['english'] != cases[record['case_id']]['english']:
            errors.append(f'Unexpected or altered case: {key}')
    if len(languages) != 10 or set(indexed) != expected:
        errors.append('Exactly ten complete 200-case language result sets are required')
    suite_review = reviews.get('suite_review') or {}
    suite_approved = (
        suite_review.get('suite_sha256') == manifest['suite_sha256']
        and suite_review.get('approved') is True
        and suite_review.get('independent_of_implementation') is True
        and bool(suite_review.get('reviewer'))
        and suite_review.get('reviewer') not in manifest['authors']
        and bool(suite_review.get('notes'))
    )
    judgments = {}
    for judgment in reviews.get('judgments', []):
        key = (judgment.get('language'), judgment.get('case_id'))
        if key in judgments:
            errors.append(f'Duplicate semantic judgment: {key}')
        judgments[key] = judgment
        if key not in expected:
            errors.append(f'Unknown judgment target: {key}')
    result = {}
    all_constructions = set(manifest['construction_counts'])
    for language in languages:
        correct = reviewed = complete = 0
        construction_correct = Counter()
        failures = []
        for row in rows:
            key = (language, row['id'])
            record = indexed.get(key)
            if not record:
                failures.append({'id': row['id'], 'reason': 'missing output'})
                continue
            complete += record['status'] == 'ok'
            review = judgments.get(key, {})
            valid = (review.get('output_sha256') == translation_identity(record)
                     and review.get('independent_of_implementation') is True
                     and bool(review.get('reviewer'))
                     and review.get('reviewer') not in manifest['authors']
                     and bool(review.get('notes'))
                     and all(type(review.get('dimensions', {}).get(k)) is bool for k in SEMANTIC_DIMENSIONS))
            reviewed += valid
            preserved = valid and all(review['dimensions'].values())
            usable = (record['status'] == 'ok' and bool(record['surface'].strip())
                      and '[' not in record['surface']
                      and normalized_sentence(record['surface']) != normalized_sentence(record['english']))
            if preserved and usable:
                correct += 1
                construction_correct[row['construction']] += 1
            else:
                failures.append({'id': row['id'], 'reason':
                                 'unreviewed or stale independent review' if not valid else
                                 'semantic failure or unavailable target output'})
        result[language] = {'total': 200, 'translator_complete': complete,
                            'independently_reviewed': reviewed, 'independently_correct': correct,
                            'verified_accuracy': correct / 200,
                            'construction_correct': dict(construction_correct),
                            'unverified_constructions': sorted(group for group in all_constructions
                                                               if construction_correct[group] < 9),
                            'failures': failures}
    evidence_ready = suite_approved and not errors and len(result) == 10
    return {'pass': evidence_ready and all(r['independently_reviewed'] == 200 and
                                           r['independently_correct'] >= 190 for r in result.values()),
            'construction_support_pass': evidence_ready and all(not r['unverified_constructions'] for r in result.values()),
            'suite_independently_approved': suite_approved, 'input_errors': errors,
            'languages': result,
            'note': 'Translator status and receipts are diagnostic only. Unreviewed is not incorrect, but cannot pass.'}


def word_errors(package):
    errors = []
    for entry in package['lexicon']:
        if not re.fullmatch(r'[a-z]{2,}', entry.get('form', '')):
            errors.append(f"lexicon {entry['gloss']}:{entry['pos']}={entry.get('form')!r}")
    for group in ('pronouns', 'demonstratives', 'interrogatives', 'particles'):
        for key, word in package['grammar'].get(group, {}).items():
            if not re.fullmatch(r'[a-z]{2,}', word):
                errors.append(f'{group}.{key}={word!r}')
    return errors


GRAMMAR_PATHS = (
    ('word_order',), ('adposition_type',), ('adjective_position',), ('possessor_position',),
    ('noun', 'plural_strategy'), ('noun', 'cases'), ('verb', 'agreement'),
    ('verb', 'negation'), ('comparison', 'strategy'), ('questions', 'strategy'),
)


def grammar_signature(package):
    values = []
    for path in GRAMMAR_PATHS:
        value = package['grammar']
        for key in path:
            value = value.get(key, {})
        values.append(json.dumps(value, sort_keys=True))
    return values


def assess_diversity(packages, observed_orders):
    """Require actual core-clause order as well as lexicon/profile differences."""
    pairs = []
    for i, a in enumerate(packages):
        for b in packages[i + 1:]:
            left = {(x['gloss'], x['pos']): x['form'] for x in a['lexicon']}
            right = {(x['gloss'], x['pos']): x['form'] for x in b['lexicon']}
            common = left.keys() & right.keys()
            identical = sum(left[k] == right[k] for k in common) / max(1, len(common))
            differences = sum(x != y for x, y in zip(grammar_signature(a), grammar_signature(b)))
            pairs.append({'languages': [a['name'], b['name']], 'common_lexemes': len(common),
                          'identical_fraction': identical, 'grammatical_differences': differences,
                          'pass': len(common) >= 100 and identical <= 0.20 and differences >= 2})
    orders = {r.get('observed') for r in observed_orders if r.get('pass')}
    return {'pass': len(packages) == 10 and len({p['seed'] for p in packages}) == 10
            and len(pairs) == 45 and all(p['pass'] for p in pairs)
            and len(observed_orders) == 10 and all(r['pass'] for r in observed_orders)
            and len(orders) >= 3,
            'pairs': pairs, 'observed_orders': observed_orders,
            'thresholds': '45 pairs: >=100 common keys, <=20% identical forms, >=2/10 grammar differences; >=3 observed word orders'}
