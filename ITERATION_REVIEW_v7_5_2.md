# Empire Of Words v7.5.2 — conservative superlative parsing iteration

## Observed v7.5.1 contrast-suite results

All three languages: 54 complete, 21 partial, 0 missing vocabulary, 5 unsupported grammar (80 total). This is unchanged in complete count from v7.4, but the two missing vocabulary errors are resolved and relative clause #63 is now explicitly diagnosed as unsupported.

## Source fix

Structured parsing now recognizes definite superlative adjective predicates, e.g. `The dog is the biggest.` as an adjective complement with a superlative degree, not an ordinary noun phrase. This prevents the English article + superlative from being discarded before grammatical realization. Added three focused regression tests. This change does not imply full superlative translation for every generated grammar, nor does it fix the broader coordination, embedded PP, or question issues.

## Test priorities

1. Validate #58 across three generated grammars, checking actual output and semantic receipts (not just status).
2. Check #57 and #60 for degree realization and compare against v7.5.1.
3. Preserve #63 as unsupported until genuine relative-clause translation exists.
4. Next major work: coordination as a clause tree with separate subjects, predicates, and scopes; embedded PP noun phrases; question scope.

No end-to-end benchmark improvement is claimed without running the actual generated language packages.
