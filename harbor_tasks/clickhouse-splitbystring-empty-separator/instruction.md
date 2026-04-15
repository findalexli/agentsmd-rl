# Fix splitByString Tokenizer Empty Separator Validation

## Problem

The `splitByString` tokenizer in ClickHouse does not properly validate its input parameters. When users pass an empty string as one of the separators in the array argument, the tokenizer should reject it with a clear error message, but currently it accepts it silently.

For example, the following queries should be rejected with an error but are not:
```sql
SELECT tokens('  a  bc d', 'splitByString', ['']);
SELECT tokens('  a  bc d', 'splitByString', [' ', '']);
```

## Expected Behavior

The tokenizer should reject invalid separator inputs with `BAD_ARGUMENTS` errors and produce the following messages:

1. When an empty string is encountered as a separator: `"Incorrect parameter of tokenizer '{}': the empty string cannot be used as a separator"`
2. When the separators argument results in an empty array of valid separators: `"Incorrect parameter of tokenizer '{}': the separators argument cannot be empty"`

The old error message text `"separators cannot be empty"` must no longer appear anywhere in the tokenizer implementation — it should be replaced by message (2) above.

## Task

Fix the splitByString tokenizer's input validation so that empty separator strings are properly rejected and the correct error messages are produced.
