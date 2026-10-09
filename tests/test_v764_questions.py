import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from semantic_audit import inspect

class QuestionIRTests(unittest.TestCase):
    def test_where_preserves_interrogative(self):
        by={'dog':[('n','dogx')],'be':[('v','bex')]}
        r=inspect('Where is the dog?',by)
        self.assertTrue(r['parsed'])
        self.assertEqual(r['question'],{'type':'wh_question','word':'where'})
        self.assertEqual(r['roles'][0]['subject'],'dog')

    def test_when_future_preserves_tense(self):
        by={'guest':[('n','guestx')],'arrive':[('v','arrivex')]}
        r=inspect('When will the guests arrive?',by)
        self.assertEqual(r['question'],{'type':'wh_question','word':'when'})
        self.assertEqual(r['roles'][0]['tense'],'future')

    def test_statement_not_question(self):
        by={'dog':[('n','dogx')],'see':[('v','seex')],'cat':[('n','catx')]}
        r=inspect('The dog sees the cat.',by)
        self.assertEqual(r['question'],{'type':'declarative','word':None})
