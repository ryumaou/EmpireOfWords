# Empire Of Words
A set of Python scripts that allow a technically literate worldbuilder to create languages and language families for imagined worlds.

Based, in part, on Perl scripts originally created by Chris Pound, with additional inspiration from other conlanging sources.

## v7.4: regression accountability and conservative lexical analysis

This release introduces `src/compare_diagnostics.py` to identify exactly which sentence IDs became partial or unsupported and which recovered. The v7.2-to-v7.3 transition lost previously complete sentences even while other sentences improved; a single total hid that churn. The comparator validates corpus length and diagnostic completeness and refuses inconsistent reports. It also prevents irregular English plurals (such as *leaves*) from being preferentially interpreted as verbs during lexical preflight. **This is a diagnostic and correctness-oriented iteration, not a claim of higher translation coverage.**

Windows example:

```cmd
python src\compare_diagnostics.py --before previous_diagnostics.txt --after current_diagnostics.txt --output regression_report.txt
```

## v7.3: English inflection and predicate disambiguation

English inflected verb lookup now favors attested verbal lemmas over accidental surface homographs. Structured predicate selection prioritizes overtly inflected verbs (e.g., *blew* over the homographic verb *wind*), and retains past tense in the grammatical IR. New packages advertise realization contract 9. Morpheme boundaries preserve grammatical affixes when the stem begins or ends with the same consonant, avoiding silent future/plural homophony. Complex prepositional subjects that cannot be represented reliably are withheld from structured realization. The audit remains a structural diagnostic rather than a semantic correctness certificate. Review benchmark deltas and unresolved constructions before accepting any increase in completion as verified accuracy.

## v7.1: grammar fidelity and overt past reference

New language packages use realization contract v7 and include an analytic past marker even when past is not a native tense. Structured realization now applies native past morphology or the generated analytic marker and records a past-tense receipt; coordinated singular noun phrases retain their individual singular number instead of being silently pluralized. The language audit includes minimal-pair past/present and coordinated-noun number checks. These checks are deliberately limited and do not certify overall translation correctness.

## v7.0: verifiable language diversity and provenance

v7.0 adds **runtime provenance** to every `translate.py --diagnostics` report: translator version and source hash, language build version, language package and grammar SHA-256 hashes, schema version, and realization-contract version. This makes stale script/package combinations immediately visible.

A new `src/audit_languages.py` compares actual generated language packages rather than their completion counts. It checks lexicon overlap by lemma/POS and surface form, compares grammar profiles and fingerprints, validates packages, and translates a fixed set of contrast probes using each language's real grammar and vocabulary. It emits a Markdown report and side-by-side CSV. A successful translation status does **not** certify semantic fidelity; inspect the contrast CSV for actual word order, morphology, and feature realization.

Windows example (run from project root):

```cmd
python src\audit_languages.py ^
  --languages output\Test1 output\Test2 output\Example ^
  --output output\language_audit
```

To audit the full advanced corpus rather than just the short contrast set, append `--corpus translations\sentences_advanced.txt`.

**Important:** If the diagnostics still say `Translator version: 6.9` or omit provenance entirely, you're executing an older translator. Also check that the language build version says `7.0` after regenerating from scratch.

## v6.9: capability-complete realization

v6.9 keeps v6.8's creation-time translation vocabulary preflight and raises the realization contract to version 6. New languages explicitly advertise stacked aspect, constituent-level coordination, copular imperatives, nominal predicates, and irregular comparison support. The analyzer now requires BE to directly license a verbal `-ing` form before diagnosing progressive aspect, preventing nouns such as *string* from creating false aspect requirements. Perfect+progressive stacks deterministically, and NP/adjective coordination is preserved inside the constituent so each generated language's NP/predicate/clause coordination strategy can actually be used.

The design goal remains creation-first: the generated package records the grammatical capabilities the realizer may rely on, while translation completeness remains strict.


## v6.8 translation-ready creation

