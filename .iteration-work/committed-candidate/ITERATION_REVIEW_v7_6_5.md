# v7.6.5 — interrogative scope and inverted copula groundwork

- Preserve the outer yes/no question type when splitting coordinated predicates or independent clauses. Previously punctuation was stripped before recursion, losing the interrogative scope for #55.
- Retain temporal adverb subjects in inverted copular questions (#14), with explicit lexical adverb realization rather than pretending a temporal adverb is a normal noun.
- Added semantic fixtures for coordinated question scope and copular temporal question.
- The five complex constructions (#61–65) remain intentionally unsupported: causal subordinate, conditional, relative, complement, passive. They need semantic IR and grammatical realization rather than completeness bypasses.
- Degree WH questions (#17) and comparison questions (#59) are not yet implemented.
- Existing generated language packages can be reused.
