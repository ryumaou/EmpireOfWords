# v7.6.6 translation engine iteration

Baseline from user v7.6.5 diagnostics: 65 complete, 10 partial, 5 unsupported out of 80 for each language.

## Changes
- Parse HOW + adjective + inverted BE questions with explicit degree scope and adjective complement.
- Realize degree questions with the target language’s generated HOW interrogative and WH placement.
- Parse causal BECAUSE clauses into a separate subordinate ClauseIR for semantic inspection.

## Deliberate limitation
The causal subordinate construction remains unsupported for surface translation until a target-language linker strategy is specified. The other four unsupported constructions are unchanged. Do not infer a new 80-sentence score from unit tests alone.