v6.8 moves another layer of translation readiness into initial language creation. When `--translations` is supplied, the builder now performs a conservative lexical/POS preflight and creates safely inferred independent roots before the language is generated. Use `--no-translation-vocabulary-preflight` to retain the older build-then-add workflow. This does not weaken translation completeness checks; it moves known corpus requirements earlier in the pipeline.

The grammar realization contract is now version 5. New languages explicitly choose strategies for participial modifiers and infinitive complements, and structural yes/no question systems record an actual operation rather than a label alone. Native perfect morphology is no longer forced into languages whose aspect inventory does not grammaticalize perfect; those languages use their generated analytic fallback. The structured IR can preserve simple participial NP modifiers such as *a tiger wearing a bell*.

## v6.7 morphosyntactic realization contract

v6.7 makes generated grammar choices first-class translation inputs. Each new language records a `realization_profile` describing word order, adposition and adjective placement, possession, noun number/case behavior, adjective comparison/adverb behavior, verb TAM/agreement behavior, questions, negation, and independently generated NP/predicate/clause coordination strategies. Translation diagnostics print this profile and record the target strategies attempted.

The structured realizer now handles shared-subject predicate coordination, preserves coordination receipts, and represents English *let's* as a first-person-plural hortative rather than lexical *let*. The analyzer no longer diagnoses apposition merely from comma count. Unsupported constructions remain unsupported unless a safe structured realizer exists.

## Overview

Empire Of Words is a deterministic, file-based conlang toolkit. It can generate a lexicon from the statistical character of a source corpus, construct a configurable grammar, create inflectional paradigms and reference material, translate supported English constructions, diagnose translation gaps, extend an existing language without regenerating it, validate generated packages, and create language-shaped personal and family names.

The tools are designed to work together around a generated `language.json` package. A seed can be supplied whenever reproducibility matters. Translation and name generation consume an existing language rather than silently rebuilding it.

The system deliberately distinguishes between what it can generate or analyze and what it cannot. Unsupported translation structures and missing vocabulary are reported rather than filled with invented target-language forms.

## Requirements

- Python 3
- No external Python packages are required by the supplied scripts.
- Commands in this README use Windows `cmd.exe` continuation syntax (`^`), but the scripts are ordinary Python programs and can be run on other platforms with normal path and shell syntax.

Run commands from the project root unless you explicitly use `--project-root`.

## Project structure

```text
Empire-Of-Words/
├── README.md
├── CHANGELOG.md
├── src/
│   ├── add_words.py
│   ├── build_language.py
│   ├── english_analyzer.py
│   ├── generate_daughter.py
│   ├── generate_names.py
│   ├── grammar_engine.py
│   ├── language_io.py
│   ├── lc.py
│   ├── translate.py
│   └── validate_language.py
├── vocabulary/
│   ├── MagicVocabulary.txt
│   ├── NamingVocabulary.txt
│   └── extra_words_example.txt
├── translations/
│   ├── sentences_default.txt
│   └── sentences_advanced.txt
├── tests/
│   └── test_analysis.py
├── data/                         # user-supplied source corpora
└── output/                       # generated at runtime
    └── <LanguageName>/
        ├── dictionary.csv
        ├── derivational_morphology.txt
        ├── etymology.txt
        ├── examples.txt
        ├── grammar.json
        ├── language.json
        ├── manifest.json
        ├── lineage.csv              # daughter languages
        ├── lineage.md               # daughter languages
        ├── paradigms.csv
        ├── reference.md
        ├── names/                # created by generate_names.py
        └── translations/         # created by translate.py
```

`data/` and `output/` may not exist in a fresh distribution. Create `data/` when you add source corpora; `output/` is created automatically when a language is built.

## Typical workflow

A normal project moves through five independent stages:

```text
source corpus + vocabulary
          │
          ▼
   build_language.py
          │
          ▼
 output/<Language>/language.json
          │
     ┌────┼───────────────┐
     ▼    ▼               ▼
 validate translate   generate names
          │
          ▼
 diagnostics / missing-word review
          │
          ▼
 supplemental vocabulary or add_words.py
```

A generated language remains stable unless you deliberately rebuild it or extend its lexicon.

# Creating a language

## Source corpus

