# Empire Of Words — project status

Production acceptance: **NOT SATISFIED**.

Evidence generated: 2026-10-17T21:23:14.717958+00:00. Python 3.14.7; win32.

## Acceptance results

| Criterion | Result | Evidence |
|---|---|---|
| 1. Regression tests | PASS | Regression, semantic fixtures, development comparison and contrast audit |
| 2. Independent holdout >=95% | FAIL / NOT VERIFIED | Coverage only: 147–151/200; independent semantic approval required |
| 3. Construction support | FAIL / NOT VERIFIED | All 20 construction groups, including conditionals, relatives, complements and passive, require at least 9/10 independently correct examples in every language |
| 4. Ten distinct languages | PASS | 45 lexical/grammar comparisons plus independent surface-order observations |
| 5. Safe vocabulary expansion | PASS | Preservation, repeatability, idempotency, malformed-input rejection and injected write failure |
| 6. Word invariants and reproducibility | PASS | All lexical/free grammatical forms [a-z]{2,}; ten repeat builds with different Python hash seeds |
| 7. No inflated semantic metrics | FAIL / NOT VERIFIED | Independent source audit and hash-bound semantic judgments required; receipts never award credit |
| 8. Clean installation | PASS | Fresh venv regression, CLI help/version and documented build/translate workflow |

## Failures and regressions

- 2. Independent holdout >=95%: Coverage only: 147–151/200; independent semantic approval required
- 3. Construction support: All 20 construction groups, including conditionals, relatives, complements and passive, require at least 9/10 independently correct examples in every language
- 7. No inflated semantic metrics: Independent source audit and hash-bound semantic judgments required; receipts never award credit

## Iteration evidence

- Version `8.0.0-dev6` restores complete translations for "This is the house that Jack built" and "Have you seen the box of candy that Lucy gave me yesterday?" across four existing languages. The structured clauses bind HOUSE as a nominal-complement object gap and BOX OF CANDY as a full object gap, respectively; the latter also retains question scope, perfect aspect, Lucy, the recipient, and the time adjunct. Proper names are borrowed with their source spelling.
- All eight changed complete development outputs have exact-hash implementation reviews in `acceptance/development_change_reviews.json`. These are not independent semantic judgments.
- Regression suite: 135 tests passed; semantic fixtures: 11 passed.
- Holdout translator completion: 147–151/200 per language; independently reviewed: 0/2,000; independently correct: 0/2,000.
- Ten-language generation: 10/10 reproducible; 45/45 distinct pairs; 3 observed core word orders.
- Vocabulary expansion: 8/8 safety checks; existing packages: 69 files preserved.
- Clean-install workflow: passed on win32 / Python 3.14.7.
- Regression comparison: 0 newly non-complete; 8 changed complete outputs; 8 exact-hash development reviews; 0 unreviewed.
- Versus prior iteration: none newly passing; none newly failing; vocabulary safety 8/8 → 8/8 checks; translation completion 1 to 1 sentences per language.

A translator completion flag is never an independent semantic correctness score.

## Next priority and architectural decision

The major parser revision is underway. Explicit conditionals preserve both clauses,
finite passives bind patient and agent, and finite relatives bind an antecedent to
a missing embedded subject or object. Each uses its generated target strategy.
Existing language packages remain immutable; incomplete contracts fail safely.
Next: remaining medial object-relative gaps, complement arguments, and complex passives.
These need broader compositional source-span and argument-binding contracts, plus
an independent target-semantic oracle.

Vocabulary expansion passes simulated writer and publication failures; power-loss
recovery remains unverified and needs a durable transaction design.
The new 200-case suite is a frozen candidate, not independently approved ground truth.
Independent suite approval, per-output review and implementation-integrity review are pending.
Do not tune translation rules on these cases; create a replacement blind holdout if exposed
cases are used during implementation. No claim of 95% correctness is made.

## Reproduce and inspect

- Full evidence: `acceptance-runs/iteration-12b/report.json`
- Command: `python -B src/run_acceptance.py --output acceptance-runs/next-iteration`
- Add `--previous <prior-run>/report.json` to enforce sentence-level development status comparisons.
- Policy and independent-review protocol: `acceptance/README.md`.
- A clean-install pass applies only to the recorded OS/Python; it is not a cross-platform certificate.
