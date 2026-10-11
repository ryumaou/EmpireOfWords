# Empire Of Words — project status

Production acceptance: **NOT SATISFIED**.

Evidence generated: 2026-10-11T17:19:59.477305+00:00. Python 3.14.7; win32.

## Acceptance results

| Criterion | Result | Evidence |
|---|---|---|
| 1. Regression tests | PASS | Regression, semantic fixtures, development comparison and contrast audit |
| 2. Independent holdout >=95% | FAIL / NOT VERIFIED | Coverage only: 144–148/200; independent semantic approval required |
| 3. Construction support | FAIL / NOT VERIFIED | All 20 construction groups, including conditionals, relatives, complements and passive, require at least 9/10 independently correct examples in every language |
| 4. Ten distinct languages | PASS | 45 lexical/grammar comparisons plus independent surface-order observations |
| 5. Safe vocabulary expansion | PASS | Preservation, repeatability, idempotency, malformed-input rejection and injected write failure |
| 6. Word invariants and reproducibility | PASS | All lexical/free grammatical forms [a-z]{2,}; ten repeat builds with different Python hash seeds |
| 7. No inflated semantic metrics | FAIL / NOT VERIFIED | Independent source audit and hash-bound semantic judgments required; receipts never award credit |
| 8. Clean installation | PASS | Fresh venv regression, CLI help/version and documented build/translate workflow |

## Failures and regressions

- 2. Independent holdout >=95%: Coverage only: 144–148/200; independent semantic approval required
- 3. Construction support: All 20 construction groups, including conditionals, relatives, complements and passive, require at least 9/10 independently correct examples in every language
- 7. No inflated semantic metrics: Independent source audit and hash-bound semantic judgments required; receipts never award credit

## Iteration evidence

- Major revision `8.0.0-dev2`: simple finite passives with an overt agent now bind patient and agent separately, realize the generated voice strategy and agent placement, and reject missing morphological voice contracts. New packages using morphological passive receive an affix; all 69 existing package files remain unchanged.
- Against iteration 07, candidate holdout translator completion increased by exactly 3/200 in each of ten languages (144-148/200 overall). Passive completion increased from 40/100 to 70/100; conditionals remained 70/100, complements 10/100, and relatives 0/100. No independent semantic judgment exists for these outputs.
- Full iteration 08b: 122 regression tests and 11 semantic fixtures passed; all existing-language contrast probes passed; zero newly incomplete and zero changed previously complete development outputs; 10/10 repeatable builds, 45/45 distinct language pairs, 8/8 vocabulary checks, and the clean-install workflow passed.
- Remaining translation failures: complex passive clauses, relative gaps, and complement arguments need a compositional source-span and role-binding architecture. Independent holdout approval, output review, and implementation-integrity review remain pending. No 95% semantic-correctness claim is made.
- Regression suite: 122 tests passed; semantic fixtures: 11 passed.
- Holdout translator completion: 144–148/200 per language; independently reviewed: 0/2,000; independently correct: 0/2,000.
- Ten-language generation: 10/10 reproducible; 45/45 distinct pairs; 3 observed core word orders.
- Vocabulary expansion: 8/8 safety checks; existing packages: 69 files preserved.
- Clean-install workflow: passed on win32 / Python 3.14.7.
- Regression comparison: 0 newly non-complete; 0 changed complete outputs requiring semantic review.
- Versus prior iteration: none newly passing; none newly failing; vocabulary safety 8/8 → 8/8 checks; translation completion 3 to 3 sentences per language.

A translator completion flag is never an independent semantic correctness score.

## Next priority and architectural decision

The major parser revision is underway. Explicit two-clause conditionals now use separate
condition and consequence IR nodes. Explicit finite passives now bind patient and agent
roles and use the target passive strategy; new morphological packages include an affix.
Existing language packages remain immutable; incomplete old strategies fail safely.
Next: role-aware relative gaps, complement arguments, and complex passive clauses.
These need a compositional source-span contract and an independent target-semantic oracle.

Vocabulary expansion passes simulated writer and publication failures; power-loss
recovery remains unverified and needs a durable transaction design.
The new 200-case suite is a frozen candidate, not independently approved ground truth.
Independent suite approval, per-output review and implementation-integrity review are pending.
Do not tune translation rules on these cases; create a replacement blind holdout if exposed
cases are used during implementation. No claim of 95% correctness is made.

## Reproduce and inspect

- Full evidence: `acceptance-runs/iteration-08b/report.json`
- Command: `python -B src/run_acceptance.py --output acceptance-runs/next-iteration`
- Add `--previous <prior-run>/report.json` to enforce sentence-level development status comparisons.
- Policy and independent-review protocol: `acceptance/README.md`.
- A clean-install pass applies only to the recorded OS/Python; it is not a cross-platform certificate.
