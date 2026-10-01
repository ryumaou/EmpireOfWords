# Empire Of Words
A set of Python scripts that allow a technically literate worldbuilder to create languages and language families for imagined worlds.

Based, in part, on Perl scripts originally created by Chris Pound, with additional inspiration from other conlanging sources.

# Conlang Project v5

Project layout:

```
project/
├── src/
├── vocabulary/
├── data/
└── output/
```

## Selecting source and vocabulary files

The preferred interface explicitly selects the base-language corpus and vocabulary definition:

```
python src/build_language.py --language-name "Khudzul" --source data/Khudzul.txt --vocabulary vocabulary/MagicVocabulary.txt --grammar-family germanic --seed 12345
```

`--source FILE` selects the source/base language corpus that the Pound model analyzes. `--vocabulary FILE` selects the vocabulary definition to generate. Relative paths are resolved from the project root, not the current working directory.

If either switch is omitted, the builder auto-selects only when exactly one candidate exists in the corresponding directory. If multiple vocabulary or source files exist, it stops and lists them so you can select one explicitly. The older positional `vocabulary corpus` syntax remains supported for compatibility.

Examples:

```
python src/build_language.py --language-name "Test One" --source data/Kusan.txt --vocabulary vocabulary/MagicVocabulary.txt --grammar-family turkic
python src/build_language.py --language-name "Test Two" --source data/Ardunaic.txt --vocabulary vocabulary/BasicVocabulary.txt --grammar-family romance
```

## Basic use

```
python src/build_language.py --language-name "Khudzul" --seed 12345
```

The default `naturalistic` mode selects a coherent grammar family. Choose one explicitly:

```
python src/build_language.py --language-name "Ardunaic" --grammar-family romance --seed 12345
python src/build_language.py --language-name "Khudzul" --grammar-family turkic --seed 12345
```

Families: `naturalistic`, `random`, `romance`, `germanic`, `slavic`, `arabic`, `turkic`, `japanese`, `celtic`, `latin`, `greek`, `indic`, `bantu`, `polynesian`, `analytic`, `agglutinative`, `fusional`, `isolating`.

These are typological inspirations, not replicas of real languages. A family sets weighted defaults; the seed still creates variation.

## Override the family

```
python src/build_language.py --language-name "Khudzul" --grammar-family germanic --word-order SOV --adjective-position after --cases 5 --gender none --seed 12345
```

Available controls:

```
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

`--grammar-morphology` is separate from `--grammar-family`, so hybrids are possible:

```
python src/build_language.py --grammar-family romance --grammar-morphology agglutinative --language-name "Hybrid"
```

## Reuse an exact grammar

Every generated language writes `output/<Language>/grammar.json`. Feed it back later:

```
python src/build_language.py --language-name "Khudzul2" --grammar-file output/Khudzul/grammar.json --seed 54321
```

When `--grammar-file` is supplied, family and grammar override switches are ignored. This lets you keep the exact grammatical architecture while generating a new lexicon from another corpus/seed.

## Outputs

As in v3: `dictionary.csv`, `derivational_morphology.txt`, `etymology.txt`, `grammar.json`, `language.json`, `paradigms.csv`, `examples.txt`, and `reference.md` under `output/<LanguageName>/`.

# Version 5: expanded grammar families and morphophonemics

Version 5 adds typological grammar presets and a surface morphophonemic layer. Family names are inspirations/profiles, not claims to reproduce any one natural language exactly.

## Additional grammar families

In addition to the v5 families, `--grammar-family` now includes:

- `semitic` — VSO/SVO weighting, gender, aspect-rich verbs, fusional/mixed morphology; light templatic stem alternation and vowel elision.
- `uralic` — SOV/SVO weighting, postpositions, many cases, agglutination; vowel harmony and boundary assimilation.
- `kartvelian` — SOV/SVO, postpositions, rich verbal agreement/TAM; consonant assimilation and epenthesis.
- `caucasian` — SOV-heavy, high case counts, possible noun classes and complex agreement; consonant-cluster repair/assimilation.
- `austronesian` — verb-initial/SVO weighting, analytic-to-agglutinative morphology; productive light reduplication and nasal assimilation.
- `dravidian` — strongly SOV/postpositional, case-rich and agglutinative; light vowel harmony and assimilation.
- `iranian` — SOV-heavy, mixed/fusional morphology; vowel elision and lenition.
- `sino-tibetan` — SVO/SOV weighting, mostly analytic/isolating grammar and particles. Tonogenesis is not simulated from a non-tonal Pound corpus.
- `berber` — VSO/SVO weighting, gender and aspect-rich verbal grammar; vowel elision and assimilation.
- `quechuan` — strongly SOV/postpositional, case-rich agglutination and agreement; light harmony and assimilation.

The existing families also receive default morphophonemic profiles. Examples include `turkic`/`uralic` vowel harmony, `celtic` initial mutation/lenition, `slavic` palatalization, `romance` elision/assimilation, `germanic` light ablaut, and `arabic`/`semitic` conservative templatic-style stem alternation.

## Morphophonemic switch

By default, the selected family chooses its associated rules:

```cmd
python src\build_language.py ^
  --language-name "Example" ^
  --source data\Source.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --grammar-family uralic ^
  --morphophonemics auto ^
  --seed 12345
```

Disable surface morphophonemics while retaining the grammar family:

```cmd
--morphophonemics none
```

Or explicitly select one or more comma-separated rules:

```cmd
--morphophonemics vowel_harmony,consonant_assimilation
```

Supported rules are:

`vowel_harmony`, `vowel_harmony_light`, `initial_mutation`, `lenition`, `elision`, `vowel_elision`, `palatalization`, `consonant_assimilation`, `nasal_assimilation`, `epenthesis`, `reduplication`, `ablaut`, and `templatic_light`.

These rules apply to generated grammatical morphology. The canonical morphemes remain recorded separately in `grammar.json`, while paradigms and examples contain their realized surface forms.

## Hybrid examples

Romance-like grammar with Uralic-style harmony:

```cmd
python src\build_language.py ^
  --language-name "HybridOne" ^
  --source data\Ardunaic.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --grammar-family romance ^
  --morphophonemics vowel_harmony,consonant_assimilation
```

Celtic-like grammar without mutation:

```cmd
python src\build_language.py ^
  --language-name "HybridTwo" ^
  --source data\Kusan.txt ^
  --vocabulary vocabulary\BasicVocabulary.txt ^
  --grammar-family celtic ^
  --morphophonemics none
```

Austronesian-like grammar with explicit reduplication:

```cmd
python src\build_language.py ^
  --language-name "IslandSpeech" ^
  --source data\IslandSource.txt ^
  --vocabulary vocabulary\MagicVocabulary.txt ^
  --grammar-family austronesian ^
  --morphophonemics reduplication,nasal_assimilation
```

## Design limitation

`templatic_light` is intentionally conservative. The Pound source model generates whole roots rather than abstract consonantal roots, so v5 performs recognizable internal vowel alternation instead of pretending to implement a full Arabic/Hebrew root-and-pattern system. A future dedicated consonantal-root generator could make that behavior substantially deeper.
