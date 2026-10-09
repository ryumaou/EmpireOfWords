import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from english_analyzer import analyze, lexical_match, tokens, lemma_candidates
from structured_realizer import parse_clause

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

 def test_together_not_comparison(self):
  by={"together":[("adv","xx")],"boy":[("n","yy")],"work":[("v","zz")]}
  a=analyze("The two boys are working together.",by)
  self.assertNotIn("comparison",a["constructions"])

 def test_lets_not_possessive(self):
  by={"go":[("v","xx")]}
  a=analyze("Let's go!",by)
  self.assertNotIn("possessive",a["constructions"])

if __name__=='__main__': unittest.main()

class StructuredIRTests(unittest.TestCase):
    def _by(self):
        return {
            'dog':[('n','dogx')], 'sleep':[('v','sleepx')], 'big':[('adj','bigx')],
            'sun':[('n','sunx')], 'shine':[('v','shinex')], 'brightly':[('adv','brightx')],
            'go':[('v','gox')], 'come':[('v','comex')], 'rain':[('n','rainx')],
            'play':[('v','playx')], 'child':[('n','childx')], 'house':[('n','housex')],
        }
    def test_structured_progressive_clause(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by=self._by()
        ir=parse_clause('The big dog is sleeping.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['progressive'])
        self.assertIsNotNone(ir)
        self.assertEqual(ir.subject.head,'dog')
        self.assertIn('big',ir.subject.adjectives)
        self.assertEqual(ir.predicate.lemma,'sleep')
        self.assertIn('progressive',ir.predicate.aspect)
    def test_structured_adverb(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by=self._by()
        ir=parse_clause('The sun shines brightly.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,[])
        self.assertIsNotNone(ir)
        self.assertEqual(ir.predicate.lemma,'shine')
        self.assertIn('brightly',ir.predicate.adverbs)


class TranslationReadyGrammarTests(unittest.TestCase):
    def test_structured_numeral_preserved(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by={'two':[('num','twox')],'child':[('n','childx')],'play':[('v','playx')]}
        ir=parse_clause('Two children played.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['simple'])
        self.assertIsNotNone(ir)
        self.assertEqual(ir.subject.numeral,'two')

    def test_grammar_contract_rejects_missing_question_particle(self):
        from language_io import validate_grammar_contract
        g={'morphemes':{},'particles':{},'verb':{'tenses':['present'],'aspects':['simple'],'moods':['indicative']},
           'questions':{'strategy':'particle'},'possession':{'strategy':'juxtaposition'},'coordination':{'strategy':'none'}}
        issues,_=validate_grammar_contract(g)
        self.assertTrue(any('yes/no particle' in x for x in issues))

    def test_grammar_contract_accepts_analytic_fallbacks(self):
        from language_io import validate_grammar_contract
        g={'morphemes':{},'particles':{'future':'fu','progressive':'pr','perfect':'pe','imperative':'im','yes_no':'qa'},
           'verb':{'tenses':['present'],'aspects':['simple'],'moods':['indicative']},
           'questions':{'strategy':'particle'},'possession':{'strategy':'juxtaposition'},'coordination':{'strategy':'none'}}
        issues,warnings=validate_grammar_contract(g)
        self.assertEqual(issues,[])
        self.assertEqual(warnings,[])


class StructuredRealizationFallbackTests(unittest.TestCase):
    def test_progressive_analytic_fallback_receipt(self):
        from structured_realizer import parse_clause, realize
        import english_analyzer as ea
        by={'dog':[('n','dogx')],'sleep':[('v','sleepx')]}
        ir=parse_clause('The dog is sleeping.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['progressive'])
        g={'pronouns':{},'morphemes':{},'noun':{'cases':['nominative']},
           'verb':{'tenses':['present'],'aspects':['simple'],'moods':['indicative'],'agreement':'none'},
           'particles':{'progressive':'progx'},'word_order':'SVO','adjective_position':'before',
           'possessor_position':'before','possession':{'strategy':'juxtaposition'},'adposition_type':'preposition',
           'adverbs':{'position':'after_verb'},'questions':{'strategy':'word-order'}}
        def noun_form(w,g,number='singular',case='nominative'): return w
        def verb_form(w,g,person='3sg',tense='present',aspect='simple',mood='indicative',negative=False): return w
        def poss(a,b,g): return a+' '+b
        def order(s,v,o,g): return ' '.join(x for x in (s,v,o) if x)
        out=realize(ir,g,by,verb_form,noun_form,poss,order,lambda w,m,g:w)
        self.assertIsNotNone(out)
        self.assertIn('progressive',out['receipts'])
        self.assertIn('progx',out['surface'])

class V65IRRegressionTests(unittest.TestCase):
    def _by(self):
        return {
          'sun':[('n','su')], 'shine':[('v','shi')], 'bright':[('adj','bri')],
          'sleep':[('v','sle')], 'dog':[('n','do')], 'big':[('adj','bi')],
          'child':[('n','chi')], 'play':[('v','pla')], 'garden':[('n','gar')], 'in':[('prep','in')], 'two':[('num','tu')],
          'henry':[('n','hen')], 'ball':[('n','bal')], 'baby':[('n','bab')], 'roll':[('v','rol')],
          'tall':[('adj','tal')], 'brother':[('n','bro')], 'be':[('v','be')],
          'john':[('n','jo')], 'elizabeth':[('n','el')], 'and':[('conj','an')],
        }
    def test_ly_adverb_uses_adjective_lemma(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        ir=parse_clause('The sun shines brightly.',self._by(),ea.lexical_match,ea.tokens,ea.lemma_candidates,[])
        self.assertIsNotNone(ir); self.assertEqual(ir.predicate.modifiers[0].lemma,'bright')
    def test_possessive_np_preserved(self):
        from structured_realizer import parse_np
        import english_analyzer as ea
        np=parse_np(["baby's",'ball'],self._by(),ea.lexical_match)
        self.assertEqual(np.head,'ball'); self.assertEqual(np.possessor.head,'baby')
    def test_subject_coordination_preserved(self):
        from structured_realizer import parse_np
        import english_analyzer as ea
        np=parse_np(['john','and','elizabeth'],self._by(),ea.lexical_match)
        self.assertEqual(np.conjunction,'and'); self.assertEqual(np.coordinated[0].head,'elizabeth')
    def test_comparative_complement_preserved(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by=self._by(); by['she']=[('n','she')]
        ir=parse_clause('She is taller than her brother.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['comparison'])
        self.assertIsNotNone(ir); self.assertIsNotNone(ir.predicate.comparison)

class MissingVocabularyRegressionTests(unittest.TestCase):
    def test_context_inference_common_gaps(self):
        from translate import infer_missing_entry
        by={'animal':[('n',None)],'sky':[('n',None)],'blue':[('adj',None)],'laugh':[('v',None)],'prove':[('v',None)]}
        self.assertEqual(infer_missing_entry('wild',['Once wild animals lived here.'],by),('wild','adj'))
        self.assertEqual(infer_missing_entry('everywhere',['Flowers grow everywhere.'],by),('everywhere','adv'))
        self.assertEqual(infer_missing_entry('gray',['Does the sky look blue or gray?'],by),('gray','adj'))
        self.assertEqual(infer_missing_entry('glee',['They laughed in glee.'],by),('glee','n'))
        self.assertEqual(infer_missing_entry('trustworthy',['He proved himself trustworthy.'],by),('trustworthy','adj'))

class V65StructuredEdgeTests(unittest.TestCase):
    def test_fronted_copular_question(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by={'be (temporary state)':[('v','be')],'hungry':[('adj','hu')]}
        ir=parse_clause('Are you hungry?',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['yes_no_question'])
        self.assertIsNotNone(ir); self.assertEqual(ir.subject.person,'2sg'); self.assertEqual(ir.predicate.complement.head,'hungry')
    def test_modal_main_verb_beats_participle_modifier(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by={'tiger':[('n','ti')],'wear':[('v','we')],'bell':[('n','be')],'starve':[('v','st')]}
        ir=parse_clause('A tiger wearing a bell will starve.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['modal'])
        self.assertIsNotNone(ir); self.assertEqual(ir.predicate.lemma,'starve')
    def test_comparative_adverb_ir(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by={'eat':[('v','ea')],'slow':[('adj','sl')]}
        ir=parse_clause('We should eat more slowly.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['modal','comparison'])
        self.assertIsNotNone(ir); self.assertIsNotNone(ir.predicate.comparison)

class V66ArchitectureTests(unittest.TestCase):
    def test_coordinated_predicates_parse(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by={'crow':[('n','cr')],'drop':[('v','dr')],'pebble':[('n','pe')],'raise':[('v','ra')],'water':[('n','wa')],'and':[('conj','an')]}
        ir=parse_clause('The crow dropped pebbles and raised water.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['coordination'])
        self.assertIsNotNone(ir); self.assertEqual(ir.predicate.lemma,'drop')
        self.assertEqual(ir.predicate.coordinated[0].lemma,'raise')
    def test_lets_is_hortative_ir(self):
        from structured_realizer import parse_clause
        import english_analyzer as ea
        by={'go':[('v','go')]}
        ir=parse_clause("Let's go!",by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['imperative'])
        self.assertIsNotNone(ir); self.assertEqual(ir.clause_type,'hortative'); self.assertEqual(ir.subject.person,'1pl')
    def test_coordinated_predicates_not_false_appositive(self):
        import english_analyzer as ea
        by={'awake':[('v','a')],'dress':[('v','d')],'go':[('v','g')],'breakfast':[('n','b')]}
        a=ea.analyze('I awoke early, dressed hastily, and went down to breakfast.',by)
        self.assertNotIn('appositive',a['constructions'])
        self.assertIn('coordination',a['constructions'])
    def test_contract_v3_requires_profile(self):
        from language_io import validate_grammar_contract
        g={'morphemes':{},'particles':{'future':'f','progressive':'p','perfect':'x','imperative':'i'},
           'verb':{'tenses':['present'],'aspects':['simple'],'moods':['indicative']},
           'questions':{'strategy':'word-order'},'possession':{'strategy':'juxtaposition'},
           'coordination':{'np':{'strategy':'juxtaposition'},'predicate':{'strategy':'juxtaposition'},'clause':{'strategy':'juxtaposition'}},
           'translation_readiness':{'contract_version':3},'realization_profile':{}}
        issues,_=validate_grammar_contract(g); self.assertTrue(any('realization profile missing' in x for x in issues))

class V66GenerationVariationTests(unittest.TestCase):
    def test_family_profiles_produce_distinct_realization_contracts(self):
        from grammar_engine import generate_grammar
        import random,itertools
        pool=[''.join(x) for x in itertools.product('ptkmnslr','aeiou','ptkmnslr','aeiou')]
        a=generate_grammar(pool,random.Random(1),'japanese',{})
        b=generate_grammar(pool,random.Random(2),'romance',{})
        self.assertEqual(a['translation_readiness']['contract_version'],9)
        self.assertNotEqual(a['realization_profile'],b['realization_profile'])
        self.assertIn('predicate',a['coordination']); self.assertIn('clause',b['coordination'])

class V66CoordinationRealizationTests(unittest.TestCase):
    def test_predicate_coordination_realizes_and_receipts(self):
        from structured_realizer import parse_clause,realize
        import english_analyzer as ea
        by={'crow':[('n','cr')],'drop':[('v','dr')],'pebble':[('n','pe')],'raise':[('v','ra')],'water':[('n','wa')],'and':[('conj','an')]}
        ir=parse_clause('The crow dropped pebbles and raised water.',by,ea.lexical_match,ea.tokens,ea.lemma_candidates,['coordination'])
        g={'pronouns':{'3pl':'te'},'morphemes':{},'noun':{'cases':['nominative']},'verb':{'tenses':['present'],'aspects':['simple'],'moods':['indicative'],'agreement':'none'},
           'particles':{'and':'ka','past':'pa'},'word_order':'SVO','adjective_position':'before','possessor_position':'before','possession':{'strategy':'juxtaposition'},
           'adposition_type':'preposition','adverbs':{'position':'after_verb','derivation':'zero'},'questions':{'strategy':'word-order'},
           'coordination':{'predicate':{'strategy':'particle'},'np':{'strategy':'particle'},'clause':{'strategy':'particle'}}}
        nf=lambda w,g,number='singular',case='nominative':w
        vf=lambda w,g,person='3sg',tense='present',aspect='simple',mood='indicative',negative=False:w
        poss=lambda a,b,g:a+' '+b; order=lambda a,b,c,g:' '.join(x for x in (a,b,c) if x)
        out=realize(ir,g,by,vf,nf,poss,order,lambda w,m,g:w)
        self.assertIsNotNone(out); self.assertIn('coordination',out['receipts']); self.assertIn('ra',out['surface'])

class V67MorphosyntaxTests(unittest.TestCase):
    def test_noun_compound_preserved(self):
        by={'sea':[('n','seaX')],'water':[('n','waterX')],'be':[('v','beX')],'salty':[('adj','saltX')]}
        g={'lexical_conversion':{'noun_to_verb':{'strategy':'zero'},'adjective_to_verb':{'strategy':'zero'},'noun_to_adjective':{'strategy':'zero'}}}
        ir=parse_clause('Sea water is salty.',by,lexical_match,tokens,lemma_candidates,[],g)
        self.assertIsNotNone(ir); self.assertEqual(ir.subject.head,'water'); self.assertIn('sea',ir.subject.noun_modifiers)

    def test_homographic_subject_does_not_steal_predicate(self):
        by={'fire':[('n','fi'),('v','fiv')],'feel':[('v','fe')],'hot':[('adj','ho')]}
        g={'lexical_conversion':{'noun_to_verb':{'strategy':'zero'},'adjective_to_verb':{'strategy':'zero'},'noun_to_adjective':{'strategy':'zero'}}}
        ir=parse_clause('The fire feels hot.',by,lexical_match,tokens,lemma_candidates,[],g)
        self.assertIsNotNone(ir); self.assertEqual(ir.subject.head,'fire'); self.assertEqual(ir.predicate.lemma,'feel')

    def test_contextual_adjective_to_verb_conversion(self):
        by={'mist':[('n','mi')],'clear':[('adj','cl')],'probably':[('adv','pr')],'away':[('adv','aw')]}
        g={'lexical_conversion':{'adjective_to_verb':{'strategy':'zero'},'noun_to_verb':{'strategy':'zero'},'noun_to_adjective':{'strategy':'zero'}}}
        ir=parse_clause('This mist will probably clear away.',by,lexical_match,tokens,lemma_candidates,['modal'],g)
        self.assertIsNotNone(ir); self.assertEqual(ir.predicate.lemma,'clear'); self.assertEqual(ir.predicate.tense,'future')


class V68CreationContractTests(unittest.TestCase):
    def test_generation_has_nonfinite_contract_without_forced_perfect(self):
        from grammar_engine import generate_grammar
        import random,itertools
        pool=[''.join(x) for x in itertools.product('ptkmnslr','aeiou','ptkmnslr','aeiou')]
        g=generate_grammar(pool,random.Random(9),'japanese',{'aspect_level':'minimal'})
        self.assertEqual(g['translation_readiness']['contract_version'],9)
        self.assertIn('participial_modifier',g['nonfinite'])
        self.assertIn('infinitive_complement',g['nonfinite'])
        self.assertNotIn('perfect',g['morphemes'])
        self.assertEqual(g['aspect_realization']['perfect'],'particle')

    def test_contract_v5_checks_nonfinite_and_structural_questions(self):
        from language_io import validate_grammar_contract
        g={'morphemes':{},'particles':{'future':'fu','progressive':'pr','perfect':'pe','imperative':'im'},
           'verb':{'tenses':['present'],'aspects':['simple'],'moods':['indicative']},
           'questions':{'strategy':'word-order'},'possession':{'strategy':'juxtaposition'},
           'coordination':{'np':{'strategy':'juxtaposition'},'predicate':{'strategy':'juxtaposition'},'clause':{'strategy':'juxtaposition'}},
           'lexical_conversion':{'noun_to_verb':{'strategy':'zero'},'adjective_to_verb':{'strategy':'zero'},'noun_to_adjective':{'strategy':'zero'}},
           'translation_readiness':{'contract_version':5},
           'realization_profile':{'word_order':'SVO','adposition_type':'preposition','adjective_position':'before','possessor_position':'before','comparison_strategy':'particle','question_strategy':'word-order','noun_compound_order':'modifier-head'}}
        issues,_=validate_grammar_contract(g)
        self.assertTrue(any('nonfinite strategy missing' in x for x in issues))
        self.assertTrue(any('structural question strategy missing' in x for x in issues))

    def test_participial_modifier_is_preserved_in_subject_np(self):
        by={'tiger':[('n','ti')],'wear':[('v','we')],'bell':[('n','be')],'starve':[('v','st')]}
        g={'lexical_conversion':{'noun_to_verb':{'strategy':'zero'},'adjective_to_verb':{'strategy':'zero'},'noun_to_adjective':{'strategy':'zero'}}}
        ir=parse_clause('A tiger wearing a bell will starve.',by,lexical_match,tokens,lemma_candidates,['modal'],g)
        self.assertIsNotNone(ir); self.assertEqual(ir.subject.head,'tiger')
        self.assertEqual(ir.subject.participial_modifiers[0].lemma,'wear')
        self.assertEqual(ir.subject.participial_modifiers[0].object.head,'bell')


class V69RegressionTests(unittest.TestCase):
    def test_string_is_not_false_progressive(self):
        from english_analyzer import detect_constructions
        by={"string":[("n","x")],"short":[("adj","y")],"be":[("v","z")]}
        self.assertNotIn("progressive", detect_constructions("This string is too short!", ["this","string","is","too","short"], by))

    def test_irregular_degree_candidates(self):
        self.assertIn("good", lemma_candidates("better"))
        self.assertIn("bad", lemma_candidates("worst"))

    def test_contract_v6_capabilities(self):
        import random
        from grammar_engine import generate_grammar
        from language_io import validate_grammar_contract
        roots=["ka"+str(i) for i in range(300)]
        g=generate_grammar(roots, random.Random(77), "naturalistic", {})
        self.assertEqual(g["translation_readiness"]["contract_version"],9)
        self.assertIn("stacked_aspect",g["translation_readiness"]["capabilities"])
        errors,_=validate_grammar_contract(g)
        self.assertEqual(errors,[])

class V71FidelityTests(unittest.TestCase):
    def test_np_coordination_preserves_individual_number(self):
        from structured_realizer import parse_np
        by={'cat':[('n','katu')], 'bird':[('n','birdu')]}
        np=parse_np(['the','cat','and','the','bird'],by,lexical_match)
        self.assertEqual(np.number,'singular')
        self.assertEqual(np.coordinated[0].number,'singular')
    def test_creation_guarantees_past_strategy(self):
        from grammar_engine import generate_grammar
        import random
        g=generate_grammar(['maka','talu','ranu','sena','katu','mori','pala','nako']*200,random.Random(712),family='random')
        self.assertTrue('past' in g['morphemes'] or g['particles'].get('past'))
        self.assertEqual(g['translation_readiness']['contract_version'],9)

class V71PastSourceTests(unittest.TestCase):
    def test_irregular_past_is_not_discarded_before_structured_parse(self):
        from grammar_engine import _normalize_for_legacy
        from structured_realizer import parse_clause
        by={'dog':[('n','doga')],'cat':[('n','cata')],'see':[('v','seva')]}
        normalized=_normalize_for_legacy('The dog saw the cat.',by)
        clause=parse_clause(normalized,by,lexical_match,tokens,lemma_candidates,[],{})
        self.assertIsNotNone(clause)
        self.assertEqual(clause.predicate.tense,'past')

class V72NegationContractTests(unittest.TestCase):
    def test_particle_negation_ignores_stray_affix(self):
        from grammar_engine import verb_form
        g={'verb':{'negation':'particle'},'morphemes':{'negative':{'form':'zz','side':'suffix'}},'particles':{'negative':'naka'}}
        self.assertEqual(verb_form('mora',g,negative=True),'naka mora')

    def test_affix_negation_ignores_stray_particle(self):
        from grammar_engine import verb_form
        g={'verb':{'negation':'affix'},'morphemes':{'negative':{'form':'zz','side':'suffix'}},'particles':{'negative':'naka'},'morphophonemics':{'rules':[]}}
        self.assertEqual(verb_form('mora',g,negative=True),'morazz')

    def test_inflection_candidates(self):
        from english_analyzer import lemma_candidates
        self.assertIn('freeze',lemma_candidates('freezes'))
        self.assertIn('dance',lemma_candidates('danced'))
        self.assertIn('carry',lemma_candidates('carried'))

class V73InflectionIntegrityTests(unittest.TestCase):
    def test_inflected_verb_avoids_noun_homograph(self):
        by={'freez':[('n','fz')],'freeze':[('v','fr')], 'danced':[('v','dc')],'dance':[('v','da')]}
        self.assertEqual(lexical_match(by,'freezes','v'),'freeze')
        self.assertEqual(lexical_match(by,'danced','v'),'dance')

    def test_irregular_past_over_verb_homograph(self):
        by={'west':[('n','we')],'wind':[('n','wi'),('v','wv')], 'blow':[('v','bl')],
            'face':[('n','fa')], 'across':[('prep','ac')], 'my':[('pron','my')]}
        ir=parse_clause('The west wind blew across my face.',by,lexical_match,tokens,lemma_candidates,[])
        self.assertIsNotNone(ir)
        self.assertEqual(ir.predicate.lemma,'blow')
        self.assertEqual(ir.predicate.tense,'past')

    def test_caress_is_singular(self):
        from structured_realizer import parse_np
        np=parse_np(['a','caress'],{'caress':[('n','ca')]},lexical_match)
        self.assertEqual(np.number,'singular')

class V73MorphemeCollisionTests(unittest.TestCase):
    def test_prefix_suffix_do_not_disappear_at_identical_boundary(self):
        from grammar_engine import affix
        g={'morphophonemics':{'rules':['initial_mutation','lenition','consonant_assimilation']}}
        self.assertNotEqual(affix('cat',{'form':'c','side':'prefix'},g),'cat')
        self.assertNotEqual(affix('cat',{'form':'t','side':'suffix'},g),'cat')

class ContrastSuiteRegressions(unittest.TestCase):
 def test_doubled_consonant_comparison(self):
  self.assertIn('big',lemma_candidates('bigger'))
  self.assertIn('big',lemma_candidates('biggest'))
  by={'big':[('adj','x')], 'dog':[('n','y')], 'cat':[('n','z')]}
  for sentence in ('The dog is bigger than the cat.','The dog is the biggest.'):
   a=analyze(sentence,by)
   self.assertNotIn('bigger',a['missing_lexemes'])
   self.assertNotIn('biggest',a['missing_lexemes'])
   self.assertIn('comparison',a['constructions'])
 def test_relative_that_detected(self):
  by={'dog':[('n','x')],'see':[('v','x')],'cat':[('n','x')],'happy':[('adj','x')]}
  a=analyze('The dog that sees the cat is happy.',by)
  self.assertIn('relative_clause',a['constructions'])
 def test_demonstrative_that_still_not_relative(self):
  by={'dog':[('n','x')],'see':[('v','x')],'cat':[('n','x')]}
  self.assertNotIn('relative_clause',analyze('That dog sees the cat.',by)['constructions'])
