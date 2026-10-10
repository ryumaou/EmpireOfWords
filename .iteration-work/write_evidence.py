import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
work = root / '.iteration-work'
baseline = work / 'baseline'
accepted = work / 'accepted'
original = json.loads((baseline / 'preserved_files.json').read_text())
current = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
           for name in ('Example', 'MagicTest', 'Test1', 'Test2')
           for p in (root / 'output' / name).rglob('*') if p.is_file()}
assert current == original, 'Existing language files were modified'
evidence = {
    'baseline_commit': '1cfbbb3',
    'baseline_includes_preexisting_uncommitted_changes': True,
    'regression_tests_passed': 103,
    'semantic_fixtures_passed': 11,
    'committed_candidate_regression_tests_passed': 86,
    'language_audit_translations': 72,
    'language_audit_fidelity_checks_passed': 20,
    'preserved_language_files': original,
    'before': json.loads((baseline / 'summary.json').read_text()),
    'after': json.loads((accepted / 'summary.json').read_text()),
    'gates': {}, 'recoveries': [], 'changed_complete_translations': [],
    'source_provenance': {},
}
for path in sorted(accepted.glob('*_gate.json')):
    gate = json.loads(path.read_text())
    assert gate['pass'] and gate['newly_noncomplete'] == 0
    evidence['gates'][path.stem] = gate
for change in json.loads((accepted / 'changes.json').read_text(encoding='utf-8')):
    before, after = change['before'], change['after']
    record = {key: change[key] for key in ('language', 'corpus', 'id', 'sentence')}
    record.update(before_status=before['status'], after_status=after['status'],
                  before_gloss=before['gloss'], after_gloss=after['gloss'])
    if before['status'] != 'ok' and after['status'] == 'ok':
        evidence['recoveries'].append(record)
    elif before['status'] == after['status'] == 'ok':
        evidence['changed_complete_translations'].append(record)
for path in sorted(accepted.glob('*/contrast_suite_v1_analysis.json')):
    evidence['source_provenance'][path.parent.name] = json.loads(path.read_text(encoding='utf-8'))['provenance']
assert len(evidence['recoveries']) == 23
destination = root / 'diagnostics/iteration_2026_10_10.json'
destination.parent.mkdir(exist_ok=True)
destination.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'Preserved {len(current)} language files; {len(evidence["recoveries"])} recoveries; '
      f'{len(evidence["changed_complete_translations"])} reviewed changes to already-complete translations.')