Put one or more source text files in `data/`. The source is used to learn the character sequences from which new roots and grammatical material are generated. It is not treated as a vocabulary translation table.

Example:

```text
data/ExampleSource.txt
```

If there is exactly one `.txt` source in `data/`, the builder can select it automatically. If there are several, select one explicitly with `--source`.

## Vocabulary definition

The main supplied vocabulary is:

```text
vocabulary/MagicVocabulary.txt
```

A basic independent entry uses:

```text
dog:n
run:v
red:adj
```

Derived entries may reference other vocabulary and named derivational modifiers, for example:

```text
dancer:n = dance:v-DOER
```

Sense-qualified vocabulary can be referenced explicitly:

```text
hair (of body):n
hair (of head):n
hairy:adj = hair (of body)-RELATING.TO
```

When an unqualified derivational reference has multiple matching sense-qualified entries, the first matching entry in vocabulary-file order is used. Prefer explicit references when the intended sense matters.

## Basic build

```cmd
python src\build_language.py ^
  --language-name "Example" ^
  --source data\ExampleSource.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --grammar-family naturalistic ^
  --seed 12345
```

Relative paths are resolved from the project root rather than the current working directory.

If exactly one source corpus and one vocabulary file are available, they may be omitted:

```cmd
python src\build_language.py --language-name "Example" --seed 12345
```

When multiple candidates exist, the builder stops and asks you to select one instead of guessing.

## Grammar families

`--grammar-family` selects a typological profile. These are inspirations and weighted structural defaults, not attempts to reproduce a particular natural language.

Available profiles are:

```text
naturalistic   random         romance        germanic
slavic         arabic         semitic        turkic
uralic         japanese       celtic         latin
greek          indic          iranian        dravidian
bantu          polynesian     austronesian   berber
quechuan       kartvelian     caucasian      sino-tibetan
analytic       agglutinative  fusional       isolating
```

Example:

```cmd
python src\build_language.py ^
  --language-name "Example" ^
  --source data\ExampleSource.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --grammar-family uralic ^
  --seed 12345
```

## Grammar overrides

Family defaults can be overridden individually:

```text
--word-order SVO|SOV|VSO|VOS|OVS|OSV
--adjective-position before|after
--adposition pre|post|preposition|postposition
--possession possessor-first|possessed-first|before|after
--gender none|2|3|classes
--cases 0..8
--articles none|definite|indefinite|both
--agreement none|subject|subject-object
--tense minimal|standard|rich
--aspect minimal|standard|rich
--mood minimal|standard|rich
--plural none|suffix|prefix|mixed
--comparison particle|affix|mixed
--questions particle|word-order|verb|mixed
--negation particle|affix|mixed
--grammar-morphology analytic|agglutinative|fusional|mixed|isolating
```

For example:

```cmd
python src\build_language.py ^
  --language-name "Example" ^
  --source data\ExampleSource.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --grammar-family germanic ^
  --word-order SOV ^
  --adjective-position after ^
  --cases 5 ^
  --gender none ^
  --seed 12345
```

Grammar family and grammar morphology are independent, so hybrid designs are possible.

## Morphophonemics

By default, a grammar family selects an associated surface morphophonemic profile:

```text
--morphophonemics auto
```

Disable the layer with:

```text
--morphophonemics none
```

Or explicitly choose comma-separated rules. Supported rules include:

```text
vowel_harmony
vowel_harmony_light
initial_mutation
lenition
elision
vowel_elision
palatalization
consonant_assimilation
nasal_assimilation
epenthesis
reduplication
ablaut
templatic_light
```

Example:

```cmd
python src\build_language.py ^
  --language-name "Hybrid" ^
  --source data\ExampleSource.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --grammar-family romance ^
  --morphophonemics vowel_harmony,consonant_assimilation ^
  --seed 12345
```

`templatic_light` performs conservative internal stem alternation. It is not a full consonantal-root-and-pattern system.

## Reusing an exact grammar

Every language package includes `grammar.json`. Reuse it to create another language with the same grammatical architecture:

