import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from semantic_audit import inspect,check
class SemanticArchitectureTests(unittest.TestCase):
    def test_independent_subject_preserved(self):
        by={x:[(p,x+'x')] for x,p in [('dog','n'),('cat','n'),('bird','n'),('see','v')]}
        r=inspect('The dog sees the cat, and the bird sees the dog.',by)
        self.assertEqual([(c['subject'],c['predicate'],c['object']) for c in r['roles']],
                         [('dog','see','cat'),('bird','see','dog')])
    def test_semantic_mismatch_is_rejected(self):
        self.assertFalse(check([{'subject':'bird'}],[{'subject':'dog'}])['passed'])
