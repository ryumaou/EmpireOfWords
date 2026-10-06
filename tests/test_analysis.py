import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from english_analyzer import analyze

BY={
 'child':[('n','x')],'walk':[('v','x')],'house':[('n','x')],'person':[('n','x')],'shout':[('v','x')],
 'think':[('v','x')],'train':[('n','x')],'leave':[('v','x')],'minute':[('n','x')],'early':[('adv','x')],
 'sure':[('adj','x')],'go':[('v','x')],'boy':[('n','x')],'bring':[('v','x')],'book':[('n','x')],
 'tall':[('adj','x')],'brother':[('n','x')],'hurt':[('v','x')], 'have':[('v','x')], 'tea':[('n','x')], 'be':[('v','x')], 'careful':[('adj','x')]
}
class AnalyzerTests(unittest.TestCase):
 def test_demonstrative_that_not_relative(self): self.assertNotIn('relative_clause',analyze('This child walked to that house yesterday.',BY)['constructions'])
 def test_short_declarative_not_imperative(self): self.assertNotIn('imperative',analyze('Some of the people shouted.',BY)['constructions'])
 def test_complementizer_that(self): self.assertIn('complement_clause',analyze('I think that this train leaves five minutes earlier today.',BY)['constructions'])
 def test_relative_who(self): self.assertIn('relative_clause',analyze('The boy who brought the book has gone.',BY)['constructions'])
 def test_reflexive_is_grammar(self): self.assertNotIn('myself',analyze('I hurt myself.',BY)['missing_lexemes'])
 def test_comparative_lemma(self): self.assertNotIn('taller',analyze('She is taller than her brother.',BY)['missing_lexemes'])
 def test_lexical_have_imperative_not_perfect(self):
  a=analyze('Have some tea.',BY); self.assertIn('imperative',a['constructions']); self.assertNotIn('perfect',a['constructions'])
 def test_be_imperative(self): self.assertIn('imperative',analyze('Be careful.',BY)['constructions'])

 def test_exclamation_not_automatically_imperative(self): self.assertNotIn('imperative',analyze('This string is too short!',BY)['constructions'])
 def test_interjection_not_imperative(self): self.assertNotIn('imperative',analyze('Alas!',BY)['constructions'])

if __name__=='__main__': unittest.main()
