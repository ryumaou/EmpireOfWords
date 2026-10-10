# Diagnostic-driven iterations — 2026-10-10

No applicable AGENTS.md was found in the repository or its ancestor locations.
The initial workspace contained extensive uncommitted changes. Validation uses
that workspace as the baseline; commits isolate the new implementation changes
and tests, rather than sweeping in the pre-existing changes.

## Validation baseline

- 95 regression tests and 11 semantic fixtures passed.
- Four existing languages: Example, Test1, Test2, MagicTest.
- Four immutable corpora: contrast (80), advanced (229), graded (1,097), default (11).
- 5,668 sentence/language combinations per validation round, plus the 18-probe
  language audit (72 translations, 20 grammatical fidelity checks).
- SHA256 snapshots cover all 65 existing files in the four language directories.
- Detailed diagnostics, JSON analyses, status gates, logs and snapshots are in
  `.iteration-work/`; no existing output file is overwritten.

## Iteration 1 — unpunctuated fronted adjuncts

An explicit nominative pronoun now bounds an initial prepositional phrase even
without a comma. A postnominal participle requires a preceding noun, preventing
the ambiguous lexical entry MORNING:v from displacing SUNNY MORNING:n.

Example, Test1 and Test2 each recover contrast #43 and advanced #74 and #83.
Contrast completeness rises from 70 to 71/80 and advanced completeness from
157 to 159/229. MagicTest stays at 70/80 and 121/229 respectively, with a corrected
contrast #43 surface retaining WE, ON, past tense and plural MOUNTAINS. Advanced
#103 / graded #328 now retain WE as subject and AT NOON as adjunct in the three
baseline languages. Graded and default coverage are unchanged.

97 regression tests, all 11 semantic fixtures, all four strict corpus gates and
all 20 grammatical fidelity checks pass. All 65 existing language files retain
their exact hashes. Successful translations with changed surfaces were reviewed
for subject, tense, number, and PP attachment.

A broader candidate requiring every participle to have a distinct lemma was
rejected: it lost two previously complete graded sentences per baseline language
(#157 and #584). Those cases expose noun/verb ambiguity and temporal-NP scope;
they need semantic accountability beyond the current lexical receipt sets.

The pre-existing untracked `test_v769_fronted_pp.py` was adjusted locally to use
an actually unavailable adjunct word for its failure check. Its prior sentence
is now a positive regression fixture in the new committed test file.

## Iteration 2 — punctuation inside discourse expressions

`Oh, dear!` now follows the existing `Oh dear!` discourse path, preserving the
original source, both interjection receipts, and the following clause's status.
Absent interjection forms still prevent completion; no language is extended.

Example, Test1 and Test2 each recover advanced #146 and graded #605. Advanced
coverage increases from 159 to 160/229; graded coverage from 352 to 353/1,097.
Contrast, default and MagicTest coverage are unchanged. MagicTest's corresponding
sentences stay incomplete because the required discourse forms are unavailable.

100 regression tests, 11 semantic fixtures, all four strict corpus gates and
20 grammatical fidelity checks pass. The only changes since iteration 1 are the
two punctuation-variant sentences in each language. All 65 language-file hashes
are unchanged. These commits are incremental to the original dirty workspace;
the pre-existing discourse handler remains uncommitted, as it was on entry.
