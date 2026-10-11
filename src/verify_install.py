"""Cross-platform, read-only installation check (not production acceptance)."""
from pathlib import Path
import subprocess
import sys


def main():
    source = Path(__file__).resolve().parent
    commands = [([source / 'translate.py', '--version'], 'translator version')]
    commands += [([source / (name + '.py'), '--help'], name) for name in (
        'build_language', 'translate', 'validate_language', 'add_words', 'generate_daughter',
        'generate_names', 'audit_languages', 'compare_diagnostics', 'quality_gate',
        'semantic_audit', 'vocabulary_preflight', 'run_acceptance', 'lc')]
    failed = []
    for args, label in commands:
        result = subprocess.run([sys.executable, '-B', *map(str, args)], capture_output=True, text=True)
        print(('PASS ' if result.returncode == 0 else 'FAIL ') + label)
        if result.returncode != 0:
            failed.append(label)
            print(result.stderr)
    print('Installation smoke check only; run run_acceptance.py for production criteria.')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
