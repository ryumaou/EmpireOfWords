# Empire Of Words — project status

Production acceptance: **NOT SATISFIED**.

Evidence generated: 2026-10-14T03:02:20.473335+00:00. Python 3.14.7; win32.

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

- Major revision `8.0.0-dev4`: clause-final object relatives now bind the main object's antecedent to an explicit embedded object gap, preserving the main subject, predicate, question scope, and the embedded predicate. Inverted HAVE questions now retain perfect aspect, and HAVE BEEN questions retain both perfect and progressive aspect.
- Against iteration 09b, candidate holdout translator completion is unchanged at 146-150/200 per language; relatives remain 20/100, passives 70/100, conditionals 70/100, and complements 10/100. This iteration corrects three distinct development sentences across four existing languages: 12 changed complete records, all with exact-hash implementation reviews, zero unreviewed changes, and zero newly incomplete records. These reviews do not count as independent semantic holdout judgments.
- Full iteration 10d: 130 regression tests, 11 semantic fixtures, contrast audit, 10/10 reproducible language builds, 45/45 distinct pairs, 8/8 vocabulary checks, and clean installation passed. All 69 existing package files remain unchanged.
- Remaining semantic failure: complex object relatives with medial material, such as "the box of candy that Lucy gave me yesterday," can still receive a legacy completion flag without bound roles. These flags are unverified and cannot support a production correctness claim. General source-span and argument binding, plus independent output review, remain required.
- Regression suite: 130 tests passed; semantic fixtures: 11 passed.
- Holdout translator completion: 146–150/200 per language; independently reviewed: 0/2,000; independently correct: 0/2,000.
- Ten-language generation: 10/10 reproducible; 45/45 distinct pairs; 3 observed core word orders.
- Vocabulary expansion: 8/8 safety checks; existing packages: 69 files preserved.
- Clean-install workflow: passed on win32 / Python 3.14.7.
- Regression comparison: 0 newly non-complete; 12 changed complete outputs; 12 exact-hash development reviews; 0 unreviewed.
- Versus prior iteration: none newly passing; none newly failing; vocabulary safety 8/8 → 8/8 checks; translation completion 0 to 0 sentences per language.

A translator completion flag is never an independent semantic correctness score.

## Next priority and architectural decision

The major parser revision is underway. Explicit conditionals preserve both clauses,
finite passives bind patient and agent, and finite relatives bind an antecedent to
a missing embedded subject or object. Each uses its generated target strategy.
Existing language packages remain immutable; incomplete contracts fail safely.
Next: medial object-relative gaps, complement arguments, and complex passives.
These need broader compositional source-span and argument-binding contracts, plus
an independent target-semantic oracle.

Vocabulary expansion passes simulated writer and publication failures; power-loss
recovery remains unverified and needs a durable transaction design.
The new 200-case suite is a frozen candidate, not independently approved ground truth.
Independent suite approval, per-output review and implementation-integrity review are pending.
Do not tune translation rules on these cases; create a replacement blind holdout if exposed
cases are used during implementation. No claim of 95% correctness is made.

## Reproduce and inspect

- Full evidence: `acceptance-runs/iteration-10d/report.json`
- Command: `python -B src/run_acceptance.py --output acceptance-runs/next-iteration`
- Add `--previous <prior-run>/report.json` to enforce sentence-level development status comparisons.
- Policy and independent-review protocol: `acceptance/README.md`.
- A clean-install pass applies only to the recorded OS/Python; it is not a cross-platform certificate.