```cmd
python src\build_language.py ^
  --language-name "RelatedLanguage" ^
  --source data\RelatedSource.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --grammar-file output\Example\grammar.json ^
  --seed 54321
```

When `--grammar-file` is supplied, grammar-family and grammar-override switches are ignored.

This is useful when creating related languages or a language family whose members should share a grammatical profile while using different lexical source material.

## Supplemental vocabulary during a build

Additional vocabulary can be kept outside the main vocabulary file:

```text
vocabulary/Example_extra.txt
```

Example:

```text
robin:n
bonfire:n
solstice:n
juicy:adj
salty:adj
```

Include it with:

```cmd
python src\build_language.py ^
  --language-name "Example" ^
  --source data\ExampleSource.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --supplemental-vocabulary vocabulary\Example_extra.txt ^
  --seed 12345
```

`--supplemental-vocabulary` may be repeated to combine multiple vocabulary packs. Duplicate entries are rejected, and a supplemental file cannot silently redefine an existing modifier with a different rule.

## Translation sentences during generation

A reusable sentence suite is a UTF-8 text file containing one English sentence per line. Blank lines and lines beginning with `#` are ignored.

```cmd
python src\build_language.py ^
  --language-name "Example" ^
  --source data\ExampleSource.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --translations translations\sentences_default.txt ^
  --grammar-family naturalistic ^
  --seed 12345
```

When supplied, these sentences replace the built-in examples written to the generated package. Unsupported vocabulary or constructions are reported rather than filled with invented target-language words.

# Generated language package

A normal build creates `output/<LanguageName>/` containing:

- `language.json` — canonical machine-readable language package: grammar, lexicon, generated forms, translation capabilities, and examples.
- `grammar.json` — reusable grammar definition.
- `dictionary.csv` — English gloss, part of speech, generated form, root/derived status, and derivation.
- `paradigms.csv` — generated noun, verb, and adjective paradigms.
- `derivational_morphology.txt` — generated derivational affixes and their source rules.
- `etymology.txt` — derivational relationships plus unresolved vocabulary/derivation errors.
- `examples.txt` — generated or requested example translations.
- `reference.md` — human-readable grammar reference.
- `manifest.json` — build provenance, seed, source/vocabulary paths and hashes, grammar selection, and build counts.

The builder exits with a nonzero status when unresolved vocabulary derivations or build errors remain, even if it was able to write useful output files. See the `UNRESOLVED / ERRORS` section of `etymology.txt` for details.

# Validating a language

Use `validate_language.py` to inspect an existing package without changing it:

```cmd
python src\validate_language.py --language output\Example
```

To audit the language against a translation suite:

```cmd
python src\validate_language.py ^
  --language output\Example ^
  --translations translations\sentences_advanced.txt ^
  --report output\Example\advanced_validation.json
```

Validation checks the package structure and can report translation coverage against a sentence suite.

# Translating with an existing language

`translate.py` loads an existing `language.json`; it does not regenerate the language.

## Translate a sentence file

```cmd
python src\translate.py ^
  --language output\Example ^
  --input translations\sentences_advanced.txt
```

The default output is:

```text
output/Example/translations/sentences_advanced.txt
```

Use `--output` to choose another path.

## Translate one sentence

```cmd
python src\translate.py ^
  --language output\Example ^
  --sentence "The warrior walked into the city."
```

The result is printed to the console.

## Translation diagnostics

```cmd
python src\translate.py ^
  --language output\Example ^
  --input translations\sentences_advanced.txt ^
  --diagnostics
```

Diagnostics classify results as:

```text
ok
partial
unresolved-vocabulary
unsupported-grammar
```

An `ok` result is intended to mean that the meaningful analyzed content was realized. `partial` is used when the analyzer recognizes content that the realizer does not preserve.

For a batch translation, diagnostics include status totals, detected constructions, missing/unrecognized English lexemes, and per-sentence reasons.

## Automatic missing-vocabulary file

Every batch translation automatically checks for genuinely missing concepts, even when `--diagnostics` is not used. When missing vocabulary is found, the translator writes:

```text
<translation-stem>_missing_words.txt
```

