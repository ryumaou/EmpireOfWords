"""v7.6.9: fronted PP semantic preservation and conservative failure tests."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from language_io import load_language
from grammar_engine import analyze_translation

class FrontedPPTests(unittest.TestCase):
    def test_fronted_adjunct_preserved_for_three_grammars(self):
        for name in ('Example','Test1','Test2'):
            with self.subTest(language=name):
                _,g,entries,forms=load_language(ROOT/'output'/name/'language.json')
                result=analyze_translation('On the mountain, we see the cat.',g,entries,forms)
                self.assertEqual(result['status'],'ok')
                self.assertIn('MOUNTAIN',result['gloss'])
                self.assertIn('ON',result['gloss'])
                self.assertIn('CAT',result['gloss'])
                self.assertIn('SEE',result['gloss'])

    def test_unavailable_fronted_adjunct_not_silently_omitted(self):
        for name in ('Example','Test1','Test2'):
            with self.subTest(language=name):
                _,g,entries,forms=load_language(ROOT/'output'/name/'language.json')
                result=analyze_translation('On a flibbertigibbet morning we started for the mountains.',g,entries,forms)
                self.assertNotEqual(result['status'],'ok')

if __name__=='__main__': unittest.main()
