## v7.6.12

- Handle leading `Madam,` and `Sir,` as vocatives, separate from the clause subject; translate only if an actual target-language form exists.
- Report a missing vocative as partial with an explicit semantic diagnostic rather than losing the addressee.
- Hash the full translation implementation (CLI, grammar engine, English analyzer, structured realizer, IR, and language IO) in diagnostics, instead of only `translate.py`.
- Add three vocative regression tests; update version test. No existing language package is regenerated.
- Proper-name coordination and preference comparisons remain unresolved.

## v7.6.11

- Separate leading interjections from the following sentence before clause analysis.
- Realize `Oh dear!` with language-specific interjection lexemes when both exist; retain a semantic receipt for each word.
- Report missing discourse forms as partial instead of silently omitting them (e.g. `Aha!`).
- Add three discourse regression tests. Existing generated languages are not regenerated.
- Proper-name coordination and vocatives remain future work.

## v7.6.10
- Added read-only corpus vocabulary and realization preflight, with per-sentence stages and missing-token candidate lemmas.
- Added three preflight regression tests; no grammar coverage claims.

## v7.6.9
- Preserve leading comma-delimited adjunct prepositional phrases as PPIR nodes, rather than treating the initial adposition as the subject.
- Realize the adjunct through each generated grammar's preposition/postposition placement rules; preserve the object noun, determiner, and semantic receipts.
- Fail closed when a fronted adjunct cannot be analyzed (e.g., unavailable adjective/lexical structure); no invented translation or false completion.
- Add two regression tests covering three existing languages. 86 tests pass.
- Contrast-suite totals remain 69 complete, 7 partial, 4 unsupported per language. This is a structural correctness improvement, not a claimed benchmark gain.
- Existing language packages remain unchanged at build version 7.6.1.

## v7.6.8
- Preserve negative-indefinite pronouns as target-language nominal arguments rather than silently dropping them; do not impose additional verbal negation.
- Resolve English comparative adjective inflections to their canonical lexical base even when a separate surface lexeme was pre-seeded (SHORTER -> SHORT+COMP). Preserve the change-of-state predicate GROW.
- Report an observable diagnostic pipeline stage (capability_gate, vocabulary, analysis_or_parse, target_realization, semantic_receipts, complete) in text and JSON.
- Add focused three-language semantic and no-false-success regression tests.
- Re-run the unchanged contrast suite on the existing language packages. Generated language build versions intentionally remain 7.6.1; languages are not regenerated.

## v7.6.7
- Realize licensed causal subordinate clauses using the generated language’s subordinate particle and placement.
- Require a semantic realization receipt before treating a diagnosed subordinate clause as supported.
- Add causal linker and fail-closed regression tests.

## v7.6.6
- Preserve HOW + adjective degree interrogatives as structured WH questions and realize with target-language interrogative strategy.
- Represent causal BECAUSE clauses as linked semantic clauses for audit, while keeping realization unsupported pending a target grammar strategy.
- Added two semantic fixtures and degree-question regression tests.

## v7.6.5

See ITERATION_REVIEW_v7_6_5.md for interrogative scope and copular question changes.

## 7.6.2
- Recursive NP prepositional attachments and semantic fixture coverage.
- Structured realization probe exposing receipts and missing predicates.
- No unverified benchmark completion claims.

## 7.6.0
- Preserve independent-clause subjects in structured IR and realization.
- Add semantic role audit with an intentionally failing known-gap fixture.
- Add regression tests and architecture roadmap.

## 7.5.2
- Conservative definite-superlative adjective-predicate parsing; three regression tests.
- See ITERATION_REVIEW_v7_5_2.md.

## 7.5.1
- Deployment verification and accurate build metadata; no new translation capabilities.

## v7.5
- Comparative/superlative doubled-consonant lemma normalization.
- Comparative construction recognition for superlatives.
- Better diagnostic classification for relative `that` followed by a finite verb.
- Contrast-suite regression tests and iteration review.

## v7.4 diagnostic quality-gate addendum
- Added `src/quality_gate.py` to reject sentence-level regressions across all languages, even when aggregate coverage is unchanged.
- Added regression-gate tests and diagnostic review. No translation accuracy improvement claimed.

## v7.4
- Add sentence-ID-level diagnostic comparison and regression tests.
- Avoid prioritizing verb homographs for irregular English plural nouns.
- Preserve conservative non-complete statuses for unrepresented grammar.

## v7.3
- Prioritize English verbal lemmas over spurious inflected surface homographs.
- Prefer overt past predicates over ambiguous earlier verb homographs.
- Preserve irregular and regular lexical past tense in structured IR.
- Preserve tense/number affixes at matching consonant boundaries.
- Withhold ambiguous multi-prepositional subjects from structured realization.
- New package version 7.3 and grammar contract 9.

## v7.2
- Contract 8 and strategy-controlled single negation.
- Extended grammatical contrast audit.
- Expanded English inflection candidates.
- Native stacked aspect uses morphophonemic affix handling.

## v7.1
- Creation contract v7: explicit analytic past fallback, versioned validation.
- Past tense realization and receipts, coordination number integrity.
- Minimal-pair fidelity checks in language diversity audit.

## v7.0
- Added translation provenance fingerprints and version reporting.
- Added side-by-side generated-language audit with lexical overlap, grammar differences, and actual translation contrast probes.
- Preserved strict completeness criteria; no claims of semantic correctness from completion status alone.

