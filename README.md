# Empire Of Words
A set of Python scripts that allow a technically literate worldbuilder to create languages and language families for imagined worlds.

Based, in part, on Perl scripts originally created by Chris Pound, with additional inspiration from other conlanging sources.

Project layout:

```text
project/
├── src/
│   ├── build_language.py
│   ├── grammar_engine.py
│   └── lc.py
├── vocabulary/
│   └── MagicVocabulary.txt
├── data/
│   └── <base-language-corpus>.txt
└── output/
```

Run from the project root:

```cmd
python src\build_language.py --language-name "My Language" --seed 12345
```

If there is one `.txt` corpus in `data`, it is selected automatically. Otherwise specify it:

```cmd
python src\build_language.py vocabulary\MagicVocabulary.txt data\my_corpus.txt --language-name "My Language" --seed 12345
```

The scripts resolve defaults from the project directory, not the shell's current directory.

## Output

Each language receives its own directory under `output`:

```text
output/My_Language/
├── dictionary.csv
├── derivational_morphology.txt
├── etymology.txt
├── language.json
├── grammar.json
├── paradigms.csv
└── reference.md
```

`language.json` is the canonical machine-readable language package. `grammar.json` contains syntax and inflectional grammar. `paradigms.csv` applies noun and verb inflection to the generated lexicon. `reference.md` is a human-readable grammar summary.

## Grammar v2

The naturalistic generator currently establishes a coherent basic grammar rather than independently randomizing every feature:

- SOV/SVO/VSO basic constituent order (weighted)
- correlated prepositions/postpositions
- adjective position
- possessor position
- optional articles
- singular/plural
- nominative, accusative, genitive, dative
- present, past, future
- simple/progressive aspect
- morphological negation
- six independent personal pronouns
- language-native grammatical morphemes generated from the same Pound model as the vocabulary

This is deliberately a v2 foundation. It keeps derivational morphology separate from inflection so later translation code can inflect a lemma without creating spurious dictionary entries.

