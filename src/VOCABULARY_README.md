# Pound Vocabulary Builder v1

Generates a full conlang dictionary from a `MagicVocabulary.txt`-style semantic vocabulary while using the faithful Christopher Pound `lc.py` transition model for the language's phonological character.

## Files

- `build_language.py` — vocabulary/derivation builder
- `lc.py` — tested faithful Python port of Christopher Pound's `lc.pl`

## Basic use

Put these files in the same directory as your vocabulary and source-language corpus, then run:

```cmd
python build_language.py MagicVocabulary.txt corpus.txt --seed 12345
```

Outputs:

- `generated_language.csv` — English/POS/generated form/root-or-derived/derivation
- `generated_language_morphology.txt` — the language-wide forms assigned to uppercase modifiers
- `generated_language_etymology.txt` — every derived form and its source expression, plus unresolved references

Choose your own filenames:

```cmd
python build_language.py MagicVocabulary.txt corpus.txt --seed 12345 --output Khudzul.csv --morphology Khudzul_morphology.txt --etymology Khudzul_etymology.txt
```

## How it works

1. Parses ordinary entries such as `water:n` as independent base vocabulary.
2. Parses uppercase modifier definitions such as `ACT.OF = Random` and `DOER = IF \\V THEN -er ELSE -r`.
3. Uses the same two-character transition model as `lc.py` to generate unique roots for independent entries.
4. Assigns each `Random` modifier one stable language-wide prefix or suffix generated from the same model. Bound morphemes may be one letter.
5. Preserves explicit modifier rules from the vocabulary. In the supplied vocabulary, the special `DOER` conditional suffix is therefore preserved rather than silently randomized.
6. Recursively resolves derived entries and compounds, including POS-qualified references such as `paint:v-DOER` and chains that reference earlier derived words.
7. Handles hyphens inside lexical glosses by resolving expressions against the actual vocabulary instead of blindly splitting every hyphen.
8. Enforces at least two ordinary A-Z letters in every independent generated root/form. Generated visible forms are plain Latin A-Z.
9. Writes unresolved references to the etymology report rather than guessing what the source intended.

## Reproducibility

Use `--seed` to reproduce a language exactly from the same vocabulary, corpus, script version, and options.

## Root length

Defaults preserve the faithful `lc.py` behavior: `--min-root 3 --max-root 7`. Because Pound's original termination test is `length > min`, the practical minimum generated root is normally four characters.

You can change the maximum, for example:

```cmd
python build_language.py MagicVocabulary.txt corpus.txt --seed 12345 --max-root 8
```

## Important: corpus size

A large vocabulary needs a sufficiently rich corpus to generate thousands of unique roots. The builder intentionally stops with an error rather than silently reuse a root if the corpus/model cannot supply enough unique forms.

## Current source-data findings for MagicVocabulary.txt

The v1 stress test parsed 5,430 vocabulary entries: 4,770 independent roots and 660 derived entries, with 22 uppercase modifier definitions. It resolved 657 derived entries. The remaining primary source references were intentionally not guessed:

- `hairy:adj = hair-RELATING.TO` — no exact `hair` base entry; the source has `hair (of body)` and `hair (of head)`.
- `Spell of Detecting Fumes:n = SPELL-know-smell` — one referenced lexical component cannot be resolved from the supplied vocabulary.
- `hairy (cantrip)` consequently depends on the unresolved `hairy:adj` entry.

Correcting those references in the vocabulary should allow them to resolve on the next run.
