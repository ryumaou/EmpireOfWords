# v7.6.10 — vocabulary and realization preflight

This is a conservative instrumentation release, not a claim of new grammatical coverage.

- Adds `src/vocabulary_preflight.py`, a read-only report for existing language packages and a translation corpus.
- Separates `unresolved-vocabulary`, `partial`, and `unsupported-grammar`, and exposes the existing pipeline's diagnostic stage for each sentence.
- Lists missing tokens, occurrence counts, and English lemma candidates. Candidate lemmas are suggestions, **not** automatically generated dictionary entries.
- Does not regenerate language packages or modify their grammars or dictionaries.
- Adds three regression tests; retains all existing regression tests.

From project root:

```powershell
python src\vocabulary_preflight.py --language output\MagicTest --input translations\contrast_suite_v1.txt --output output\MagicTest\preflight_v7_6_10.json
python -m unittest discover -s tests -v
```

The ZIP includes the original three baseline language packages from v7.6.9. If you updated MagicTest locally after the previous release, retain your local MagicTest package: it is not included as an updated replacement in this archive.

Next implementation work: interjection segmentation, vocative/proper-name coordination, fronted phrases, and preference questions. No additional complete translations are claimed in this instrumentation release.
