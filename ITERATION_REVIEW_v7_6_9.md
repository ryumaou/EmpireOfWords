# Empire Of Words v7.6.9 — Conservative fronted adjunct handling

## Implemented

The structured parser now recognizes a **comma-delimited** leading prepositional adjunct such as `On the mountain, we see the cat.` and preserves the fronted PP as a first-class `PPIR` in the main predicate. Each generated grammar independently realizes its adposition and object. The source tokens are preserved for receipt checking.

The change deliberately does **not** claim support for the existing contrast-suite sentence `On a sunny morning we started for the mountains.`. That sentence lacks a comma, and its modifier `sunny` is not reliably representable in all existing packages. It remains partial instead of dropping the adjunct.

## Verified

- 86 automated unit tests pass.
- Example, Test1, and Test2 each retain 69 complete / 7 partial / 4 unsupported on the original 80-sentence contrast suite.
- New probe `On the mountain, we see the cat.` completes in all three languages and preserves ON, MOUNTAIN, SEE, CAT in the gloss.
- No language packages were regenerated.

## Next targets

Explicit proper-name/vocative handling, licensed interjection forms, and comparative preference questions. The source language lexicon must provide or derive valid target-language forms; avoid copying English names or silently dropping exclamations.
