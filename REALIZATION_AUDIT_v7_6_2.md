# v7.6.2: semantic attachment and realization probes

`python src/semantic_audit.py` checks five semantic fixtures, including nested NP attachments.

`semantic_audit.realization_probe(sentence, by, grammar)` exposes parse status, surface, gloss, receipts, and missing predicate receipts. It requires an actual grammar and lexicon. The presence of a predicate receipt does not by itself prove correct morphology or meaning.

The translator may still select a legacy fallback when structured realization fails. The probe deliberately reports structured realization only, allowing the fallback boundary to be identified. The 80-sentence corpus must be rerun with real language packages; this release does not claim an improved completion rate.
