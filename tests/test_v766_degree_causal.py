import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from semantic_audit import inspect, realization_probe

class DegreeAndCausalTests(unittest.TestCase):
    def test_degree_question_has_adjective_scope(self):
        by={'wide':[('adj','widex')],'river':[('n','riverx')],'be':[('v','bex')]}
        result=inspect('How wide is the river?',by)
        self.assertTrue(result['parsed'])
        self.assertEqual(result['degree_question'],'wide')
        self.assertEqual(result['question'],{'type':'wh_question','word':'how'})
        self.assertEqual(result['roles'][0]['subject'],'river')
    def test_causal_clause_keeps_both_predicates(self):
        by={x:[(p,x+'x')] for x,p in {'dog':'n','see':'v','cat':'n','be':'v','small':'adj'}.items()}
        result=inspect('The dog sees the cat because the cat is small.',by)
        self.assertEqual(result['roles'][0]['predicate'],'see')
        self.assertEqual(result['subordination']['roles'][0]['predicate'],'be')
        self.assertEqual(result['subordination']['relation'],'cause')
    def test_causal_clause_not_falsely_realized(self):
        by={x:[(p,x+'x')] for x,p in {'dog':'n','see':'v','cat':'n','be':'v','small':'adj'}.items()}
        result=realization_probe('The dog sees the cat because the cat is small.',by,{})
        self.assertTrue(result['parsed'])
        self.assertFalse(result['realized'])

if __name__=='__main__':unittest.main()
