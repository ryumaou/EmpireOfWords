# v7.6.0 — architecture-first development milestone

This release starts the structured-meaning refactor rather than claiming a completed parser replacement.

## Implemented

- Independent clauses retain their own subjects and predicates in `ClauseIR.coordinated` instead of being reduced to shared-subject predicate coordination. This addresses the structural cause of contrast sentence #23.
- The realizer applies the language's **clause** coordination strategy to independent clauses and keeps the existing **predicate** coordination strategy for shared-subject actions.
- New `src/semantic_audit.py` and `translations/semantic_fixtures_v1.json` inspect language-independent semantic roles before target-language realization.
- The fixture runner intentionally fails on sentence #27: the intermediate verb *dressed* is still lost. This is a **known gap**, not a passing test. Add more fixtures as new constructions are implemented.

## How to run (Windows CMD)

```
python src\semantic_audit.py --fixtures translations\semantic_fixtures_v1.json
python -m unittest discover -s tests -v
python src\translate.py --version
```

The semantic audit exits nonzero until all fixtures pass. That is intentional: it exposes known semantic omissions and prevents declaring success based on aggregate completion counts.

## Next engineering work

1. Replace two-predicate special casing with an arbitrary-length predicate list, preserving modifiers, tense, and arguments for each action.
2. Model coordinated NPs and embedded PPs with source-span accountability.
3. Separate question scope, modality, and clause type; preserve them across coordinated predicates.
4. Evaluate spaCy dependency parsing as an optional English-analysis adapter against these fixtures. Do not make it mandatory until it beats the deterministic parser on held-out tests.
5. Expand fixtures and validate all three generated languages against both benchmark corpora with the existing quality gate.

## Evidence and limitations

The uploaded v7.5.2 contrast diagnostics are 55/80 complete in each of three languages. This release was not rerun against those complete language packages, which were not bundled with the diagnostic files. Do not claim a new completion rate until that is done. The semantic fixtures are deliberately narrow and do not certify the full meaning of an English sentence.
