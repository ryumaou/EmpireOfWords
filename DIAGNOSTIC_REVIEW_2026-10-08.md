# Diagnostic review — v7.4

Three language runs each show 157 complete / 51 partial / 0 missing vocabulary /
21 unsupported out of 229. This is +1 complete compared with v7.3 and -1
compared with v7.2. Different grammar fingerprints and the audit's 18/18
minimal-pair probe results support grammatical differentiation, but do not
establish semantic correctness across the full corpus.

## Highest-priority implementation work

1. Build an English constituent representation for fronted adpositional phrases
   and embedded noun-phrase modifiers. Examples: #74, #76, #82, #83, #85.
2. Handle predicate and clause coordination without dropping the second verb,
   arguments, or conjunction. Examples: #134, #142, #143, #159.
3. Represent copular and auxiliary-inverted questions. Examples: #106, #113,
   #149, #171.
4. Preserve noun-number, inflection and lexical coverage in context. Examples:
   #79, #131, #179.
5. Implement separately tested appositive, relative, subordinate, and
   complement-clause representations before marking these as complete.

Do not replace structural fidelity with optimistic 'complete' classifications.
The new quality gate enforces no *new* status regressions by sentence and
language. A future semantic gate must additionally verify feature receipts.
