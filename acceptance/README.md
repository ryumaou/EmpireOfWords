# Production acceptance

The original 80-sentence suite remains a development regression suite. Passing it
does not certify production readiness. `PROJECT_STATUS.md` is the persistent
release status; `run_acceptance.py` updates it after each completed iteration.

Run from a standard Python 3 installation; no third-party modules are required:

```text
python -B src/verify_install.py
python -B -m unittest discover -s tests -q
python -B src/run_acceptance.py --output acceptance-runs/iteration-01
python -B src/run_acceptance.py --output acceptance-runs/iteration-02 --previous acceptance-runs/iteration-01/report.json
```

Use a new output directory each time. The runner preserves every existing
`output/` file and only expands vocabulary in copies of newly generated packages.
Exit 0 means all eight acceptance criteria pass; exit 1 means failed or incomplete
evidence; exit 2 means invalid configuration. A missing independent review is not
a successful semantic assessment. Failed trials remain visible in the report.

Previously complete development outputs that change remain visible in
`regressions.changed_complete`. The regression gate accepts a change only with an
exact-hash, dimension-by-dimension development review supplied through
`--development-reviews` (default `development_change_reviews.json`). Such reviews
are scoped to the development comparison; they never approve a holdout output or
satisfy the independent semantic-review criteria. New incomplete outputs always
fail the comparison.

## Frozen holdout and scope

`holdout_v1.tsv` contains 200 distinct candidate sentences, ten in each of twenty
construction groups. The text is disjoint from all development `.txt` corpora.
`holdout_manifest.json` pins the text hash and construction counts. All 200 cases
remain in the denominator for each of ten generated languages. Unsupported
sentences and missing vocabulary cannot be excluded to raise the score.

The suite was authored during this implementation, without consulting translation
results. It is **not yet independently approved**. An independent reviewer must
evaluate representativeness, ambiguity and semantic intent before release use.
Do not train or tune the translator on these cases. If they become development
examples, retire them and obtain a replacement blind, independently curated suite.
The runner will not silently edit or normalize away failing cases.

The numerical gate is at least 190/200 independently correct outputs **in each**
of ten languages, with all 200 assessed. Construction support separately requires
at least nine independently correct examples in each ten-case construction group
for every language.
Passing the numerical threshold while all conditionals fail cannot pass release.

## Independent semantic evidence

The gate in `src/acceptance_gate.py` has no parser/realizer imports and does not read
the translator's IR, gloss or receipts. `holdout_outputs.json` exposes the actual
source and target surface plus code/package hashes. Reviewers use the generated
language's grammar, dictionary and paradigms to assess the output independently.
Roles, tense/aspect/mood, polarity, scope, reference, lexical content and target
grammar must all be preserved. Any ambiguity must be resolved in the independently
approved test specification, not opportunistically after seeing a target output.

Supply a review JSON using `--reviews path/to/reviews.json`. The default review
file intentionally contains no approvals or judgments. A complete file has:

```json
{
  "suite_review": {
    "suite_sha256": "HASH_FROM_MANIFEST",
    "approved": true,
    "reviewer": "INDEPENDENT_REVIEWER_ID",
    "independent_of_implementation": true,
    "notes": "Review method, semantic specifications and ambiguity decisions."
  },
  "implementation_review": {
    "source_sha256": "HASH_FROM_REPORT",
    "approved": true,
    "reviewer": "INDEPENDENT_REVIEWER_ID",
    "independent_of_implementation": true,
    "notes": "Source audit: no fallback English, invented receipts or sentence-specific shortcuts."
  },
  "judgments": [{
    "language": "Acceptance01",
    "case_id": "H001",
    "output_sha256": "HASH_FROM_HOLDOUT_OUTPUTS",
    "reviewer": "INDEPENDENT_REVIEWER_ID",
    "independent_of_implementation": true,
    "notes": "Explain target forms, agent/patient roles and relevant grammatical markers.",
    "dimensions": {
      "roles": true,
      "tense_aspect_mood": true,
      "polarity": true,
      "scope": true,
      "reference": true,
      "lexical_content": true,
      "target_grammar": true,
      "no_english_fallback": true,
      "no_fabricated_receipts": true
    }
  }]
}
```

The example is a schema illustration, not approval. There must be 2,000 actual
judgments. A changed source file, package or surface invalidates its judgment.
Duplicate judgments and self-review by the recorded suite author are rejected.
Reviewer identity/independence is an auditable human attestation, not something
the software can authenticate. Keep signed review material with release records.
Gate unit tests use explicitly synthetic judgments solely to test rejection logic.

## Generation and installation evidence

Ten fixed seeds and ten family profiles are built twice from the same source and
vocabulary, using different Python hash seeds. No holdout text is supplied to the
builder's vocabulary preflight. Every independent lexical word and free grammar
word must match `[a-z]{2,}`; bound affixes may be one letter. Repeated output trees
must match byte for byte. Morphophonemics is disabled for these ten baseline
languages so simple surface-order observations can identify unchanged lexical
stems without borrowing the translator's own morphology implementation.

Every pair must share at least 100 lexical keys, have no more than 20% identical
forms, and differ in at least two of ten grammatical dimensions. Core-clause
surfaces must demonstrate their declared word order, with at least three orders
across the ten languages. This is a meaningful baseline, not exhaustive proof of
all grammatical features or every available morphophonemic configuration.

Vocabulary tests include repeated requests, exact preservation of old lexemes and
grammar, deterministic additions, malformed input, and a simulated dictionary
write failure. Failed writes must leave a complete package unchanged.

The clean-install check creates a new stdlib-only virtual environment without pip,
copies release inputs without bytecode caches, and runs regression tests, all CLI
help entry points and the documented build/translation workflow. It certifies
only the OS/Python recorded in the report. Other platforms need their own run.