The file is directly compatible with `add_words.py`. Confidently normalized lemmas and parts of speech are active `gloss:pos` entries; occurrence counts and provenance are comments. Words whose part of speech cannot be inferred safely remain commented under `REVIEW REQUIRED` and therefore are ignored by `add_words.py` until you edit them.

For example:

```text
# Empire Of Words - missing vocabulary required by this translation
# Language: Northern

robin:n  # 2 occurrences
pebble:n  # 3 occurrences; from pebbles
seize:v  # 1 occurrence; from seized

# REVIEW REQUIRED - POS could not be inferred safely; not active add_words entries.
# strangeword  (1)
```

Apply the reviewed file directly:

```cmd
python src\add_words.py ^
  --language output\Northern ^
  --words output\Northern\translations\sentences_missing_words.txt ^
  --seed 67890
```

If no missing concepts are found, no missing-word file is retained. Detailed diagnostic and analysis files still require `--diagnostics`.

The missing-vocabulary pass distinguishes lexical additions from translation-realizer failures as far as the deterministic analyzer can do so. Review the file before applying it: an unusual inflection or ambiguous English word can still require human judgment.

The translation engine is deterministic and intentionally conservative. It does not use an AI model to invent target-language forms.

# Extending an existing dictionary

Use `add_words.py` when you want to add independent roots to an existing language without regenerating its current vocabulary.

Create a file such as:

```text
vocabulary/Example_extra.txt
```

with entries like:

```text
robin:n
bonfire:n
solstice:n
juicy:adj
salty:adj
```

Then run:

```cmd
python src\add_words.py ^
  --language output\Example ^
  --words vocabulary\Example_extra.txt ^
  --seed 67890
```

The script:

- preserves all existing lexical forms;
- learns new word shapes from the existing root lexicon;
- generates only genuinely new roots;
- skips entries already present;
- updates `language.json` and `dictionary.csv`;
- appends applicable paradigms to `paradigms.csv`;
- records the extension in `language.json`; and
- creates `language.json.bak` before modifying the package.

`add_words.py` currently accepts independent `gloss:pos` roots only. Add derivational definitions to a vocabulary file and rebuild if you need new derived entries.

When the target is a daughter language, additions are local lexical innovations. `add_words.py` updates `lineage.csv` and `lineage.md`, records the current language as the word's origin, and does not modify the parent or sibling languages. Descendants generated afterward inherit both the word and its original point of entry into the family.

# Creating daughter languages

`generate_daughter.py` evolves an existing generated language into a historically related daughter language. Unlike a fresh build, it begins with the parent language's lexicon and grammar, applies ordered regular sound changes, optionally introduces grammatical drift, and replaces a controlled fraction of inherited roots with lexical innovations.

The result is a normal Empire Of Words language package. It can be translated with, extended with `add_words.py`, used for proper-name generation, validated, or used as the parent of another daughter language. This allows branching and multi-generation language families.

## Basic daughter generation

```cmd
python src\generate_daughter.py ^
  --parent output\RootLanguage ^
  --language-name "DaughterLanguage" ^
  --profile balanced ^
  --seed 24680
```

The three built-in evolution profiles are:

```text
conservative   fewer regular sound changes, little lexical replacement, little grammar drift
balanced       moderate sound change and vocabulary turnover
divergent      stronger sound change, more lexical replacement, and more opportunities for grammar drift
```

Profiles are convenient defaults rather than opaque presets. The exact changes selected for a daughter are written into its package.

## Controlling historical distance

Profile settings can be overridden independently:

```cmd
python src\generate_daughter.py ^
  --parent output\RootLanguage ^
  --language-name "Northern" ^
  --profile balanced ^
  --sound-rules 8 ^
  --lexical-replacement 0.08 ^
  --grammar-drift 0.30 ^
  --seed 1001
```

`--sound-rules` controls the number of ordered regular sound changes. `--lexical-replacement` is a fraction from 0 to 1 specifying how many inherited root lexemes are replaced by innovations. `--grammar-drift` is a probability from 0 to 1 applied to the supported syntactic drift dimensions.

