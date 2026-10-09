# 2026-10-09 diagnostic review and controlled-corpus iteration

## Observed baseline
All three supplied v7.4 diagnostic files report 229 sentences: 157 complete, 51 partial, 0 missing vocabulary, 21 unsupported. The audit reports distinct grammar fingerprints, 18 complete probes, and passing tense, number, and negation contrasts.

## Findings
- Coordinated predicates and multi-verb chains: #134, #142, #143, #159, #171.
- Questions: #84, #106, #113, #149, #171.
- Possession/reflexives: #180.
- Complex subject noun phrases and fronted adjuncts: #74, #76, #79, #82.
- Unsupported syntax: passives, relatives, appositives, subordinate and complement clauses.
- The shared outcome pattern across three typologically different languages points to shared analysis/realization constraints; not proof of a specific code defect.

## Changes in this iteration
- Added controlled contrast suite and CSV manifest. The suite deliberately includes both likely supported and unsupported constructions.
- Strengthened the quality gate: optional exact corpus identity checks prevent false comparisons between different same-length English test sets; changed text for recorded non-complete sentence IDs is rejected even without corpus files.
- Gate explicitly warns if corpus files are omitted; no change in the translator's completion rate is claimed.

## Next implementation order
1. Parser and IR: robust predicate coordination and independent tense/aspect/negation on each verb.
2. Copular/auxiliary questions including WH and modal combinations.
3. PP attachments, possessive NP hierarchy, and appositive vs vocative disambiguation.
4. Extend subordinate/relative/passive syntax only after the relevant IR can preserve roles.
5. Evaluate controlled contrasts for semantic receipts and grammatical placement, not just `ok`.

## Corpus policy
Keep `translations/sentences_advanced.txt` unchanged as a longitudinal benchmark. Run `translations/contrast_suite_v1.txt` separately. Never treat added easy sentences as improved coverage on the 229-sentence benchmark.
