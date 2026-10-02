# v5.7

- Added repeatable `--supplemental-vocabulary` to `build_language.py`.
- Added `add_words.py` to extend an existing generated language without regenerating old forms.
- Added diagnostic `*_missing_words.txt` review queue.
- Added `vocabulary/extra_words_example.txt`.
- Updated package/tool version markers to 5.7.

# Changelog

## 5.6

- Strengthened translation completeness: recognized lexical concepts, including subject nouns/adjectives, must leave a gloss receipt.
- Added grammatical realization receipts for progressive/perfect aspect, negation, yes/no questions, imperative mood, possession, comparison, and modals.
- Improved ordinary period-ended imperative handling; lexical `have`, `be`, and `do` can be imperative rather than being automatically treated as auxiliaries.
- Added conservative yes/no question de-inversion for the legacy realizer (`Did ...?`, pronoun `Is/Are/Was/Were ...?`).
- Refined progressive detection so an `-ing` adjective is not automatically treated as progressive when the lexicon identifies it as adjectival.
- Generic clause glosses now retain the realized subject NP rather than replacing it with opaque `SUBJ`, allowing completeness validation of modifiers and coordinated subjects.
- Tool/package version updated to 5.6; schema remains version 2 and existing v5.5 language packages remain loadable.


## 5.5

- Refactored English analysis into shared `english_analyzer.py`.
- Refactored generated-language loading/validation into shared `language_io.py`.
- Added `validate_language.py` with optional translation-suite audit and JSON report.
- Fixed demonstrative `that` being mistaken for a relative-clause marker.
- Distinguished complement-clause `that` from relative-clause markers.
- Removed sentence-length heuristic that mislabeled short declaratives as imperatives.
- Added grammatical handling for reflexives and possessive `'s`.
- Added proper-name classification instead of treating names as ordinary missing vocabulary.
- Expanded conservative lemma handling for irregular verbs, comparatives, superlatives, plurals, and adverbs.
- Added package schema/tool version metadata.
- Added reproducibility `manifest.json` to new builds with source/vocabulary hashes and build settings.
- Added regression tests for analyzer behavior.
- Retained deterministic/no-invention translation policy and partial/unresolved diagnostics.


## v5.8
- Added `src/generate_names.py`, a standalone proper-name generator for existing language packages.
- Personal names preserve the central `prop.pl` short/long pairing method, using a three-vowel cutoff by default.
- Added `vocabulary/NamingVocabulary.txt` with semantic family/clan-name formulas.
- Family names are built from existing generated-language lexical roots and retain formula-derived meanings.
- Family-name compounding applies the language's configured morphophonemic boundary rules.
- Name generation does not modify `language.json` or the dictionary.
- Outputs both human-readable TXT and structured CSV reports.