Regular sound changes apply to inherited lexical forms and grammatical material. Independent lexical words retain the project's minimum two-letter visible form rule. Lexical replacement is separate from sound change: a changed cognate remains inherited, while a replacement is explicitly marked as an innovation.

## Lineage records

A daughter package adds:

```text
lineage.csv
lineage.md
```

`lineage.csv` records each lexical entry's English gloss, part of speech, parent form, daughter form, inheritance status, applied changes, and origin language. The daughter's `dictionary.csv` carries the same ancestry information. Local additions and lexical replacements are marked as innovations at the language where they entered the family; descendants preserve that origin until a later replacement occurs.

`lineage.md` summarizes the parent, evolution profile, seed, ordered sound changes, grammar changes, and lexical-replacement statistics. `language.json` stores the same ancestry metadata in its `lineage` object.

This makes ancestry inspectable rather than inferred from spelling similarity.

## Branching a family

Generate sister languages from the same parent with different seeds or profiles:

```cmd
python src\generate_daughter.py --parent output\Proto --language-name "North" --profile balanced --seed 101
python src\generate_daughter.py --parent output\Proto --language-name "South" --profile balanced --seed 202
```

Then continue either branch:

```cmd
python src\generate_daughter.py --parent output\North --language-name "NorthCoastal" --profile conservative --seed 303
```

`NorthCoastal` records `North` as its immediate parent, while `North` retains its own ancestry back to `Proto`. The packages therefore form an explicit family tree.

## Shared-history branches

If two daughter languages should share early innovations, first generate an intermediate ancestor and branch from it. For example:

```text
Proto
  │
  └── EarlyNorthern
        ├── Highland
        └── Coastal
```

This is preferable to independently generating `Highland` and `Coastal` from `Proto`, because their shared sound and grammar changes are then genuinely inherited from `EarlyNorthern`.

# Generating proper names

`generate_names.py` creates names from an existing language without modifying its dictionary.

There are two complementary naming systems.

## Personal names

Personal names are generated from the statistical character of the language's existing root vocabulary. Candidate forms are divided into short and long pools according to vowel count, and a personal name combines one element from each pool in randomized order.

These are phonological creations. The program does not invent semantic meanings for them.

Generate personal names with:

```cmd
python src\generate_names.py ^
  --language output\Example ^
  --mode personal ^
  --count 50 ^
  --seed 12345
```

The short/long boundary defaults to three vowels. For languages whose word shapes make that unsuitable, override it:

```text
--vowel-cutoff 2
```

## Family and clan names

Family names use semantic formulas from:

```text
vocabulary/NamingVocabulary.txt
```

Examples of formula structure include:

```text
black+bear
dragon+hunter
moon+flower
black+flower+river
```

Every component must exist in the generated language lexicon. The generator combines the language's actual forms, applies configured boundary morphophonemics, and reports both the resulting name and its semantic source.

A result can therefore record:

```text
Family name: <generated compound>
Meaning: black bear
Formula: black+bear
Language roots: <form for black> + <form for bear>
```

A formula is skipped when one or more required concepts are absent. Add culturally important missing concepts with supplemental vocabulary or `add_words.py`, then rerun name generation.

Generate family names with:

```cmd
python src\generate_names.py ^
  --language output\Example ^
  --mode family ^
  --naming-vocabulary vocabulary\NamingVocabulary.txt ^
  --count 50 ^
  --seed 12345
```

## Full names

The default mode combines a generated personal name with a meaningful family name:

```cmd
python src\generate_names.py ^
  --language output\Example ^
  --count 25 ^
  --seed 12345
```

Equivalent explicit mode:

```text
--mode full
```

`--mode all` is also accepted by the script.

Default output is written under:

```text
output/Example/names/
```

with both a human-readable text file and a CSV containing the full name, personal name, family name, family-name meaning, source formula, personal generation components, and family source forms.

Use `--output` to select a different text output path; the CSV is written beside it.

# Testing

Run the supplied regression tests from the project root:

```cmd
python -m unittest discover -s tests -v
```

The tests cover important English-analysis distinctions used by the translation pipeline.

