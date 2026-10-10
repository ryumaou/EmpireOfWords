"""v7.6.10 preflight must be read-only and reflect translator diagnostics."""
import sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from language_io import load_language
from vocabulary_preflight import inspect_corpus

class PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.grammar,cls.entries,cls.forms=load_language(ROOT/'output'/'Example'/'language.json')
    def test_known_sentence_complete(self):
        r=inspect_corpus(['The dog sees the cat.'],self.grammar,self.entries,self.forms)
        self.assertEqual(r['statuses'],{'ok':1})
        self.assertEqual(r['missing_tokens'],[])
    def test_unknown_lexeme_reported_without_mutation(self):
        before=len(self.entries)
        r=inspect_corpus(['The dog sees the zzzfictionalobject.'],self.grammar,self.entries,self.forms)
        self.assertEqual(r['statuses'],{'unresolved-vocabulary':1})
        self.assertIn('zzzfictionalobject',[w['token'] for w in r['missing_tokens']])
        self.assertEqual(len(self.entries),before)
    def test_diagnosed_grammar_not_misclassified_as_vocabulary(self):
        r=inspect_corpus(['If the dog sees the cat, the bird will fly.'],self.grammar,self.entries,self.forms)
        self.assertEqual(r['statuses'],{'unsupported-grammar':1})
        self.assertEqual(r['stages'],{'capability_gate':1})
if __name__=='__main__':unittest.main()
