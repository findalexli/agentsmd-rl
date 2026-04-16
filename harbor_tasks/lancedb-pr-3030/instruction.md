# Fix Empty Hybrid Search Result Handling

## Problem

LanceDB's hybrid search crashes with `IndexError: list index out of range` when applying hard filters that result in zero matches. This happens in the `_combine_hybrid_results` method in `python/python/lancedb/query.py`.

The crash occurs because empty result tables are passed through the full reranker pipeline, which expects at least one result to process.

## Symptoms

- Search crashes with `IndexError: list index out of range`
- Crash happens in `lancedb/query.py` in the `_combine_hybrid_results` method
- Occurs when both vector search and full-text search return zero results after filtering

## Task

Modify the `_combine_hybrid_results` method to handle empty result sets gracefully. When both `vector_results` and `fts_results` have zero rows, the method should return early with a properly constructed empty table that:

1. Has the `_relevance_score` column (required by downstream code)
2. Properly merges the schemas from both input tables
3. Respects the `with_row_ids` flag (drops `_rowid` column if `with_row_ids=False`)

## Key Files

- `python/python/lancedb/query.py` - Contains the `_combine_hybrid_results` method

## Hints

- Look for the `_combine_hybrid_results` static method in the `LanceHybridQueryBuilder` class
- The method receives `vector_results` and `fts_results` as PyArrow tables
- PyArrow's `pa.unify_schemas()` can merge schemas from two tables
- The `_relevance_score` column should be of type `pa.float32()`
- Test your fix by creating empty tables and calling the method directly
