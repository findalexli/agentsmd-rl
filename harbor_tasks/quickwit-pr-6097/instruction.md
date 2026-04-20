# TermsQuery Numeric Values Task

## Background

Quickwit implements an Elasticsearch-compatible query DSL. The `TermsQuery` struct in `quickwit/quickwit-query/src/elastic_query_dsl/terms_query.rs` parses Elasticsearch-style terms queries from JSON.

## The Problem

The `TermsQuery` currently only accepts string values in term arrays. When a user submits a terms query with numeric values (as permitted by the Elasticsearch API), parsing fails with an error.

For example, this Elasticsearch query is valid:
```json
{ "user.id": [1, 2] }
```

But Quickwit rejects it because it only expects strings like `["1", "2"]`.

## Expected Behavior

The `TermsQuery` parser should accept the same input formats that Elasticsearch accepts:

- String values: `["alice", "bob"]`
- Numeric values: `[1, 2]`
- Mixed values: `["alice", 2]`

After parsing, the internal `values` field should be a `Vec<String>` with all values converted to their string representation.

## Verification

The fix is correct when:

1. A terms query JSON like `{"user.id": [1, 2]}` successfully parses
2. After parsing, `terms_query.values` contains `["1", "2"]` (not `["alice", "bob"]` — just convert integers to strings)
3. The field name `"user.id"` is preserved
4. All existing terms query tests continue to pass (no regressions)

### Test Requirements

Your implementation must include test functions that will be invoked by the test oracle:

- A test function named `test_terms_query_not_string` must exist in the `elastic_query_dsl::terms_query` module and pass when run via `cargo test -p quickwit-query --lib test_terms_query_not_string`
- A test function named `test_terms_query_single_term` must exist and pass via `cargo test -p quickwit-query --lib test_terms_query_single_term`

The test oracle runs these specific test function names to verify the fix.