# Empire Of Words

A set of Python scripts that allow a technically literate worldbuilder to create languages and language families for imagined worlds.

Based, in part, on Perl scripts originally created by Chris Pound, with additional inspiration from other conlanging sources.

Empire Of Words generates a language from a source text and an English vocabulary list. The resulting package contains a dictionary, grammar, inflectional paradigms, examples, and reference files. You can then translate supported English sentences, expand the vocabulary, evolve daughter languages, and generate names without rebuilding the original language.

The scripts require Python 3 and no third-party packages. Run the commands below from the project root. They use forward slashes, which Python also accepts on Windows. Choose a new language name when building so you do not overwrite an existing package.

## Create a language

The source text supplies character patterns for new words; the vocabulary file supplies English concepts. `vocabulary/MagicVocabulary.txt` is an example vocabulary, and entries such as `dog:n`, `run:v`, and `red:adj` can be added to your own file. Use `--seed` to reproduce the same build from the same inputs.

```sh
python -B src/build_language.py --language-name MyLanguage --source data/magic.txt --vocabulary vocabulary/MagicVocabulary.txt --grammar-family naturalistic --seed 12345
```

The package is written to `output/MyLanguage/`. Select a grammar profile with `--grammar-family` or override individual choices such as `--word-order SOV`, `--cases 5`, and `--morphophonemics none`. Run `python -B src/build_language.py --help` for all options.

To include another vocabulary file or seed words needed by a sentence collection during creation:

```sh
python -B src/build_language.py --language-name MyLanguageWithExtras --source data/magic.txt --vocabulary vocabulary/MagicVocabulary.txt --supplemental-vocabulary vocabulary/extra_words_example.txt --translations translations/sentences_default.txt --seed 12345
```

To build a different language with the same grammar, use the first package's `grammar.json`:

```sh
python -B src/build_language.py --language-name RelatedLanguage --source data/magic.txt --vocabulary vocabulary/MagicVocabulary.txt --grammar-file output/MyLanguage/grammar.json --seed 54321
```

## Translate English

Translate a single sentence or a text file using an existing package:

```sh
python -B src/translate.py --language output/MyLanguage --sentence "The dog sees the cat."
python -B src/translate.py --language output/MyLanguage --input translations/sentences_default.txt --diagnostics
```

Batch output is written under `output/MyLanguage/translations/` by default. Diagnostics show completed, partial, unsupported, and missing-vocabulary cases. The translator reports constructions it cannot safely express; it does not guarantee correct translation of arbitrary English.

## Expand vocabulary

Create a UTF-8 text file with one independent `gloss:pos` entry per line, such as `robin:n` or `wander:v`, then add its roots to an existing language:

```sh
python -B src/add_words.py --language output/MyLanguage --words vocabulary/my_words.txt --seed 67890
```

Existing words and grammar are preserved. The package records the additions and keeps a backup of its previous `language.json`. For derived entries, edit a vocabulary definition and build a new language.

## Validate and compare languages

Validate a package, optionally against an English sentence file:

```sh
python -B src/validate_language.py --language output/MyLanguage
python -B src/validate_language.py --language output/MyLanguage --translations translations/sentences_default.txt
```

Compare generated packages and their grammar behavior:

```sh
python -B src/audit_languages.py --languages output/MyLanguage output/RelatedLanguage --output language_audit
```

## Create a language family

Evolve a daughter language from an existing package. The daughter records inherited forms, sound changes, lexical innovations, and its parent language.

```sh
python -B src/generate_daughter.py --parent output/MyLanguage --language-name DaughterLanguage --profile balanced --seed 24680
```

Profiles are `conservative`, `balanced`, and `divergent`. You can also set `--sound-rules`, `--lexical-replacement`, and `--grammar-drift`. Generate multiple daughters from one parent to create branches.

## Generate names

Personal names follow the language's word shapes. Family and clan names combine concepts from `vocabulary/NamingVocabulary.txt` using the language's actual words. Full names combine both.

```sh
python -B src/generate_names.py --language output/MyLanguage --mode personal --count 50 --seed 12345
python -B src/generate_names.py --language output/MyLanguage --mode family --naming-vocabulary vocabulary/NamingVocabulary.txt --count 50 --seed 12345
python -B src/generate_names.py --language output/MyLanguage --mode full --count 25 --seed 12345
```

Results are written under `output/MyLanguage/names/` by default.

## Check the installation

```sh
python -B src/verify_install.py
python -B -m unittest discover -s tests -q
```