# Script reference

## `src/build_language.py`

Creates a complete language package.

Important options:

```text
--language-name NAME
--source FILE
--vocabulary FILE
--supplemental-vocabulary FILE    repeatable
--translations FILE
--grammar-family FAMILY
--grammar-file FILE
--morphophonemics RULES
--seed NUMBER
--min-root NUMBER
--max-root NUMBER
--project-root PATH
```

Use `python src\build_language.py --help` for the complete grammar-override list.

## `src/translate.py`

Translates one sentence or a sentence file with an existing language.

```text
--language PATH
--input FILE | --sentence TEXT
--output FILE
--diagnostics
--project-root PATH
```

## `src/validate_language.py`

Validates an existing language package and optionally audits a translation suite.

```text
--language PATH
--translations FILE
--report FILE
--project-root PATH
```

## `src/add_words.py`

Adds independent vocabulary roots without regenerating existing forms.

```text
--language PATH
--words FILE
--seed NUMBER
--project-root PATH
```

## `src/generate_daughter.py`

```text
--parent PATH
--language-name NAME
--profile conservative|balanced|divergent
--seed NUMBER
--sound-rules NUMBER
--lexical-replacement FRACTION
--grammar-drift FRACTION
--output DIRECTORY
--project-root PATH
```

## `src/generate_names.py`

Generates personal, family, or full names from an existing language.

```text
--language PATH
--naming-vocabulary FILE
--mode personal|family|full|all
--count NUMBER
--seed NUMBER
--vowel-cutoff NUMBER
--output FILE
--project-root PATH
```

# Reproducibility and project management

For repeatable results, record the seed used for each operation. A language build records its primary build information in `manifest.json`, including hashes of the selected source and vocabulary files. Keep source corpora, vocabulary supplements, grammar files, translation suites, and seeds under version control if you want to reproduce a worldbuilding project later.

A practical organization for several related languages is:

```text
data/
├── ProtoLanguage.txt
├── DaughterNorth.txt
└── DaughterSouth.txt

vocabulary/
├── MagicVocabulary.txt
├── SharedCulture.txt
├── NorthernCulture.txt
└── SouthernCulture.txt

output/
├── ProtoLanguage/
├── NorthernLanguage/
└── SouthernLanguage/
```

You can reuse a common `grammar.json`, vary source corpora and seeds, share supplemental vocabulary packs, or combine those techniques depending on how closely related the imagined languages should be.

# Design principles and limitations

Empire Of Words favors reproducibility and inspectability over opaque generation. Generated forms, derivations, grammar choices, paradigms, translation diagnostics, and name etymologies are written to ordinary text, CSV, Markdown, and JSON files.

The grammar-family profiles are broad typological inspirations rather than linguistic simulations of specific real-world languages. The English translator supports a growing inventory of constructions but is not a general-purpose natural-language parser. Unsupported grammar is diagnosed instead of silently approximated, and missing target-language concepts are reported instead of invented.

Personal names are language-shaped but semantically arbitrary. Family/clan names have meanings only when those meanings are grounded in the semantic formulas and vocabulary forms used to construct them.

## Structured translation and grammar realization

Empire Of Words analyzes English before realization and refuses to label a translation complete when recognized lexical or grammatical information was dropped. Generated grammars now record explicit clause-level strategies for coordination, possession, modality, perfect aspect, questions, relative clauses, and complement clauses in addition to word order and morphology.

The translation path is:

```text
English source
    -> deterministic English analysis
    -> normalized clause features
    -> generated grammar strategies
    -> target-language realization
    -> completeness validation
```

English auxiliary inversion is normalized before realization, so constructions such as `Can you ...?`, `Have they ...?`, and `Will she ...?` are realized according to the generated language's question strategy rather than copied from English. Imperative detection requires verbal evidence; exclamation punctuation alone does not create imperative mood. Noun-phrase realization is lemma-aware and supports inflected nouns, adjectives, possessive determiners, and simple possessive noun phrases.

