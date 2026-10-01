# Empire Of Words
A set of Python scripts that allow a technically literate worldbuilder to create languages and language families for imagined worlds.

Based, in part, on Perl scripts originally created by Chris Pound, with additional inspiration from other conlanging sources.

# Conlang Project v3

Project layout:

```
project/
├── src/
│   ├── build_language.py
│   ├── grammar_engine.py
│   └── lc.py
├── vocabulary/
│   └── MagicVocabulary.txt
├── data/
│   └── base_language.txt
└── output/
```

Run from the project root:

```
python src/build_language.py --language-name "Khudzul" --seed 12345
```

Or choose files explicitly:

```
python src/build_language.py vocabulary/MagicVocabulary.txt data/germanic.txt --language-name "Khudzul" --seed 12345
```

## v3 grammar features

In addition to v2 noun number/case, tense/aspect, syntax, pronouns, articles, and derivational morphology, v3 adds:

- subject agreement: 1/2/3 person × singular/plural
- demonstratives: proximal/distal × singular/plural
- interrogatives: who, what, where, when, why, how, which
- comparative and superlative adjective morphology
- genitive possessive constructions
- yes/no question particle and generated placement
- wh-question strategy (in-situ or fronted)
- imperative, subjunctive, and conditional moods
- generated example sentences with English, surface form, and interlinear-style morpheme gloss

## Output

Each language is written to `output/<LanguageName>/`:

- `dictionary.csv` — roots and derived vocabulary
- `derivational_morphology.txt` — vocabulary-building modifiers
- `etymology.txt` — derivational history and unresolved references
- `grammar.json` — machine-readable grammar
- `language.json` — canonical combined language package
- `paradigms.csv` — noun, verb/agreement/mood, and adjective comparison forms
- `examples.txt` — generated sentences and glosses
- `reference.md` — readable grammar reference plus examples

All grammatical forms are generated from the same Pound `lc` phonological model as the lexicon. The generator does not invent target-language words during sentence generation; examples are assembled from the generated lexicon and grammar.
