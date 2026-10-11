"""Compositional conditionals must preserve clause roles and target grammar."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from grammar_engine import analyze_translation
from language_io import load_language


class ConditionalClauseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.languages = [load_language(ROOT / 'output' / name / 'language.json')
                         for name in ('Example', 'MagicTest', 'Test1', 'Test2')]

    def test_source_order_does_not_override_target_conditional_order(self):
        for _, grammar, entries, forms in self.languages:
            with self.subTest(order=grammar['conditional_clause']['position'], seed=grammar.get('seed')):
                front = analyze_translation('If the dog runs, the cat sleeps.', grammar, entries, forms)
                trailing = analyze_translation('The cat sleeps if the dog runs.', grammar, entries, forms)
                self.assertEqual(front['status'], 'ok')
                self.assertEqual(trailing['status'], 'ok')
                self.assertEqual(front['surface'], trailing['surface'])
                clause = front['ir']['structured_clause']
                self.assertEqual(clause['predicate']['lemma'], 'sleep')
                self.assertEqual(clause['subject']['head'], 'cat')
                self.assertEqual(clause['subordinate_relation'], 'condition')
                self.assertEqual(clause['subordinate']['predicate']['lemma'], 'run')
                self.assertEqual(clause['subordinate']['subject']['head'], 'dog')
                self.assertEqual(front['ir']['realization_receipts'].count('condition_relation'), 1)
                marker = grammar['particles']['conditional']
                self.assertEqual(front['surface'].split().count(marker), 1)
                if grammar['conditional_clause']['position'] == 'initial':
                    self.assertTrue(front['surface'].startswith(marker + ' '))
                else:
                    self.assertIn(' ' + marker + ' ', front['surface'])

    def test_negation_stays_in_its_own_clause(self):
        _, grammar, entries, forms = self.languages[0]
        for sentence, main_negative, condition_negative in (
            ('If the dog runs, the cat does not sleep.', True, False),
            ('If the dog does not run, the cat sleeps.', False, True),
        ):
            with self.subTest(sentence=sentence):
                result = analyze_translation(sentence, grammar, entries, forms)
                self.assertEqual(result['status'], 'ok')
                clause = result['ir']['structured_clause']
                self.assertEqual(clause['predicate']['negative'], main_negative)
                self.assertEqual(clause['subordinate']['predicate']['negative'], condition_negative)

    def test_missing_target_linker_and_ambiguous_boundary_fail_closed(self):
        _, grammar, entries, forms = self.languages[0]
        without_linker = copy.deepcopy(grammar)
        without_linker['particles'].pop('conditional')
        result = analyze_translation('If the dog runs, the cat sleeps.', without_linker, entries, forms)
        self.assertNotEqual(result['status'], 'ok')
        self.assertTrue(result['surface'].startswith('['))
        ambiguous = analyze_translation('If the dog runs the cat sleeps.', grammar, entries, forms)
        self.assertEqual(ambiguous['status'], 'unsupported-grammar')

    def test_embedded_question_if_is_not_a_condition(self):
        _, grammar, entries, forms = self.languages[0]
        result = analyze_translation('The dog sees if the cat sleeps.', grammar, entries, forms)
        self.assertNotEqual(result['status'], 'ok')
        self.assertTrue(result['surface'].startswith('['))


if __name__ == '__main__':
    unittest.main()
