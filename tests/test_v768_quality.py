"""Conservative v7.6.8 semantic and diversity regression checks."""
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from language_io import load_language, TOOL_VERSION
from grammar_engine import analyze_translation

class QualityTests(unittest.TestCase):
    def test_version(self):
        self.assertEqual(TOOL_VERSION,'7.6.12')

    def test_negative_indefinite_and_change_of_state(self):
        for name in ('Example','Test1','Test2'):
            with self.subTest(language=name):
                _,g,entries,forms=load_language(ROOT/'output'/name/'language.json')
                neg=analyze_translation('The dog sees nothing.',g,entries,forms)
                self.assertEqual(neg['status'],'ok')
                self.assertIn('NOTHING-NEG.INDEF',neg['gloss'])
                self.assertNotIn('SEE-NEG',neg['gloss'])
                comp=analyze_translation('The days grow shorter.',g,entries,forms)
                self.assertEqual(comp['status'],'ok')
                self.assertIn('SHORT-COMP',comp['gloss'])
                self.assertIn('GROW',comp['gloss'])

    def test_unsupported_remains_unsupported(self):
        for name in ('Example','Test1','Test2'):
            _,g,e,f=load_language(ROOT/'output'/name/'language.json')
            result=analyze_translation('If the dog sees the cat, the bird will fly.',g,e,f)
            self.assertEqual(result['status'],'unsupported-grammar')
            self.assertEqual(result['ir']['diagnostic_stage'],'capability_gate')

    def test_unresolved_names_not_invented(self):
        for name in ('Example','Test1','Test2'):
            _,g,e,f=load_language(ROOT/'output'/name/'language.json')
            result=analyze_translation('John and Elizabeth are friends.',g,e,f)
            self.assertNotEqual(result['status'],'ok')
            self.assertEqual(result['ir']['diagnostic_stage'],'analysis_or_parse')

if __name__=='__main__': unittest.main()
