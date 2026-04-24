# Fix Empty Hybrid Search Result Handling

## Problem

LanceDB's hybrid search crashes with `IndexError: list index out of range` when applying hard filters that result in zero matches.

The crash occurs because empty result tables are passed through the full reranker pipeline, which expects at least one result to process. This happens when both `vector_results` and `fts_results` have `num_rows == 0`.

## Symptoms

- Search crashes with `IndexError: list index out of range`
- Crash happens in `python/python/lancedb/query.py`
- Occurs when both vector search and full-text search return zero results after filtering

## Expected Behavior

The code should gracefully handle empty result sets. When both `vector_results` and `fts_results` have zero rows:

1. Return early before the reranking logic executes
2. Return a properly constructed empty table that:
   - Has the `_relevance_score` column (required by downstream code)
   - Properly merges the schemas from both input tables using `vector_results.schema` and `fts_results.schema`
   - Respects the `with_row_ids` flag by dropping the `_rowid` column when `with_row_ids=False`
   - Uses `pa.unify_schemas()` for schema merging

## Key Files

- `python/python/lancedb/query.py`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
