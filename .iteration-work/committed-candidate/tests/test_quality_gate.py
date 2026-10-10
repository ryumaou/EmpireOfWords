import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from quality_gate import evaluate
class GateTests(unittest.TestCase):
 def test_reject_regression_even_if_aggregate_unchanged(self):
  before={'Example':{'version':'7.4','total':2,'summary':{'Complete':1},'records':{2:{'sentence':'B','status':'partial','reason':'x'}}}}
  after={'Example':{'version':'7.5','total':2,'summary':{'Complete':1},'records':{1:{'sentence':'A','status':'partial','reason':'x'}}}}
  result=evaluate(before,after)
  self.assertFalse(result['pass']);self.assertEqual(result['newly_noncomplete'],1);self.assertEqual(result['newly_complete'],1)
 def test_reject_missing_language(self):
  with self.assertRaises(ValueError):evaluate({'A':{}},{'B':{}})
 def test_allow_budget(self):
  before={'A':{'version':'a','total':1,'summary':{'Complete':1},'records':{}}}
  after={'A':{'version':'b','total':1,'summary':{'Complete':0},'records':{1:{'sentence':'A','status':'partial','reason':'x'}}}}
  self.assertTrue(evaluate(before,after,1)['pass'])

class CorpusIntegrityTests(unittest.TestCase):
 def test_reject_changed_noncomplete_sentence(self):
  b={'A':{'version':'a','total':2,'summary':{'Complete':1},'records':{2:{'sentence':'The dog sees the cat.','status':'partial','reason':'x'}}}}
  a={'A':{'version':'b','total':2,'summary':{'Complete':1},'records':{2:{'sentence':'The cat sees the dog.','status':'partial','reason':'x'}}}}
  with self.assertRaisesRegex(ValueError,'changed'): evaluate(b,a)
 def test_corpus_identity_rejects_same_size_changed_text(self):
  import tempfile
  from quality_gate import corpus_identity
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'a.txt';b=Path(d)/'b.txt'
   a.write_text('The dog sees the cat.\n');b.write_text('The cat sees the dog.\n')
   self.assertNotEqual(corpus_identity(a),corpus_identity(b))
 def test_corpus_identity_normalizes_line_endings(self):
  import tempfile
  from quality_gate import corpus_identity
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'a.txt';b=Path(d)/'b.txt'
   a.write_bytes(b'The dog sees the cat.\r\n');b.write_bytes(b'The dog sees the cat.\n')
   self.assertEqual(corpus_identity(a),corpus_identity(b))
