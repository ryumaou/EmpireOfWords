# Empire Of Words — language diversity and realization audit

## Package provenance and validity

- **Example**: 5327 lexical entries; build version 7.6.1; package SHA256 `4f259a7477bebca611e666c6c3aa0a66e58de82ecc56655c3a669629b8cef3e7`; validation errors 0; warnings 2
- **Test1**: 5327 lexical entries; build version 7.6.1; package SHA256 `00e9fc347bb3ee71cb9a712885298c4e35cdeb303cbf1ade82360efa9a22cb8b`; validation errors 0; warnings 8
- **Test2**: 5279 lexical entries; build version 7.6.1; package SHA256 `1614ab40862004232a7392c48082a0085741736bc47db22c5c37d4982e32cc4e`; validation errors 0; warnings 4

## Declared grammatical contrasts

| Feature | Example | Test1 | Test2 |
|---|---|---|---|
| word_order | SOV | VSO | SOV |
| adposition_type | postposition | preposition | postposition |
| adjective_position | before | after | before |
| possessor_position | before | after | before |
| plural_strategy | suffix | mixed | mixed |
| comparison_strategy | particle | mixed | particle |
| question_strategy | particle | mixed | word-order |
| negation_strategy | affix | particle | particle |
| morphology_type | mixed | mixed | isolating |
| future | affix | particle | particle |
| progressive | affix | affix | affix |
| perfect | particle | affix | affix |
| imperative | affix | affix | affix |

## Pairwise lexical and grammatical overlap

- **Example vs Test1**: 5327 shared lemma/POS keys; 0 identical forms (0.0%); 59 shared surface types out of 10585 unique combined surface types (0.6%); 10/13 differing profile fields; grammar fingerprints different.
- **Example vs Test2**: 5269 shared lemma/POS keys; 0 identical forms (0.0%); 90 shared surface types out of 10510 unique combined surface types (0.9%); 6/13 differing profile fields; grammar fingerprints different.
- **Test1 vs Test2**: 5269 shared lemma/POS keys; 0 identical forms (0.0%); 385 shared surface types out of 10209 unique combined surface types (3.8%); 7/13 differing profile fields; grammar fingerprints different.

## Contrast probes

A matching success flag does not prove equivalent grammatical behavior. Inspect surface output and semantic receipts in the CSV.


## Grammatical fidelity checks

- **Example past/present contrast**: PASS; both complete=True; distinct surface=True.
- **Example coordinated singular nouns**: PASS; CAT/BIRD unexpectedly plural=False.
- **Example negation strategy surface**: PASS; particle tokens=0; strategy=affix. The gloss NEG is a semantic label, not an additional surface marker.
- **Example future/present contrast**: PASS; distinct surface=True.
- **Example singular/plural object contrast**: PASS; distinct surface=True.
- **Test1 past/present contrast**: PASS; both complete=True; distinct surface=True.
- **Test1 coordinated singular nouns**: PASS; CAT/BIRD unexpectedly plural=False.
- **Test1 negation strategy surface**: PASS; particle tokens=1; strategy=particle. The gloss NEG is a semantic label, not an additional surface marker.
- **Test1 future/present contrast**: PASS; distinct surface=True.
- **Test1 singular/plural object contrast**: PASS; distinct surface=True.
- **Test2 past/present contrast**: PASS; both complete=True; distinct surface=True.
- **Test2 coordinated singular nouns**: PASS; CAT/BIRD unexpectedly plural=False.
- **Test2 negation strategy surface**: PASS; particle tokens=1; strategy=particle. The gloss NEG is a semantic label, not an additional surface marker.
- **Test2 future/present contrast**: PASS; distinct surface=True.
- **Test2 singular/plural object contrast**: PASS; distinct surface=True.
- Probe sentences: 18
- Same status across all languages: 18/18
- All-language complete probes: 18
- Identical surface among all-language complete probes: 0/18

## Interpretation

Identical completion rates alone do not imply identical languages. Distinct surface forms alone do not prove correct syntax. Manually inspect contrast_probes.csv for grammatical order, morphology, agreement, and semantic fidelity. This audit does not claim to certify translation correctness.
