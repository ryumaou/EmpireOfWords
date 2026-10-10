import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from grammar_engine import load_translation_sentences

phase = sys.argv[1]
destination = WORK / phase
destination.mkdir(exist_ok=True)
languages = sorted(p.parent.name for p in (ROOT / 'output').glob('*/language.json'))
corpora = sorted((ROOT / 'translations').glob('*.txt'))
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for name in languages for p in (ROOT / 'output' / name).rglob('*') if p.is_file()}
(destination / 'preserved_files.json').write_text(json.dumps(manifest, indent=2))
def run(args, label, allowed=(0,)):
    result = subprocess.run([sys.executable, '-B', *args], cwd=ROOT, capture_output=True, text=True)
    (destination / (label + '.log')).write_text(result.stdout + result.stderr, encoding='utf-8')
    if result.returncode not in allowed:
        print(result.stdout, result.stderr)
        raise SystemExit(f'{label}: exit {result.returncode}')
    return result

run(['-m', 'unittest', 'discover', '-s', 'tests', '-v'], 'regression')
run(['src/semantic_audit.py'], 'semantic')
summary = {}
for corpus in corpora:
    stem = corpus.stem
    for name in languages:
        out = destination / name / (stem + '.txt')
        run(['src/translate.py', '--language', 'output/' + name, '--input', str(corpus),
             '--output', str(out), '--diagnostics'], name + '_' + stem, (0, 2))
        data = json.loads(out.with_name(stem + '_analysis.json').read_text(encoding='utf-8'))
        summary[name + '/' + stem] = data['summary']
    if phase != 'baseline':
        gate = ['src/quality_gate.py', '--before']
        gate += [str(WORK / 'baseline' / name / (stem + '_diagnostics.txt')) for name in languages]
        gate += ['--after'] + [str(destination / name / (stem + '_diagnostics.txt')) for name in languages]
        gate += ['--before-corpus', str(corpus), '--after-corpus', str(corpus), '--json-output',
                 str(destination / (stem + '_gate.json'))]
        print(run(gate, stem + '_gate').stdout.strip())
run(['src/audit_languages.py', '--languages', *['output/' + n for n in languages],
     '--output', str(destination / 'audit')], 'audit')
audit = (destination / 'audit/language_audit.md').read_text(encoding='utf-8')
if ': FAIL' in audit:
    raise SystemExit('Contrast audit failure')
if phase != 'baseline':
    original = json.loads((WORK / 'baseline/preserved_files.json').read_text())
    assert manifest == original, 'Existing language files changed'
    changes = []
    for corpus in corpora:
        for name in languages:
            filename = corpus.stem + '_analysis.json'
            before = json.loads((WORK / 'baseline' / name / filename).read_text(encoding='utf-8'))
            after = json.loads((destination / name / filename).read_text(encoding='utf-8'))
            for i, (a, b) in enumerate(zip(before['sentences'], after['sentences']), 1):
                if (a['status'], a['surface'], a['gloss']) != (b['status'], b['surface'], b['gloss']):
                    changes.append({'language': name, 'corpus': corpus.stem, 'id': i,
                                    'sentence': a['english'], 'before': a, 'after': b})
    (destination / 'changes.json').write_text(json.dumps(changes, indent=2), encoding='utf-8')
    print('Changed translations:', len(changes))
(destination / 'summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
print('All checks passed; existing language files preserved:', len(manifest))
