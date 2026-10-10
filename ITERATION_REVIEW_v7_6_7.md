# v7.6.7: Causal subordinate-clause realization

The deterministic realizer now supports the **because** causal relation when the generated grammar explicitly licenses a subordinate particle and placement. Both clauses must independently realize successfully. The completeness guard continues to classify other diagnosed constructions as unsupported. A causal construction is exempted from unsupported status **only** when a structured realization emits a `causal_relation` receipt.

The grammar contract uses `subordinate_clause.strategy=particle`, `subordinate_clause.position=before|after`, and `particles.subordinate`. `before` places the linked reason clause before the main clause; `after` places it after. This is a first implementation of causal subordination, not arbitrary nested subordination.

Run the 80-sentence suite on Example, Test1 and Test2 to validate #61. No language rebuild is necessary.
