# Contrast-suite review and focused v7.5 iteration

All three v7.4 contrast diagnostics agree: 54 complete, 20 partial, 2 unresolved vocabulary, 4 unsupported (80 total).

## Confirmed defects addressed

- English `bigger` and `biggest` did not derive `big` because of the doubled final consonant. Candidate derivation now handles regular doubled-consonant comparatives/superlatives.
- Superlatives such as `biggest` now register comparison in construction analysis.
- `The dog that sees the cat is happy` was misclassified as simple. The analyzer now recognizes this relative-clause shape when `that` precedes a recognizable finite verb. This **does not implement relative-clause realization**; the diagnostic should now accurately identify an unsupported/limited construction.

## Structural failures still open

- Coordinated clauses/predicates: #23, #24, #27, #31, #55.
- Questions: #14-17, #55.
- Embedded prepositional phrases: #42-44.
- Possessive plus reflexive: #35.
- Subordinate, conditional, complement, passive: #61, #62, #64, #65.

## Testing policy

Keep the original 229-sentence advanced corpus and 80-sentence contrast suite as separate translation-only benchmarks. Generate languages with the established source and vocabulary. Test existing language packages with the updated translator before regenerating; this isolates translation changes. Keep all previously complete sentence statuses as a regression baseline and manually inspect target-language semantic fidelity.

No claim is made that v7.5 raises overall completion rate: the actual language packages were not included with the diagnostics, so end-to-end translation counts could not be verified.
