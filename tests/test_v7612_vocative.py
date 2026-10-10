"""Vocatives must be represented separately from clause subjects."""
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from language_io import load_language
from grammar_engine import analyze_translation

class VocativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.g,cls.e,cls.f=load_language(ROOT/'output'/'Example'/'language.json')
    def test_missing_vocative_not_dropped(self):
        r=analyze_translation('Madam, I will obey your command.',self.g,self.e,self.f)
        self.assertEqual(r['status'],'partial')
        self.assertEqual(r['reason'],'unrealized vocative: madam')
        self.assertEqual(r['ir']['vocative'],'madam')
    def test_known_vocative_realized(self):
        # Use a lexicon entry as a stand-in for a known address term.
        from grammar_engine import _lexicon
        # Existing entries are preserved; this test only exercises a synthetic lookup.
        from unittest.mock import patch
        original=_lexicon
        def with_address(entries,forms):
            by=original(entries,forms)
            by['madam']=[('n','testhonorific')]
            return by
        with patch('grammar_engine._lexicon',side_effect=with_address):
            r=analyze_translation('Madam, I will obey your command.',self.g,self.e,self.f)
        self.assertEqual(r['status'],'ok',r['reason'])
        self.assertTrue(r['surface'].startswith('testhonorific, '))
        self.assertIn('VOC:MADAM',r['gloss'])
    def test_no_vocative_unchanged(self):
        self.assertEqual(analyze_translation('I will obey your command.',self.g,self.e,self.f)['status'],'ok')
if __name__=='__main__': unittest.main()
