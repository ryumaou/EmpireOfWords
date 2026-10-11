# Empire Of Words — project status

Production acceptance: **NOT SATISFIED**.

Evidence generated: 2026-10-11T18:00:39.560194+00:00. Python 3.14.7; win32.

## Acceptance results

| Criterion | Result | Evidence |
|---|---|---|
| 1. Regression tests | PASS | Regression, semantic fixtures, development comparison and contrast audit |
| 2. Independent holdout >=95% | FAIL / NOT VERIFIED | Coverage only: 146–150/200; independent semantic approval required |
| 3. Construction support | FAIL / NOT VERIFIED | All 20 construction groups, including conditionals, relatives, complements and passive, require at least 9/10 independently correct examples in every language |
| 4. Ten distinct languages | PASS | 45 lexical/grammar comparisons plus independent surface-order observations |
| 5. Safe vocabulary expansion | PASS | Preservation, repeatability, idempotency, malformed-input rejection and injected write failure |
| 6. Word invariants and reproducibility | PASS | All lexical/free grammatical forms [a-z]{2,}; ten repeat builds with different Python hash seeds |
| 7. No inflated semantic metrics | FAIL / NOT VERIFIED | Independent source audit and hash-bound semantic judgments required; receipts never award credit |
| 8. Clean installation | PASS | Fresh venv regression, CLI help/version and documented build/translate workflow |

## Failures and regressions

- 2. Independent holdout >=95%: Coverage only: 146–150/200; independent semantic approval required
- 3. Construction support: All 20 construction groups, including conditionals, relatives, complements and passive, require at least 9/10 independently correct examples in every language
- 7. No inflated semantic metrics: Independent source audit and hash-bound semantic judgments required; receipts never award credit

## Iteration evidence

- Major revision `8.0.0-dev3`: subject-relative clauses now bind an overt antecedent to an explicit embedded subject gap and realize the generated relative marker before or after the noun phrase. Ambiguous nesting and object gaps remain unresolved by this structured path; all 69 existing package files remain unchanged.
- Against iteration 08b, candidate holdout translator completion rose exactly 2/200 in each of ten languages (146-150/200 overall). Relative-clause completion rose from 0/100 to 20/100; passives remained 70/100, conditionals 70/100, and complements 10/100. These are unreviewed completion flags.
- Full iteration 09b: 125 regression tests, 11 semantic fixtures, all existing-language contrast checks, 10/10 repeatable builds, 45/45 distinct language pairs, 8/8 vocabulary checks, and clean installation passed. The development comparison found 4 newly complete contrast records (one per existing language), zero newly incomplete, and zero changed previously complete outputs.
- Known semantic-audit gap: the legacy translator can label an object-relative question such as "Have you seen the flowers that the children brought?" complete without an explicit object-gap binding. Existing completion flags need independent semantic review; this case is not evidence of correct object-relative support. A general argument-binding model and revised acceptance judgment are needed before that path can be trusted.
- Regression suite: 125 tests passed; semantic fixtures: 11 passed.
- Holdout translator completion: 146–150/200 per language; independently reviewed: 0/2,000; independently correct: 0/2,000.
- Ten-language generation: 10/10 reproducible; 45/45 distinct pairs; 3 observed core word orders.
- Vocabulary expansion: 8/8 safety checks; existing packages: 69 files preserved.
- Clean-install workflow: passed on win32 / Python 3.14.7.
- Regression comparison: 0 newly non-complete; 0 changed complete outputs requiring semantic review.
- Versus prior iteration: none newly passing; none newly failing; vocabulary safety 8/8 → 8/8 checks; translation completion 2 to 2 sentences per language.

A translator completion flag is never an independent semantic correctness score.

## Next priority and architectural decision

The major parser revision is underway. Explicit conditionals preserve both clauses,
finite passives bind patient and agent, and subject relatives bind an antecedent to
a missing embedded subject. Each uses its generated target-language strategy.
Existing language packages remain immutable; incomplete contracts fail safely.
Next: object-relative gaps, complement arguments, and complex passive clauses.
These need broader compositional source-span and argument-binding contracts, plus
an independent target-semantic oracle.

Vocabulary expansion passes simulated writer and publication failures; power-loss
recovery remains unverified and needs a durable transaction design.
The new 200-case suite is a frozen candidate, not independently approved ground truth.
Independent suite approval, per-output review and implementation-integrity review are pending.
Do not tune translation rules on these cases; create a replacement blind holdout if exposed
cases are used during implementation. No claim of 95% correctness is made.

## Reproduce and inspect

- Full evidence: `acceptance-runs/iteration-09b/report.json`
- Command: `python -B src/run_acceptance.py --output acceptance-runs/next-iteration`
- Add `--previous <prior-run>/report.json` to enforce sentence-level development status comparisons.
- Policy and independent-review protocol: `acceptance/README.md`.
- A clean-install pass applies only to the recorded OS/Python; it is not a cross-platform certificate.
