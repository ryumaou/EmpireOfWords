# Empire Of Words
A set of Python scripts that allow a technically literate worldbuilder to create languages and language families for imagined worlds.

Based, in part, on Perl scripts originally created by Chris Pound, with additional inspiration from other conlanging sources.

# Conlang Project v3

Project layout:

```
project/
├── src/
├── vocabulary/
├── data/
└── output/
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
