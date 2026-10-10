# v7.6.3 — Structured source priority and translation trace

## Observed baseline
v7.6.2 diagnostics: Example, Test1, and Test2 each 59/80 complete, 16 partial, 5 unsupported. Five semantic fixtures passed. Sentence #27 still reports a dropped `dressed` despite the semantic audit preserving `dress`.

## Change
`grammar_engine.analyze_translation` now attempts structured analysis and realization against **the original English sentence first**, and attempts legacy-normalized English only if original structured realization fails. Legacy normalization can insert `did` and alter verb forms, obscuring coordination and past-tense analysis. Legacy translation remains available as a final fallback. Translation IR now records `structured_source` and `structured_realized` for investigation.

## Scope and limitations
This release does **not** claim that #27 is fixed on the user's three language packages: they were not included in the project archive, so actual end-to-end corpus scores have not been remeasured. The 5 unsupported grammatical constructions remain unsupported. Question and comparative handling have not been expanded in this patch. The semantic audit remains a parser-level test, not a certification of target-language fidelity.

## Validation
72 automated tests passed, including a new regression test proving that original English is preferred to a legacy `did` normalization when structured realization succeeds.

## Next verification
Run the 80-sentence contrast suite against Example, Test1, and Test2, compare sentence #27 and inspect `structured_source`, `structured_realized`, and `realization_receipts` in JSON translation output. Retain both diagnostics and translation outputs.
