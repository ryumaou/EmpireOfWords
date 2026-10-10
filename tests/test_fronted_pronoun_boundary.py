"""Fronted adjuncts must preserve the PP, subject, tense, and destination."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from grammar_engine import analyze_translation
from language_io import load_language


class FrontedPronounBoundaryTests(unittest.TestCase):
    def test_comma_and_no_comma_have_identical_meaning(self):
        for name in ('Example', 'Test1', 'Test2'):
            _, grammar, entries, forms = load_language(ROOT / 'output' / name / 'language.json')
            results = [analyze_translation(s, grammar, entries, forms) for s in (
                'On a sunny morning we started for the mountains.',
                'On a sunny morning, we started for the mountains.')]
            with self.subTest(language=name):
                for result in results:
                    self.assertEqual(result['status'], 'ok', result['reason'])
                    clause = result['ir']['structured_clause']
                    self.assertEqual(clause['subject']['person'], '1pl')
                    self.assertEqual(clause['predicate']['lemma'], 'start')
                    self.assertEqual(clause['predicate']['tense'], 'past')
                    adjunct, destination = clause['predicate']['pps']
                    self.assertEqual((adjunct['adposition'], adjunct['object']['head']), ('on', 'morning'))
                    self.assertEqual(adjunct['object']['adjectives'], ['sunny'])
                    self.assertEqual((destination['adposition'], destination['object']['head']), ('for', 'mountain'))
                    self.assertEqual(destination['object']['number'], 'plural')
                self.assertEqual(results[0]['surface'], results[1]['surface'])
                self.assertEqual(results[0]['gloss'], results[1]['gloss'])

    def test_unknown_adjunct_cannot_disappear(self):
        _, grammar, entries, forms = load_language(ROOT / 'output/Example/language.json')
        result = analyze_translation('On a flibbertigibbet morning we started for the mountains.', grammar, entries, forms)
        self.assertNotEqual(result['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
