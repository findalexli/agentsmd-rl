# Add detailed eval metrics for signal matching step

## Problem

The e2e grouping eval in `products/signals/eval/eval_grouping_e2e.py` currently captures only a single `correct_match` binary metric for each signal's matching decision. This makes it impossible to separately evaluate:

1. **Pre-specificity accuracy** — how often the LLM matcher gets it right *before* the specificity judge intervenes.
2. **Query diversity** — whether the generated search queries are meaningfully different from each other (measured by pairwise cosine distance between query embeddings).
3. **Candidate diversity** — whether different queries retrieve distinct candidate sets (measured by 1 minus Jaccard similarity).

Additionally, the `SPECIFICITY_SPLIT` failure mode conflates two different things: it was used when the specificity judge split a correct match into a new report, but this is really just an `UNDERGROUP` caused by the specificity judge. The failure mode enum should only have `NONE`, `UNDERGROUP`, and `OVERGROUP`.

## Expected Behavior

1. The `MatchFailureMode` enum should have only three members: `NONE`, `UNDERGROUP`, `OVERGROUP`.
2. The `_match` method should return both the pre-specificity and post-specificity match results so they can be evaluated independently.
3. The `_capture_match_quality` method should emit four metrics per signal:
   - `correct_match` — post-specificity correctness (existing, but failure classification updated)
   - `correct_match_pre_specificity` — pre-specificity correctness
   - `query_diversity` — average pairwise cosine distance between query embeddings
   - `candidate_diversity` — average (1 − Jaccard) across candidate sets
4. The cosine distance computation currently inlined in `mock.py`'s `search` method should be extracted into a reusable `cosine_distance` static method on `EmbeddingStore`, and used by both search and the diversity calculation.
5. After making these code changes, update the `products/signals/eval/AGENTS.md` documentation to reflect the new metrics, remove `SPECIFICITY_SPLIT` references, and add HogQL query examples for the new measurements.

## Files to Look At

- `products/signals/eval/eval_grouping_e2e.py` — eval orchestrator with matching pipeline and metric capture
- `products/signals/eval/mock.py` — in-memory embedding store with cosine search
- `products/signals/eval/AGENTS.md` — documentation for the eval system including metric tables and SQL queries
