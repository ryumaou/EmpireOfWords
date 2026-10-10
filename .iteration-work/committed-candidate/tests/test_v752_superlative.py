import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from english_analyzer import analyze, lexical_match, tokens, lemma_candidates
from structured_realizer import parse_clause

BY={'dog':[('n','dogx')],'big':[('adj','bigx')],'cat':[('n','catx')],'be':[('v','bex')]}
class SuperlativeRegression(unittest.TestCase):
 def test_superlative_is_predicate_not_object(self):
  raw='The dog is the biggest.'
  ir=parse_clause(raw,BY,lexical_match,tokens,lemma_candidates,analyze(raw,BY)['constructions'])
  self.assertIsNotNone(ir)
  self.assertIsNone(ir.predicate.object)
  self.assertEqual(ir.predicate.complement.head,'big')
  self.assertEqual(ir.predicate.comparison.degree,'superlative')
 def test_comparative_still_comparative(self):
  raw='The dog is bigger than the cat.'
  ir=parse_clause(raw,BY,lexical_match,tokens,lemma_candidates,analyze(raw,BY)['constructions'])
  self.assertIsNotNone(ir)
  self.assertEqual(ir.predicate.comparison.degree,'comparative')
 def test_plain_noun_predicate_unaffected(self):
  raw='The dog is the cat.'
  ir=parse_clause(raw,BY,lexical_match,tokens,lemma_candidates,analyze(raw,BY)['constructions'])
  self.assertIsNotNone(ir)
  self.assertIsNone(ir.predicate.comparison)
