# Fix sparseGrams Tokenizer Token-Length Bug

## The Problem

The `sparseGrams` tokenizer function generates tokens that exceed the `max_ngram_length` parameter when `min_ngram_length` is set to values other than 3.

## Symptom

Calling `tokens('hello world', 'sparseGrams', 5, 5)` returns tokens longer than 5 characters, when all tokens should be exactly 5 characters long (since min=5, max=5). The issue manifests as tokens that are 6 or more characters instead of being constrained to the specified maximum.

## Expected Behavior

After the fix:
- `tokens('abcde', 'sparseGrams', 5, 5)` returns `['abcde']`
- `tokens('hello world', 'sparseGrams', 5, 5)` returns only tokens of exactly 5 characters
- `arrayAll(t -> length(t) = 5, tokens('hello world', 'sparseGrams', 5, 5))` returns `1` (true)
- `tokens('abcdefgh', 'sparseGrams', 3, 5)` returns only tokens between 3 and 5 characters inclusive

## Technical Context

The sparseGrams tokenizer is implemented in `src/Functions/sparseGramsImpl.h`. The tokenizer maintains a convex hull data structure and computes token lengths during iteration. The length calculation involves the difference between `right_symbol_index` and `possible_left_symbol_index`, plus an offset derived from the n-gram length parameters.

## Verification

The fix can be verified by checking that all generated tokens respect the `max_ngram_length` constraint across different `min_ngram_length` settings:

```sql
SELECT tokens('hello world', 'sparseGrams', 5, 5);
SELECT arrayAll(t -> length(t) <= 5, tokens('hello world', 'sparseGrams', 5, 5));
SELECT arrayAll(t -> length(t) >= 5, tokens('hello world', 'sparseGrams', 5, 5));
SELECT tokens('abcdefgh', 'sparseGrams', 3, 5);
```
