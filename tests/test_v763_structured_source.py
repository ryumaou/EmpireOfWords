import sys, unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import grammar_engine

class SourcePriorityTests(unittest.TestCase):
    def test_raw_source_preferred_to_legacy_did_normalization(self):
        class IR:
            def to_dict(self): return {'test': True}
        ir=IR()
        seen=[]
        def parse(source,*args):
            seen.append(source)
            return ir
        def realize(*args):
            return {'surface':'ok','gloss':'AWAKE DRESS GO','receipts':['awake','dress','go'],'ir':{},'strategies':{}}
        sentence='I awoke early, dressed hastily, and went to breakfast.'
        with patch.object(grammar_engine,'_analyze_english',return_value={'tokens':[], 'constructions':['coordination'],'lexical_items':[], 'missing_lexemes':[]}),\
             patch.object(grammar_engine,'_normalize_for_legacy',return_value='I did awake early dressed hastily and went to breakfast.'),\
             patch.object(grammar_engine,'_prepare_for_legacy',side_effect=lambda x,*args:x),\
             patch.object(grammar_engine,'_parse_structured_clause',side_effect=parse),\
             patch.object(grammar_engine,'_realize_structured_clause',side_effect=realize):
            out=grammar_engine.analyze_translation(sentence,{},[],{})
        self.assertEqual(seen,[sentence])
        self.assertEqual(out['ir']['structured_source'],sentence)
        self.assertTrue(out['ir']['structured_realized'])
        self.assertEqual(out['status'],'ok')
