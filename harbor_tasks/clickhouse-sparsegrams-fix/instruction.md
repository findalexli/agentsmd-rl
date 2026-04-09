# Fix sparseGrams Tokenizer Length Bug

The `sparseGrams` tokenizer in ClickHouse is generating tokens that are longer than the specified maximum length. This is a bug in the tokenizer implementation.

## Symptom

When using `tokens('hello world', 'sparseGrams', 5, 5)` (min_length=5, max_length=5), some generated tokens have length greater than 5 characters, violating the max_length constraint.

## Location

The bug is in `src/Functions/sparseGramsImpl.h` in the `calculateRemoveBatch` method.

## What to Fix

The length calculation for ngrams uses a hard-coded value that doesn't respect the `min_ngram_length` parameter. The calculation needs to use the minimum ngram length parameter to correctly compute token lengths.

Look for the `calculateRemoveBatch` method and examine how `length` is calculated in the two `while` loops that process the convex hull. The hard-coded `+ 2` should be replaced with a calculation based on `min_ngram_length`.

## Testing

After the fix, the tokenizer should respect the max_ngram_length parameter:
- All tokens generated with `tokens('hello world', 'sparseGrams', 5, 5)` should have length <= 5
- All tokens should also have length >= 5 (the min_ngram_length)

## Hints

- The fix involves changing how `length` is computed in two places within `calculateRemoveBatch`
- The calculation involves `right_symbol_index`, `possible_left_symbol_index`, and `min_ngram_length`
