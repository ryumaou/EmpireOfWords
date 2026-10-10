"""Mixed punctuation must preserve every command and its own arguments."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from grammar_engine import analyze_translation
from language_io import load_language


class SemicolonCommandTests(unittest.TestCase):
    def test_three_commands_keep_mood_and_arguments(self):
        for name in ('Example', 'Test1', 'Test2'):
            _, grammar, entries, forms = load_language(ROOT / 'output' / name / 'language.json')
            reference = analyze_translation('Take this note, carry it to your mother, and wait for an answer.', grammar, entries, forms)
            for source in (
                'Take this note, carry it to your mother; and wait for an answer.',
                'Take this note; carry it to your mother; and wait for an answer.',
            ):
                result = analyze_translation(source, grammar, entries, forms)
                with self.subTest(language=name, source=source):
                    self.assertEqual(result['status'], 'ok', result['reason'])
                    first = result['ir']['structured_clause']['predicate']
                    predicates = [first, *first['coordinated']]
                    self.assertEqual([p['lemma'] for p in predicates], ['take', 'carry', 'wait'])
                    self.assertEqual([p['mood'] for p in predicates], ['imperative'] * 3)
                    self.assertEqual(first['object']['head'], 'note')
                    self.assertEqual(predicates[1]['object']['head'], 'it')
                    self.assertEqual(predicates[1]['pps'][0]['object']['head'], 'mother')
                    self.assertEqual(predicates[2]['pps'][0]['object']['head'], 'answer')
                    self.assertEqual(result['surface'], reference['surface'])
                    self.assertEqual(result['gloss'], reference['gloss'])

    def test_explicit_subject_cannot_become_shared_command(self):
        _, grammar, entries, forms = load_language(ROOT / 'output/Example/language.json')
        result = analyze_translation('Take this note; the bird sees the cat; and wait for an answer.', grammar, entries, forms)
        clause = result['ir']['structured_clause']
        if clause:
            predicates = clause['predicate']['coordinated']
            self.assertFalse(any(p['lemma'] == 'see' and p['mood'] == 'imperative' for p in predicates))


if __name__ == '__main__':
    unittest.main()
