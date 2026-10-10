import sys, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from ir import ClauseIR,PredicateIR
import structured_realizer as sr

class CausalTests(unittest.TestCase):
    def setUp(self):
        self.child=ClauseIR(None,PredicateIR('be'))
        self.main=ClauseIR(None,PredicateIR('see'),subordinate=self.child,subordinate_relation='cause')
        self.g={'subordinate_clause':{'strategy':'particle','position':'after'},'particles':{'subordinate':'kax'}}
    def fake_realize(self,clause,*args,**kwargs):
        if clause is self.child:
            return {'surface':'CAT SMALL BE','gloss':'CAT SMALL BE','receipts':['cat','small','be']}
        return None
    def test_linker_and_both_clause_receipts(self):
        # Realize recursively through a controlled, complete verb/NP fixture.
        g=dict(self.g)
        with patch.object(sr,'_convert_form',return_value='vex'), patch.object(sr,'realize_np',return_value=('dogx','DOG',{'dog'})):
            # Only valid subordinate realizer is patched at recursion boundary.
            original=sr.realize
            def wrapper(clause,*args,**kwargs):
                if clause is self.child: return self.fake_realize(clause)
                return original(clause,*args,**kwargs)
            with patch.object(sr,'realize',side_effect=wrapper):
                result=wrapper(self.main,g,{},lambda *a:'vex',lambda *a:'nx',lambda *a:'px',lambda *a:'',lambda *a:'ax')
        self.assertIsNotNone(result)
        self.assertIn('kax CAT SMALL BE',result['surface'])
        self.assertIn('causal_relation',result['receipts'])
        self.assertIn('small',result['receipts'])
    def test_no_linker_is_failure(self):
        self.g['particles']={}
        with patch.object(sr,'_convert_form',return_value='vex'):
            result=sr.realize(self.main,self.g,{},lambda *a:'vex',lambda *a:'nx',lambda *a:'px',lambda *a:'',lambda *a:'ax')
        self.assertIsNone(result)

if __name__=='__main__':unittest.main()
