"""Punctuation variants cannot drop discourse lexemes or conceal body failure."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from grammar_engine import analyze_translation, _lexicon
from language_io import load_language


class DiscoursePunctuationTests(unittest.TestCase):
    def test_comma_variant_preserves_source_and_both_interjections(self):
        for name in ('Example', 'Test1', 'Test2'):
            _, grammar, entries, forms = load_language(ROOT / 'output' / name / 'language.json')
            source = 'Oh, dear! the wind has blown my hat away!'
            result = analyze_translation(source, grammar, entries, forms)
            reference = analyze_translation('the wind has blown my hat away!', grammar, entries, forms)
            by = _lexicon(entries, forms)
            markers = [next(form for pos, form in by[word] if pos == 'interj') for word in ('oh', 'dear')]
            with self.subTest(language=name):
                self.assertEqual(result['english'], source)
                self.assertEqual(result['status'], 'ok', result['reason'])
                self.assertEqual(result['surface'], ' '.join(markers) + '! ' + reference['surface'])
                self.assertEqual(result['gloss'], 'OH DEAR! ' + reference['gloss'])
                self.assertEqual(result['ir']['discourse_receipts'], ['oh', 'dear'])
                self.assertIn('perfect', result['ir']['realization_receipts'])

    def test_missing_interjection_is_not_silently_dropped(self):
        _, grammar, entries, forms = load_language(ROOT / 'output/Example/language.json')
        def without_dear(e, f):
            by = _lexicon(e, f)
            by.pop('dear', None)
            return by
        with patch('grammar_engine._lexicon', side_effect=without_dear):
            result = analyze_translation('Oh, dear! The dog sees the cat.', grammar, entries, forms)
        self.assertEqual(result['status'], 'partial')
        self.assertNotIn('discourse_receipts', result['ir'])

    def test_failed_clause_is_not_promoted(self):
        _, grammar, entries, forms = load_language(ROOT / 'output/Example/language.json')
        result = analyze_translation('Oh, dear! The dog sees the flibbertigibbet.', grammar, entries, forms)
        self.assertNotEqual(result['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
