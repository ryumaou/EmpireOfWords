import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from semantic_audit import inspect

class SeriesTests(unittest.TestCase):
    def test_three_actions_preserved(self):
        by={x:[(p,x+'x')] for x,p in [('awake','v'),('dress','v'),('go','v'),('early','adv'),('hastily','adv'),('breakfast','n')]}
        roles=inspect('I awoke early, dressed hastily, and went to breakfast.',by)['roles']
        self.assertEqual([r['predicate'] for r in roles],['awake','dress','go'])
        self.assertEqual([r['tense'] for r in roles],['past']*3)
    def test_explicit_second_subject_not_replaced(self):
        by={x:[(p,x+'x')] for x,p in [('dog','n'),('cat','n'),('bird','n'),('see','v')]}
        roles=inspect('The dog sees the cat, and the bird sees the dog.',by)['roles']
        self.assertEqual([r['subject'] for r in roles],['dog','bird'])
