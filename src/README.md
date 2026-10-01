# Christopher Pound Language Tools — Faithful Python Ports

These Python scripts are based directly on the four supplied Perl files.

## `lc.py`

Port of `lc.pl`, Christopher Pound's language confluxer.

The core algorithm is preserved: it builds a table keyed by two-character
pairs. Every character observed after a pair is appended to that pair's
possible continuations, so duplicate observations naturally weight the random
choice. Word starts are recorded separately. Generated words are Markov-like
walks through those pair transitions.

Original-compatible command:

```bash
python lc.py -50 source.txt
```

Statistics/hash mode:

```bash
python lc.py -s source.txt
```

Modern syntax with reproducible Python random seed:

```bash
python lc.py 50 source.txt --seed 1234
```

The Perl defaults `min_length=3` and `max_length=7` are preserved.

## `new_lc.py`

Port of the supplied `new-lc.pl`. It is the same basic conflux algorithm as
`lc.pl`, but writes directly to a named output file.

Original-compatible command:

```bash
python new_lc.py -25 language.txt source.txt
```

Modern:

```bash
python new_lc.py 25 language.txt source.txt --seed 1234
```

## `fix.py`

Port of `fix.pl`.

It chooses a single random affix length of 2, 3, or 4 characters. It then
extracts about one affix per ten input words. One third of candidates come from
word beginnings and two thirds from endings. Candidates must contain at least
one of `aeiouy`.

About half of the original words are printed unchanged. The other half receive
one randomly selected derived prefix or suffix. When two vowels would collide
at the join, one vowel is removed just as in the Perl script.

```bash
python lc.py -100 source.txt | python fix.py
```

A `--seed` option was added only to make Python runs reproducible.

## `prop.py`

Port of `prop.pl`, which creates proper names.

It counts `a e i o u` in every input word. Words with fewer than 3 vowels go
into the short-name pool; words with 3 or more go into the long-name pool.
The larger pool is truncated to the smaller pool's size. One word is popped
from each pool, the first ASCII letter is capitalized, and the two components
are printed in random order.

```bash
python lc.py -500 source.txt | python prop.py
```

The original cutoff is 3 vowels. A `--vowel-cutoff` option is provided for
experimentation while retaining 3 as the default.

## Typical pipelines

Generate vocabulary:

```bash
python lc.py -100 source.txt
```

Generate vocabulary and make it look more language-like:

```bash
python lc.py -100 source.txt | python fix.py
```

Generate proper names:

```bash
python lc.py -500 source.txt | python prop.py
```

Generate a reusable language file:

```bash
python new_lc.py -500 language.txt source.txt
python fix.py language.txt > language-fixed.txt
python prop.py language.txt > proper-names.txt
```

## Fidelity notes

The algorithms, constants, and important quirks of the supplied Perl are
preserved. The Python ports add:

- UTF-8 file handling
- argparse/help output
- optional `--seed` for reproducible testing
- useful error messages instead of undefined behavior/infinite recursion

Python and Perl use different pseudorandom-number generators, so an identical
numeric seed does NOT imply byte-for-byte identical random output. The intended
algorithm and probability weighting are the same.

## Windows / legacy corpus encoding

The ports now read source files as UTF-8 when valid and otherwise fall back to
Windows-1252. They never use Unicode replacement characters to hide decoding
errors. Standard input/output/error are explicitly configured as UTF-8, which
keeps Python-to-Python pipelines such as the following independent of the
Windows console code page:

```bash
python lc.py -100 source.txt | python fix.py
python lc.py -500 source.txt | python prop.py
```

This specifically fixes the `UnicodeEncodeError` involving U+FFFD that could
occur when an older Windows-1252 corpus was initially decoded as UTF-8 with
replacement enabled.
