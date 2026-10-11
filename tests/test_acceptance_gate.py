"""Adversarial release-gate tests; synthetic reviews are not release evidence."""
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from acceptance_gate import (SEMANTIC_DIMENSIONS, assess_diversity, assess_holdout,
                             load_suite, translation_identity, word_errors)


class HoldoutGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.manifest = load_suite(ROOT)

    def evidence(self):
        outputs = []
        judgments = []
        for language in range(10):
            for case in self.cases:
                record = {'case_id': case['id'], 'english': case['english'], 'language': str(language),
                          'package_sha256': 'a' * 64, 'source_sha256': 'b' * 64,
                          'status': 'ok', 'surface': 'kaluno vetisa molaro'}
                outputs.append(record)
                judgments.append({'case_id': case['id'], 'language': str(language),
                                  'output_sha256': translation_identity(record), 'reviewer': 'test-independent-reviewer',
                                  'independent_of_implementation': True, 'notes': 'Synthetic gate test fixture only.',
                                  'dimensions': {k: True for k in SEMANTIC_DIMENSIONS}})
        reviews = {'suite_review': {'suite_sha256': self.manifest['suite_sha256'], 'approved': True,
                                   'independent_of_implementation': True, 'reviewer': 'test-independent-reviewer',
                                   'notes': 'Synthetic test approval, never persisted as production evidence.'},
                   'judgments': judgments}
        return outputs, reviews

    def test_suite_is_frozen_disjoint_and_has_twenty_groups(self):
        self.assertEqual(len(self.cases), 200)
        self.assertEqual(len(self.manifest['construction_counts']), 20)
        self.assertEqual(set(self.manifest['construction_counts'].values()), {10})

    def test_empty_review_never_passes_even_with_all_ok(self):
        outputs, _ = self.evidence()
        for r in outputs:
            r['receipts'] = ['perfect', 'all roles preserved', 'complete']
        result = assess_holdout(self.cases, self.manifest, outputs, {'judgments': []})
        self.assertFalse(result['pass'])
        self.assertEqual(result['languages']['0']['independently_reviewed'], 0)
        self.assertEqual(result['languages']['0']['translator_complete'], 200)

    def test_valid_independent_evidence_passes(self):
        outputs, reviews = self.evidence()
        result = assess_holdout(self.cases, self.manifest, outputs, reviews)
        self.assertTrue(result['pass'])
        self.assertTrue(result['construction_support_pass'])

    def test_exact_95_percent_threshold_without_reducing_denominator(self):
        outputs, reviews = self.evidence()
        for review in reviews['judgments'][:10]:
            review['dimensions']['roles'] = False
        result = assess_holdout(self.cases, self.manifest, outputs, reviews)
        self.assertTrue(result['pass'])
        self.assertFalse(result['construction_support_pass'])
        self.assertEqual(result['languages']['0']['verified_accuracy'], 0.95)
        reviews['judgments'][10]['dimensions']['scope'] = False
        self.assertFalse(assess_holdout(self.cases, self.manifest, outputs, reviews)['pass'])

    def test_unsupported_cases_cannot_be_excluded(self):
        outputs, reviews = self.evidence()
        outputs = [r for r in outputs if int(r['case_id'][1:]) <= 160]
        result = assess_holdout(self.cases, self.manifest, outputs, reviews)
        self.assertFalse(result['pass'])
        self.assertTrue(result['input_errors'])
        self.assertEqual(result['languages']['0']['total'], 200)

    def test_source_package_and_surface_changes_expire_reviews(self):
        outputs, reviews = self.evidence()
        for field in ('surface', 'source_sha256', 'package_sha256'):
            altered = copy.deepcopy(outputs)
            altered[0][field] = 'changed'
            with self.subTest(field=field):
                result = assess_holdout(self.cases, self.manifest, altered, reviews)
                self.assertFalse(result['pass'])
                self.assertEqual(result['languages']['0']['independently_reviewed'], 199)

    def test_english_fallback_is_not_correct_even_if_review_claims_it_is(self):
        outputs, reviews = self.evidence()
        for i in range(11):
            outputs[i]['surface'] = outputs[i]['english']
            reviews['judgments'][i]['output_sha256'] = translation_identity(outputs[i])
        self.assertFalse(assess_holdout(self.cases, self.manifest, outputs, reviews)['pass'])

    def test_duplicates_and_self_review_are_rejected(self):
        outputs, reviews = self.evidence()
        reviews['judgments'].append(reviews['judgments'][0])
        self.assertFalse(assess_holdout(self.cases, self.manifest, outputs, reviews)['pass'])
        reviews['judgments'].pop()
        reviews['suite_review']['reviewer'] = self.manifest['authors'][0]
        self.assertFalse(assess_holdout(self.cases, self.manifest, outputs, reviews)['pass'])

    def test_truthy_strings_are_not_boolean_semantic_evidence(self):
        outputs, reviews = self.evidence()
        reviews['judgments'][0]['dimensions']['polarity'] = 'true'
        self.assertFalse(assess_holdout(self.cases, self.manifest, outputs, reviews)['pass'])


class GenerationInvariantTests(unittest.TestCase):
    def test_all_free_words_must_be_plain_latin_and_at_least_two_letters(self):
        package = {'lexicon': [{'gloss': 'dog', 'pos': 'n', 'form': 'kaluno'}],
                   'grammar': {'pronouns': {'1sg': 'ma'}, 'morphemes': {'past': {'form': 'a'}}}}
        self.assertEqual(word_errors(package), [])  # One-letter BOUND affixes are legal.
        for bad in ('a', '', 'ñala', 'ka-la', 'two words', 'ka2'):
            with self.subTest(form=bad):
                altered = copy.deepcopy(package)
                altered['lexicon'][0]['form'] = bad
                self.assertTrue(word_errors(altered))
        package['grammar']['pronouns']['1sg'] = 'i'
        self.assertTrue(word_errors(package))

    def test_renamed_clones_are_not_ten_languages(self):
        packages = [{'name': f'Language{i}', 'seed': i,
                     'grammar': {'word_order': 'SVO'},
                     'lexicon': [{'gloss': f'word{j}', 'pos': 'n', 'form': f'form{j}'} for j in range(100)]}
                    for i in range(10)]
        observations = [{'pass': True, 'observed': 'SVO'} for _ in packages]
        result = assess_diversity(packages, observations)
        self.assertFalse(result['pass'])
        self.assertEqual(len(result['pairs']), 45)
        self.assertTrue(all(p['identical_fraction'] == 1 for p in result['pairs']))


if __name__ == '__main__':
    unittest.main()