# Changelog

## 6.8
- Added translation-vocabulary preflight during initial creation when `--translations` is supplied; safely inferred lemma/POS requirements are generated as roots before the package is built.
- Added `--no-translation-vocabulary-preflight` for the legacy build-then-extend workflow.
- Raised the translation-readiness grammar contract to version 5.
- Added generated non-finite strategies for participial modifiers and infinitive complements.
- Added structural operations for word-order/verb question strategies and contract validation for them.
- Added structured IR/realization for simple participial NP modifiers.
- Removed the legacy forced perfect morpheme; languages without native perfect now use the analytic fallback.
- Expanded regression coverage to 38 tests.

## 6.7
- Added realization-contract v4 with productive lexical conversion strategies.
- Added language-specific noun-compound order and compositional noun adjunct realization.
- Added target article/demonstrative realization and grammatical case roles for subjects, objects, possessors, PP objects, and comparison standards.
- Made structured predicate selection context-sensitive so noun/verb homographs do not steal the predicate slot.
- Added contextual noun→verb and adjective→verb realization without inventing unrelated lexical roots.
- Added quantifier/determiner handling in NPIR.
- Preserved v6.6 language-specific coordination and morphosyntactic realization profiles.
- Expanded regression coverage for noun compounds, contextual lexical conversion, and homographic predicates.


- Added realization-contract v3 and a generated morphosyntactic `realization_profile`.
- Generation now exposes noun, adjective, and verb behavior contracts plus independent NP/predicate/clause coordination strategies.
- Structured realizer consumes generated coordination strategy and realizes shared-subject coordinated predicates.
- Added hortative IR for *let's* instead of flattening it to lexical *let*.
- Removed comma-count apposition heuristic that misclassified coordinated predicates.
- Diagnostics now print the target realization profile and per-sentence target strategy traces.
- Kept no-false-success safeguards for genuinely unsupported syntax.

## 6.4
- Added a translation-readiness grammar contract checked at language creation and package validation.
- Generated analytic fallback particles for future, progressive, perfect, and imperative meanings without forcing those features into every typological profile.
- Structured realization now uses those fallbacks instead of silently degrading unsupported target inflection.
- Structured NPs now preserve and realize lexical numerals such as `two`.
- Modal particle placement now follows the generated grammar strategy.


## 6.3
- Added `ir.py` with explicit ClauseIR, NPIR, PredicateIR, and PPIR structures.
- Added `structured_realizer.py` for conservative grammar-driven realization of simple clauses, NP structure, tense/aspect/modal stacks, adverbs, PPs, imperatives, possession, and yes/no questions.
- Structured translations now emit explicit realization receipts used by completeness validation.
- Retained the v6.2 legacy realizer as a conservative fallback whenever the structured parser cannot safely represent a sentence.
- Diagnosed complex constructions remain unsupported until their dedicated structured realizers are implemented.

## 6.5
- Expanded structured IR with explicit modifiers, comparison state, coordinated noun phrases, richer possessive NPs, and more precise realization receipts.
- Added translation-ready adverb derivation (`adverbs.derivation = zero`) so English -ly meanings can reuse an existing adjective root when the generated grammar permits zero derivation.
- Fixed TAM fallback selection: an inventory label is no longer treated as realizable morphology unless its morpheme actually exists; analytic future/progressive/perfect/imperative fallbacks are used when needed.
- Improved fronted copular questions, linking/adjective predicates, modal main-verb selection, comparative adverbs, numerals, multiword possessors, derived DIM/AUG nouns, and question/comparison receipts.
- Corrected missing-vocabulary accounting. Genuine absent lexemes now report `unresolved-vocabulary` instead of being hidden inside `partial` when a legacy surface happens to exist.
- Expanded contextual POS inference for the automatic missing-word queue. The advanced regression corpus now completes a translate -> add_words -> translate cycle with zero missing vocabulary in the bundled synthetic end-to-end test.
- Kept diagnosed high-complexity constructions (relative/complement/conditional/subordinate/passive/quotation/apposition) conservative rather than claiming false completeness.


## 6.9
- Raised translation-readiness realization contract to version 6.
- Added explicit capability declarations for stacked aspect, constituent coordination, copular imperatives, nominal predicates, and irregular comparison.
- Fixed false progressive detection for ordinary `-ing` nouns such as `string`.
- Added deterministic perfect+progressive aspect stacking.
- Prevented NP/adjective conjunctions from being prematurely split as clause coordination.
- Added coordinated predicative adjective realization through the generated predicate-coordination strategy.
- Added nominal copular complement representation and improved copular imperative handling.
- Added irregular degree lemmatization (better/best -> good; worse/worst -> bad; far forms -> far).

## 7.6.1
- Preserve comma-separated shared-subject predicate series in structured IR.
- Make semantic audit default fixture path installation-relative.
- Correct generated language build version metadata.

## 7.6.3
- Prefer original English in structured analysis/realization; use legacy-normalized text only as fallback.
- Record structured source and realization success in translation IR for debugging.
- Add regression test for three-predicate original-source priority.
- See ITERATION_REVIEW_v7_6_3.md for limitations and verification.

## 7.6.4
- Represent WHERE/WHEN interrogative adjuncts in ClauseIR and realize using target WH strategy.
- Add interrogative semantic fixtures and assertions.
