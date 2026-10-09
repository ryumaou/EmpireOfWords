# v7.6.1 — Predicate-series preservation

The v7.6.0 contrast-suite baseline is 56/80 complete per language, 19 partial, 5 unsupported. The new parser handles comma-separated shared-subject action series without discarding intermediate predicates. Semantic fixtures test sentence #27 and #31. The audit fixture path now resolves relative to the script. Language build metadata now reports v7.6.1.

This is a constrained deterministic parser extension, **not** the proposed hybrid dependency-parser integration. The new output has not been benchmarked with user-generated language packages. No completion-rate improvement is claimed.
