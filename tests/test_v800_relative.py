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

    def test_medial_object_gap_in_subject_relative(self):
        result=self.translate('The dog that the cat sees is happy.')
        self.assertEqual(result['status'],'ok')
        main=result['ir']['structured_clause']
        self.assertEqual(main['subject']['head'],'dog')
        self.assertEqual(main['predicate']['complement']['head'],'happy')
        child=main['relative_clause']
        self.assertEqual(child['subject']['head'],'cat')
        self.assertEqual(child['predicate']['lemma'],'see')
        self.assertIsNone(child['predicate']['object'])
        self.assertEqual(child['gap_role'],'object')
        self.assertEqual(child['gap_antecedent']['head'],'dog')
        self.assertIn('REL',result['gloss'])

    def test_ambiguous_scope_remains_unresolved(self):
        for sentence in ('The dog that sees the cat that runs is happy.',
                         'The dog that the cat sees the bird chases is happy.'):
            with self.subTest(sentence=sentence):
                result=self.translate(sentence)
                self.assertNotEqual(result['status'],'ok')
                self.assertIn(result['surface'],('[UNRESOLVED]','[PARTIAL]'))

    def test_unbound_complex_relative_is_not_complete(self):
        for sentence in ('The dog sees the cat that the bird chased yesterday.',
                         'The box of candy that Lucy gave me yesterday is red.'):
            with self.subTest(sentence=sentence):
                result=self.translate(sentence)
                self.assertNotEqual(result['status'],'ok')

    def test_proper_agent_and_copular_complement_gap(self):
        sentence='This is the house that Jack built.'
        for name in ('Example','MagicTest','Test1','Test2'):
            with self.subTest(language=name):
                _,grammar,entries,forms=load_language(ROOT/'output'/name/'language.json')
                result=analyze_translation(sentence,grammar,entries,forms)
                self.assertEqual(result['status'],'ok')
                main=result['ir']['structured_clause']
                self.assertEqual(main['subject']['head'],'this')
                self.assertEqual(main['predicate']['complement']['head'],'house')
                self.assertEqual(main['relative_host_role'],'complement')
                child=main['relative_clause']
                self.assertEqual(child['subject']['head'],'Jack')
                self.assertTrue(child['subject']['proper_name'])
                self.assertEqual(child['predicate']['lemma'],'build')
                self.assertEqual(child['predicate']['tense'],'past')
                self.assertEqual(child['gap_role'],'object')
                self.assertEqual(child['gap_antecedent'],main['predicate']['complement'])
                self.assertIn('NAME:JACK',result['gloss'])
                self.assertIn(grammar['particles']['relative'],result['surface'].split())

    def test_attached_antecedent_recipient_and_time(self):
        sentence='Have you seen the box of candy that Lucy gave me yesterday?'
        for name in ('Example','MagicTest','Test1','Test2'):
            with self.subTest(language=name):
                _,grammar,entries,forms=load_language(ROOT/'output'/name/'language.json')
                result=analyze_translation(sentence,grammar,entries,forms)
                self.assertEqual(result['status'],'ok')
                main=result['ir']['structured_clause']
                self.assertEqual(main['clause_type'],'yes_no_question')
                self.assertIn('perfect',main['predicate']['aspect'])
                antecedent=main['predicate']['object']
                self.assertEqual(antecedent['head'],'box')
                self.assertEqual(antecedent['attached_pps'][0]['object']['head'],'candy')
                self.assertEqual(main['predicate']['pps'],[])
                child=main['relative_clause']
                self.assertEqual(child['subject']['head'],'Lucy')
                self.assertEqual(child['predicate']['lemma'],'give')
                self.assertEqual(child['predicate']['indirect_object']['person'],'1sg')
                self.assertEqual(child['predicate']['modifiers'][0]['lemma'],'yesterday')
                self.assertEqual(child['gap_antecedent'],antecedent)
                self.assertIn('RECIPIENT',result['gloss'])
                self.assertIn('REL',result['gloss'])
                self.assertIn(grammar['particles']['relative'],result['surface'].split())

    def test_medial_object_gap_across_existing_languages(self):
        sentence='The dog that the cat sees runs.'
        for name in ('Example','MagicTest','Test1','Test2'):
            with self.subTest(language=name):
                _,grammar,entries,forms=load_language(ROOT/'output'/name/'language.json')
                result=analyze_translation(sentence,grammar,entries,forms)
                self.assertEqual(result['status'],'ok')
                main=result['ir']['structured_clause']
                self.assertEqual(main['relative_clause']['gap_role'],'object')
                self.assertEqual(main['relative_clause']['gap_antecedent'],main['subject'])
                self.assertIn(grammar['particles']['relative'],result['surface'].split())

    def test_clause_final_object_gap_keeps_both_predicates_and_arguments(self):
        for sentence,main_subject,object_head,child_subject,child_verb in (
            ('The dog sees the cat that the bird chased.','dog','cat','bird','chase'),
            ('Have you seen the flowers that the children brought?','you','flower','child','bring')):
            with self.subTest(sentence=sentence):
                result=self.translate(sentence)
                self.assertEqual(result['status'],'ok')
                main=result['ir']['structured_clause']
                self.assertEqual(main['subject']['head'],main_subject)
                self.assertEqual(main['predicate']['object']['head'],object_head)
                if sentence.startswith('Have '):
                    self.assertIn('perfect',main['predicate']['aspect'])
                    self.assertIn('PERF',result['gloss'])
                self.assertEqual(main['relative_host_role'],'object')
                child=main['relative_clause']
                self.assertEqual(child['subject']['head'],child_subject)
                self.assertEqual(child['predicate']['lemma'],child_verb)
                self.assertIsNone(child['predicate']['object'])
                self.assertEqual(child['gap_role'],'object')
                self.assertEqual(child['gap_antecedent']['head'],object_head)
                self.assertIn(self.grammar['particles']['relative'],result['surface'].split())
                self.assertIn('REL',result['gloss'])
                self.assertIn('SEE',result['gloss'])

    def test_object_gap_marker_position_and_missing_marker(self):
        sentence='The dog sees the cat that the bird chased.'
        before=copy.deepcopy(self.grammar)
        after=copy.deepcopy(self.grammar)
        before['relative_clause']['position']='before'
        after['relative_clause']['position']='after'
        first=self.translate(sentence,before)
        last=self.translate(sentence,after)
        self.assertEqual(first['status'],last['status'])
        self.assertEqual(first['status'],'ok')
        self.assertNotEqual(first['surface'],last['surface'])
        after['particles'].pop('relative')
        failed=self.translate(sentence,after)
        self.assertEqual(failed['status'],'unsupported-grammar')
        self.assertEqual(failed['surface'],'[UNRESOLVED]')

    def test_inverted_perfect_and_progressive_scope(self):
        for sentence,aspects in (('Have you seen the monkeys in the zoo?',['perfect']),
                                 ('Have you been writing at my desk?',['perfect','progressive'])):
            with self.subTest(sentence=sentence):
                result=self.translate(sentence)
                self.assertEqual(result['status'],'ok')
                predicate=result['ir']['structured_clause']['predicate']
                self.assertEqual(predicate['aspect'],aspects)
                for aspect in aspects:
                    self.assertIn('PERF' if aspect=='perfect' else 'PROG',result['gloss'])

    def test_existing_languages_bind_object_gap_and_question_scope(self):
        sentence='Have you seen the flowers that the children brought?'
        for name in ('Example','MagicTest','Test1','Test2'):
            with self.subTest(language=name):
                _,grammar,entries,forms=load_language(ROOT/'output'/name/'language.json')
                result=analyze_translation(sentence,grammar,entries,forms)
                self.assertEqual(result['status'],'ok')
                main=result['ir']['structured_clause']
                self.assertEqual(main['clause_type'],'yes_no_question')
                self.assertEqual(main['subject']['person'],'2sg')
                self.assertEqual(main['predicate']['lemma'],'see')
                self.assertEqual(main['predicate']['object']['head'],'flower')
                self.assertIn('perfect',main['predicate']['aspect'])
                child=main['relative_clause']
                self.assertEqual(child['subject']['head'],'child')
                self.assertEqual(child['predicate']['lemma'],'bring')
                self.assertEqual(child['predicate']['tense'],'past')
                self.assertEqual(child['gap_role'],'object')
                self.assertEqual(child['gap_antecedent']['head'],'flower')
                self.assertIn(grammar['particles']['relative'],result['surface'].split())


if __name__=='__main__':unittest.main()
