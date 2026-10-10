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

Example, Test1 and Test2 each recover advanced #146 and graded #455. Advanced
coverage increases from 159 to 160/229; graded coverage from 352 to 353/1,097.
Contrast, default and MagicTest coverage are unchanged. MagicTest's corresponding
sentences stay incomplete because the required discourse forms are unavailable.

100 regression tests, 11 semantic fixtures, all four strict corpus gates and
20 grammatical fidelity checks pass. The only changes since iteration 1 are the
two punctuation-variant sentences in each language. All 65 language-file hashes
are unchanged. These commits are incremental to the original dirty workspace;
the pre-existing discourse handler remains uncommitted, as it was on entry.

## Iteration 3 — semicolon-separated commands

Mixed comma/semicolon action series now preserve TAKE, CARRY and WAIT as three
imperatives, each with its own arguments. The extension is limited to overt
verb-initial commands; independent subjects cannot be silently inherited.
Advanced #142 and graded #449 recover in all four languages (eight additional
sentence/language recoveries). Final coverage is:

| Language | Contrast /80 | Advanced /229 | Graded /1,097 | Default /11 |
|---|---:|---:|---:|---:|
| Example | 70 → 71 | 157 → 161 | 352 → 354 | 11 → 11 |
| Test1 | 70 → 71 | 157 → 161 | 352 → 354 | 11 → 11 |
| Test2 | 70 → 71 | 157 → 161 | 352 → 354 | 11 → 11 |
| MagicTest | 70 → 70 | 121 → 122 | 300 → 301 | 11 → 11 |

The committed discourse punctuation implementation now directly checks both
interjections and the following clause, so it does not require the pre-existing
uncommitted discourse handler. The fronted-pronoun path also handles its own
comma-delimited variant. No pre-existing source change is swept into the commits.

A broader fronted-phrase candidate passed all status gates but falsely recovered
advanced #168 / graded #633: it represented DRESS as a noun coordinated with NIGHT
instead of a second predicate. That semantic regression was rejected, the parser
boundary narrowed, and a negative regression fixture added. The false gains are
not included in the final table.

Final validation: 103 regression tests, 11 semantic fixtures, four strict corpus
gates (5,668 translations), 72 language-audit probes and 20 grammatical fidelity
checks. All pass; zero newly non-complete sentences. All 65 existing language
files have unchanged hashes. There are 23 recovered sentence/language combinations
overall; these include the same English examples repeated across separate corpora.
The isolated staged checkout also passes all 86 of its committed regression tests.
Machine-readable counts, corpus identities, per-sentence recoveries, source
fingerprints and preservation hashes are in `diagnostics/iteration_2026_10_10.json`.

## Boundary for the next major revision

Per the user's instruction, pause before the next major version revision.
No major version bump or architecture rewrite was started. The nine remaining
contrast failures in Example/Test1/Test2 are accounted for:

- #24: named subjects have no attested lexical forms or explicit borrowing policy.
- #59: preference/alternative questions need choice scope and comparative-adverb
  semantics; assigning a yes/no question receipt is insufficient.
- #62–65: conditional, relative, complement and passive constructions need embedded
  clause, argument/gap and voice representations plus validated realization.
- #66, #67, #69: AHA, ALAS and MADAM are absent from the immutable packages.
  MagicTest also lacks the required OH DEAR interjection forms (#68), for ten
  remaining contrast failures. No replacement roots were invented.

Broader corpus failures additionally expose predicate-versus-noun ambiguity,
NP/PP attachment, temporal noun phrases, elliptical comparisons, object/complement
roles, apposition and quotations. For example, ENOUGH exists only as a determiner
in Example, while WARM has both adjective and noun entries. Resolving "Are you
warm enough now?" requires degree scope and typed lexical realization, not simply
allowing the existing determiner form to count as an adverb.

The next major revision should introduce source-span and role-aware receipts,
typed constituent/valency parsing, scoped coordination and explicit alternative
question/embedded-clause IR. The rejected DRESS gain demonstrates why more broad
regex coverage is unsafe with the current set-of-lemmas completeness guard.
Missing vocabulary remains a separate limit under the preservation constraint.
Not all supplied sentences pass; the stopping point is this structural boundary,
not a claim that coverage or semantic verification is exhaustive.
