# Empire Of Words v7.6.8 — controlled contrast-suite iteration

## Baseline and provenance

The source is the user-provided complete v7.6.7 project ZIP. All three existing generated language packages are preserved byte-for-byte, including their v7.6.1 build provenance. Only translator source, diagnostics, tests, documentation, and newly generated translation/audit reports have been updated.

**Important baseline distinction:** the three diagnostic files uploaded separately on October 10 reported 67/80 complete, 9 partial, and 4 unsupported. The archived `output/<language>/contrast_suite_v1_diagnostics.txt` files inside the full project ZIP instead report **66/80 complete, 9 partial, and 5 unsupported**. They are not the same run. The release comparison against the actual archived project is therefore **66 -> 69 complete**, while comparison against the separately uploaded newer reports is **67 -> 69 complete**. The quality gate compares against the archived project and reports no regressions.

## Changes

- `The dog sees nothing.`: a negative indefinite is preserved as a lexical pronoun object (`NOTHING-NEG.INDEF`) rather than silently dropped. No extra verbal negation is introduced.
- `The days grow shorter.`: comparative surface forms are resolved to the canonical adjective when available; `SHORT-COMP` and the change-of-state predicate `GROW` are both preserved.
- Diagnostic JSON and text now expose an observed stage: `capability_gate`, `vocabulary`, `analysis_or_parse`, `target_realization`, `semantic_receipts`, or `complete`.
- Four new unit tests cover version, semantic preservation across all three generated languages, fail-closed unsupported grammar, and unresolved names.

## Validation

- Unit tests: 84 passed.
- Contrast suite, each language: 69 complete, 7 partial, 0 unresolved vocabulary, 4 unsupported grammar.
- Quality gate against diagnostics stored in original complete ZIP: PASS, 0 regressions, 3 recoveries per language (the extra recovery compared with the two new semantic fixes reflects a stale diagnostic report in the archive).
- Language audit: three valid packages, distinct grammar fingerprints, 0 identical forms for shared lexical keys in all three pairwise comparisons; 0 identical full surfaces across the 69 all-language-complete contrast probes.

## Deliberately not claimed or changed

- Generated language grammars and dictionaries have **not** been regenerated.
- Proper names absent from the generated lexicon (John, Elizabeth, Madam) are not fabricated. They remain partial.
- Complex conditional, relative, complement, and passive clauses remain explicitly unsupported.
- Completion status is not a substitute for independent semantic or linguistic correctness review.
- Existing homophone warnings remain in generated language packages.

## Next iteration

Prioritize proper-name policy and vocatives; licensed fronted prepositional phrases; comparative preference questions; discourse interjections; and a semantic contrast audit on actual target forms. Preserve the conservative fail-closed statuses and package diversity audit.
