"""Compositional subject-relative gap and target marker checks."""
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from grammar_engine import analyze_translation
from language_io import load_language, validate_grammar_contract


class RelativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.grammar,cls.entries,cls.forms=load_language(ROOT/'output/Example/language.json')

    def translate(self,sentence,grammar=None):
        return analyze_translation(sentence,grammar or self.grammar,self.entries,self.forms)

    def test_subject_gap_binds_antecedent_and_object(self):
        sentence='The dog that sees the cat is happy.'
        result=self.translate(sentence)
        self.assertEqual(result['status'],'ok')
        main=result['ir']['structured_clause']
        self.assertEqual(main['subject']['head'],'dog')
        self.assertEqual(main['predicate']['complement']['head'],'happy')
        self.assertEqual(main['relative_host_role'],'subject')
        relative=main['relative_clause']
        self.assertIsNone(relative['subject'])
        self.assertEqual(relative['gap_role'],'subject')
        self.assertEqual(relative['gap_antecedent']['head'],'dog')
        self.assertEqual(relative['predicate']['lemma'],'see')
        self.assertEqual(relative['predicate']['object']['head'],'cat')
        self.assertIn(self.grammar['particles']['relative'],result['surface'].split())
        self.assertIn('REL',result['gloss'])
        swapped=self.translate('The cat that sees the dog is happy.')
        self.assertEqual(swapped['status'],'ok')
        self.assertNotEqual(result['surface'],swapped['surface'])
        self.assertEqual(swapped['ir']['structured_clause']['relative_clause']['gap_antecedent']['head'],'cat')

    def test_target_marker_placement_and_missing_contract(self):
        sentence='The dog that sees the cat runs.'
        before=copy.deepcopy(self.grammar)
        after=copy.deepcopy(self.grammar)
        before['relative_clause']['position']='before'
        after['relative_clause']['position']='after'
        first=self.translate(sentence,before)
        last=self.translate(sentence,after)
        self.assertEqual(first['status'],last['status'])
        self.assertEqual(first['status'],'ok')
        self.assertNotEqual(first['surface'],last['surface'])
        marker=self.grammar['particles']['relative']
        self.assertEqual(first['surface'].split()[0],marker)
        self.assertNotEqual(last['surface'].split()[0],marker)
        del after['particles']['relative']
        failed=self.translate(sentence,after)
        self.assertEqual(failed['status'],'unsupported-grammar')
        self.assertEqual(failed['surface'],'[UNRESOLVED]')
        after['translation_readiness']['contract_version']=11
        issues,_=validate_grammar_contract(after)
        self.assertIn('contract v11 requires relative particle',issues)

    def test_object_gap_and_ambiguous_scope_remain_unresolved(self):
        for sentence in ('The dog that the cat sees is happy.',
                         'The dog that sees the cat that runs is happy.'):
            with self.subTest(sentence=sentence):
                result=self.translate(sentence)
                self.assertNotEqual(result['status'],'ok')
                self.assertIn(result['surface'],('[UNRESOLVED]','[PARTIAL]'))


if __name__=='__main__':unittest.main()
