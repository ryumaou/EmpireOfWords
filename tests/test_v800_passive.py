"""Role-aware passive contracts and fail-closed translation checks."""
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from grammar_engine import analyze_translation
from language_io import load_language, validate_grammar_contract


class PassiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _,cls.grammar,cls.entries,cls.forms=load_language(ROOT/'output/Example/language.json')

    def translate(self,sentence,grammar=None):
        return analyze_translation(sentence,grammar or self.grammar,self.entries,self.forms)

    def test_patient_agent_swap_changes_roles_and_surface(self):
        forward=self.translate('The cat was seen by the dog.')
        reverse=self.translate('The dog was seen by the cat.')
        self.assertEqual(forward['status'],'ok')
        self.assertEqual(reverse['status'],'ok')
        self.assertNotEqual(forward['surface'],reverse['surface'])
        for result,patient,agent in ((forward,'cat','dog'),(reverse,'dog','cat')):
            clause=result['ir']['structured_clause']
            self.assertEqual(clause['subject']['head'],patient)
            self.assertEqual(clause['predicate']['patient']['head'],patient)
            self.assertEqual(clause['predicate']['agent']['head'],agent)
            self.assertEqual(clause['predicate']['voice'],'passive')
            self.assertIn(self.grammar['particles']['passive'],result['surface'].split())
            self.assertIn('PASS',result['gloss'])
            self.assertIn('AGENT',result['gloss'])

    def test_missing_voice_contract_fails_closed(self):
        missing=copy.deepcopy(self.grammar)
        missing['passive']['strategy']='morphological'
        missing['morphemes'].pop('passive',None)
        result=self.translate('The cat was seen by the dog.',missing)
        self.assertEqual(result['status'],'unsupported-grammar')
        self.assertEqual(result['surface'],'[UNRESOLVED]')

    def test_morphological_passive_and_contract(self):
        grammar=copy.deepcopy(self.grammar)
        grammar['passive']['strategy']='morphological'
        grammar['morphemes']['passive']={'side':'suffix','form':'paxi'}
        grammar['translation_readiness']['contract_version']=10
        result=self.translate('The cat was seen by the dog.',grammar)
        self.assertEqual(result['status'],'ok')
        self.assertIn('PASS',result['gloss'])
        self.assertNotIn(self.grammar['particles']['passive'],result['surface'].split())
        issues,_=validate_grammar_contract(grammar)
        self.assertEqual(issues,[])
        del grammar['morphemes']['passive']
        issues,_=validate_grammar_contract(grammar)
        self.assertIn('contract v10 requires passive morpheme',issues)

    def test_complex_or_unrecognized_participle_remains_unresolved(self):
        for sentence in ('The cat was seen by the dog near the house.',
                         'The cat was hidden by the dog.'):
            with self.subTest(sentence=sentence):
                result=self.translate(sentence)
                self.assertNotEqual(result['status'],'ok')


if __name__=='__main__':unittest.main()
