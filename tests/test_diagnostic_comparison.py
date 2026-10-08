import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from compare_diagnostics import compare,parse
class ComparisonTests(unittest.TestCase):
 def test_regression_and_recovery(self):
  before={'version':'7.2','total':3,'summary':{'Complete':2},'records':{2:{'sentence':'Second','status':'partial','reason':'x'}}}
  after={'version':'7.3','total':3,'summary':{'Complete':2},'records':{1:{'sentence':'First','status':'partial','reason':'y'}}}
  delta=compare(before,after)
  self.assertEqual([x['id'] for x in delta['newly_noncomplete']],[1])
  self.assertEqual([x['id'] for x in delta['newly_complete']],[2])
 def test_reject_mismatched_corpus(self):
  with self.assertRaises(ValueError):compare({'total':1},{'total':2})
