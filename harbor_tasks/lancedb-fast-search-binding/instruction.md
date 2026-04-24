# Task: Add fast_search() method to LanceFtsQueryBuilder

## Problem

The `LanceFtsQueryBuilder` class in `python/python/lancedb/query.py` is missing a `fast_search()` method that should allow users to skip flat searches of unindexed data during full-text search (FTS) queries. This feature already exists in the underlying `Query` model (which has a `fast_search` field) and is already implemented in other query builders like `LanceVectorQueryBuilder`, but `LanceFtsQueryBuilder` lacks this capability.

Currently, attempting to call `.fast_search()` on an FTS query results in an AttributeError:

```python
table.search("query", query_type="fts").fast_search()  # AttributeError: 'LanceFtsQueryBuilder' object has no attribute 'fast_search'
```

## Expected Behavior

After the fix, users should be able to chain `.fast_search()` in FTS queries:

```python
table.search("query", query_type="fts").fast_search().limit(10).to_list()
```

The `fast_search()` method should:

1. Have a docstring explaining that it skips flat search of unindexed data (keywords: "unindexed" or "flat search")
2. Return the builder instance to allow method chaining
3. Have a return type annotation indicating it returns `LanceFtsQueryBuilder`
4. Pass the fast search setting through to the `Query` constructor in `to_query_object()`

## Hints

- Look at how other query builders (like `LanceVectorQueryBuilder`) implement `fast_search()` for reference
- The `Query` model already has a `fast_search` field defined
- The method should follow the same builder pattern as other methods like `phrase_query()`

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