Translation diagnostics remain the regression mechanism. `complete` means all recognized source features have realization receipts; `partial` means some recognized content was not realized; `unresolved-vocabulary` means a required concept is absent; and `unsupported-grammar` means the analyzer understood a construction that the deterministic realizer cannot yet safely express.

## Structured realization (v6.3)

v6.3 introduces an explicit intermediate representation (`ClauseIR`, `NPIR`, `PredicateIR`, and `PPIR`) and a conservative grammar-driven structured realizer. Supported simple clauses are parsed into semantic roles and grammatical features before target-language realization. Each successful structured realization records receipts for lexical and grammatical content; completeness validation uses those receipts to prevent silent loss of meaning. Sentences outside the current structured subset fall back to the established legacy realizer, while positively diagnosed complex constructions remain unsupported rather than being flattened.

## Translation status semantics (v6.3)

Translation diagnostics distinguish four outcomes:

- `ok` / Complete: every required lexical and grammatical feature has a realization receipt.
- `partial`: the construction is supported or recognized, but the deterministic realizer could not safely express every required feature. Surface output is withheld as `[PARTIAL]` when necessary.
- `unresolved-vocabulary`: a genuine lexical concept is absent from the language package; batch translation writes the automatic `*_missing_words.txt` queue when an addable lemma/POS can be inferred safely.
- `unsupported-grammar`: reserved for positively diagnosed constructions for which no deterministic realization strategy is implemented. A realizer pattern miss by itself is not classified as unsupported grammar.

This distinction is intentional: Empire Of Words does not count a translation as complete merely because it can produce plausible-looking target text.


## Translation-ready grammar generation (v6.4)

v6.4 validates a realization contract when a language is created. A grammar feature that advertises a particle or inflectional strategy must have the material required to realize it. Generated languages also receive analytic fallback particles for future, progressive, perfect, and imperative meanings. These fallbacks do not change the typological profile: native morphology remains preferred when present, while the fallback gives the deterministic translator a way to preserve an English grammatical meaning that the target language does not encode with the same inflection. Structured noun phrases also preserve lexical numerals.

## Structured realization and lexical convergence (v6.7)

v6.7 tightens the contract between generated grammar, the English analyzer, structured IR, and the target-language realizer. Modifiers, comparisons, coordinated noun phrases, possessors, numerals, tense/aspect/mood features, and question marking now carry explicit realization receipts. A translation is complete only when those represented features are actually realized.

Generated grammars now record an adverb derivation strategy. The default translation-ready strategy is zero derivation: when English `-ly` maps to an existing adjective lemma (for example `brightly` -> `bright`), the target may use that adjective form adverbially rather than requiring a redundant independent adverb root.

The missing-vocabulary loop is also stricter. Analyzer-confirmed absent lexemes are classified as missing vocabulary, and the batch `*_missing_words.txt` file uses contextual POS inference to make substantially more entries directly consumable by `add_words.py`. The intended cycle remains:

```cmd
python src\translate.py --language output\Example --input translations\sentences_advanced.txt --diagnostics
python src\add_words.py --language output\Example --words output\Example\translations\sentences_advanced_missing_words.txt --seed 67890
python src\translate.py --language output\Example --input translations\sentences_advanced.txt --diagnostics
```

After the second translation, a remaining missing-vocabulary count represents a real unresolved lexical-analysis case rather than a partial sentence hidden by legacy realization.


## Realization contract v4 (v6.7)
Generated languages now specify productive lexical conversion and noun-compound behavior in addition to the v6.6 morphosyntactic profile. The structured realizer also applies target article morphology and available grammatical cases. Lexical conversion is context-sensitive: it may satisfy a required verbal/adjectival sense from an existing semantic root, but it is not used as a generic predicate guess.


## v7.2: grammatical integrity

- Negation follows the generated particle/affix/mixed strategy, with one licensed marker per clause.
- Comparison audit includes negation, future tense, and number minimal pairs.
- Expanded English candidate lemmatization for inflected forms; no new roots are fabricated.
- Contract version 8 declares single-negation realization.

Run `python src/audit_languages.py --languages output/Test1 output/Test2 output/Example --output output/language_audit` after regenerating language packages.
