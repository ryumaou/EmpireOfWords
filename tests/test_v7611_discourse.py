"""Discourse expressions must be translated, never silently dropped."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from language_io import load_language
from grammar_engine import analyze_translation

class DiscourseTests(unittest.TestCase):
    def test_oh_dear_realized_all_baselines(self):
        for name in ('Example','Test1','Test2'):
            with self.subTest(name=name):
                _,g,e,f=load_language(ROOT/'output'/name/'language.json')
                r=analyze_translation('Oh dear! The wind has blown my hat away!',g,e,f)
                self.assertEqual(r['status'],'ok',r['reason'])
                self.assertIn('OH DEAR!',r['gloss'])
                self.assertEqual(r['ir']['discourse_receipts'],['oh','dear'])
    def test_unknown_interjection_not_dropped(self):
        for name in ('Example','Test1','Test2'):
            with self.subTest(name=name):
                _,g,e,f=load_language(ROOT/'output'/name/'language.json')
                r=analyze_translation('Aha! I have caught you!',g,e,f)
                self.assertEqual(r['status'],'partial')
                self.assertIn('discourse',r['reason'])
    def test_no_interjection_no_change(self):
        _,g,e,f=load_language(ROOT/'output'/'Example'/'language.json')
        self.assertEqual(analyze_translation('The dog sees the cat.',g,e,f)['status'],'ok')
if __name__=='__main__':unittest.main()
